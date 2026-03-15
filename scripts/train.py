import pandas as pd
import os
from mlxtend.frequent_patterns import apriori, association_rules
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

    df = pd.read_csv(DATA_PATH)
    
    # Clean the dataset
    df.dropna(subset=[df.columns[1]], inplace=True) # Drop missing Itemnames
    df[df.columns[1]] = df[df.columns[1]].astype(str).str.strip() # Strip whitespaces
    
    # Due to dataset size, let's filter for a specific subset to avoid MemoryError (e.g., Country='France')
    if 'Country' in df.columns:
        df = df[df['Country'] == 'France']
    else:
        # If no Country column, just sample to top 2000 transactions to save memory
        top_txns = df[df.columns[0]].drop_duplicates().head(2000)
        df = df[df[df.columns[0]].isin(top_txns)]

    transaction_col = df.columns[0]
    item_col = df.columns[1]

    print("Creating basket matrix...")
    # Create basket matrix
    basket = (df.groupby([transaction_col, item_col])[item_col]
              .count().unstack().reset_index().fillna(0)
              .set_index(transaction_col))
    
    # Convert quantities to 1/0
    basket_sets = basket.map(lambda x: 1 if x > 0 else 0)
    
    print(f"Matrix shape: {basket_sets.shape}")
    print("Generating frequent itemsets...")
    # Lower support for the real dataset
    frequent_itemsets = apriori(basket_sets, min_support=0.05, use_colnames=True)
    
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
