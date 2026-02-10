import json
import os
import pandas as pd
import numpy as np
import logging

class NbSPostprocessor:
    """
    Physics-Informed Postprocessor for NbS Imputation.
    
    Refines the output of the GAIN generator by applying hard physical 
    constraints, diurnal pattern alignment, and seam smoothing to ensure
    temporal consistency.
    """

    def __init__(self, rules_path=None):
        """
        Args:
            rules_path (str): Path to the physics_rules.json file.
        """
        if rules_path is None:
            # Look for rules in the PS-NAD directory relative to this file
            self.rules_path = os.path.join(os.path.dirname(__file__), '../../ps-nad/src/physics_rules.json')
        else:
            self.rules_path = rules_path
            
        self.rules = self._load_rules()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("NbSPostprocessor")

    def _load_rules(self):
        """Loads physical constraints from JSON."""
        if not os.path.exists(self.rules_path):
            self.logger.error(f"Rules file not found at {self.rules_path}")
            return {}
        try:
            with open(self.rules_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error parsing rules: {e}")
            return {}

    def apply_physical_bounds(self, df_imputed, target_col):
        """
        Clips imputed values to the hard min/max physical limits defined in rules.
        """
        rule = self.rules.get(target_col)
        if not rule:
            return df_imputed
            
        min_val = rule.get('min_value', -np.inf)
        max_val = rule.get('max_value', np.inf)
        
        df_imputed[target_col] = df_imputed[target_col].clip(lower=min_val, upper=max_val)
        return df_imputed

    def apply_diurnal_constraints(self, df_imputed, target_col, mask):
        """
        Ensures imputed values fall within expected diurnal (hourly) ranges.
        """
        rule = self.rules.get(target_col)
        if not rule or 'diurnal_expectations' not in rule:
            return df_imputed

        expectations = rule['diurnal_expectations']
        
        # Only check points where mask is 0 (imputed)
        imputed_indices = df_imputed[mask[target_col] == 0].index
        
        for idx in imputed_indices:
            hour = str(idx.hour)
            if hour in expectations:
                low, high = expectations[hour]
                val = df_imputed.at[idx, target_col]
                if val < low or val > high:
                    # Soft clip to diurnal bounds
                    df_imputed.at[idx, target_col] = np.clip(val, low, high)
        
        return df_imputed

    def smooth_seams(self, df_imputed, target_col, mask, window=3):
        """
        Performs linear smoothing at the 'seams' where observed data meets imputed data.
        This prevents artificial 'steps' that can trigger false positives in downstream detectors.
        """
        rule = self.rules.get(target_col)
        max_delta = rule.get('max_delta_per_hour', np.inf) if rule else np.inf
        
        data = df_imputed[target_col].values
        m = mask[target_col].values
        
        for i in range(1, len(data)):
            # Detect a transition from observed to imputed
            if m[i-1] == 1 and m[i] == 0:
                delta = data[i] - data[i-1]
                if abs(delta) > max_delta:
                    self.logger.info(f"Smoothing entry seam for {target_col} at index {i}")
                    # Apply a small linear correction to the first 'window' points of the imputation
                    correction = delta - (np.sign(delta) * max_delta * 0.8)
                    for j in range(min(window, len(data)-i)):
                        weight = (window - j) / window
                        data[i+j] -= correction * weight
            
            # Detect a transition from imputed back to observed
            elif m[i-1] == 0 and m[i] == 1:
                delta = data[i] - data[i-1]
                if abs(delta) > max_delta:
                    self.logger.info(f"Smoothing exit seam for {target_col} at index {i}")
                    # Apply a small linear correction to the last 'window' points of the imputation
                    correction = delta - (np.sign(delta) * max_delta * 0.8)
                    for j in range(1, min(window + 1, i)):
                        weight = (window - (j-1)) / window
                        data[i-j] += correction * weight

        df_imputed[target_col] = data
        return df_imputed

    def process_imputed_stream(self, df_imputed, mask, target_cols=None):
        """
        Executes the full post-processing pipeline for designated columns.
        """
        if target_cols is None:
            target_cols = [col for col in df_imputed.columns if col in self.rules]
            
        df_result = df_imputed.copy()
        
        for col in target_cols:
            self.logger.info(f"Post-processing column: {col}")
            df_result = self.apply_physical_bounds(df_result, col)
            df_result = self.apply_diurnal_constraints(df_result, col, mask)
            df_result = self.smooth_seams(df_result, col, mask)
                
        return df_result

if __name__ == "__main__":
    # Test logic
    # Mocking a dataframe and mask for verification
    timestamps = pd.date_range("2025-01-01", periods=10, freq="H")
    test_df = pd.DataFrame({"PM2.5": [10, 12, 100, 95, 90, 85, 10, 12, 11, 10]}, index=timestamps)
    test_mask = pd.DataFrame({"PM2.5": [1, 1, 0, 0, 0, 0, 1, 1, 1, 1]}, index=timestamps)
    
    post = NbSPostprocessor()
    if post.rules:
        refined_df = post.process_imputed_stream(test_df, test_mask)
        print("Original with jump:\n", test_df["PM2.5"].values)
        print("Refined values:\n", refined_df["PM2.5"].values)
    else:
        print("Could not load rules. Check path to physics_rules.json.")