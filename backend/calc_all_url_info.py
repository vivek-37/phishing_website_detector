import pandas as pd
from urllib.parse import urlparse
import string
import requests
from sklearn.preprocessing import LabelEncoder
import random
import tldextract

# Helper Functions to Extract Features
def count_special_chars(url):
    special_chars = set("!@#$%^*()[]{}/\\")
    return sum(1 for char in url if char in special_chars)

def is_https(url):
    return 1 if urlparse(url).scheme == "https" else 0

def is_domain_ip(domain):
    # Check if the domain is an IP address
    domain_no_dot = domain.replace('.','')
    for a in domain_no_dot:
        if not a.isdigit():
            return 0
    return 1

def tld_legitimate_prob(tld):
    df = pd.read_csv("phishing_website_detector/PhiUSIIL_Phishing_URL_Dataset.csv")
    tld_dict = df.drop_duplicates().set_index("TLD")["TLDLegitimateProb"].to_dict()
    return tld_dict[tld]


def no_of_letters_in_url(url):
    return sum(1 for char in url if char.isalpha())

def letter_ratio_in_url(url):
    total_chars = len(url)
    if total_chars == 0:
        return 0
    return no_of_letters_in_url(url) / total_chars

def no_of_digits_in_url(url):
    return sum(1 for char in url if char.isdigit())

def digit_ratio_in_url(url):
    total_chars = len(url)
    if total_chars == 0:
        return 0
    return no_of_digits_in_url(url) / total_chars

def no_of_other_special_chars_in_url(url):
    special_chars = set("!@#$%^*()[]{}/\\")
    return sum(1 for char in url if char in special_chars)

def special_char_ratio_in_url(url):
    total_chars = len(url)
    if total_chars == 0:
        return 0
    return no_of_other_special_chars_in_url(url) / total_chars


# Main Function to Process URL and Make Prediction
def predict_from_url(url, model, label_encoders=None):
    # Extract Features

    if not url.startswith(("http://", "https://")):
        urlfull = "http://" + url  # Ensure proper parsing
    domain = urlparse(url).netloc
    print(domain)

    extracted = tldextract.extract(domain)
    tld = extracted.suffix

    
    features = {
        'FILENAME': '',  # Placeholder: You can extract filename logic if needed
        'URL': url,
        'URLLength': len(url),
        'Domain': domain,
        'DomainLength': len(domain),
        'IsDomainIP': is_domain_ip(domain),
        'TLD': tld,
        'CharContinuationRate': sum(1 for i in range(1, len(domain)) if domain[i].isalpha() == domain[i-1].isalpha()) / len(url) if len(url) > 0 else 0,
        'TLDLegitimateProb': tld_legitimate_prob(tld),
        'URLCharProb': 0.05 + 0.05*random.random(),
        'TLDLength': len(tld),
        'NoOfSubDomain': domain.count('.') - 1 if domain.count('.') > 0 else 0,
        'HasObfuscation': 1 if url.count('%') >= 1 else 0,
        'NoOfObfuscatedChar': url.count('%')*3,
        'ObfuscationRatio': url.count('%')*3/len(url),
        'NoOfLettersInURL': no_of_letters_in_url(url),
        'LetterRatioInURL': letter_ratio_in_url(url),
        'NoOfDegitsInURL': no_of_digits_in_url(url),
        'DegitRatioInURL': digit_ratio_in_url(url),
        'NoOfEqualsInURL': url.count('='),
        'NoOfQMarkInURL': url.count('?'),
        'NoOfAmpersandInURL': url.count('&'),
        'NoOfOtherSpecialCharsInURL': no_of_other_special_chars_in_url(url),
        'SpacialCharRatioInURL': special_char_ratio_in_url(url),
        'IsHTTPS': is_https(url)
    }
    print(features)
    # Convert Features to DataFrame
    feature_df = pd.DataFrame([features])
    
    # Fit label encoders (if not already fitted)
    for column, encoder in label_encoders.items():
        if column in feature_df.columns:
            if not hasattr(encoder, "classes_"):
                encoder.fit(feature_df[column].astype(str))  # Fit on available data
            feature_df[column] = encoder.transform(feature_df[column].astype(str))
    
    # Make Prediction
    print(feature_df)
    prediction = model.predict(feature_df)
    return prediction[0]

# Example Usage
# Load your trained Random Forest model (replace model with your actual model)
from sklearn.ensemble import RandomForestClassifier
import pickle  # For loading the trained model

# Load the pre-trained model
with open("phishing_website_detector/X1.pkl", "rb") as file:
    model = pickle.load(file)

# Example Label Encoders (replace with your actual encoders)
label_encoders = { 
    'FILENAME': LabelEncoder(),
    'URL': LabelEncoder(),
    'Domain': LabelEncoder(),
    'TLD': LabelEncoder()
}

# Example URL
url = "https://www.southbankmosaics.com"

# Predict
print('predicting')
result = predict_from_url(url, model, label_encoders)
print("Prediction:", result) # change the given function so that it fits the trained model rf in the notebook also write the predicted output for example urls