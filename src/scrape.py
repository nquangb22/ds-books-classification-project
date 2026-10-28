# Scrape Fiction and Nonfiction books from books.toscrape.com
import os
import re
import time
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
CATEGORIES = {
    "Fiction": BASE_URL + "catalogue/category/books/fiction_10/index.html",
    "Nonfiction": BASE_URL + "catalogue/category/books/nonfiction_13/index.html"
}
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
RAW_DIR = "data/raw"
IMAGE_DIR = "data/raw/images"


def get_page(url):
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    response.encoding = "utf-8"
    time.sleep(0.5)
    return BeautifulSoup(response.text, "html.parser")


def get_book_links(category_url):
    links = []
    page_url = category_url

    while page_url is not None:
        soup = get_page(page_url)
        books = soup.find_all("article", class_="product_pod")

        for book in books:
            href = book.find("h3").find("a")["href"]
            links.append(urljoin(page_url, href))

        next_button = soup.find("li", class_="next")
        if next_button is None:
            page_url = None
        else:
            page_url = urljoin(page_url, next_button.find("a")["href"])

    return links


def get_book_id(url):
    # Example: .../soumission_998/index.html -> 998
    folder = url.rstrip("/").split("/")[-2]
    match = re.search(r"_(\d+)$", folder)
    if match is None:
        raise ValueError("Cannot find book ID in URL: " + url)
    return int(match.group(1))


def download_image(image_url, upc):
    path = IMAGE_DIR + "/" + upc + ".jpg"

    if os.path.exists(path) and os.path.getsize(path) > 0:        
        return path

    try:
        response = requests.get(image_url, timeout=15)
        response.raise_for_status()
        with open(path, "wb") as image_file:
            image_file.write(response.content)
        time.sleep(0.2)
        return path
    except requests.RequestException as error:
        print("Could not download image for", upc, error)
        return ""


def scrape_book(url, category):
    soup = get_page(url)
    title = soup.find("h1").text.strip()

    table = {}
    for row in soup.find("table").find_all("tr"):
        key = row.find("th").text.strip()
        value = row.find("td").text.strip()
        table[key] = value

    upc = table["UPC"]
    price = float(table["Price (excl. tax)"].replace("£", ""))
    price_incl_tax = float(table["Price (incl. tax)"].replace("£", ""))
    num_reviews = int(table["Number of reviews"])

    digits = ""
    for character in table["Availability"]:
        if character.isdigit():
            digits += character
    availability = int(digits) if digits else 0

    star_tag = soup.find("p", class_="star-rating")
    rating = ratings_from_tag(star_tag)

    description = ""
    header = soup.find("div", id="product_description")
    if header is not None:
        description_tag = header.find_next_sibling("p")
        if description_tag is not None:
            description = description_tag.text.strip()

    crumbs = soup.find("ul", class_="breadcrumb").find_all("li")
    breadcrumb_category = crumbs[2].text.strip()
    if breadcrumb_category != category:
        print("Warning: category mismatch for", title)

    image_src = soup.find("div", id="product_gallery").find("img")["src"]
    image_url = urljoin(url, image_src)
    image_path = download_image(image_url, upc)

    return {
        "book_id": get_book_id(url),
        "title": title,
        "category": category,
        "product_url": url,
        "image_url": image_url,
        "image_path": image_path,
        "description": description,
        "price": price,
        "rating": rating,
        "upc": upc,
        "price_incl_tax": price_incl_tax,
        "availability": availability,
        "num_reviews": num_reviews
    }


def ratings_from_tag(star_tag):
    for name, number in RATINGS.items():
        if name in star_tag["class"]:
            return number
    raise ValueError("Unknown star rating")


def main():
    os.makedirs(IMAGE_DIR, exist_ok=True)
    all_books = []
    failed_books = []

    for category_name, category_url in CATEGORIES.items():
        print("Scraping category:", category_name)
        links = get_book_links(category_url)
        print("Found", len(links), "books")

        for count, link in enumerate(links, start=1):
            try:
                all_books.append(scrape_book(link, category_name))
            except Exception as error:
                print("Failed:", link, error)
                failed_books.append((link, category_name))

            if count % 10 == 0:
                print(count, "of", len(links), "processed")

    # Try failed book pages one more time
    if failed_books:
        print("Retrying", len(failed_books), "failed book pages...")
    still_failed = []
    for link, category_name in failed_books:
        try:
            all_books.append(scrape_book(link, category_name))
        except Exception as error:
            print("Failed again:", link, error)
            still_failed.append(link)

    columns = [
        "book_id", "title", "category", "product_url", "image_url",
        "image_path", "description", "price", "rating", "upc",
        "price_incl_tax", "availability", "num_reviews"
    ]
    df = pd.DataFrame(all_books, columns=columns)
    # Keep duplicates in raw data. Cleaning will handle them.
    csv_path = RAW_DIR + "/books_raw.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    print("\nSaved", len(df), "books to", csv_path)
    print("\nBooks by category:")
    print(df["category"].value_counts())
    print("Duplicate UPCs:", df["upc"].duplicated().sum())
    print("Duplicate book IDs:", df["book_id"].duplicated().sum())
    print("Missing descriptions:", (df["description"] == "").sum())

    missing_images = 0
    for path in df["image_path"]:
        if not path or not os.path.exists(path) or os.path.getsize(path) == 0:
            missing_images += 1
    print("Missing or empty images:", missing_images)
    print("Failed book pages after retry:", len(still_failed))
    for link in still_failed:
        print(link)


if __name__ == "__main__":
    main()