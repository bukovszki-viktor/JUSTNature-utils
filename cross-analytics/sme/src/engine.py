import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import logging

class SMEMatchmaker:
    """
    SME: Similarity & Matchmaking Engine
    Calculates contextual alignment between JUSTNature CiPeLs.
    """

    def __init__(self):
        self.scaler = StandardScaler()
        self.cities = []
        self.feature_matrix = None
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("SME-Engine")

    def build_feature_matrix(self, city_data_df):
        """Transforms city data into a normalized numerical matrix."""
        self.cities = city_data_df.index.tolist()
        
        # Filter for numeric data types only (float, int, bool) to prevent TypeError
        numeric_df = city_data_df.select_dtypes(include=['number', 'bool'])
        
        # Log dropped columns for transparency
        dropped = [c for c in city_data_df.columns if c not in numeric_df.columns]
        if dropped:
            self.logger.warning(f"Ignored non-numeric columns for similarity: {dropped}")
            
        # Handle potential NaNs with median filling
        clean_df = numeric_df.fillna(numeric_df.median())
        self.feature_matrix = self.scaler.fit_transform(clean_df)
        self.logger.info(f"Feature matrix built for {len(self.cities)} cities.")

    def calculate_similarity(self):
        """Pairwise cosine similarity calculation."""
        if self.feature_matrix is None:
            raise ValueError("Feature matrix not built.")
            
        sim_scores = cosine_similarity(self.feature_matrix)
        return pd.DataFrame(sim_scores, index=self.cities, columns=self.cities)

    def find_top_matches(self, city_name, similarity_df, top_n=3):
        """Returns the most similar peer cities."""
        if city_name not in similarity_df.index:
            return pd.Series(dtype=float)
            
        matches = similarity_df[city_name].sort_values(ascending=False)
        return matches.iloc[1:top_n+1]