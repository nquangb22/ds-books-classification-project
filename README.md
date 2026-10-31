# Fiction vs Nonfiction Book Classification

Course project for the Data Science course, University of Turku.

**Authors:** Khanh Hung Doan, Nhat Quang Bui, Doan Nhan Ta, Trung Minh Vu Nguyen

This repository contains the code, data and results for the project report. The task is binary classification of books into **Fiction** and **Nonfiction**, using data scraped from [books.toscrape.com](http://books.toscrape.com/). The project covers web scraping, data cleaning and exploratory analysis, feature engineering, model training and model evaluation. The methods and results are described in the report.

## Contents and how they relate to the report

| Report section | Code | Outputs |
|---|---|---|
| Data Scraping | `src/scrape.py` | `data/raw/books_raw.csv`, `data/raw/images/` |
| Data Cleaning and Analysis | `notebooks/cleaning_eda.ipynb` | `data/clean/books_clean.csv`, `data/clean/cleaning_log.md`, `report/desc_length_by_category.png` |
| Feature Engineering | `notebooks/c_features.ipynb` | `data/features/*.csv`, `data/features/feature_notes.md` |
| Model Training and Evaluation | `notebooks/d_modeling.ipynb` | `data/features/split.csv`, `results/` |

Each stage reads only the output files of the previous stage. Books are identified across all stages by `book_id`, a stable ID taken from the product URL.

## Data

- **Source:** all books in the Fiction and Nonfiction categories of books.toscrape.com, including pagination.
- **Size:** 175 books, 110 Nonfiction (62.9%) and 65 Fiction (37.1%).
- **Scraped fields:** title, category (target label, taken from the category page), description, cover image, price, star rating, UPC, availability and number of reviews.

## Reproducing the results

Requirements: Python 3 and the packages in `requirements.txt`.

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook
```

Run the notebooks in this order, each with **Kernel → Restart Kernel and Run All Cells**:

1. `notebooks/cleaning_eda.ipynb`
2. `notebooks/c_features.ipynb`
3. `notebooks/d_modeling.ipynb`

The scraped data and images are included in the repository, so scraping is not needed to reproduce the results. To scrape again, run `python src/scrape.py` from the project root. Re-running the notebooks reproduces the committed outputs and results.

## Repository structure

```
src/scrape.py                 scraper
notebooks/                    cleaning/EDA, feature engineering, modeling
data/raw/                     scraped data and 175 cover images
data/clean/                   cleaned dataset and cleaning log
data/features/                feature matrices, train/test split and notes
results/                      model comparison tables and confusion matrix
report/                       figures used in the report
requirements.txt
```

## References

- Books to Scrape: http://books.toscrape.com/
- Pedregosa et al. (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, 2825-2830.
- Beautiful Soup: https://www.crummy.com/software/BeautifulSoup/
- pandas: https://pandas.pydata.org/
- langdetect: https://pypi.org/project/langdetect/
