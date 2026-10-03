import joblib
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from pathlib import Path

# Initialize Flask app
ProductStore_sales_revenue_api = Flask("SuperKart Product Store Sales Revenue Predictor")

# Load the trained Superkart Product Store Sales model
MODEL_PATH = Path(__file__).with_name("SuperKart_model_v1_0.joblib")
model = joblib.load(MODEL_PATH)

# Feature Preprocessing function: standardizes incoming JSON payload request attributes into a model-ready matrix format
def preprocess_features(input_df):
    df = input_df.copy()

    # 1. Clean categorical text variations
    if 'Product_Sugar_Content' in df.columns:
        df['Product_Sugar_Content'] = df['Product_Sugar_Content'].replace({'reg': 'Regular'})

    # 2. Extract structural high-level product character prefixes
    if 'Product_Id' in df.columns:
        df['Product_Id_char'] = df['Product_Id'].str[:2]
    else:
        # Default for single prediction if 'Product_Id' is not provided (e.g., in UI payload)
        df['Product_Id_char'] = 'FD' 

    # 3. Calculate store maturity in years since establishment
    if 'Store_Establishment_Year' in df.columns:
        df['Store_Age_Year'] = 2026 - df['Store_Establishment_Year'].astype(int)
    elif 'Store_Age_Years' in df.columns:
        # Use 'Store_Age_Years' if directly provided (e.g., from UI payload)
        df['Store_Age_Year'] = df['Store_Age_Years']
    else:
        df['Store_Age_Year'] = 17  # median default replacement

    # 4. Group detailed items into Perishables/Non-Perishables
    perishable_types = ["Dairy", "Meat", "Frozen Foods", "Fruits and Vegetables", "Seafood"]
    if 'Product_Type' in df.columns:
        df['Product_Type_Category'] = df['Product_Type'].apply(lambda x: "Perishable" if x in perishable_types else "Non Perishable")
    elif 'Product_Type_Category' in df.columns:
        # Use 'Product_Type_Category' if directly provided
        df['Product_Type_Category'] = df['Product_Type_Category']
    else:
        df['Product_Type_Category'] = "Non Perishable"

    # 5. Apply ordinal label-encoding structures for Store_Size
    if 'Store_Size' in df.columns:
        # Handle both raw text (e.g., 'Medium') and UI-formatted text (e.g., '2(Medium)')
        df['Store_Size'] = df['Store_Size'].astype(str).replace(r'^\d\((.*?)\)$', r'\1', regex=True)
        df['Store_Size'] = df['Store_Size'].replace({"Small": 1, "Medium": 2, "High": 3})
    else:
        df['Store_Size'] = 2 # Median default replacement

    # 6. Reconstruct precise model feature columns to align perfectly with the estimator matrix shape
    expected_features = [
        'Product_Weight', 'Product_Allocated_Area', 'Product_MRP', 'Store_Size', 'Store_Age_Year',
        'Product_Sugar_Content_No Sugar', 'Product_Sugar_Content_Regular',
        'Store_Location_City_Type_Tier 2', 'Store_Location_City_Type_Tier 3',
        'Store_Type_Food Mart', 'Store_Type_Supermarket Type1', 'Store_Type_Supermarket Type2',
        'Product_Id_char_FD', 'Product_Id_char_NC', 'Product_Type_Category_Perishable'
    ]

    # Initialize a new DataFrame with zeroes, ensuring all expected columns are present
    final_df = pd.DataFrame(0, index=df.index, columns=expected_features)

    # Populate numerical continuous fields
    for col in ['Product_Weight', 'Product_Allocated_Area', 'Product_MRP', 'Store_Size', 'Store_Age_Year']:
        if col in df.columns:
            final_df[col] = df[col]

    # Set active category dummy flags based on feature encoding logic
    if 'Product_Sugar_Content' in df.columns:
        final_df['Product_Sugar_Content_No Sugar'] = (df['Product_Sugar_Content'] == 'No Sugar').astype(int)
        final_df['Product_Sugar_Content_Regular'] = (df['Product_Sugar_Content'] == 'Regular').astype(int)

    if 'Store_Location_City_Type' in df.columns:
        final_df['Store_Location_City_Type_Tier 2'] = (df['Store_Location_City_Type'] == 'Tier 2').astype(int)
        final_df['Store_Location_City_Type_Tier 3'] = (df['Store_Location_City_Type'] == 'Tier 3').astype(int)

    if 'Store_Type' in df.columns:
        final_df['Store_Type_Food Mart'] = (df['Store_Type'] == 'Food Mart').astype(int)
        final_df['Store_Type_Supermarket Type1'] = (df['Store_Type'] == 'Supermarket Type1').astype(int)
        final_df['Store_Type_Supermarket Type2'] = (df['Store_Type'] == 'Supermarket Type2').astype(int)

    if 'Product_Id_char' in df.columns:
        # Handle both raw 'FD' and UI-formatted 'FD(Food)'
        df['Product_Id_char_clean'] = df['Product_Id_char'].astype(str).replace(r'\(.*\)', '', regex=True).str.strip()
        final_df['Product_Id_char_FD'] = (df['Product_Id_char_clean'] == 'FD').astype(int)
        final_df['Product_Id_char_NC'] = (df['Product_Id_char_clean'] == 'NC').astype(int)

    if 'Product_Type_Category' in df.columns:
        # Handle both raw 'Perishable' and UI-formatted 'Perishables'
        df['Product_Type_Category_clean'] = df['Product_Type_Category'].astype(str).replace(r's$', '', regex=True) # Remove 's' if present
        final_df['Product_Type_Category_Perishable'] = (df['Product_Type_Category_clean'] == 'Perishable').astype(int)

    return final_df[expected_features] # Ensure the order of columns is correct

# Define a route for the home page
@ProductStore_sales_revenue_api.get('/')
def home():
  return "Welcome to the SuperKart Product Store Sales Prediction API!"

# Define an endpoint to predict price for a single product
@ProductStore_sales_revenue_api.post('/v1/superkart_salesrevenue_predictor')
def predict_sales_price():
    # Get JSON data from the request
    sales_data = request.get_json()

    # Convert the extracted data into a DataFrame
    input_data = pd.DataFrame([sales_data])

    # Preprocess the input data
    processed_input = preprocess_features(input_data)

    # Make a prediction using the trained model
    prediction = model.predict(processed_input).tolist()[0]

    # Return the prediction as a JSON response
    return jsonify({'Predicted_Sales_Total': prediction})

# Define an endpoint to predict price for a batch of sales
@ProductStore_sales_revenue_api.post('/v1/salesbatch')
def predict_sales_batch():
    # Get the uploaded CSV file from the request
    file = request.files['file']

    # Read the file into a DataFrame
    input_data = pd.read_csv(file)

    # Preprocess the batch data
    processed_input = preprocess_features(input_data)

    # Make predictions for the batch data
    predictions = model.predict(processed_input).tolist()

    # Add predictions to the DataFrame
    input_data['Predicted_Sales_Total'] = predictions

    # Convert results to dictionary
    result = input_data.to_dict(orient="records")

    return jsonify(result)

# Run the Flask app in debug mode
if __name__ == '__main__':
    ProductStore_sales_revenue_api.run(debug=True, host='0.0.0.0', port=7860)
