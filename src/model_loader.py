import warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*protected namespace.*")
import os
# import mlflow
import joblib
import pandas as pd

class ModelLoader:
    def __init__(self, model_name = "customer-churn-predictor", stage = "Production") :
        print("Loading model from file...")
        self.model = joblib.load(os.getenv("MODEL_PATH", "/app/models/model.pkl"))
        # os.getenv reads the env variable, the second argument is a fallback default
        print("Model loaded successfully!")
        

        # # Connecting to MLflow database
        # mlflow.set_tracking_uri("sqlite:///mlflow.db")

        # print(f"Loading model : {model_name}, stage : {stage}")

        # # Loading from Model Registry instead of run_id
        # try:
        #     model_uri = f"models:/{model_name}/{stage}"
        #     self.model = mlflow.sklearn.load_model(model_uri)
        #     print(f"Loaded model from registry : {model_uri}")

        # except Exception as e:
        #     # Fallback : load latest version if no production model
        #     print(f"No {stage} model found, loading latest version...")
        #     model_uri = f"models/{model_name}/latest"
        #     self.model = mlflow.sklearn.load_model(model_uri=model_uri)
        #     print(f"Loaded latest model : {model_uri}")
        # Features
        self.features = [
            'age', 'income', 'tenure_years', 'num_purchases',
            'website_visits', 'days_since_last_purchase', 'satisfaction_score',
            'has_credit_card', 'is_newsletter_subscribed'
        ]
    
    def predict(self, data: dict):
        row = {f: [data.get(f, 0)] for f in self.features}
        df = pd.DataFrame(row)
        
        try:
            prob = self.model.predict_proba(df)[0][1]
            return {"will_buy_probability": round(float(prob), 3)}
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}"}