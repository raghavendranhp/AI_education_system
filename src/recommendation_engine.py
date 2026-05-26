import pandas as pd
import numpy as np
import os
import joblib
from sklearn.metrics.pairwise import cosine_similarity

class HybridRecommender:
    def __init__(self, models_dir: str = '../models'):
        self.models_dir = models_dir
        self.interaction_matrix = None
        self.popularity_scores = None
        self.load_artifacts()

    def load_artifacts(self):
        try:
            self.interaction_matrix = joblib.load(os.path.join(self.models_dir, 'interaction_matrix.pkl'))
            self.popularity_scores = joblib.load(os.path.join(self.models_dir, 'popularity_scores.pkl'))
        except Exception as e:
            print(f"Warning: Recommender artifacts not found in {self.models_dir}. {e}")

    def build_and_save_artifacts(self, student_vle_path: str):
        print("Building Hybrid Recommendation Artifacts...")
        # To avoid massive memory issues, we sample or group aggressively
        df = pd.read_csv(student_vle_path, usecols=['id_student', 'id_site', 'sum_click'], nrows=1000000)
        
        # 1. Collaborative Matrix
        interaction = df.groupby(['id_student', 'id_site'])['sum_click'].sum().reset_index()
        # Filter sparse interactions to save memory
        user_counts = interaction['id_student'].value_counts()
        item_counts = interaction['id_site'].value_counts()
        
        interaction = interaction[interaction['id_student'].isin(user_counts[user_counts > 5].index)]
        interaction = interaction[interaction['id_site'].isin(item_counts[item_counts > 5].index)]
        
        matrix = interaction.pivot(index='id_student', columns='id_site', values='sum_click').fillna(0)
        
        # Normalize rows
        matrix_norm = matrix.div(matrix.sum(axis=1), axis=0).fillna(0)
        
        # 2. Popularity Scores
        popularity = interaction.groupby('id_site')['sum_click'].sum()
        popularity_norm = popularity / popularity.max()
        
        os.makedirs(self.models_dir, exist_ok=True)
        joblib.dump(matrix_norm, os.path.join(self.models_dir, 'interaction_matrix.pkl'))
        joblib.dump(popularity_norm, os.path.join(self.models_dir, 'popularity_scores.pkl'))
        
        self.interaction_matrix = matrix_norm
        self.popularity_scores = popularity_norm
        print("Artifacts saved successfully.")

    def recommend(self, student_id: int, top_n: int = 5) -> list:
        if self.interaction_matrix is None or self.popularity_scores is None:
            return [{"error": "Models not loaded."}]
            
        # Cold start handling
        if student_id not in self.interaction_matrix.index:
            pop_recs = self.popularity_scores.sort_values(ascending=False).head(top_n)
            return [{"site_id": k, "score": v, "reason": "Popularity Fallback (Cold Start)"} for k, v in pop_recs.items()]
            
        # Collaborative Similarity
        student_vec = self.interaction_matrix.loc[[student_id]]
        similarities = cosine_similarity(student_vec, self.interaction_matrix).flatten()
        sim_series = pd.Series(similarities, index=self.interaction_matrix.index)
        
        similar_students = sim_series.sort_values(ascending=False)[1:6].index
        collab_scores = self.interaction_matrix.loc[similar_students].mean()
        
        # Hybrid Scoring (0.7 Collab + 0.3 Popularity)
        combined_scores = pd.DataFrame({'collab': collab_scores, 'popular': self.popularity_scores}).fillna(0)
        combined_scores['hybrid'] = 0.7 * combined_scores['collab'] + 0.3 * combined_scores['popular']
        
        # Filter already interacted
        student_interacted = self.interaction_matrix.loc[student_id]
        combined_scores = combined_scores[student_interacted == 0]
        
        recs = combined_scores.sort_values(by='hybrid', ascending=False).head(top_n)
        
        return [{"site_id": idx, "score": row['hybrid'], "reason": "Hybrid Match (High Peer Activity)"} for idx, row in recs.iterrows()]

if __name__ == '__main__':
    recommender = HybridRecommender()
    recommender.build_and_save_artifacts('../data/raw/studentVle.csv')
