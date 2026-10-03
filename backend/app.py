import joblib
import pandas as pd
from flask import Flask, request, jsonify
from pathlib import Path

# Initialize Flask app
ProductStore_sales_revenue_api = Flask("SuperKart Product Store Sales Revenue Predictor")

# Load the trained Superkart Product Store Sales model
MODEL_PATH = Path(__file__).with_name("SuperKart_model_v1_0.joblib")
model = joblib.load(MODEL_PATH)

# Define a route for the home page
@ProductStore_sales_revenue_api.get('/')
def home():
  return "Welcome to the SuperKart Product Store Sales Prediction API!"

# Define an endpoint to predict price for a single product
@ProductStore_sales_revenue_api.post('/v1/superkart_salesrevenue_predictor')
def predict_sales_price():
    # Get JSON data from the request
    sales_data = request.get_json()

    # Extract relevant features from the input data
    sample = {
        'Product_Weight': sales_data['Product_Weight'],
        'Product_Sugar_Content': sales_data['Product_Sugar_Content'],        
        'Product_Allocated_Area': sales_data['Product_Allocated_Area'],  
        'Product_MRP': sales_data['Product_MRP'], 
        'Store_Size': sales_data['Store_Size'],
        'Store_Location_City_Type': sales_data['Store_Location_City_Type'],
        'Store_Type': sales_data['Store_Type'],
        'Product_Id_char': sales_data['Product_Id_char'],
        'Store_Age_Years': sales_data['Store__Age_Years'],
        'Product_Type_Category': sales_data['Product_Type'],     
    }

    # Convert the extracted data into a DataFrame
    input_data = pd.DataFrame([sample])

    # Make a prediction using the trained model
    prediction = model.predict(input_data).tolist()[0]

    # Return the prediction as a JSON response
    return jsonify({'Predicted_Sales_Total': prediction})

# Define an endpoint to predict price for a batch of sales
@ProductStore_sales_revenue_api.post('/v1/salesbatch')
def predict_sales_batch():
    # Get the uploaded CSV file from the request
    file = request.files['file']

    # Read the file into a DataFrame
    input_data = pd.read_csv(file)

    # Make predictions for the batch data
    predictions = model.predict(input_data).tolist()

    # Add predictions to the DataFrame
    input_data['Predicted_Sales_Total'] = predictions

    # Convert results to dictionary
    result = input_data.to_dict(orient="records")

    return jsonify(result)

# Run the Flask app in debug mode
if __name__ == '__main__':
    ProductStore_sales_revenue_api.run(debug=True)
