import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap
import joblib

def run_shap_analysis():
    print("=" * 60)
    print("DAY 8: SHAP EXPLAINABILITY ANALYSIS")
    print("=" * 60)
    
    # Load model and data
    model = joblib.load("random_forest_model.joblib")
    
    feature_cols = ['CouponRate', 'YearsToMaturity', 'YieldToMaturity', 'ModifiedDuration', 'Convexity']
    
    # Load test set
    test_df = pd.read_csv("test_scaled.csv")
    X_test = test_df[feature_cols]
    
    # Initialize TreeExplainer
    print("Calculating SHAP values...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)
    
    # Plot 1: Summary Plot
    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values, X_test, feature_names=feature_cols, show=False)
    plt.title("SHAP Summary Plot (Random Forest Model)", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig("shap_summary.png", dpi=300)
    plt.close()
    print("SHAP Summary Plot saved to: shap_summary.png")
    
    # Plot 2: Dependence Plot for YieldToMaturity
    plt.figure(figsize=(8, 6))
    # SHAP has its own dependence plot function, let's use it
    # We can pass matplotlib=True or show=False and save
    shap.dependence_plot("YieldToMaturity", shap_values, X_test, feature_names=feature_cols, show=False)
    plt.title("SHAP Dependence Plot: YieldToMaturity", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig("shap_dependence_yield.png", dpi=300)
    plt.close()
    print("SHAP Yield Dependence Plot saved to: shap_dependence_yield.png")
    
    # Plot 3: Dependence Plot for YearsToMaturity
    plt.figure(figsize=(8, 6))
    shap.dependence_plot("YearsToMaturity", shap_values, X_test, feature_names=feature_cols, show=False)
    plt.title("SHAP Dependence Plot: YearsToMaturity", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig("shap_dependence_maturity.png", dpi=300)
    plt.close()
    print("SHAP Maturity Dependence Plot saved to: shap_dependence_maturity.png")
    
    print("=" * 60)

if __name__ == "__main__":
    run_shap_analysis()
