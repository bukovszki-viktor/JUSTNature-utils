# Comprehensive SEM Impact Report: Szombathely Diagnostic Suite
**Generated:** 2026-02-20 11:12 | **N:** 30

## 1. Descriptive Statistics (Indicator Reliability)
Standardized means and variance for the kept survey indicators.

|      |    mean |      std |   min |   max |
|:-----|--------:|---------:|------:|------:|
| er1  | 4.66667 | 0.479463 |     4 |     5 |
| er2  | 2.33333 | 0.802296 |     1 |     4 |
| er3  | 4.1     | 0.661764 |     3 |     5 |
| ec1  | 4.03333 | 0.668675 |     3 |     5 |
| ec2  | 4.26667 | 0.52083  |     3 |     5 |
| ec3  | 4.36667 | 0.490133 |     4 |     5 |
| ec4  | 3.63333 | 0.808717 |     2 |     5 |
| sek1 | 3.66667 | 0.844182 |     2 |     5 |
| sek2 | 3       | 0.830455 |     2 |     5 |
| sek3 | 2.6     | 0.855006 |     1 |     5 |
| atb1 | 3.46667 | 0.776079 |     2 |     5 |
| atb2 | 3.6     | 0.770132 |     3 |     5 |
| atb3 | 4.3     | 0.534983 |     3 |     5 |
| sn1  | 4.06667 | 0.691492 |     3 |     5 |
| sn2  | 3.63333 | 1.03335  |     1 |     5 |
| sn3  | 3       | 0.787839 |     1 |     4 |
| pbc1 | 2.86667 | 0.776079 |     2 |     4 |
| pbc2 | 3.76667 | 0.504007 |     3 |     5 |
| pbc3 | 4.2     | 0.550861 |     3 |     5 |
| pbc4 | 3.9     | 0.661764 |     3 |     5 |
| bi1  | 3.6     | 0.770132 |     2 |     5 |
| bi2  | 4.3     | 0.702213 |     3 |     5 |
| bi3  | 3.2     | 0.805156 |     2 |     5 |
| pb1  | 1.3     | 0.651259 |     1 |     4 |
| pb2  | 1.56667 | 0.8172   |     1 |     4 |
| pb3  | 4.53333 | 0.571346 |     3 |     5 |

## 2. Latent Variable Mapping (Construct Definitions)
| Latent Variable | Mapped Indicators | Descriptive Scope |
| :--- | :--- | :--- |
| **ER** | er1 | Every member of the public should accept... |
| **EC** | ec1, ec3, ec4 | Human interferences with nature often pr..., Human beings are severely abusing the en..., I am worried about the environment.... |
| **SEK** | sek1, sek2, sek3 | I have the knowledge and skills to behav..., I know about several ways to participate..., I am aware of specific problems of my ci... |
| **ATB** | atb1, atb2, atb3 | Adoption of eco-friendly behavior is a g..., I think it is useful to behave pro-envir..., It is wise to conserve energy.... |
| **SN** | sn1, sn2, sn3 | Most people who are important to me thin..., Most people who are important to me want..., I feel social pressure to preserve the e... |
| **PBC** | pbc1 | I find it easy to be friendly with the e... |
| **BI** | bi1, bi2, bi3 | I will try to reduce my carbon footprint..., I intend to engage in behaviors to prote..., I plan to stop wasting natural resources... |
| **PB** | pb1 | I have participated in policy consultati... |

## 3. Professional Data Validation
* **Multivariate Normality (Kurtosis):** 650.6426 (p=0.0000)
* **Outlier Detection:** 0 multivariate outliers identified.

