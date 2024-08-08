import argparse
import requests
import pandas as pd
from bs4 import BeautifulSoup
import sys

# Function to get articles from a single subcategory page
def get_articles_from_subcategory(base_url, subcategory):
    url = f"{base_url}?from={subcategory}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = [a.get_text() for a in soup.select('.mw-category-group ul li a')]
    return articles

# Function to scrape Wikipedia category
def scrape_wikipedia_category(category_url):
    base_url = category_url
    all_articles = []
    for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        articles = get_articles_from_subcategory(base_url, char)
        all_articles.extend(articles)
    df = pd.DataFrame(all_articles, columns=["Article"])
    return df

# Function to process articles and find matches
def process_articles(df, target_column, output_file):
    df[target_column] = df[target_column].str.replace('^Talk:', '', regex=True)
    two_word_articles = df[df[target_column].str.split().str.len() == 2][target_column]

    def find_and_combine_matches(articles, limit=100):
        combined_articles = []
        used_indices = set()
        for i, article in enumerate(articles):
            if i in used_indices:
                continue
            words = article.split()
            for j, other_article in enumerate(articles):
                if j in used_indices or i == j:
                    continue
                other_words = other_article.split()
                if words[1] == other_words[0]:
                    combined_articles.append(f'{words[0]} {words[1]} {other_words[1]}')
                    used_indices.update([i, j])
                    break
            if len(combined_articles) >= limit:
                break
        return combined_articles

    combined_matches = find_and_combine_matches(two_word_articles, limit=100)

    for i in range(0, len(combined_matches), 3):
        print(' | '.join(combined_matches[i:i+3]))

    combined_df = pd.DataFrame(combined_matches, columns=['Combined Article'])
    combined_df.to_csv(output_file, index=False)
    print(f'Successfully combined {len(combined_matches)} articles.')

# Main function to handle CLI input
def main():
    parser = argparse.ArgumentParser(description='Scrape Wikipedia or process CSV.')
    parser.add_argument('-w', '--wiki', type=str, help='Wikipedia category link')
    parser.add_argument('-c', '--csv', type=str, help='Input CSV file')
    parser.add_argument('-t', '--target', type=str, help='Target column name for CSV processing')
    parser.add_argument('-o', '--output', type=str, default='output.csv', help='Output CSV file')
    args = parser.parse_args()

    if args.wiki:
        if not args.wiki.startswith('https://en.wikipedia.org/wiki/Category:'):
            print('Invalid Wikipedia category link. Please provide a valid link.')
            sys.exit(1)
        df = scrape_wikipedia_category(args.wiki)
        process_articles(df, 'Article', args.output)
    elif args.csv:
        if not args.csv.endswith('.csv'):
            print('Invalid CSV file. Please provide a valid CSV file.')
            sys.exit(1)
        if not args.target:
            print('Please provide a target column name with -t.')
            sys.exit(1)
        df = pd.read_csv(args.csv)
        if args.target not in df.columns:
            print(f'Target column "{args.target}" not found in CSV file.')
            sys.exit(1)
        process_articles(df, args.target, args.output)
    else:
        print('Please provide either a Wikipedia category link with -w or a CSV file with -c.')
        sys.exit(1)

if __name__ == '__main__':
    main()
