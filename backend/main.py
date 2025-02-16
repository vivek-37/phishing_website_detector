from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import validators
from calc_all_url_info import *
from playwright.sync_api import sync_playwright
import os
import pickle
from sklearn.preprocessing import LabelEncoder

# Create FastAPI instance
app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Enable CORS (Allow Frontend Requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (Change this to your frontend URL in production)
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Define Request Model
class URLRequest(BaseModel):
    url: str

def get_dynamic_html(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)  # Wait for JavaScript execution
        html_content = page.content()
        browser.close()
        return html_content


@app.post("/llmSentiment")
async def sentiment(url):
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
    html_content = get_dynamic_html()
    
    openai_api_url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
    Analyze the following webpage's HTML content and determine if it is a phishing website or not.
    - Return the result in JSON format.
    - The JSON should have:
      - "sentiment": "phishing" or "not phishing"
      - "explanations": A list of 3 reasons supporting the decision.
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

    response = requests.post(openai_api_url, json=data, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

@app.post("/llmClassification")
def classify_phishing(url, html_content):
    '''
    send a request to openai api and get output of the form:
    classification: 1 or 2 keyword classification
    '''
    openai_api_url = "https://api.openai.com/v1/chat/completions"

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
    response = requests.post(openai_api_url, json=data, headers=headers)
    
    if response.status_code == 200:
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


# API Endpoint to Receive URL from Frontend
@app.post("/scan")
async def scan_url(data: URLRequest):
    received_url = data.url.strip()  # Remove extra spaces

    if not validators.url(received_url):
        raise HTTPException(status_code=400, detail="Invalid URL")

    if not received_url:
        raise HTTPException(status_code=400, detail="No URL received")

    print(f"✅ Received URL: {received_url}")  # Print URL in backend

    # call calc
    with open("X1.pkl", "rb") as file:
        model = pickle.load(file)

    label_encoders = { 
    'FILENAME': LabelEncoder(),
    'URL': LabelEncoder(),
    'Domain': LabelEncoder(),
    'TLD': LabelEncoder()
    }

    result_url_scan = predict_from_url(received_url, model, label_encoders)
    if result_url_scan == 1:
        conclusion_url = "Possible phishing website"
    else:
        conclusion_url = "Mostly safe website"
    
    return {
        "message1": "URL received successfully", "url": received_url,
        "message2": f"Phishing URL Predictor says that it is a {conclusion_url}",
        "message3": "Querying LLM Sentiment"
    }


# Run the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
