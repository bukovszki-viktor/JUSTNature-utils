import pandas as pd
import numpy as np

class NbSVectorizer:
    """
    Utility to convert qualitative NbS descriptors and IUCN scores 
    into numerical vectors for the SME Engine.
    """

    def __init__(self):
        # Mapping for IUCN Global Standard qualitative answers
        self.iucn_mapping = {
            "Yes": 1.0,
            "Partial": 0.5,
            "No": 0.0,
            "N/A": 0.0
        }

    def encode_iucn_scores(self, df, columns):
        """
        Converts 'Yes/No/Partial' columns into numerical scores.
        """
        df_encoded = df.copy()
        for col in columns:
            if col in df_encoded.columns:
                df_encoded[col] = df_encoded[col].map(self.iucn_mapping).fillna(0.0)
        return df_encoded

    def one_hot_encode_nbs_types(self, df, col_name='NbS_Type'):
        """
        Converts categorical NbS types (e.g., 'Green Wall') into binary columns.
        """
        if col_name not in df.columns:
            return df
        return pd.get_dummies(df, columns=[col_name], prefix="type")

    def prepare_feature_set(self, df, iucn_cols=None, categorical_cols=None):
        """
        Processes a raw city metadata table into a fully numerical feature matrix.
        """
        processed_df = df.copy()
        
        if iucn_cols:
            processed_df = self.encode_iucn_scores(processed_df, iucn_cols)
            
        if categorical_cols:
            for col in categorical_cols:
                processed_df = self.one_hot_encode_nbs_types(processed_df, col)
                
        return processed_df