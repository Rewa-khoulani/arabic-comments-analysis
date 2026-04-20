

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
from typing import List, Optional
from models.classifier import InstagramClassifier
from models.sentiment import InstagramSentiment
from models.summarizer import InstagramSummarizer

app = FastAPI(title="Instagram AI Suite")



# Threading optimization
try:
    torch.set_num_threads(2) # Limit threads to prevent contention on Windows
except Exception as e:
    print(f"Warning: Could not set num_threads: {e}")

# Initialize Models
print("Initializing models...")
classifier = InstagramClassifier()
sentiment = InstagramSentiment()
summarizer = InstagramSummarizer()
print("Models initialized.")



# ==============================================================================
# API Endpoints
# ==============================================================================

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Instagram AI Suite API",
        "endpoints": {
            "Classifier": "/predict_classifier",
            "Sentiment": "/predict_sentiment",
            "Summarizer": "/summarize",
            "Legacy Predict": "/predict"
        },
        "docs": "/docs"
    }

class CommentBatchInput(BaseModel):
    texts: List[str]

class SingleCommentInput(BaseModel):
    text: str

@app.post("/predict_classifier")
async def predict_classifier_batch(input: CommentBatchInput):
    if not input.texts: return []
    return classifier.predict(input.texts)

@app.post("/predict_sentiment")
async def predict_sentiment_batch(input: CommentBatchInput):
    if not input.texts: return []
    return sentiment.predict(input.texts)

@app.post("/summarize")
async def summarize_comments(input: CommentBatchInput):
    return {"summary": summarizer.summarize(input.texts)}

# Legacy/Default Endpoint (Classifier Single)
@app.post("/predict")
async def predict_comment(input: SingleCommentInput):
    results = classifier.predict([input.text])
    return results[0]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
