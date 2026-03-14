import pandas as pd
import os
from mlxtend.frequent_patterns import apriori, association_rules

DATA_PATH = "data/dataset.csv"
MODELS_DIR = "models"

def create_dummy_data():
    """Create a dummy dataset if the Kaggle dataset is not present."""
    os.makedirs("data", exist_ok=True)
    data = {
        'Transaction': [1, 1, 1, 2, 2, 3, 3, 3, 4, 4, 5, 5, 5],
        'Item': ['Milk', 'Bread', 'Butter', 'Bread', 'Butter', 'Milk', 'Bread', 'Cheese', 'Milk', 'Cheese', 'Milk', 'Bread', 'Butter']
    }
    df = pd.DataFrame(data)
    df.to_csv(DATA_PATH, index=False)
    print("Created dummy dataset.")

def main():
    if not os.path.exists(DATA_PATH):
        create_dummy_data()

    df = pd.read_csv(DATA_PATH)
    
    # Create basket matrix
    basket = (df.groupby(['Transaction', 'Item'])['Item']
              .count().unstack().reset_index().fillna(0)
              .set_index('Transaction'))
    
    # Convert quantities to 1/0
    basket_sets = basket.applymap(lambda x: 1 if x > 0 else 0)
    
    print("Generating frequent itemsets...")
    frequent_itemsets = apriori(basket_sets, min_support=0.2, use_colnames=True)
    
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
