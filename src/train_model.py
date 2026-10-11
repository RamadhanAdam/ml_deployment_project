import warnings

warnings.filterwarnings(
    "ignore", category=UserWarning, message=".*protected namespace.*"
)

from src.preprocessing import Preprocessor
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import mlflow
import mlflow.sklearn

# Setting up MLflow
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("container-project")

mlflow.autolog(
    log_input_examples=True,  # Helps with model serving later
    log_model_signatures=True,  # Documents expected input/output
    silent=True,  # Supress autolog warnings
    log_datasets=True,
    extra_tags={"project": "customer-prediction", "environment": "production"},
)

with mlflow.start_run():
    # Loading and preparing data
    prep = Preprocessor()
    df = prep.load_data()
    X, y = prep.split_xy(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Training model (autolog captures params and model automatically)
    model = RandomForestClassifier(n_estimators=50, n_jobs=1, random_state=42)
    model.fit(X_train, y_train)

    # Log test accuracy (autolog only logs training score)
    test_accuracy = model.score(X_test, y_test)
    mlflow.log_metric("test_accuracy", test_accuracy)

    print(f"Test accuracy: {test_accuracy:.3f}")

    # Registering the model in Model Registry
    model_uri = f"runs:/{mlflow.active_run().info.run_id}/model"
    mlflow.register_model(
        model_uri=model_uri, name="customer-churn-predictor"  # registry name
    )
    print(f"Model registered as 'customer-churn-predictor'")
