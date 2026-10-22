# Books Classification: Fiction vs Nonfiction

Group project for the Data Science course (University of Turku).
We scrape book data from [books.toscrape.com](http://books.toscrape.com/), engineer features, and train a binary classifier to predict whether a book is **Fiction** or **Nonfiction**.

**Deadline:** November 2 (final report as PDF on Moodle, 4-6 pages, max 2 images)

## Team and roles

| Stage | Owner                  | Main output | Report section |
|---|------------------------|---|---|
| A. Scraping | `Khanh Hung Doan`      | `data/raw/books_raw.csv`, `data/raw/images/` | Data Scraping |
| B. Cleaning + EDA | `Nhat Quang Bui`       | `data/clean/books_clean.csv` | Data Cleaning and Analysis |
| C. Feature engineering | `Doan Nhan Ta`         | `data/features/` | Feature Engineering |
| D. Modeling + evaluation | `Trung Minh Vu Nguyen` | `results/` | Model Training, Model Evaluation |

Introduction, Conclusion and Discussion, and References are written together. One person acts as report editor (`<name>`).

## Repo structure

```
data/
  raw/          <- A's output (scraped data, untouched afterwards)
    images/
  clean/        <- B's output
  features/     <- C's output
notebooks/      <- one notebook per person per stage
src/            <- reusable scripts (scraper, cleaning helpers, ...)
results/        <- D's metrics, plots, tables
report/         <- report drafts and figures
requirements.txt
README.md
```

## Data contract

Everyone codes against these formats, so we are never blocked waiting on each other.
**`book_id` is the join key across all stages.** Do not rename it or reorder rows without keeping it.

### Stage A -> B: `data/raw/books_raw.csv`

| Column | Type | Description |
|---|---|---|
| `book_id` | int | Unique ID assigned by the scraper |
| `title` | str | Book title |
| `category` | str | `Fiction` or `Nonfiction` (the target label, taken from the category page it was scraped from) |
| `product_url` | str | URL of the book's product page |
| `image_url` | str | URL of the cover image |
| `image_path` | str | Relative path to the downloaded image, e.g. `data/raw/images/12.jpg` |
| `description` | str | Product description text (may be empty) |
| `price` | float | Price (currency symbol removed) |
| `rating` | int | Star rating, 1-5 |

> Extra scraped columns are allowed, but A must list them here.

### Stage B -> C: `data/clean/books_clean.csv`

Same columns as the raw file, but cleaned:

- No duplicate books, no corrupted or unopenable images, no rows with a missing label
- Text columns stripped of stray whitespace and odd characters
- Numeric columns have the right types
- Every `image_path` points to a valid file

B also writes `data/clean/cleaning_log.md`: what was removed or changed, how many rows, and why. This feeds directly into the report.

### Stage C -> D: `data/features/`

- `features_<name>.csv` (or `.npy` plus an ID file): one row per `book_id`, one column per feature
- `feature_notes.md`: how each feature set was built and why

### Train/test split

D defines the split once and saves it as `data/features/split.csv` with columns `book_id, split` (`train` / `test`). Everyone uses the same split. Fit things like TF-IDF vocabularies on the training set only.

## Setup

```bash
git clone https://github.com/<owner>/<repo>.git
cd <repo>
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

`requirements.txt` should include at least: `requests`, `beautifulsoup4`, `pandas`, `numpy`, `scikit-learn`, `pillow`, `matplotlib`, `jupyter`.

## How to run

1. **Scrape:** `python src/scrape.py` (writes `data/raw/`)
2. **Clean + EDA:** run `notebooks/b_cleaning_eda.ipynb` (writes `data/clean/`)
3. **Features:** run `notebooks/c_features.ipynb` (writes `data/features/`)
4. **Model + evaluate:** run `notebooks/d_modeling.ipynb` (writes `results/`)

> Update file names above if yours differ.

## Git workflow

- Never commit directly to `main`. Work on your own branch, e.g. `part-b-cleaning`.
- Commit small and often with clear messages.
- When a stage is done, open a **Pull Request** and let one teammate glance at it before merging.
- Run `git pull origin main` before you start working each day.
- Stay in your own files and folders to avoid merge conflicts. One notebook per person per stage.
- Do not commit large files or credentials.

## Handoff checklist

When you finish a stage, post in the group chat:

1. What you pushed and where
2. Row counts and anything unusual (class ratio, dropped rows, weird data)
3. Any change to the data contract above (and update this README)

## Data source and ethics

Data comes from [books.toscrape.com](http://books.toscrape.com/), a sandbox site built for scraping practice. Keep a small delay between requests.

## AI use

Per the course brief: generative AI may be used for debugging insight and for advice on formatting and spelling. We do not submit generated code or generated text. All code and report text are written by us.

## References

To be filled in as we go (data source, scikit-learn, any model papers).
