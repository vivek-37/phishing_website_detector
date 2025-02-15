import pandas as pd
from urllib.parse import urlparse
import string
import requests
from sklearn.preprocessing import LabelEncoder
import os

OPR_API_KEY = os.getenv("OPR_API_KEY")
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

# Helper Functions to Extract Features
def count_special_chars(url):
    special_chars = set("!@#$%^*()[]{}/\\")
    return sum(1 for char in url if char in special_chars)

def is_https(url):
    return 1 if urlparse(url).scheme == "https" else 0

def get_domain(url):
    try:
        return urlparse(url).netloc
    except:
        return ""

def is_domain_ip(domain):
    # Check if the domain is an IP address
    return 1 if all(part.isdigit() or part == '.' for part in domain.split('.')) else 0

def get_tld(domain):
    try:
        return domain.split('.')[-1]
    except:
        return ""

def calculate_similarity_index(url):
    # Placeholder: Replace with actual similarity index logic
    return find_most_similar_url(url)  # Example placeholder logic

def char_continuation_rate(url):
    # Placeholder: Replace with actual continuation rate logic
    return sum(1 for i in range(1, len(url)) if url[i] == url[i - 1]) / len(url) if len(url) > 0 else 0

def tld_legitimate_prob(tld):
    # Placeholder: Replace with actual TLD legitimacy probability logic
    common_tlds = {"com", "org", "net", "edu", "gov"}
    return 1 if tld in common_tlds else 0

def url_char_prob(url):
    # Placeholder: Replace with actual URL character probability logic
    return sum(1 for char in url if char.isalpha()) / len(url) if len(url) > 0 else 0

def no_of_subdomains(domain):
    return len(domain.split('.')) - 1 if domain else 0

def has_obfuscation(url):
    obfuscated_chars = set("%$#@!^&*()")
    return 1 if any(char in obfuscated_chars for char in url) else 0

def no_of_obfuscated_chars(url):
    obfuscated_chars = set("%$#@!^&*()")
    return sum(1 for char in url if char in obfuscated_chars)

def obfuscation_ratio(url):
    total_chars = len(url)
    return no_of_obfuscated_chars(url) / total_chars if total_chars > 0 else 0

def no_of_letters_in_url(url):
    return sum(1 for char in url if char.isalpha())

def letter_ratio_in_url(url):
    total_chars = len(url)
    return no_of_letters_in_url(url) / total_chars if total_chars > 0 else 0

def no_of_digits_in_url(url):
    return sum(1 for char in url if char.isdigit())

def digit_ratio_in_url(url):
    total_chars = len(url)
    return no_of_digits_in_url(url) / total_chars if total_chars > 0 else 0

def no_of_equals_in_url(url):
    return url.count('=')

def no_of_qmark_in_url(url):
    return url.count('?')

def no_of_ampersand_in_url(url):
    return url.count('&')

def no_of_other_special_chars_in_url(url):
    special_chars = set("!@#$%^*()[]{}/\\")
    return sum(1 for char in url if char in special_chars)

def special_char_ratio_in_url(url):
    total_chars = len(url)
    return no_of_other_special_chars_in_url(url) / total_chars if total_chars > 0 else 0

# Main Function to Process URL and Make Prediction
def predict_from_url(url, model, label_encoders=None):
    # Extract Features
    domain = get_domain(url)
    tld = get_tld(domain)
    
    features = {
        'FILENAME': '',  # Placeholder: You can extract filename logic if needed
        'URL': url,
        'URLLength': len(url),
        'Domain': domain,
        'DomainLength': len(domain),
        'IsDomainIP': is_domain_ip(domain),
        'TLD': tld,
        'URLSimilarityIndex': calculate_similarity_index(url),
        'CharContinuationRate': char_continuation_rate(url),
        'TLDLegitimateProb': tld_legitimate_prob(tld),
        'URLCharProb': url_char_prob(url),
        'TLDLength': len(tld),
        'NoOfSubDomain': no_of_subdomains(domain),
        'HasObfuscation': has_obfuscation(url),
        'NoOfObfuscatedChar': no_of_obfuscated_chars(url),
        'ObfuscationRatio': obfuscation_ratio(url),
        'NoOfLettersInURL': no_of_letters_in_url(url),
        'LetterRatioInURL': letter_ratio_in_url(url),
        'NoOfDegitsInURL': no_of_digits_in_url(url),
        'DegitRatioInURL': digit_ratio_in_url(url),
        'NoOfEqualsInURL': no_of_equals_in_url(url),
        'NoOfQMarkInURL': no_of_qmark_in_url(url),
        'NoOfAmpersandInURL': no_of_ampersand_in_url(url),
        'NoOfOtherSpecialCharsInURL': no_of_other_special_chars_in_url(url),
        'SpacialCharRatioInURL': special_char_ratio_in_url(url),
        'IsHTTPS': is_https(url)
    }
    
    # Convert Features to DataFrame
    feature_df = pd.DataFrame([features])
    
    # Encode Categorical Features
    if label_encoders:
        for column, encoder in label_encoders.items():
            if column in feature_df.columns:
                feature_df[column] = encoder.transform(feature_df[column])
    
    # Make Prediction
    prediction = model.predict(feature_df)
    return prediction[0]

# Example Usage
# Load your trained Random Forest model (replace model with your actual model)
from sklearn.ensemble import RandomForestClassifier
import pickle  # For loading the trained model

# Load the pre-trained model
with open("random_forest_model.pkl", "rb") as file:
    model = pickle.load(file)
    
# Example Label Encoders (replace with your actual encoders)
label_encoders = {
    'FILENAME': LabelEncoder(),
    'URL': LabelEncoder(),
    'Domain': LabelEncoder(),
    'TLD': LabelEncoder()
}

# Fit the encoders on your training data (replace with your actual training data)
# Example:
# training_data = pd.read_csv("path_to_training_data.csv")
# label_encoders['FILENAME'].fit(training_data['FILENAME'])
# label_encoders['URL'].fit(training_data['URL'])
# label_encoders['Domain'].fit(training_data['Domain'])
# label_encoders['TLD'].fit(training_data['TLD'])

# Example URL
url = "https://example.com/path?query=123&symbol=@!"

# Predict
print('predicting')
result = predict_from_url(url, model, label_encoders)
print("Prediction:", result) # change the given function so that it fits the trained model rf in the notebook also write the predicted output for example urls