## 4. Full Parameter Listing (Refined Model)
| Left Val | Op | Right Val | Estimate | P-Value | Significance |
| :--- | :--- | :--- | :--- | :--- | :--- |
| BI | ~ | SN | 0.6710 | 0.0063 | Significant |
| er1 | ~ | ER | 1.0000 | Fixed | Baseline/Fixed |
| ec1 | ~ | EC | 1.0000 | Fixed | Baseline/Fixed |
| ec3 | ~ | EC | 0.8997 | 0.0001 | Significant |
| ec4 | ~ | EC | 0.8037 | 0.0092 | Significant |
| sek1 | ~ | SEK | 1.0000 | Fixed | Baseline/Fixed |
| sek2 | ~ | SEK | 0.9732 | 0.0000 | Significant |
| sek3 | ~ | SEK | 0.5517 | 0.0190 | Significant |
| atb1 | ~ | ATB | 1.0000 | Fixed | Baseline/Fixed |
| atb2 | ~ | ATB | 1.4621 | 0.0069 | Significant |
| atb3 | ~ | ATB | 1.3753 | 0.0039 | Significant |
| sn1 | ~ | SN | 1.0000 | Fixed | Baseline/Fixed |
| sn2 | ~ | SN | 1.9666 | 0.0000 | Significant |
| sn3 | ~ | SN | 0.8898 | 0.0006 | Significant |
| pbc1 | ~ | PBC | 1.0000 | Fixed | Baseline/Fixed |
| bi1 | ~ | BI | 1.0000 | Fixed | Baseline/Fixed |
| bi2 | ~ | BI | 0.9535 | 0.0048 | Significant |
| bi3 | ~ | BI | 1.1115 | 0.0044 | Significant |
| pb1 | ~ | PB | 1.0000 | Fixed | Baseline/Fixed |
| ATB | ~~ | ATB | 0.1419 | 0.1586 | Baseline/Fixed |
| ATB | ~~ | PB | 0.0794 | 0.1432 | Baseline/Fixed |
| BI | ~~ | BI | 0.1255 | 0.1210 | Baseline/Fixed |
| EC | ~~ | EC | 0.2420 | 0.0281 | Significant |
| EC | ~~ | ATB | 0.0118 | 0.7506 | Baseline/Fixed |
| EC | ~~ | ER | 0.0236 | 0.6051 | Baseline/Fixed |
| EC | ~~ | PB | -0.0566 | 0.3718 | Baseline/Fixed |
| EC | ~~ | PBC | 0.0474 | 0.5239 | Baseline/Fixed |
| EC | ~~ | SEK | 0.0327 | 0.6577 | Baseline/Fixed |
| EC | ~~ | SN | 0.1234 | 0.0518 | Baseline/Fixed |
| ER | ~~ | ER | 0.1042 | 0.0003 | Significant |
| ER | ~~ | ATB | 0.0488 | 0.1986 | Baseline/Fixed |
| ER | ~~ | PB | -0.0333 | 0.5476 | Baseline/Fixed |
| ER | ~~ | PBC | 0.1222 | 0.0780 | Baseline/Fixed |
| ER | ~~ | SEK | 0.0399 | 0.5459 | Baseline/Fixed |
| ER | ~~ | SN | 0.0227 | 0.6118 | Baseline/Fixed |
| PB | ~~ | PB | 0.1659 | 0.0017 | Significant |
| PBC | ~~ | PBC | 0.1913 | 0.0109 | Significant |
| PBC | ~~ | ATB | 0.0299 | 0.5834 | Baseline/Fixed |
| PBC | ~~ | PB | -0.0934 | 0.3039 | Baseline/Fixed |
| SEK | ~~ | SEK | 0.4755 | 0.0128 | Significant |
| SEK | ~~ | ATB | 0.1609 | 0.0558 | Baseline/Fixed |
| SEK | ~~ | PB | 0.1873 | 0.0559 | Baseline/Fixed |
| SEK | ~~ | PBC | -0.0604 | 0.5722 | Baseline/Fixed |
| SEK | ~~ | SN | 0.0966 | 0.2077 | Baseline/Fixed |
| SN | ~~ | SN | 0.2665 | 0.0152 | Significant |
| SN | ~~ | ATB | 0.1043 | 0.0674 | Baseline/Fixed |
| SN | ~~ | PB | 0.0219 | 0.7182 | Baseline/Fixed |
| SN | ~~ | PBC | 0.1955 | 0.0247 | Significant |
| atb1 | ~~ | atb1 | 0.4405 | 0.0001 | Significant |
| atb2 | ~~ | atb2 | 0.2701 | 0.0006 | Significant |
| atb3 | ~~ | atb3 | 0.0084 | 0.7942 | Baseline/Fixed |
| bi1 | ~~ | bi1 | 0.3278 | 0.0026 | Significant |
| bi2 | ~~ | bi2 | 0.2534 | 0.0043 | Significant |
| bi3 | ~~ | bi3 | 0.3233 | 0.0053 | Significant |
| ec1 | ~~ | ec1 | 0.1902 | 0.0047 | Significant |
| ec3 | ~~ | ec3 | 0.0363 | 0.3301 | Baseline/Fixed |
| ec4 | ~~ | ec4 | 0.4759 | 0.0002 | Significant |
| er1 | ~~ | er1 | 0.1180 | 0.0000 | Significant |
| pb1 | ~~ | pb1 | 0.2442 | 0.0000 | Significant |
| pbc1 | ~~ | pbc1 | 0.3909 | 0.0000 | Significant |
| sek1 | ~~ | sek1 | 0.2134 | 0.0409 | Significant |
| sek2 | ~~ | sek2 | 0.2163 | 0.0322 | Significant |
| sek3 | ~~ | sek3 | 0.5619 | 0.0002 | Significant |
| sn1 | ~~ | sn1 | 0.1956 | 0.0003 | Significant |
| sn2 | ~~ | sn2 | 0.0013 | 0.9861 | Baseline/Fixed |
| sn3 | ~~ | sn3 | 0.3890 | 0.0001 | Significant |

