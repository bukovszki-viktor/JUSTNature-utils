import pandas as pd
import os

def generate_sample(schema_type="standard"):
    """
    Generates a high-fidelity sample dataset for the SME tool.
    Supports different metadata configurations to test the engine's flexibility.
    
    Args:
        schema_type (str): 'standard' for basic CiPeL data, 
                          'extended' for deep-dive research data.
    """
    
    # 1. Define the base cities used in the JUSTNature project
    cities = ['Budapest', 'Chania', 'Gzira', 'Leuven', 'Milan', 'Munich']
    
    # 2. Define data configurations based on the schema_type
    if schema_type == "extended":
        # Extended schema includes extra environmental indicators and socio-economic data
        data = {
            'City': cities,
            'PM2.5_Avg': [15.2, 18.5, 22.1, 12.8, 28.4, 14.1],
            'NO2_Avg': [22.4, 15.1, 35.6, 18.2, 45.1, 20.5], # Extra indicator
            'Temp_Reduction': [2.1, 1.2, 0.5, 3.4, 1.8, 2.9],
            'Population_Density': [3300, 1200, 4500, 1800, 7500, 4800],
            'Social_Vulnerability_Index': [0.4, 0.2, 0.6, 0.1, 0.7, 0.3], # Social layer
            'Avg_Wind_Speed': [3.2, 5.4, 4.1, 2.8, 1.5, 3.1],
            'NbS_Type': ['Park', 'Coastal', 'Urban Forest', 'Park', 'Green Wall', 'Park'],
            'IUCN_Biodiversity': ['Yes', 'Partial', 'No', 'Yes', 'Partial', 'Yes'],
            'IUCN_Governance': ['Yes', 'Yes', 'Partial', 'Yes', 'No', 'Yes'],
            'IUCN_Economics': ['Partial', 'No', 'No', 'Yes', 'Yes', 'Partial']
        }
    else:
        # Standard JUSTNature baseline schema
        data = {
            'City': cities,
            'PM2.5_Avg': [15.2, 18.5, 22.1, 12.8, 28.4, 14.1],
            'Temp_Reduction': [2.1, 1.2, 0.5, 3.4, 1.8, 2.9],
            'Population_Density': [3300, 1200, 4500, 1800, 7500, 4800],
            'Avg_Wind_Speed': [3.2, 5.4, 4.1, 2.8, 1.5, 3.1],
            'NbS_Type': ['Park', 'Coastal', 'Urban Forest', 'Park', 'Green Wall', 'Park'],
            'IUCN_Biodiversity': ['Yes', 'Partial', 'No', 'Yes', 'Partial', 'Yes'],
            'IUCN_Governance': ['Yes', 'Yes', 'Partial', 'Yes', 'No', 'Yes']
        }
    
    df = pd.DataFrame(data)
    
    # 3. Handle Output Path
    output_dir = "data/raw"
    output_path = os.path.join(output_dir, "city_metadata.csv")
    os.makedirs(output_dir, exist_ok=True)
    
    df.to_csv(output_path, index=False)
    print(f"--- SME Sample Data Generated ---")
    print(f"Schema: {schema_type.upper()}")
    print(f"Columns: {list(df.columns)}")
    print(f"Destination: {output_path}")

if __name__ == "__main__":
    # You can toggle between 'standard' and 'extended' here to test the SME's flexibility
    generate_sample(schema_type="extended")