# After training, promote the model to production stage
import mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri("sqlite:///mlflow.db")
client = MlflowClient()

# Get latest version
model_name = "customer-churn-predictor"
latest_versions = client.get_latest_versions(model_name, stages=["None"])

if latest_versions:
    version = latest_versions[0].version

    # Promote to production
    client.transition_model_version_stage(
        name=model_name, version=version, stage="Production"
    )
    print(f"Model version {version} promoted to Production")
else:
    print("No model versions found")