## 5. Residual Correlation Matrix (Model Strain)
Values > 0.1 identify variables where the model is 'straining' to fit the raw data.

|      |       atb1 |        atb2 |        atb3 |          bi1 |        bi2 |        bi3 |          ec1 |         ec3 |         ec4 |         er1 |
|:-----|-----------:|------------:|------------:|-------------:|-----------:|-----------:|-------------:|------------:|------------:|------------:|
| atb1 |  0.0331304 | -0.0816319  |  0.0118156  |  0.436809    |  0.37113   |  0.438429  |  0.145636    |  0.322665   |  0.596597   |  0.11607    |
| atb2 | -0.0816319 |  0.0332608  |  0.0274351  |  0.246138    |  0.176715  | -0.0499004 | -0.140581    |  0.178198   |  0.398555   | -0.00631773 |
| atb3 |  0.0118156 |  0.0274351  |  0.0331766  |  0.151464    |  0.15048   | -0.07217   | -0.266989    |  0.0364713  |  0.232922   |  0.00741116 |
| bi1  |  0.436809  |  0.246138   |  0.151464   |  0.0333543   | -0.0120532 |  0.0826298 | -7.54001e-05 |  0.0219001  |  0.646132   |  0.332211   |
| bi2  |  0.37113   |  0.176715   |  0.15048    | -0.0120532   |  0.033359  | -0.0211214 | -0.116731    |  0.164323   |  0.210091   |  0.36645    |
| bi3  |  0.438429  | -0.0499004  | -0.07217    |  0.0826298   | -0.0211214 |  0.0333598 |  0.200537    |  0.296981   |  0.373614   |  0.224027   |
| ec1  |  0.145636  | -0.140581   | -0.266989   | -7.54001e-05 | -0.116731  |  0.200537  |  0.0333135   |  0.0335759  | -0.0174532  | -0.0378824  |
| ec3  |  0.322665  |  0.178198   |  0.0364713  |  0.0219001   |  0.164323  |  0.296981  |  0.0335759   |  0.0333607  | -0.00358912 |  0.00732015 |
| ec4  |  0.596597  |  0.398555   |  0.232922   |  0.646132    |  0.210091  |  0.373614  | -0.0174532   | -0.00358912 |  0.0333085  |  0.0695769  |
| er1  |  0.11607   | -0.00631773 |  0.00741116 |  0.332211    |  0.36645   |  0.224027  | -0.0378824   |  0.00732015 |  0.0695769  |  0.0333905  |

## 6. Modification Indices (Suggested Improvements)
Modification Indices estimate the gain in model fit if specific paths were added.

### Mathematical Constraint Note
Modification Indices (MI) were not calculable due to a non-positive definite Fisher Information Matrix. This is expected in small sample sizes (N=30) where the parameter-to-observation ratio is high. Please refer to Section 5 (Residual Matrix) to identify potential paths for model expansion manually.

## 7. Model Fit Overview
| Metric | Result | Benchmark |
| :--- | :--- | :--- |
| **CFI** (Comp. Fit) | 0.5929 | > 0.90 |
| **TLI** (Tucker-Lewis) | 0.4488 | > 0.90 |
| **RMSEA** (Error) | 0.1888 | < 0.08 |
| **SRMR** (Residuals) | 0.0000 | < 0.08 |
