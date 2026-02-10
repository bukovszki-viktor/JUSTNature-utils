# Context-Aware Neural Imputer (CAN-Imputer) Methodology

## 1. Core Architecture: Generative Adversarial Imputation Nets (GAIN)
The heart of the system is a **Generative Adversarial Network (GAN)** optimized for tabular data imputation.

### The Two-Player Game
1.  **Generator ($G$)**:
    *   **Input**: The incomplete data vector $X$ + Random Noise $Z$ + Mask Vector $M$.
    *   **Goal**: Create a "complete" vector where missing values are filled so realistically that the Discriminator cannot distinguish them from observed data.
2.  **Discriminator ($D$)**:
    *   **Input**: The complete vector (mix of real observed values and Generator's guesses).
    *   **Goal**: Determine which components were originally observed ($m=1$) vs. imputed ($m=0$).
    *   **Output**: A probability matrix of the same shape as the input.

$$ \min_G \max_D V(D, G) = \mathbb{E}[ \log(D(X)) + \log(1 - D(G(X + Z))) ] $$

## 2. Context-Aware Enhancements
Standard GAIN models often fail on environmental time-series because they lack temporal awareness. We solve this with **Cyclical Feature Encoding**.

### Temporal Injection
Raw timestamps are useless to a neural network. We convert time-of-day into continuous orthogonal signals:
$$ \text{Hour}_{\sin} = \sin\left(\frac{2\pi \cdot h}{24}\right), \quad \text{Hour}_{\cos} = \cos\left(\frac{2\pi \cdot h}{24}\right) $$
This ensures that "23:00" and "00:00" are numerically close, preserving the diurnal cycle logic (e.g., temperature drops at night).

## 3. Physics-Informed Post-Processing
Neural networks are purely statistical and can hallucinate physically impossible values (e.g., negative PM2.5 or 300°C temperature). 

The `NbSPostprocessor` enforces strict physical laws:
1.  **Hard Bounds**: 
    *   $PM2.5 \ge 0$
    *   $-20 \le Temp \le 50$
2.  **Diurnal Consistency**: Restricts rapid non-physical jumps (Rate of Change limits).
3.  **Seam Smoothing**: Applies a weighted blend at the boundaries of imputed gaps to prevent "step" artifacts in the time series.

## 4. Evaluation Metrics
We measure performance not just by accuracy, but by distribution fidelity:
*   **RMSE (Root Mean Square Error)**: Accuracy of point estimates.
*   **MAE (Mean Absolute Error)**: Robustness to outliers.
*   **KS-Test (Kolmogorov-Smirnov)**: Measures if the *distribution* of imputed values matches the natural distribution of the observed data.
