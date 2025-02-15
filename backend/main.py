from fastapi import FastAPI
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
    return

# Function to classify phishing type using OpenAI API
def classify_phishing(url):
    return 


# Test route
@app.get("/")
def main():
    return {"message": "FastAPI backend is running!"}




