import streamlit as st
import pandas as pd
import requests
from pathlib import Path
import os

# Fallback backend URL for testing purposes
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:7860")

# Streamlit UI for SuperKart Product Store Sales Prediction
st.title("SuperKart Product Store Sales Prediction App")
st.write("This app helps in predicting the future sales for Superkart.")
st.write("Move the sliders below to adjust values and get a prediction.")

# Collect user input using sliders
Product_Weight = st.number_input("Enter the weight of the product", min_value=0.0,value=12.66)
Product_Sugar_Content = st.selectbox("Select Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
Product_Allocated_Area = st.number_input("Ratio of the allocated display area", min_value=0.0, value=0.027)
Product_MRP = st.number_input("Maximum retail price of each product",min_value=0.0, value=117.08)
Store_Size = st.selectbox("Select the Store Size", ["1(Small)", "2(Medium)", "3(High)"])
Store_Location_City_Type = st.selectbox("Select the Store Location", ["Tier 1", "Tier 2", "Tier 3"])
Store_Type = st.selectbox("Select the Store Type", ["Departmental Store", "Food Mart", "Supermarket Type 1", "Supermarket Type 2","Supermarket Type 3"])
Product_Id_char = st.selectbox("Product ID",["FD(Food)", "DR (Drinks)", "NC(Non-Consumables)"])
Store_Age_Year = st.number_input("Enter the number of years established", min_value=0, value=16)
Product_Type_Category = st.selectbox("Select the Product Type", ["Perishables", "Non-Perishables"])

# Create input DataFrame
input_data = {
  "Product_Weight": Product_Weight,
  "Product_Sugar_Content": Product_Sugar_Content,
  "Product_Allocated_Area": Product_Allocated_Area,
  "Product_MRP": Product_MRP,
  "Store_Size": Store_Size,
  "Store_Location_City_Type": Store_Location_City_Type,
  "Store_Type": Store_Type,
  "Product_Id_char": Product_Id_char,
  "Store_Age_Years": Store_Age_Year,
  "Product_Type_Category": Product_Type_Category
}

#Making prediction when the "Predict" Button is clicked
if st.button("Predict"):
    response = requests.post(f"{BACKEND_URL}/v1/superkart_salesrevenue_predictor",json=input_data)    # Send Data to Flask API
    if response.status_code == 200:
        result = response.json()["Predicted_Sales_Total"]
        st.success(f"Predicted Sales Total (in dollar):{result:.2f}")
    else:
        st.error("Unable to connect to the prediction API")

# Batch Prediction
st.subheader("Batch Prediction")

# Allow users to upload a CSV file for batch prediction
upload_file = st.file_uploader("Upload CSV file for batch prediction", type=["csv"])

#Make batch prediction when the "Predict Batch" button is clicked
if upload_file is not None:
  if st.button("Predict Batch",type="primary"):
    response = requests.post(f"{BACKEND_URL}/v1/salesbatch", files={"file":upload_file.getvalue()})    # Send file to Flask API
    if response.status_code == 200:
      result_df = pd.DataFrame(response.json())
      st.write(result_df)
      st.success("Batch Prediction completed successfully!")
    else:
        st.error("Unable to connect to the prediction API")
