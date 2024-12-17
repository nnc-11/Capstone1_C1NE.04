import os

class PathManager:
    def __init__(self):
        # FNDDetectorAI
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def get_svm_model_path(self):
        return os.path.join(self.project_root, 'models', 'SVM_ver7.pkl')

    def get_tfidf_vectorizer_path(self):
        return os.path.join(self.project_root, 'models', 'Tfidf_ver7.pkl')

    def get_bert_model_path(self):
        return os.path.join(self.project_root, 'models', 'bert')
    
    def get_PBERT(self):
        return os.path.join(self.project_root, 'models', 'PBert')
    
    def get_ModelSimCSE_VN(self):
        return os.path.join(self.project_root, 'models', 'ModelSimCSE_VN')
