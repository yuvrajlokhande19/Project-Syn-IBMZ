import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

def train_model():
    print("Loading dataset...")
    data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'artifacts', 'synthetic_hospital_data_10k.csv')
    df = pd.read_csv(data_path)

    print("Preparing data...")
    features = ['grid_voltage', 'flood_index', 'route_congestion']
    X = df[features]
    y = df['is_anomaly']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training RandomForestClassifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    print("Evaluating model...")
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))

    model_path = os.path.join(os.path.dirname(__file__), '..', 'artifacts', 'anomaly_model.pkl')
    print(f"Exporting model to {model_path}...")
    joblib.dump(model, model_path)
    print("Model training and export complete.")

if __name__ == "__main__":
    train_model()
