from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from classifier-eng import LogClassifier

app = FastAPI(title="Log Classifier API", version="1.0")
classifier = LogClassifier()

class TextPayload(BaseModel):
    text: str

@app.post("/classify")
def classify_text(payload: TextPayload):
    if not payload.text:
        raise HTTPException(status_code=400, detail="Text payload cannot be empty")
    result = classifier.classify(payload.text)
    return {"classifiers": result}

# Set up Jinja2 templates directory
templates = Jinja2Templates(directory="templates")

@app.get("/ui", response_class=HTMLResponse)
def read_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})