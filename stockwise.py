# stock_price_predictor_advanced.py

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, r2_score

import warnings
warnings.filterwarnings('ignore')

# Create output directory
os.makedirs('outputs', exist_ok=True)

# 1. Load and Clean Data
def load_data(path='Data/RELIANCE.csv'):
    df = pd.read_csv(path)
    df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values('Date', inplace=True)
    df.dropna(inplace=True)
    return df

# 2. Preprocess: Create multi-day targets
def preprocess(df):
    df = df.copy()
    df['Target'] = df['Close'].shift(-1)
    df['Future_Close_3'] = df['Close'].shift(-3).rolling(3).mean()
    df['Future_Close_5'] = df['Close'].shift(-5).rolling(5).mean()
    df.dropna(inplace=True)

    features = ['Open', 'High', 'Low', 'Close', 'Volume']
    X = df[features]
    y = df['Target']
    future_y_3 = df['Future_Close_3']
    future_y_5 = df['Future_Close_5']

    return X, y, future_y_3, future_y_5, df['Date']

# 3. Train Model
def train_model(X, y):
    tscv = TimeSeriesSplit(n_splits=5)
    model = LinearRegression()

    scores = []
    for train_index, test_index in tscv.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        model.fit(X_train, y_train)
        scores.append(model.score(X_test, y_test))

    print("Average R² Score (TimeSeries CV):", np.mean(scores))
    model.fit(X, y)  # Train on full
    return model

# 4. Evaluate and Visualize
def evaluate_model(model, X, y, dates):
    y_pred = model.predict(X)

    mse = mean_squared_error(y, y_pred)
    r2 = r2_score(y, y_pred)

    print(f"MSE: {mse:.2f}")
    print(f"R² Score: {r2:.4f}")

    results_df = pd.DataFrame({
        'Date': dates,
        'Actual': y,
        'Predicted': y_pred
    })

    results_df.to_csv('outputs/predictions.csv', index=False)

    plt.figure(figsize=(14, 6))
    plt.plot(results_df['Date'], results_df['Actual'], label='Actual')
    plt.plot(results_df['Date'], results_df['Predicted'], label='Predicted', linestyle='--')
    plt.title('Stock Price Prediction vs Actual')
    plt.xlabel('Date')
    plt.ylabel('Close Price')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('outputs/full_predictions_plot.png')
    plt.close()

# 5. Save Model
def save_model(model):
    joblib.dump(model, 'outputs/stock_model.pkl')
    print("Model saved to outputs/stock_model.pkl")

# Main
if __name__ == '__main__':
    df = load_data()
    X, y, y3, y5, dates = preprocess(df)

    model = train_model(X, y)
    evaluate_model(model, X, y, dates)
    save_model(model)

    print("✅ All tasks completed. Outputs saved to /outputs/")
