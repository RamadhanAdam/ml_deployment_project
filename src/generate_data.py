import pandas as pd
import numpy as np
import os

np.random.seed(42)
os.makedirs("./data", exist_ok=True)

n = 1_000_000

df = pd.DataFrame(
    {
        "age": np.random.randint(18, 80, n),
        "income": np.random.randint(20000, 200000, n),
        "tenure_years": np.random.randint(0, 20, n),
        "num_purchases": np.random.poisson(3, n),
        "website_visits": np.random.poisson(10, n),
        "days_since_last_purchase": np.random.exponential(30, n).astype(int),
        "has_credit_card": np.random.randint(0, 2, n),
        "satisfaction_score": np.random.randint(1, 6, n),
        "is_newsletter_subscribed": np.random.randint(0, 2, n),
    }
)

prob = 1 / (
    1
    + np.exp(
        -(
            0.02 * (df["age"] - 40)
            + 0.00001 * (df["income"] - 50000)
            + 0.1 * df["tenure_years"]
            + 0.05 * df["num_purchases"]
            + 0.01 * df["website_visits"]
            - 0.01 * df["days_since_last_purchase"]
            + 0.3 * df["has_credit_card"]
            + 0.1 * (df["satisfaction_score"] - 3)
            + 0.2 * df["is_newsletter_subscribed"]
        )
    )
)

df["will_buy"] = (np.random.random(n) < prob).astype(int)

df.to_csv("./data/data.csv", index=False)
print(f"Generated {n} rows in ./data/data.csv")
