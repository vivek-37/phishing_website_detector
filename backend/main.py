from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Create FastAPI instance
app = FastAPI()

# Enable CORS (Allow Frontend Requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (Change this to your frontend URL in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Define Request Model
class URLRequest(BaseModel):
    url: str

# API Endpoint to Receive URL from Frontend
@app.post("/scan")
async def scan_url(data: URLRequest):
    received_url = data.url.strip()  # Remove extra spaces
    
    if not received_url:
        raise HTTPException(status_code=400, detail="No URL received")

    print(f"✅ Received URL: {received_url}")  # Print URL in backend

    return {"message": "URL received successfully", "url": received_url}

# Run the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
