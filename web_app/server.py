from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
import uvicorn
import shutil
import os
import json
from datetime import datetime

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="web_app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="web_app/templates")

# Data Storage
REVIEWS_FILE = "web_app/reviews.json"

# Team Data from teams.txt
TEAM_MEMBERS = [
    {
        "name": "Shailendra Mani Pandey",
        "role": "Cse 2024022015 3rd year",
        "image": "Shailendra.jpeg"
    },
    {
        "name": "Vaibhav Singh",
        "role": "Cse 2024022018 3rd year",
        "image": "default.jpg"
    },
    {
        "name": "Suyash Shukla",
        "role": "Cse 2023021260 3rd year",
        "image": "suyash.jpeg"
    },
    {
        "name": "Divyanshu Nath Tripathi",
        "role": "Cse 2024022006 3rd year",
        "image": "default.jpg"
    },
    {
        "name": "Ankur Kumar",
        "role": "Cse 2024022003 3rd year",
        "image": "Ankur.jpeg"
    },
    {
        "name": "Kartikey Singh",
        "role": "Cse 2024022010 3rd year",
        "image": "Kartikey.jpeg"
    },
    {
        "name": "Govind Verma",
        "role": "Cse 2024022007 3rd year",
        "image": "default.jpg"
    }
]

def load_reviews():
    if os.path.exists(REVIEWS_FILE):
        try:
            with open(REVIEWS_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_review(review):
    reviews = load_reviews()
    reviews.insert(0, review) # Prepend new review
    with open(REVIEWS_FILE, "w") as f:
        json.dump(reviews, f, indent=4)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    reviews = load_reviews()
    # Limit to top 3 for the landing page
    recent_reviews = reviews[:3]
    return templates.TemplateResponse("index.html", {"request": request, "reviews": recent_reviews})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "team": TEAM_MEMBERS})

@app.post("/submit_review")
async def submit_review(
    gamertag: str = Form(...), 
    rating: str = Form(...), 
    message: str = Form(...)
):
    review = {
        "gamertag": gamertag,
        "rating": rating,
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    save_review(review)
    return RedirectResponse(url="/?success=true", status_code=303)

@app.get("/download")
async def download_client():
    # Create a zip of the local_client directory
    shutil.make_archive("client_pack", 'zip', "local_client")
    return FileResponse("client_pack.zip", media_type='application/zip', filename="HandsFreePlay_Client.zip")

if __name__ == "__main__":
    uvicorn.run("web_app.server:app", host="0.0.0.0", port=8000, reload=True)
