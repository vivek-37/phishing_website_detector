import requests
from urllib.parse import urlparse

OPR_API_KEY = os.getenv("OPR_API_KEY", "your-opr-api-key")
# API_KEY = "YOUR-API-KEY-HERE"  # Replace with your actual API key
TOP_SITES_URL = "https://openpagerank.com/api/v1.0/getPageRank"

def get_min(src, tar):
    """Returns the shortest and longest URL along with the length of the shortest URL."""
    return (src, tar, len(src)) if len(src) <= len(tar) else (tar, src, len(tar))

def get_url_similarity_index(src, tar):
    """Calculates the similarity index between two URLs."""
    X, Y, n = get_min(src, tar)
    N = max(len(src), len(tar))
    SI = 0
    a = 50 / N
    nsum = (N * (N + 1)) // 2

    i = 0
    while i < n:
        if X[i] == Y[i]:
            SI += a + (50 * (N - i)) / nsum
        else:
            # Remove unmatched character from longest URL
            Y = Y[:i] + Y[i + 1:]
            # Recalculate shortest, longest, and n
            X, Y, n = get_min(src, tar)
            i -= 1  # Adjust index after removal
        i += 1
    
    return SI

def extract_domain(url):
    """Extracts the domain name from a given URL."""
    parsed_url = urlparse(url)
    return parsed_url.netloc or parsed_url.path  # Handles cases where netloc might be empty

def get_top_websites():
    """Fetches the top websites using Open Page Rank API."""
    headers = {"API-OPR": OPR_API_KEY}
    
    response = requests.get(TOP_SITES_URL, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if "response" in data and isinstance(data["response"], list):
            return [entry["domain"] for entry in data["response"] if "domain" in entry]
    else:
        print(f"Error fetching top websites: {response.status_code} - {response.text}")
        return []

def find_most_similar_url(src):
    """Finds the most similar URL to the input URL from the top 10 million websites."""
    top_websites = get_top_websites()
    if not top_websites:
        print("Could not fetch top websites.")
        return 

    src_domain = extract_domain(src)
    most_similar_url = None
    highest_similarity = -1

    for website in top_websites:
        similarity = get_url_similarity_index(src_domain, website)
        if similarity > highest_similarity:
            highest_similarity = similarity
            most_similar_url = website

    if most_similar_url:
        print(f"Most similar URL: {most_similar_url}")
        print(f"Similarity Index: {highest_similarity}")
    else:
        print("No similar URLs found.")
    return highest_similarity

# Example usage
# src_url = "https://example.com/login"  # Replace with the URL you want to compare
# find_most_similar_url(src_url)
