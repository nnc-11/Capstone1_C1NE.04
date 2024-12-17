import os
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class HistoricalVerifier:
    def __init__(self, model_path, embedding_dir, threshold=0.7):
        self.model = SentenceTransformer(model_path)
        self.embedding_dir = embedding_dir
        self.threshold = threshold
        self.reference_embeddings, self.reference_sentences = self._load_all_embeddings()

    def _load_all_embeddings(self):
        all_embeddings = []
        all_sentences = []
        """for filename in sorted(os.listdir(self.embedding_dir)):
            if filename.endswith('_results.csv'):
                df = pd.read_csv(os.path.join(self.embedding_dir, filename))
                """
        for i in range(1, 10): # max 73 file
            filename = f"{i}_results.csv"  
            filepath = os.path.join(self.embedding_dir, filename)  
            if os.path.exists(filepath): 
                df = pd.read_csv(filepath)

                embeddings = np.array([eval(emb) for emb in df['embedding']])
                all_embeddings.append(embeddings)
                all_sentences.extend(df['sentence'].tolist())
        return np.concatenate(all_embeddings), all_sentences

    def verify_text(self, input_text):
        input_sentences = [s.strip() for s in input_text.split('.') if s.strip()]
        input_embeddings = self.model.encode(input_sentences)
        verification_results = []
        overall_similarities = []

        for sentence, embedding in zip(input_sentences, input_embeddings):
            similarities = cosine_similarity([embedding], self.reference_embeddings)[0]
            max_similarity = np.max(similarities)
            most_similar_index = np.argmax(similarities)
            most_similar_sentence = self.reference_sentences[most_similar_index]
            overall_similarities.append(max_similarity)
            verification_results.append({
                'input_sentence': sentence,
                'max_similarity': max_similarity,
                'most_similar_sentence': most_similar_sentence,
                'is_accurate': max_similarity >= self.threshold
            })

        overall_confidence = np.mean(overall_similarities)
        return {
            'overall_confidence': overall_confidence,
            'is_historically_accurate': overall_confidence >= self.threshold,
            'sentence_details': verification_results
        }

    def interactive_verify(self, input_text):
            result = self.verify_text(input_text)
            s="LS model: <br>"
            #print("\n--- Results ---")
            s+=(f"<br>Overall Confidence: {result['overall_confidence']:.2%}")
            s+=(f"<br>Verification Status: {'Accurate' if result['is_historically_accurate'] else 'Needs Verification'}")

            s+=("<br>Supporting Information:<br>")
            for detail in result['sentence_details']:
                #print(f" - Input: {detail['input_sentence']}")
                s+=(f"<br>Most Similar: {detail['most_similar_sentence']}")
                #print(f"   Similarity: {detail['max_similarity']:.2%}")
               # print(f"   Accurate: {'Yes' if detail['is_accurate'] else 'No'}")"""
            return s

# Example usage
if __name__ == "__main__":
    model_path = "N:\FNDDetectorAI\models\ModelSimCSE_VN"
    embedding_dir = "N:\FNDDetectorAI\models\PBert"
    verifier = HistoricalVerifier(model_path, embedding_dir)
    s = verifier.interactive_verify("Thời kỳ đồ đá")
    print(s)
