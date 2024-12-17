import torch
import numpy as np
from transformers import BertTokenizerFast, BertForSequenceClassification

class BERTModel:
    def __init__(self, model_path):
        self.tokenizer = BertTokenizerFast.from_pretrained(model_path)
        self.model = BertForSequenceClassification.from_pretrained(model_path)

    def predict(self, text):
        inputs = self.tokenizer(text, truncation=True, padding=True, 
                              max_length=512, return_tensors="pt")
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=1).numpy()[0]
        class_label = np.argmax(probabilities)
        return class_label, probabilities
