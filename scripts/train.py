import pandas as pd
import os
from mlxtend.frequent_patterns import fpgrowth, association_rules
import kagglehub

DATA_PATH = "data/dataset.csv"
MODELS_DIR = "models"

def get_kaggle_data():
    """Download the Kaggle dataset if not already present."""
    os.makedirs("data", exist_ok=True)
    print("Downloading dataset using kagglehub...")
    path = kagglehub.dataset_download("aslanahmedov/market-basket-analysis")
    
    # Usually datasets contain a single CSV or we can find it
    for file in os.listdir(path):
        if file.endswith('.csv'):
            df = pd.read_csv(os.path.join(path, file), sep=';')
            df.to_csv(DATA_PATH, index=False)
            print("Kaggle dataset saved to data/dataset.csv")
            return

def main():
    if not os.path.exists(DATA_PATH):
        get_kaggle_data()

    df = pd.read_csv(DATA_PATH, low_memory=False)
    
    print("Cleaning the full dataset...")
    # Clean the dataset
    df.dropna(subset=[df.columns[0], df.columns[1]], inplace=True) # Drop missing Invoice/Itemnames
    df[df.columns[1]] = df[df.columns[1]].astype(str).str.strip().str.upper() # Strip and uppercase items for consistency
    
    # Filter out canceled transactions (which often start with 'C') and postage
    df = df[~df[df.columns[0]].astype(str).str.startswith('C')]
    df = df[df[df.columns[1]] != 'POSTAGE']
    
    transaction_col = df.columns[0]
    item_col = df.columns[1]

    print("Creating sparse basket matrix for the ENTIRE dataset...")
    # Group by transaction and item, unstacking to a matrix. 
    # Use boolean to save huge amounts of memory.
    basket = (df.groupby([transaction_col, item_col])[item_col]
              .count().unstack().fillna(0))
    
    # Convert to strict boolean to save memory and optimize FP-Growth
    basket_sets = basket.astype(bool)
    
    print(f"Matrix shape: {basket_sets.shape}")
    print("Generating frequent itemsets using FP-Growth (Ultra Fast)...")
    # FP-growth is highly scalable so we can use lower support on the entire dataset
    frequent_itemsets = fpgrowth(basket_sets, min_support=0.015, use_colnames=True)
    
    print("Generating association rules...")
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.0)
    
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    # Convert frozensets to strings for saving
    frequent_itemsets['itemsets'] = frequent_itemsets['itemsets'].apply(lambda x: ','.join(list(x)))
    rules['antecedents'] = rules['antecedents'].apply(lambda x: ','.join(list(x)))
    rules['consequents'] = rules['consequents'].apply(lambda x: ','.join(list(x)))
    
    frequent_itemsets.to_csv(os.path.join(MODELS_DIR, "frequent_itemsets.csv"), index=False)
    rules.to_csv(os.path.join(MODELS_DIR, "association_rules.csv"), index=False)
    print("Models saved successfully in /models")

if __name__ == "__main__":
    main()
