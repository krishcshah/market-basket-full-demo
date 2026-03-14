# Market Basket Analysis Demo

This project demonstrates Market Basket Analysis using the Apriori algorithm.

## Structure
- `/data`: Contains the dataset (place the Kaggle dataset here).
- `/scripts`: Data preprocessing and training scripts.
- `/models`: Saved association rules and itemsets.
- `/backend`: FastAPI application serving recommendations.
- `/frontend`: Next.js/React frontend (setup required).
- `/notebooks`: Educational Jupyter notebook for exploration.

## How to run

1. Install backend requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the training script to generate rules:
   ```bash
   python scripts/train.py
   ```
3. Start the FastAPI backend:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```
4. Set up the frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
