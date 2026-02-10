import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from src.engine import SMEMatchmaker
from src.utils.vectorizer import NbSVectorizer

# JUSTNature Brand Colors
INDIGO = '#4831D4'
GREEN = '#CCF381'
WHITE = '#FFFFFF'

def plot_similarity_heatmap(sim_matrix, output_path):
    """
    Generates a high-contrast brand-aligned heatmap of the similarity matrix.
    """
    cities = sim_matrix.index.tolist()
    n = len(cities)
    
    # Create brand-aligned colormap (White to Indigo)
    cmap = mcolors.LinearSegmentedColormap.from_list("JustNature", [WHITE, INDIGO])
    
    plt.figure(figsize=(10, 8), facecolor=WHITE)
    im = plt.imshow(sim_matrix, cmap=cmap)
    
    # Formatting the colorbar
    cbar = plt.colorbar(im)
    cbar.set_label('Similarity Index (Cosine)', size=11, labelpad=10)
    
    # Setting axis labels
    plt.xticks(np.arange(n), cities, rotation=45, ha='right', fontsize=10)
    plt.yticks(np.arange(n), cities, fontsize=10)
    
    # Annotating cells with numeric values
    for i in range(n):
        for j in range(n):
            val = sim_matrix.iloc[i, j]
            # Dynamic text color for readability against dark indigo background
            text_color = WHITE if val > 0.7 else "black"
            plt.text(j, i, f"{val:.2f}", ha="center", va="center", 
                     color=text_color, fontweight='bold', fontsize=9)
            
    plt.title("SME: CITY CONTEXTUAL SIMILARITY MATRIX", pad=25, fontweight='bold', fontsize=14)
    plt.tight_layout()
    
    # Ensure directory exists and save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Heatmap visualization saved to: {output_path}")

def main():
    print("="*60)
    print("   JUSTNature SME: DYNAMIC MATCHMAKING ENGINE")
    print("="*60)

    # 1. Load Input Data
    data_path = "data/raw/city_metadata.csv"
    
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found. Please run generate_sample_metadata.py first.")
        return

    print(f"Loading city metadata from: {data_path}")
    raw_df = pd.read_csv(data_path).set_index('City')

    # 2. Dynamic Feature Detection
    all_cols = raw_df.columns.tolist()
    iucn_cols = [c for c in all_cols if c.startswith('IUCN_')]
    
    categorical_cols = [
        c for c in all_cols 
        if raw_df[c].dtype == 'object' and c not in iucn_cols
    ]
    
    print(f"Detected IUCN Features: {iucn_cols}")
    print(f"Detected Categorical Features: {categorical_cols}")

    # 3. Vectorization Phase
    print("\nPhase 1: Vectorizing qualitative and categorical data...")
    vectorizer = NbSVectorizer()
    processed_df = vectorizer.prepare_feature_set(
        raw_df, 
        iucn_cols=iucn_cols, 
        categorical_cols=categorical_cols
    )

    # 4. Matchmaking Phase
    print("Phase 2: Calculating multi-dimensional similarity...")
    engine = SMEMatchmaker()
    # The engine now internally filters for numeric data to prevent TypeError
    engine.build_feature_matrix(processed_df)
    sim_matrix = engine.calculate_similarity()
    
    # 5. Export Results (CSV)
    output_dir = "data/output"
    os.makedirs(output_dir, exist_ok=True)
    sim_matrix.to_csv(f"{output_dir}/similarity_matrix.csv")
    print(f"Similarity matrix saved to {output_dir}/similarity_matrix.csv")

    # 6. Visualization Phase (Heatmap)
    print("Phase 3: Generating brand-aligned heatmap...")
    plot_similarity_heatmap(sim_matrix, "docs/similarity_heatmap.png")

    # 7. Peer Insight Generation
    print("\n" + "-"*45)
    print("      SCIENTIFIC PEER MATCHES")
    print("-"*45)
    for city in raw_df.index:
        match = engine.find_top_matches(city, sim_matrix, top_n=1)
        if not match.empty:
            peer_name = match.index[0]
            score = match.values[0]
            print(f"[{city:9}] ↔ [{peer_name:9}] | Alignment: {score:.3f}")
    print("-"*45)

if __name__ == "__main__":
    main()