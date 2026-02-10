# SME Methodology: Similarity & Matchmaking Engine

## 1. Scientific Basis
The **SME (Similarity & Matchmaking Engine)** is designed to identify "Scientific Peers" among JUSTNature CiPeLs (City Practice Labs). Unlike simple clustering, SME uses a **multi-dimensional contextual alignment** approach to ensure that cities are matched not just by size, but by their *Nature-based Solution (NbS) profile* and *governance maturity*.

## 2. The Vectorization Pipeline
The engine transforms qualitative city metadata into a high-dimensional numerical space.

### A. Quantitative Features (Direct Ingestion)
Numerical indicators are normalized using Z-score standardization ($z = \frac{x - \mu}{\sigma}$).
*   **Examples**: `PM2.5_Baseline`, `Population_Density`, `Temp_Reduction`.

### B. Qualitative Features (One-Hot Encoding)
Categorical descriptors are exploded into binary orthogonal vectors.
*   **Input**: `NbS_Type = "Green Wall"`
*   **Vector**: `[is_Green_Wall=1, is_Park=0, is_Coastal=0, ...]`

### C. IUCN Standard Scoring (Ordinal Encoding)
The engine integrates the **IUCN Global Standard for NbS**, converting self-assessment answers into weighted scores:
*   `Yes` $\rightarrow$ **1.0** (Full Alignment)
*   `Partial` $\rightarrow$ **0.5** (In Progress)
*   `No` / `N/A` $\rightarrow$ **0.0** (Gap)

### D. Robustness Handling
To prevent skewing from missing data, the engine applies:
1.  **Type Filtering**: Automatically isolates numeric/boolean columns.
2.  **Median Imputation**: Fills gaps with the median value of the dataset, minimizing the impact of outliers.

## 3. Similarity Calculation
Once the feature matrix $M$ ($n \times m$) is built, the engine calculates the **Cosine Similarity** between every pair of cities (A and B):

$$
\text{Similarity}(A, B) = \frac{A \cdot B}{\|A\| \|B\|} = \frac{\sum_{i=1}^{n} A_i B_i}{\sqrt{\sum_{i=1}^{n} A_i^2} \sqrt{\sum_{i=1}^{n} B_i^2}}
$$

*   **Range**: [-1, 1], where **1.0** indicates identical contextual profiles.
*   **Output**: A dense $n \times n$ matrix representing the "Peer Network".

## 4. Visualization & Insight
*   **Heatmap**: A high-contrast brand-aligned matrix allows for rapid identification of clusters.
*   **Peer Matching**: The engine extracts the Top-N closest neighbors for each city, enabling targeted knowledge exchange (e.g., *Budapest should talk to Leuven about Governance*).
