from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from playwright.async_api import async_playwright
import asyncio
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
async def get_dynamic_html(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=60000)  # Wait for JavaScript execution
        html_content = await page.content()
        await browser.close()
        return html_content

# Function to analyze sentiment using OpenAI API
def analyze_sentiment(url):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": ""},
            {"role": "user", "content": ""}
        ]
    }
    response = requests.post(OPENAI_API_URL, json=data, headers=headers)
    
    if response.status_code == 200:
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

# Function to classify phishing type using OpenAI API
def classify_phishing(url):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": ""},
            {"role": "user", "content": ""}
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

# Recieving input from a form and starts computing all parameters
@app.post("/")
def main(url: str = Form(...))



