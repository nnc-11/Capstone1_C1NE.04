import joblib

class SVMModel:
    def __init__(self, svm_path, tfidf_path):
        self.classifier = joblib.load(svm_path)
        self.vectorizer = joblib.load(tfidf_path)

    def predict(self, text):
        text_tfidf = self.vectorizer.transform([text])
        prediction = self.classifier.predict(text_tfidf)
        proba = self.classifier.predict_proba(text_tfidf)[0]
        return prediction[0], proba
