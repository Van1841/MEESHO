import streamlit as st
import datetime
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase Setup
if not firebase_admin._apps:
    cred = credentials.Certificate("meesho-round-2-firebase-adminsdk-fbsvc-15b34b9e02.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Streamlit Page Config
st.set_page_config(page_title="Product Form", layout="centered")

# App Title
st.title("Sell Online - Product Details Form")
st.markdown("---")

# Step 1: Basic Product Details
st.header("Product Details")
categories = [
    "Fashion", "Electronics", "Home Decor", "Beauty", "Books", "Toys", "Groceries", "Automobile Accessories",
    "Mobile Accessories", "Furniture", "Others"
]
category = st.selectbox("Product Category", categories)
custom_category = ""
if category == "Others":
    custom_category = st.text_input("Specify Custom Category")

product_name = st.text_input("Product Name")
product_description = st.text_area("Product Description")
cost_price = st.number_input("Cost Price to Make (₹)", min_value=1)

# Submit Button
if st.button("Submit & Save Details"):
    if category == "Others" and custom_category.strip() == "":
        st.error("Please enter your custom category before submitting!")
    elif product_name.strip() == "" or product_description.strip() == "":
        st.error("Please fill all required details!")
    else:
        final_category = custom_category if category == "Others" else category
        data = {
            "Category": final_category,
            "Product Name": product_name,
            "Product Description": product_description,
            "Cost Price": cost_price,
            "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        db.collection("products").add(data)

        # Save to CSV as well
        df = pd.DataFrame([data])
        try:
            df.to_csv("user_product_data.csv", mode='a', header=not pd.read_csv("user_product_data.csv").empty, index=False)
        except FileNotFoundError:
            df.to_csv("user_product_data.csv", mode='w', header=True, index=False)

        st.success("Your product details have been saved!")
        st.balloons()
