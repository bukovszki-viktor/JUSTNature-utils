import json
import os
import logging
import pandas as pd
import numpy as np

class PhysicsGate:
    """
    Physics-Informed Gating (PIG) Module
    
    This module validates statistical anomalies detected by the ML layer.
    It applies physical constraints (hard limits, rate of change, diurnal patterns,
    and proxy correlations) to determine if a data spike is physically 
    plausible or a sensor malfunction.
    """

    def __init__(self, rules_path=None):
        """
        Initialize the Physics Gate with a set of rules.
        
        Args:
            rules_path (str): Path to the physics_rules.json file.
        """
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("PhysicsGate")

        if rules_path is None:
            # Default to the same directory as this script
            rules_path = os.path.join(os.path.dirname(__file__), 'physics_rules.json')
            
        self.rules = self._load_rules(rules_path)

    def _load_rules(self, path):
        """Loads physical constraints from a JSON file."""
        if not os.path.exists(path):
            self.logger.warning(f"Rules file not found at {path}. Using empty ruleset.")
            return {}
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading rules file: {e}")
            return {}

    def validate_event(self, variable_name, current_val, previous_val, timestamp=None, proxy_data=None):
        """
        Validates a single data point against physical rules and returns a detailed report.
        
        Args:
            variable_name (str): The name of the indicator (e.g., 'PM2.5').
            current_val (float): The current measurement value.
            previous_val (float): The immediately preceding measurement.
            timestamp (datetime): Timestamp of the measurement for diurnal checks.
            proxy_data (dict): Optional dictionary of context variables.
            
        Returns:
            dict: Detailed validation report including validity, score, and reason.
        """
        rule = self.rules.get(variable_name)
        if not rule:
            return {"valid": True, "physical_score": 1.0, "reason": "No physical rules defined."}

        # 1. Hard Limit Check (Min/Max)
        if current_val < rule.get('min_value', -float('inf')) or \
           current_val > rule.get('max_value', float('inf')):
            return {"valid": False, "physical_score": 0.0, "reason": "Reasonableness Error: Value outside physical range."}

        # 2. Rate of Change Check (Diffusion/Jump Limit)
        if previous_val is not None:
            delta = abs(current_val - previous_val)
            max_delta = rule.get('max_delta_per_hour', float('inf'))
            if delta > max_delta:
                # If it's just over the limit, we might assign a low score instead of immediate rejection
                if delta > max_delta * 2:
                    return {"valid": False, "physical_score": 0.1, "reason": "Stability Error: Rate of change exceeds physical diffusion limits."}

        # 3. Diurnal Cycle Check (Optional)
        if timestamp is not None and 'diurnal_expectations' in rule:
            hour = timestamp.hour
            expected_range = rule['diurnal_expectations'].get(str(hour))
            if expected_range:
                if current_val < expected_range[0] or current_val > expected_range[1]:
                    # This is suspicious but not necessarily an error on its own
                    self.logger.debug(f"Diurnal deviation at hour {hour} for {variable_name}")

        # 4. Correlation Check (Physics-Informed Gating)
        if proxy_data:
            # Check Wind Speed vs Pollutant Correlation (Typical Negative Correlation)
            if 'wind_speed' in proxy_data and rule.get('wind_speed_correlation') == 'negative':
                wind_speed = proxy_data['wind_speed']
                # High wind usually prevents extreme local PM spikes
                if wind_speed > 15 and current_val > (previous_val * 3 if previous_val else 50):
                    return {"valid": False, "physical_score": 0.2, "reason": "Correlation Error: Spike detected during high-wind dispersion."}

            # Check Rain vs Soil Moisture Correlation (Typical Positive Correlation)
            if 'rain' in proxy_data and rule.get('rain_correlation') == 'positive':
                if proxy_data['rain'] == 0 and previous_val is not None and current_val > (previous_val + 5):
                     return {"valid": False, "physical_score": 0.3, "reason": "Correlation Error: Moisture increase detected without precipitation."}

        return {"valid": True, "physical_score": 1.0, "reason": "Physically Validated Event."}

    def process_anomalies(self, df, anomaly_indices, target_col, proxy_cols=None):
        """
        Filters a list of statistical anomalies through the physical gate using batch processing.
        
        Args:
            df (pd.DataFrame): The full dataset (must have a DatetimeIndex).
            anomaly_indices (pd.Index): Indices flagged by the ML detector.
            target_col (str): The name of the variable to validate.
            proxy_cols (list): List of column names to use as physical context.
            
        Returns:
            pd.DataFrame: A report detailing which anomalies are 'Real Events' vs 'Hardware Errors'.
        """
        if df.empty or len(anomaly_indices) == 0:
            return pd.DataFrame()

        results = []
        
        for idx in anomaly_indices:
            current_val = df.loc[idx, target_col]
            
            # Efficiently find the previous valid observation
            try:
                pos = df.index.get_loc(idx)
                previous_val = df.iloc[pos - 1][target_col] if pos > 0 else None
            except (KeyError, IndexError):
                previous_val = None
            
            # Extract proxy data
            proxies = df.loc[idx, proxy_cols].to_dict() if proxy_cols else None
            
            # Extract timestamp if the index is datetime-like
            timestamp = idx if isinstance(idx, pd.Timestamp) else None
            
            validation = self.validate_event(
                variable_name=target_col, 
                current_val=current_val, 
                previous_val=previous_val, 
                timestamp=timestamp,
                proxy_data=proxies
            )
            
            results.append({
                "timestamp": idx,
                "value": current_val,
                "physical_score": validation['physical_score'],
                "is_physically_valid": validation['valid'],
                "status": "Real Event" if validation['valid'] else "Hardware Error",
                "reason": validation['reason']
            })
            
        return pd.DataFrame(results).set_index("timestamp")

if __name__ == "__main__":
    # Example logic for testing the module
    print("Testing Physics Gate Module with Enhanced Logic...")
    
    # Example ruleset for demonstration
    example_rules = {
        "PM2.5": {
            "min_value": 0,
            "max_value": 500,
            "max_delta_per_hour": 50,
            "wind_speed_correlation": "negative"
        }
    }
    
    # Create temp rules file for testing
    with open('physics_rules.json', 'w') as f:
        json.dump(example_rules, f)
        
    gate = PhysicsGate('physics_rules.json')
    
    # Test 1: Impossible Spike
    res = gate.validate_event("PM2.5", 450, 20, proxy_data={'wind_speed': 25.0})
    print(f"Test 1 (High Wind Spike): {res['status']} - {res['reason']}")
    
    # Test 2: Out of Range
    res = gate.validate_event("PM2.5", -5, 10)
    print(f"Test 2 (Negative Value): {res['status']} - {res['reason']}")

    # Clean up
    if os.path.exists('physics_rules.json'):
        os.remove('physics_rules.json')