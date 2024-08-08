import pandas as pd

# Read the CSV file
df = pd.read_csv('JEOPARDY_CSV.csv')

print(df.columns)

# Strip "Talk:" from the beginning of every string
df[' Answer'] = df[' Answer'].str.replace('^Talk:', '', regex=True)

# Find all strings that are exactly two words
two_word_articles = df[df[' Answer'].str.split().str.len() == 2][' Answer']

# Function to find and combine matches
def find_and_combine_matches(articles, limit=1000):
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

# Find and combine 100 matches
combined_matches = set(find_and_combine_matches(two_word_articles, limit=1000))

# Print the combined matches, 3 per line
for i in range(0, len(combined_matches), 7):
    print(' | '.join(list(combined_matches)[i:i+7]))

# Optional: Save combined matches to a CSV file
combined_df = pd.DataFrame(combined_matches, columns=['Combined Article'])
combined_df.to_csv('jeopardy.csv', index=False)

print(f'Successfully combined {len(combined_matches)} articles.')