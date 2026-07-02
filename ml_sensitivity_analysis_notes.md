# Machine Learning Sensitivity Analysis Report

## Overview
This document summarizes the sensitivity analysis comparing the classical second-order analytical model (Modified Duration + Convexity) against three Machine Learning models (Random Forest, XGBoost, Multi-Layer Perceptron Neural Network) and a simple average Ensemble.

## Findings
1. **Model Performance**:
   - The **Neural Network** shows the highest accuracy in predicting bond pricing under interest rate shocks.
   - For yield shifts within $\pm 50$ basis points, all models (analytical and ML) align closely, showing that the second-order duration-convexity approximation is highly accurate for small shocks.
   
2. **Divergence at Extreme Shocks**:
   - Beyond $\pm 100$ basis points, the **Random Forest** and **XGBoost** models begin to show pricing plateaus. This is a typical limitation of decision-tree based models, which cannot extrapolate beyond the range of training data.
   - The **Neural Network** and the **Analytical Model** remain smooth and continue to model the quadratic curvature (convexity) effectively.
   - At extreme yield drops ($-150$ to $-200$ bps), tree-based models significantly underestimate portfolio price gains, whereas the Neural Network captures the non-linear pricing effects and matches the analytical curve.

3. **Ensemble Performance**:
   - The Ensemble average is dragged down by the tree-based models at extreme yield changes, making the individual Neural Network model the superior choice for pricing extreme shocks.
