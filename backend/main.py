from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Market Basket Analysis API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
RULES_FILE = os.path.join(MODELS_DIR, "association_rules.csv")

rules_df = None

import numpy as np

@app.on_event("startup")
def load_models():
    global rules_df
    if os.path.exists(RULES_FILE):
        rules_df = pd.read_csv(RULES_FILE)
        # Handle inf values for JSON compliance
        rules_df.replace([np.inf, -np.inf], None, inplace=True)
        # Also drop NaNs which become nulls in JSON correctly via pandas fillna, but None works better
        rules_df.fillna("Infinity", inplace=True)
    else:
        print("Warning: Rules file not found. Run scripts/train.py first.")

class RecommendRequest(BaseModel):
    items: list[str]

@app.get("/rules")
def get_rules(limit: int = 10):
    if rules_df is None:
        return {"error": "Rules not loaded"}
    
    top_rules = rules_df.sort_values('lift', ascending=False).head(limit)
    return top_rules.to_dict(orient="records")

@app.get("/top-products")
def get_top_products():
    if rules_df is None:
        return {"error": "Rules not loaded"}
    
    # Extract unique items from antecedents/consequents
    all_items = set()
    for items in rules_df['antecedents']:
        all_items.update(items.split(','))
    return {"top_products": list(all_items)}

@app.post("/recommend")
def recommend_products(req: RecommendRequest):
    if rules_df is None:
        return {"error": "Rules not loaded"}
    
    # Store everything uppercase to match training dataset standardization
    user_items = {item.strip().upper() for item in req.items}
    recommendations = []
    
    for _, row in rules_df.iterrows():
        antecedents = set(row['antecedents'].split(','))
        consequents = row['consequents'].split(',')
        
        # If user has the antecedent items, recommend the consequents
        if antecedents.issubset(user_items):
            for item in consequents:
                if item not in user_items:
                    recommendations.append({
                        "item": item,
                        "confidence": row['confidence'],
                        "lift": row['lift']
                    })
    
    # Sort by lift
    recommendations = sorted(recommendations, key=lambda x: x['lift'], reverse=True)
    
    # Deduplicate keeping highest lift
    seen = set()
    unique_recs = []
    for rec in recommendations:
        if rec['item'] not in seen:
            seen.add(rec['item'])
            unique_recs.append(rec)
            
    return {"recommendations": unique_recs[:5]}
