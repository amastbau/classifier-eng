from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from classifiereng import LogClassifier

# Create the FastAPI app with metadata for better documentation.
app = FastAPI(
    title="Log Classifier API",
    description="API for classifying log texts and providing a UI to test the endpoints",
    version="1.0.0"
)

# Initialize the classifier.
classifier = LogClassifier()

# Define the payload model.
class TextPayload(BaseModel):
    text: str

# Endpoint to classify log text.
@app.post("/classify", summary="Classify Log Text", tags=["Classification"])
def classify_text(payload: TextPayload):
    """
    Classify the provided log text using the LogClassifier.
    
    - **payload.text**: The log text to be classified.
    """
    if not payload.text:
        raise HTTPException(status_code=400, detail="Text payload cannot be empty")
    result = classifier.classify(payload.text)
    return {"classifiers": result}

# Set up Jinja2 templates directory.
templates = Jinja2Templates(directory="templates")

# GET endpoint to render the UI form.
@app.get("/ui", response_class=HTMLResponse, summary="UI for Testing Classifier", tags=["UI"])
def get_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})

# POST endpoint to process the form submission.
@app.post("/ui", response_class=HTMLResponse, summary="Classify Log Text via UI", tags=["UI"])
def post_ui(request: Request, text: str = Form(...)):
    result = classifier.classify(text)
    return templates.TemplateResponse("index.html", {"request": request, "result": result})