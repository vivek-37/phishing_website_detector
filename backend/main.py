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
def analyze_sentiment(url, html_content):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Analyse HTML input of a webpage and perform a Sentiment analysis to detemine if it is a phishing website or not."},
            {"role": "user", "content": html_content}
        ]
    }
    response = requests.post(OPENAI_API_URL, json=data, headers=headers)
    
    if response.status_code == 200:
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

# Function to classify phishing type using OpenAI API
def classify_phishing(url, html_content):
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
    response = requests.post(OPENAI_API_URL, json=data, headers=headers)
    
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
    '''
    try:
        # Get the webpage content
        html_content = get_dynamic_html(url)

        # Perform sentiment analysis
        result = analyze_sentiment(url, html_content)

        # Determine phishing type if suspicious
        if "phishing" in result.lower():
            phishing_type = classify_phishing(url, html_content)
            return {"status": "phishing", "type": phishing_type}
        else:
            return {"status": "safe"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
