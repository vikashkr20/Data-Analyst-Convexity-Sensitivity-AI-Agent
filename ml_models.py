import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from xgboost import XGBRegressor
import mlflow
import mlflow.sklearn
import mlflow.xgboost
import joblib

def load_data():
    try:
        df = pd.read_csv("bond_portfolio_krd.csv")
    except FileNotFoundError:
        df = pd.read_csv("bond_portfolio_recalc.csv")
    return df

def train_and_evaluate():
    df = load_data()
    
    # Define features and target
    feature_cols = ['CouponRate', 'YearsToMaturity', 'YieldToMaturity', 'ModifiedDuration', 'Convexity']
    target_col = 'CleanPrice'
    
    X = df[feature_cols].copy()
    y = df[target_col].copy()
    
    # Split 80/20 train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Save the scaler
    joblib.dump(scaler, "scaler.joblib")
    print("Scaler saved to scaler.joblib")
    
    # Set explicit SQLite tracking database to avoid file tracking maintenance mode
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("MatRisk_Bond_Pricing_ML")
    
    models = {
        "Random_Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "XGBoost": XGBRegressor(n_estimators=200, max_depth=4, learning_rate=0.1, random_state=42),
        "Neural_Network": MLPRegressor(hidden_layer_sizes=(128, 64, 32), max_iter=1000, random_state=42)
    }
    
    results = []
    
    print("=" * 60)
    print("DAY 8: TRAINING MACHINE LEARNING MODELS")
    print("=" * 60)
    
    for name, model in models.items():
        print(f"Training {name}...")
        
        with mlflow.start_run(run_name=name):
            model.fit(X_train_scaled, y_train)
            
            # Predict
            y_pred = model.predict(X_test_scaled)
            
            # Evaluate
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            print(f"  {name:15s} | RMSE: {rmse:.4f} | MAE: {mae:.4f} | R²: {r2:.4f}")
            
            # Log metrics to MLflow
            mlflow.log_params(model.get_params() if hasattr(model, 'get_params') else {})
            mlflow.log_metric("RMSE", rmse)
            mlflow.log_metric("MAE", mae)
            mlflow.log_metric("R2", r2)
            
            # Save model file locally
            model_filename = f"{name.lower()}_model.joblib"
            joblib.dump(model, model_filename)
            
            # Log as a generic file artifact to avoid skops/torch loading crash
            mlflow.log_artifact(model_filename)
                
            results.append({
                "Model": name,
                "RMSE": rmse,
                "MAE": mae,
                "R2": r2
            })
            
    results_df = pd.DataFrame(results)
    print("\nModel Comparison Table:")
    print(results_df.to_string(index=False))
    results_df.to_csv("ml_model_comparison.csv", index=False)
    
    # Save the split dataset for SHAP explainability
    train_data = pd.DataFrame(X_train_scaled, columns=feature_cols)
    train_data['CleanPrice'] = y_train.values
    train_data.to_csv("train_scaled.csv", index=False)
    
    test_data = pd.DataFrame(X_test_scaled, columns=feature_cols)
    test_data['CleanPrice'] = y_test.values
    test_data.to_csv("test_scaled.csv", index=False)
    
    # Plot Feature Importance
    sns.set_theme(style="darkgrid")
    
    rf_model = models["Random_Forest"]
    xgb_model = models["XGBoost"]
    
    rf_importances = rf_model.feature_importances_
    xgb_importances = xgb_model.feature_importances_
    
    importance_df = pd.DataFrame({
        'Feature': feature_cols,
        'Random_Forest': rf_importances,
        'XGBoost': xgb_importances
    })
    
    importance_melted = pd.melt(importance_df, id_vars='Feature', var_name='Model', value_name='Importance')
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=importance_melted, x='Feature', y='Importance', hue='Model', palette='viridis')
    plt.title("Feature Importance: Random Forest vs. XGBoost", fontsize=14, fontweight='bold')
    plt.ylabel("Relative Importance")
    plt.tight_layout()
    plt.savefig("ml_feature_importance.png", dpi=300)
    plt.close()
    print("\nFeature importance plot saved to: ml_feature_importance.png")
    print("=" * 60)

if __name__ == "__main__":
    train_and_evaluate()
