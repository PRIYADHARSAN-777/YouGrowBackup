import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import joblib

# Configuration Settings
CONFIG = {
    'random_state': 42,
    'test_size': 0.2,
    'model_save_path': 'trained_model.pkl'
}

class AIAgent:
    def __init__(self):
        self.model = RandomForestClassifier(random_state=CONFIG['random_state'])
        self.scaler = StandardScaler()

    def load_data(self, file_path):
        # Load dataset
        data = pd.read_csv(file_path)
        return data

    def preprocess_data(self, data):
        # Basic preprocessing steps
        X = data.drop('target', axis=1)
        y = data['target']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=CONFIG['test_size'], random_state=CONFIG['random_state'])
        X_train = self.scaler.fit_transform(X_train)
        X_test = self.scaler.transform(X_test)
        return X_train, X_test, y_train, y_test

    def train(self, X_train, y_train):
        # Training the model
        self.model.fit(X_train, y_train)

    def predict(self, X_test):
        # Making predictions
        return self.model.predict(X_test)

    def evaluate(self, y_test, y_pred):
        # Evaluating model performance
        print('Accuracy:', accuracy_score(y_test, y_pred))
        print('Confusion Matrix:\n', confusion_matrix(y_test, y_pred))
        print('Classification Report:\n', classification_report(y_test, y_pred))

    def save_model(self):
        # Save trained model
        joblib.dump(self.model, CONFIG['model_save_path'])
        print('Model saved at', CONFIG['model_save_path'])

# Usage
# agent = AIAgent()
# data = agent.load_data('data.csv')
# X_train, X_test, y_train, y_test = agent.preprocess_data(data)
# agent.train(X_train, y_train)
# y_pred = agent.predict(X_test)
# agent.evaluate(y_test, y_pred)
# agent.save_model()