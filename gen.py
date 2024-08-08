import requests
import pandas as pd
from bs4 import BeautifulSoup

base_url = "https://en.wikipedia.org"
category_url = "https://en.wikipedia.org/wiki/Category:21st-century_American_sportsmen"

def get_articles_from_subcategory(subcategory, category_url):
    url = f"{category_url}?from={subcategory}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = [a.get_text() for a in soup.select('.mw-category-group ul li a')]
    return articles

def gen_def(category_url):
    all_articles = []
    for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        articles = get_articles_from_subcategory(char, category_url)
        all_articles.extend(articles)

    # Create a DataFrame
    return pd.DataFrame(all_articles, columns=["Article"])


def main():
    # Save to CSV
    gen_def(category_url).to_csv('popular_athletes.csv', index=False)

    print(f'Successfully scraped  articles.')