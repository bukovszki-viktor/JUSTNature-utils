# Methodology: Physico-Statistical NbS Anomaly Detector (PS-NAD)

## 1. Overview
The **PS-NAD** system employs a hybrid "Physico-Statistical" approach to validate environmental sensor data. This dual-layer architecture is designed to distinguish between **Real Environmental Events** (e.g., a pollution spike due to inversion) and **Sensor Errors** (e.g., drift, electronics failure).

## 2. Architecture
The pipeline consists of three main stages:

### Stage 1: Data Preprocessing
Raw sensor data is ingested and transformed to ensure high-quality input for the detection layers.
- **Cleaning**: Removal of duplicate timestamps and interpolation of minor gaps.
- **Scaling**: Features are standardized (Z-score normalization) or MinMax scaled. This is critical for distance-based algorithms like Isolation Forest.
- **Feature Engineering**: Temporal features (hour of day) are extracted to help models learn diurnal patterns.

### Stage 2: Statistical Detection (The "Stat" Layer)
**Algorithm**: Isolation Forest (Unsupervised)
- **Goal**: Identify outliers based purely on statistical distribution in high-dimensional space.
- **Inputs**: Primary variables (e.g., PM2.5, Temperature) and contextual variables (Wind Speed).
- **Output**: A binary flag (`-1` for anomaly, `1` for normal) and an anomaly score.
- **Why Isolation Forest?**: It effectively isolates anomalies without needing labeled training data, which is rare in sensor networks.

### Stage 3: Physics-Informed Gating (The "Physico" Layer)
**Module**: Physics Gate (PIG)
- **Goal**: Validate the statistical anomalies against known physical laws and domain constraints.
- **Logic**: If the Stat Layer flags a point, the Physics Gate asks: *"Is this physically possible?"*

#### Validation Rules
1.  **Feasibility Check (Hard Limits)**:
    *   Is the value within the sensor's physical range? (e.g., PM2.5 cannot be negative).
2.  **Stability Check (Rate of Change)**:
    *   Does the value jump faster than diffusion allows? (e.g., PM2.5 rising 100 µg/m³ in 1 hour is suspicious).
3.  **Diurnal Consistency**:
    *   Does the value match expected day/night cycles?
4.  **Cross-Variable Correlation**:
    *   **Wind Interaction**: High wind speeds typically disperse pollutants. A spike in PM2.5 during a gale is flagged as a likely sensor error.
    *   **Temperature**: Sudden drops not correlated with weather fronts are suspect.

## 3. Classification Outcome
The system outputs a final classification for each anomaly:
*   **Real Event**: The data is statistically abnormal but physically plausible. (Action: Alert Environmental Team).
*   **Hardware Error**: The data violates physical rules. (Action: Flag for Maintenance).
