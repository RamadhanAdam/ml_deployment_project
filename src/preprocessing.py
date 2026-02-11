import pandas as pd
import os

class Preprocessor:
    def __init__(self):
        self.features = [
            'age', 'income', 'tenure_years', 'num_purchases',
            'website_visits', 'days_since_last_purchase', 'satisfaction_score',
            'has_credit_card', 'is_newsletter_subscribed'
        ]
        self.target = 'will_buy'
    
    def load_data(self, path='./data/data.csv'):
        return pd.read_csv(path)
    
    def split_xy(self, df):
        X = df[self.features]
        y = df[self.target] if self.target in df.columns else None
        return X, y