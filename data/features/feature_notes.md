# Feature engineering notes (Part C)

## 1. Input data and train/test split
- Input: `data/clean/books_clean.csv` (175 rows and 10 columns).
- Combined each book's `title` and `description` into `text` (filled missing values with `""`).
- Merged the split from `data/features/split.csv` with the dataframe on `book_id`. `split.csv` is defined by Stage D (`notebooks/d_modeling.ipynb`) using `train_test_split` (`test_size=0.2`, `stratify=category`, `random_state=42`), giving 140 train / 35 test books with 62.9% Nonfiction and 37.1% Fiction.
- We only fit on `train_texts` to build the word columns using information from the training set only (only the unique words from the training books can be turned into columns). That way, when all 175 book rows are created with `transform`, the model only has information from the training set to apply to the test set, preventing any information from leaking from the test set.

## 2. Word-count features (`features_word_counts.csv`)
- Build the first feature set file in which each row represents the book with occurrences of each word.
- Used `CountVectorizer(stop_words="english", min_df=2)`:
  - Learn word columns from training books only (`fit(train_texts)`).
  - Count those words in all books (`transform(df["text"])`).
  - Create a dataframe in which each row is like a vector, the first entry is the `book_id`, the rest is the number of occurrences of the word of that column.
- Why `stop_words="english"` and `min_df=2`:
  - `stop_words="english"`: Words like "the", "and", "is", "to", "of" are English grammar filler words (stop words). They appear in every single book (both Fiction and Nonfiction), so they don't help predict the book's category at all. Removing them keeps only meaningful words.
  - `min_df=2` (minimum document frequency = 2 books): Only keeps words that appear in at least 2 training books. If a word only appears in 1 single book (like a specific character's name or a random typo), it cannot help the model recognize patterns across other books, and it adds thousands of useless columns (noise).
- Output: `data/features/features_word_counts.csv` (175 rows × 2115 columns, indexed by `book_id`).

## 3. TF-IDF features (`features_tfidf.csv`)
- Build the second feature set file in which each vector/row represents the book and the importance of each word.
- Used `TfidfVectorizer(stop_words="english", min_df=2)`:
  - Learns vocab and calculates rarity weight of each word from training books (`fit(train_texts)`).
  - Calculates the TF-IDF value for each word in every book (`transform(df["text"])`).
- TF-IDF puts more importance on words that are rarer across all training books and appear many times in the book. It is useful compared to raw word counts because those words usually describe the subject or genre of that book, hence an important factor in classifying the book as either Fiction or Nonfiction.
- Output: `data/features/features_tfidf.csv` (175 rows × 2115 columns, indexed by `book_id`).
- Top highest-weighted words for Fiction unique from Nonfiction: secrets, daughter, wife, son, novel
- Top highest-weighted words for Nonfiction unique from Fiction: god, people, america, readers, work

## 4. Image features (`features_images.csv`)
- Build the third feature set, in which each row represents the cover image's RGB color mean, standard deviation and distribution of color intensity.
- For each book cover in `image_path`:
  - Resizing to 64×64 standardizes the varying cover resolutions into a uniform 4,096-pixel grid and speeds up computation
  - Converts the image into the 3-dimensional array of numbers (64 rows, 64 columns, 3 color values) and divides each entry by 255.0 so the value ranges from 0 to 1 in decimal.
  - `r_mean, g_mean, b_mean`: how red/green/blue the picture in 64x64 is on average.
  - `r_std, g_std, b_std`: how different is the red/green/blue of every pixel from the mean red/green/blue of the image.
  - `r_bin_0–r_bin_7, g_bin_0–g_bin_7, b_bin_0–b_bin_7`: for each color there are 8 bins, each bin showing what fraction of pixels in the cover is in that range of color intensity
- Why we extract image features:
  - Each book on the website has both text (`title` + `description`) and a cover image.
  - In Stage B (EDA), simple brightness alone was a weak signal, so we want to test text-only vs. image-only vs. both combined.
  - By extracting the average RGB colors (`r_mean, g_mean, b_mean`), color contrast (`r_std, g_std, b_std`), and fraction of pixels having the intensity (`r_bin_0–r_bin_7, g_bin_0–g_bin_7, b_bin_0–b_bin_7`) into `features_images.csv`, Stage D can test whether book cover colors/contrast can predict Fiction vs. Nonfiction on their own, or if combining image features with text features improves the model's accuracy.
- Output: `data/features/features_images.csv` (175 rows × 30 columns, indexed by `book_id`).
