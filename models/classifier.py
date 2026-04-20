from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from utils import preprocess_arabic_text

class InstagramClassifier:
    def __init__(self):
        self.MODEL_PATH = "RewaKh/instagram-arabic-classifier"
        self.ID_TO_LABEL = {0: "Other", 1: "Question", 2: "Fact", 3: "Inappropriate"}
        self.model = None
        self.tokenizer = None
        self.load_model()

    def load_model(self):
        print("Loading Classifier Model...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_PATH)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.MODEL_PATH)
        self.model.eval()
        try:
            self.model = torch.quantization.quantize_dynamic(
                self.model, {torch.nn.Linear}, dtype=torch.qint8
            )
            print("Classifier Model quantized.")
        except Exception as e:
            print(f"Classifier quantization failed: {e}")

    def predict(self, texts):
        cleaned_texts = [preprocess_arabic_text(text) for text in texts]
        encoding = self.tokenizer(
            cleaned_texts, 
            padding=True, 
            truncation=True, 
            max_length=128, 
            return_tensors="pt"
        )
        
        with torch.no_grad():
            outputs = self.model(**encoding)
            probs = torch.softmax(outputs.logits, dim=-1)
            pred_ids = torch.argmax(probs, dim=-1).tolist()
            confidences = [probs[i][pred_id].item() for i, pred_id in enumerate(pred_ids)]
        
        results = []
        for i, pred_id in enumerate(pred_ids):
            results.append({
                "pred_label_id": pred_id,
                "pred_label_name": self.ID_TO_LABEL[pred_id],
                "confidence": round(confidences[i], 4),
                "cleaned_text": cleaned_texts[i]
            })
        return results