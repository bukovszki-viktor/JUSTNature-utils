# JUSTNature SME Tool
**Similarity & Matchmaking Engine for CiPeLs**

The SME tool identifies "Scientific Peers" among city practice labs by analyzing multi-dimensional contextual data (environmental, governance, and NbS profiles).

## Documentation
*   [**Methodology**](docs/methodology.md): The scientific basis, vectorization logic, and mathematical formulas (Cosine Similarity, Z-scores).
*   [**User Guide**](docs/user_guide.md): Instructions for generating sample data, running the engine, and interpreting the visualization.

## Quick Start
```bash
# 1. Generate Metadata
python sample_gen.py

# 2. Run Matchmaker
python run_matchmaking.py
```
**Output**: Heatmaps and similarity matrices in `data/output` and `docs`.
