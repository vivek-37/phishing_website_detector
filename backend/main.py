from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from playwright.sync_api import sync_playwright
import os

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request model
class URLRequest(BaseModel):
    url: str

# Function to fetch dynamic HTML (async version for FastAPI)
def get_dynamic_html(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)  # Wait for JavaScript execution
        html_content = page.content()
        browser.close()
        return html_content

# Function to analyze sentiment using OpenAI API
def analyze_sentiment_html(url, html_content):
    '''
    Send a request to OpenAI API and get output in JSON format:
    {
        "sentiment": "phishing" or "not phishing",
        "explanations": [
            "Reason 1",
            "Reason 2",
            "Reason 3"
        ]
    }
    '''
    api_url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
    Analyze the following webpage's HTML content and determine if it is a phishing website or not.
    - Return the result in JSON format.
    - The JSON should have:
      - `"sentiment"`: `"phishing"` or `"not phishing"`
      - `"explanations"`: A list of 3 reasons supporting the decision.
    HTML Content:
    {html_content}
    """

    data = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a cybersecurity expert analyzing web pages for phishing. Respond in JSON"},
            {"role": "user", "content": prompt}
        ],
        "response_format": "json"
    }

    response = requests.post(api_url, json=data, headers=headers)
    
    if response.status_code == 200:
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

# Function to classify phishing type using OpenAI API
def classify_phishing(url, html_content):
    '''
    send a request to openai api and get output of the form:
    classification: 1 or 2 keyword classification
    '''
    api_url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Analyse HTML input of a phishing website and classify what type of phishing website it is."},
            {"role": "user", "content": html_content}
        ]
    }
    response = requests.post(api_url, json=data, headers=headers)
    
    if response.status_code == 200:
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


# Test route
@app.get("/")
def test():
    return {"message": "FastAPI backend is running!"}

@app.post("/")
def main(url: str = Form(...)):
    '''
    Recieving input from a form and starts computing all parameters
    
    model part:
    1. decode url submitted by user into some dataset categories, also check if it exists
    2. run the url_model with this data and get its score
    3. scrape website for specific parameters present in dataset
    4. run the other model with the data and get its score
    

    api part:
    1. run a sentiment analysis based on html data
    2. run a sentiment analysis based on webpage image data
    3. if flagged as a phishing website, classify the type of phishing website 
    '''
    try:
        # Get the webpage content
        html_content = get_dynamic_html(url)

        # Perform sentiment analysis
        result = analyze_sentiment_html(url, html_content)

        # Determine phishing type if suspicious
        if "phishing" in result.lower():
            phishing_type = classify_phishing(url, html_content)
            return {"status": "phishing", "type": phishing_type}
        else:
            return {"status": "safe"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
