from app.paths import PathManager
from modules.fake_news_detector import FakeNewsDetector
from modules.UrlText_Ver1 import input_UrlText
if __name__ == "__main__":
    # Tạo instance của PathManager
    path_manager = PathManager()
    
    # Sử dụng các phương thức của PathManager để lấy đường dẫn
    detector = FakeNewsDetector(
        svm_path=path_manager.get_svm_model_path(),
        tfidf_path=path_manager.get_tfidf_vectorizer_path(),
        bert_path=path_manager.get_bert_model_path()
    )
        
    while True:
        text = input("\nEnter text to analyze (or 'q' to quit): ")
        #text = input("\nEnter url to analyze (or 'q' to quit): ")
        #text = input_UrlText(text).get_Text_in_Url()['content']

        if text.lower() == 'q':
            break
        
        prediction, confidence = detector.predict(text)
        if prediction is not None:
            print("\n=== Ensemble Results ===")
            print(f"\nPrediction: {'FAKE' if prediction == 1 else 'REAL'}, Confidence: {confidence:.2f}%")
