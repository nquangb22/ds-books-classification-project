# Cleaning log (Part B)
## 1. Raw data
- Source: data/raw/books_raw.csv (scraped on 25 October 2026)
- Total 175 books: 110 Nonfiction, 65 Fiction (~63/37, imbalanced)
- 13 columns, no missing values, types already correct
- 0 duplicate UPCs / book_ids, 0 failed pages, 0 missing images
## 2. Descriptions
Problem 1: "...more" at the end
- Found: 171/175 descriptions end with "...more"
- Meaning: leftover website text, which would become a fake "common word"
- Solution: removed it

Problem 2: repeated text
- Found: 167/175 start with a cut-off preview, then the full text again
- Meaning: words counted twice, inflates length features
- How detected: first 50 characters appear again later in the text
- Done: kept only the full (second) copy
- Check after cleaning: 0 repeats, 0 "...more"
- Avg length: 1598 -> 1231 characters (-23%)

Odd cases:
- 4 books had no “...more”: 3 normal short descriptions (untouched) + Kindle 
- 4 books had “...more” but no repeated preview (171 vs 167): only “...more” was stripped
- Kindle Paperwhite User’s Guide: description = title (placeholder), set to empty, row kept
## 3. Language 
- Detected: 173 en, 1 fr (Soumission, kept), 1 none (Kindle)
## 4. Columns
- Dropped columns: price_incl_tax, num_reviews, availability
- Why: price_incl_tax is identical to price, while num_reviews is always 0. Availability is just store property
- Kept price/rating: class means nearly equal, random according to the site 
## 5. Output
- Saved books_clean.csv, 175 rows × 10 columns 
- 10 columns are book_id, upc, title, category, description, lang, image_path, price, rating, product_url.
- Empty description = no description; fill with '' before vectorizing
## 6. EDA
Class balance:
- Nonfiction 62.9%, Fiction 37.1%
- Majority-class baseline = 62.9% accuracy -> D should also report F1 / balanced accuracy
- desc_len and brightness are EDA-only, not saved

Description length (characters after cleaning):
- Median: Fiction 1067, Nonfiction 1235
- Nonfiction more spread out (std 700 vs 382), outliers up to ~4900
- Middle 50% overlap heavily -> length alone is a weak signal
- Plot saved: report/desc_length_by_category.png

Images:
- 0 broken, all RGB
- Sizes vary (widths 115-318 px, heights vary too) -> resize before pixel features
- Brightness (grayscale mean, 0-255): Fiction 137, Nonfiction 148
- Std ~55-61 in both classes -> big overlap, weak signal

Price / rating:
- Class means nearly equal (see section 4), random according to the site

Takeaway for C and D:
- Simple features (length, brightness, price, rating) barely separate the classes
- Main signal is probably in the description words -> focus on text features
- Worth testing: text only vs image only vs both