from fastapi import FastAPI, Query
from pydantic import BaseModel

# Import ModelLoader (same folder, so just .model_loader)
from src.model_loader import ModelLoader

app = FastAPI()
loader = ModelLoader()  # Initialize once, reuse for all requests

# Data Model
class CustomerData(BaseModel):
    age: int = 25
    income: int = 30000
    tenure_years: int = 2
    num_purchases: int = 1
    website_visits: int = 5
    days_since_last_purchase: int = 10
    satisfaction_score: int = 3
    has_credit_card: int = 0
    is_newsletter_subscribed: int = 0

@app.get('/')
async def api_root():
    return {"message": "ML Prediction API"}

@app.post("/predict/")
async def predict(data: CustomerData):
    """POST predict with JSON body"""
    return loader.predict(data.dict())

@app.get("/predict/")
async def predict_get(
    age: int = 25,
    income: int = 30000,
    tenure_years: int = 2,
    num_purchases: int = 1,
    website_visits: int = 5,
    days_since_last_purchase: int = 10,
    satisfaction_score: int = 3,
    has_credit_card: int = 0,
    is_newsletter_subscribed: int = 0
):
    """GET predict with query parameters"""
    data = {
        "age": age, "income": income, "tenure_years": tenure_years,
        "num_purchases": num_purchases, "website_visits": website_visits,
        "days_since_last_purchase": days_since_last_purchase,
        "satisfaction_score": satisfaction_score,
        "has_credit_card": has_credit_card,
        "is_newsletter_subscribed": is_newsletter_subscribed
    }
    
    return loader.predict(data)

#health endpoint
@app.get("/health")
def health_check():
    # Returns a simple JSON response — {"status": "ok"}
    # The CronJob will call this to confirm the API is alive
    return {"status": "ok", "model": "loaded"}


# Run with: uvicorn src.api:app --host 0.0.0.0 --port 8000

# from src.model_loader import ModelLoader
# from fastapi import FastAPI, Query
# from pydantic import BaseModel

# app = FastAPI()

# # Data Model
# class CustomerData(BaseModel):
#     age: int = 25
#     income: int = 30000
#     tenure_years: int = 2
#     num_purchases: int = 1
#     website_visits: int = 5
#     days_since_last_purchase: int = 10
#     satisfaction_score: int = 3
#     has_credit_card: int = 0
#     is_newsletter_subscribed: int = 0

# @app.get('/')
# async def api_root():
#     return {"message": "ML Prediction API"}

# @app.post("/predict/")
# async def predict(
#     data: CustomerData,
#     run_id: str = Query(None, description="MLflow run ID (optional, uses latest if not provided)")
# ):
#     loader = ModelLoader()  
#     return loader.predict(data.dict())

# @app.get("/predict/")
# async def predict_get(
#     age: int = 25,
#     income: int = 30000,
#     tenure_years: int = 2,
#     num_purchases: int = 1,
#     website_visits: int = 5,
#     days_since_last_purchase: int = 10,
#     satisfaction_score: int = 3,
#     has_credit_card: int = 0,
#     is_newsletter_subscribed: int = 0,
#     run_id: str = Query(None, description="MLflow run ID (optional)")
# ):
#     data = {
#         "age": age, "income": income, "tenure_years": tenure_years,
#         "num_purchases": num_purchases, "website_visits": website_visits,
#         "days_since_last_purchase": days_since_last_purchase,
#         "satisfaction_score": satisfaction_score,
#         "has_credit_card": has_credit_card,
#         "is_newsletter_subscribed": is_newsletter_subscribed
#     }
    
#     loader = ModelLoader()  
#     return loader.predict(data)

# # uvicorn src.api:app --host 0.0.0.0 --port 8000