import numpy as np
from modules.svm_model import SVMModel
from modules.bert_model import BERTModel
from modules.preprocessing import TextPreprocessor

class FakeNewsDetector:
    def __init__(self, svm_path, tfidf_path, bert_path):
        self.svm_model = SVMModel(svm_path, tfidf_path)
        self.bert_model = BERTModel(bert_path)
        self.preprocessor = TextPreprocessor()
        self.weights = {'svm': 0.0, 'bert': 1.0}
    
    def set_weights(self, svm_weight, bert_weight):
        if not np.isclose(svm_weight + bert_weight, 1.0):
            raise ValueError("Weights must sum to 1")
        self.weights = {'svm': svm_weight, 'bert': bert_weight}

    def predictSVM(self, text):
        try:
            processed_text = self.preprocessor.preprocess_text(text)
            svm_pred, svm_proba = self.svm_model.predict(processed_text)
            return svm_pred, svm_proba
        except Exception as e:
            print(f"Error during prediction: {e}")
            return None, None
    def predictBERT(self, text):
        try:
            processed_text = self.preprocessor.preprocess_text(text)
            bert_pred, bert_proba = self.bert_model.predict(processed_text)
            return bert_pred, bert_proba
        except Exception as e:
            print(f"Error during prediction: {e}")
            return None, None   
    def predict(self, text):
        try:
            processed_text = self.preprocessor.preprocess_text(text)
            svm_pred, svm_proba = self.svm_model.predict(processed_text)
            bert_pred, bert_proba = self.bert_model.predict(processed_text)

            # Calculate weighted probabilities
            """"""
            weighted_proba = np.zeros(2)
            weighted_proba += self.weights['svm'] * svm_proba
            weighted_proba += self.weights['bert'] * bert_proba
            
            final_pred = np.argmax(weighted_proba)
            confidence = weighted_proba[final_pred] * 100

            #print results
            print("\n=== Model Predictions ===")
            print(f"SVM Prediction: {'FAKE' if svm_pred == 1 else 'REAL'} "
                  f"(REAL: {svm_proba[0]*100:.2f}%, FAKE: {svm_proba[1]*100:.2f}%)")
            print(f"BERT Prediction: {'FAKE' if bert_pred == 1 else 'REAL'} "
                  f"(REAL: {bert_proba[0]*100:.2f}%, FAKE: {bert_proba[1]*100:.2f}%)")
            #"""

            return final_pred, confidence
        except Exception as e:
            print(f"Error during prediction: {e}")
            return None, None
