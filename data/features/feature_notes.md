# Feature engineering notes

## Purpose
Convert cleaned book titles and descriptions into numerical
features linked to book_id.

## Planned method
Combine each book's title and description.
Use CountVectorizer to generate word-count features.

## Planned output
features_word_counts.csv:
one row per book_id and one column per word feature.

## Status
Prototype using three example books.
Final features will use the cleaned data from stage B.
