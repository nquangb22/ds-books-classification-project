# Cleaning log (Part B)
## Raw data
- Source: data/raw/books_raw.csv (scraped in 25 October 2026)
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
- 4 books had no "...more": 3 normal short descriptions (untouched)
- Kindle Paperwhite User's Guide: description = title (placeholder)
- TODO: decide (empty string vs keep + flag)


