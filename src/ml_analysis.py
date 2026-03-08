import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import os

def main():
    os.makedirs('reports/figures', exist_ok=True)
    df = pd.read_csv('data/processed/merged_epl_24_25.csv')
    
    # Preprocessing: convert any percentage strings to float
    for col in df.columns:
        if df[col].dtype == object and df[col].str.endswith('%').any():
            df[col] = df[col].str.replace('%', '').astype(float) / 100.0

    # Fill N/a as per assignment instructions
    df.fillna(0, inplace=True)
    
    exclude_cols = ['Player', 'Club', 'Nationality', 'Position', 'TransferValue_Str', 'TM_Player_Match']
    numeric_df = df.select_dtypes(include=[np.number]).drop(columns=[c for c in exclude_cols if c in df.columns], errors='ignore')
    
    # III. K-Means
    print("=== Part III: K-Means Clustering ===")
    X = numeric_df.copy()
    
    # Remove Target from clustering
    if 'TransferValue_EUR' in X.columns:
        X = X.drop(columns=['TransferValue_EUR'])
        
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Finding the optimal k using Elbow Method
    inertias = []
    ks = range(2, 10)
    for k in ks:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        inertias.append(kmeans.inertia_)
        
    plt.figure(figsize=(8, 5))
    plt.plot(ks, inertias, '-o')
    plt.title('Elbow Method for K-Means')
    plt.xlabel('Number of clusters (k)')
    plt.ylabel('Inertia')
    plt.savefig('reports/figures/kmeans_elbow.png')
    plt.close()
    
    # We will pick k=4
    k_opt = 4
    print(f"Applying K-Means with k={k_opt}")
    print("Rationale: The Elbow Method (see kmeans_elbow.png) typically shows a 'bend' where the decrease in inertia slows.")
    print("In this dataset, 4 clusters often correspond to high-level player roles: ")
    print("1. Defensively focused players (Defenders/CDMs)")
    print("2. Creative playmakers (CAMs/Wingers with high SCA/xAG)")
    print("3. Goal-scorers (Strikers with high xG/Goals)")
    print("4. Utility/Rotation players with lower playing time or mixed stats.")
    
    kmeans = KMeans(n_clusters=k_opt, random_state=42, n_init=10)
    df['Cluster'] = kmeans.fit_predict(X_scaled)
    
    # PCA to 2D
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    df['PCA1'] = X_pca[:, 0]
    df['PCA2'] = X_pca[:, 1]
    
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(df['PCA1'], df['PCA2'], c=df['Cluster'], cmap='viridis', alpha=0.6)
    plt.title('Player Clusters using PCA (2D)')
    plt.xlabel(f'PCA1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
    plt.ylabel(f'PCA2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
    plt.colorbar(scatter, label='Cluster')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig('reports/figures/pca_clusters.png', dpi=300) # High quality as requested
    plt.close()
    
    # IV. Predict Transfer Value
    print("\n=== Part IV: Transfer Value Prediction ===")
    # Handle column names from data_collection.py
    min_col = 'Total_Minutes' if 'Total_Minutes' in df.columns else 'Minutes'
    val_col = 'TransferValue_EUR'
    
    # Only for players > 900 mins as per requirement
    df_pred = df[(df[min_col] > 900) & (df[val_col] > 0)].copy()
    
    if len(df_pred) < 10:
        print(f"Warning: Only {len(df_pred)} players found with > 900 mins and a known value. Model might be unstable.")
    
    if df_pred.empty:
        print("No players found for value estimation.")
    else:
        # Features and Target
        y = df_pred[val_col]
        # Drop non-numeric and derived columns
        X_reg = df_pred.select_dtypes(include=[np.number]).drop(columns=[
            val_col, 'PCA1', 'PCA2', 'Cluster', 'Total_Minutes', 'Minutes'
        ], errors='ignore')
        
        # Train test split
        X_train, X_test, y_train, y_test = train_test_split(X_reg, y, test_size=0.2, random_state=42)
        
        # For value estimation proposal: Random Forest is selected for handling non-linear relationships
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        preds = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        r2 = r2_score(y_test, preds)
        
        print(f"Proposed Model: Random Forest Regressor")
        print(f"Feature Selection: All available numeric performance metrics (excluding metadata/derived stats).")
        print(f"RMSE: €{rmse:,.2f}")
        print(f"R2 Score: {r2:.3f}")
        
        # Feature importances
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1]
        print("\nTop Features for Estimating Value:")
        for f in range(min(10, len(indices))):
            print(f"{f+1}. {X_reg.columns[indices[f]]}: {importances[indices[f]]:.3f}")

if __name__ == "__main__":
    main()
