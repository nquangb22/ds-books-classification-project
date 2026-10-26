# Scraper for Fiction and Nonfiction books from books.toscrape.com
# Run from the project folder with: python src/scrape.py

import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://books.toscrape.com/"

categories = {
    "Fiction": BASE_URL + "catalogue/category/books/fiction_10/index.html",
    "Nonfiction": BASE_URL + "catalogue/category/books/nonfiction_13/index.html"
}

ratings = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

RAW_DIR = "data/raw"
IMAGE_DIR = "data/raw/images"

# Create the folders if they do not exist yet
os.makedirs(IMAGE_DIR, exist_ok=True)


def get_page(url):
    # Download a page and turn it into a BeautifulSoup object-p;/.,mi89
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    response.encoding = "utf-8"

    time.sleep(0.5)

    return BeautifulSoup(response.text, "html.parser")


def get_book_links(category_url):
    # Collect the links from every page in a category
    links = []
    page_url = category_url

    while page_url is not None:
        soup = get_page(page_url)

        books = soup.find_all("article", class_="product_pod")

        for book in books:
            href = book.find("h3").find("a")["href"]
            book_url = urljoin(page_url, href)
            links.append(book_url)

        # Check if there is another page
        next_button = soup.find("li", class_="next")

        if next_button is not None:
            next_link = next_button.find("a")["href"]
            page_url = urljoin(page_url, next_link)
        else:
            page_url = None

    return links


def download_image(image_url, upc):
    # Save the cover image using the book's UPC
    image_path = IMAGE_DIR + "/" + upc + ".jpg"

    if os.path.exists(image_path):
        if os.path.getsize(image_path) > 0:
            return image_path

    try:
        response = requests.get(image_url, timeout=15)
        response.raise_for_status()

        with open(image_path, "wb") as image_file:
            image_file.write(response.content)

        time.sleep(0.2)
        return image_path

    except requests.RequestException as error:
        print("Could not download image for", upc, error)
        return ""


def scrape_book(url, category):
    # Scrape the information from one book page
    soup = get_page(url)

    title = soup.find("h1").text.strip()

    # Read the information in the product table
    table = {}

    for row in soup.find("table").find_all("tr"):
        key = row.find("th").text.strip()
        value = row.find("td").text.strip()
        table[key] = value

    upc = table["UPC"]

    price = float(table["Price (excl. tax)"].replace("£", ""))
    price_incl_tax = float(
        table["Price (incl. tax)"].replace("£", "")
    )

    num_reviews = int(table["Number of reviews"])

    # Get the number of available copies
    availability_text = table["Availability"]
    digits = ""

    for character in availability_text:
        if character.isdigit():
            digits = digits + character

    if digits != "":
        availability = int(digits)
    else:
        availability = 0

    # Convert the rating from a word to a number
    star_tag = soup.find("p", class_="star-rating")
    rating = ratings[star_tag["class"][1]]

    # Get the description if the page has one
    description = ""

    description_header = soup.find("div", id="product_description")

    if description_header is not None:
        description_tag = description_header.find_next_sibling("p")

        if description_tag is not None:
            description = description_tag.text.strip()

    # Check the category using the breadcrumb
    breadcrumb = soup.find("ul", class_="breadcrumb")
    breadcrumb_items = breadcrumb.find_all("li")
    breadcrumb_category = breadcrumb_items[2].text.strip()

    if breadcrumb_category != category:
        print("Warning: category mismatch for", title)

    # Get the cover image URL
    image_tag = soup.find("div", id="product_gallery").find("img")
    image_url = urljoin(url, image_tag["src"])

    image_path = download_image(image_url, upc)

    # Return all the information about this book
    book = {
        "upc": upc,
        "title": title,
        "category": category,
        "description": description,
        "rating": rating,
        "price": price,
        "price_incl_tax": price_incl_tax,
        "availability": availability,
        "num_reviews": num_reviews,
        "product_url": url,
        "image_url": image_url,
        "image_path": image_path
    }

    return book


# Scrape both categories
all_books = []
failed_books = []

for category_name, category_url in categories.items():
    print("Scraping category:", category_name)

    links = get_book_links(category_url)
    print("Found", len(links), "books")

    count = 0

    for link in links:
        try:
            book = scrape_book(link, category_name)
            all_books.append(book)

        except Exception as error:
            print("Failed to scrape:", link)
            print("Reason:", error)
            failed_books.append(link)

        count = count + 1

        if count % 10 == 0:
            print(count, "of", len(links), "books processed")

# Create a DataFrame from the scraped books
df = pd.DataFrame(all_books)

# Remove duplicate books using their UPC
if not df.empty:
    df = df.drop_duplicates(subset="upc")

    # Create the ID used to join data between project stages
    df.insert(0, "book_id", range(1, len(df) + 1))

    # Keep the required columns first, followed by extra information
    df = df[
        [
            "book_id",
            "title",
            "category",
            "product_url",
            "image_url",
            "image_path",
            "description",
            "price",
            "rating",
            "upc",
            "price_incl_tax",
            "availability",
            "num_reviews"
        ]
    ]

# Save the results to a CSV file
csv_path = RAW_DIR + "/books_raw.csv"
df.to_csv(csv_path, index=False, encoding="utf-8")

# Print some checks to help us review the data
print()
print("Saved", len(df), "books to", csv_path)

if not df.empty:
    print()
    print("Books in each category:")
    print(df["category"].value_counts())

    print()
    print("Duplicate UPCs:", df["upc"].duplicated().sum())
    print("Missing descriptions:", (df["description"] == "").sum())

    missing_images = 0

    for path in df["image_path"]:
        if path == "":
            missing_images = missing_images + 1
        elif not os.path.exists(path):
            missing_images = missing_images + 1
        elif os.path.getsize(path) == 0:
            missing_images = missing_images + 1

    print("Missing or empty images:", missing_images)

print("Failed book pages:", len(failed_books))

for link in failed_books:
    print(link)