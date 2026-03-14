# Market Basket Analysis Demo

This project is a full-stack machine learning web application that recommends products based on what is currently in a user's shopping cart. It uses association rule mining to find items that are frequently purchased together.

## How the Model Works

The recommendation engine is built on the Apriori algorithm using the mlxtend Python library. Market Basket Analysis looks at past transaction data to find patterns. It calculates three main metrics to determine product relationships:
* Support: How frequently an itemset appears in the dataset.
* Confidence: The likelihood that a user will buy item B if they already have item A.
* Lift: The strength of the association. A lift greater than 1 means the items are likely to be bought together.

The model processes transaction data, generates frequent itemsets, and extracts association rules. These rules are saved as CSV files and loaded into the backend API to serve real-time recommendations.

## Tech Stack

* Machine Learning: Python, pandas, scikit-learn, mlxtend
* Backend: FastAPI, uvicorn
* Frontend: Next.js, React, TailwindCSS

## Local Setup

To run this project on your local machine, you will need to start both the Python backend and the Next.js frontend.

### 1. Train the Model and Start the Backend

First, install the Python dependencies:
ash
pip install -r requirements.txt


Next, run the training script. If you do not have the complete Kaggle dataset in the data folder, the script will automatically generate a dummy dataset so you can test the application immediately.
ash
python scripts/train.py


Once the script finishes, it will save the generated rules into the models folder. Now you can start the backend server:
ash
cd backend
python -m uvicorn main:app --reload

The API will be available at http://127.0.0.1:8000.

### 2. Start the Frontend

Open a new terminal window and navigate to the frontend folder:
ash
cd frontend
npm install
npm run dev

The web interface will be available at http://localhost:3000.

## Deployment Guide

This project is structured so the backend can be hosted on Render and the frontend on Vercel.

### Deploying the Backend (Render)

1. Create a new Web Service on Render and connect your GitHub repository.
2. Set the Language to Python 3.
3. Leave the Root Directory blank.
4. Set the Build Command to: pip install -r requirements.txt
5. Set the Start Command to: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
6. Deploy the service and copy the provided .onrender.com URL.

Note: Free instances on Render spin down after 15 minutes of inactivity. The first API request after a period of inactivity might take up to a minute to respond while the server wakes up.

### Deploying the Frontend (Vercel)

1. Import the repository into Vercel.
2. Set the Framework Preset to Next.js.
3. Change the Root Directory to 'frontend'.
4. Add an Environment Variable named NEXT_PUBLIC_API_URL and set its value to your Render URL (do not include a trailing slash at the end of the URL).
5. Click Deploy.
