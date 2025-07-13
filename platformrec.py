# import streamlit as st

# st.set_page_config(page_title="Platform Recommendation", layout="centered")

# st.title("🛒 Platform Recommendation")

# # Dummy inputs for now (replace with session state or database fetch)
# category = st.selectbox("Product Category:", ["Fashion", "Electronics", "Home Decor", "Beauty", "Others"])
# stock = st.number_input("Enter Your Selling Capacity (Units):", min_value=1)

# platform = ""

# if category == "Fashion" and stock <= 50:
#     platform = "Meesho"
# elif category == "Electronics" and stock > 50:
#     platform = "Flipkart or Amazon"
# elif category == "Home Decor":
#     platform = "Flipkart"
# elif category == "Beauty" and stock <= 50:
#     platform = "Meesho or Nykaa"
# else:
#     platform = "Shopify or Wix"

# if st.button("Get Recommendation"):
#     st.success(f"We recommend using **{platform}** for your product!")
#     if platform == "Meesho":
#         st.markdown("[Go to Meesho Seller Page](https://supplier.meesho.com)")
#     elif "Amazon" in platform:
#         st.markdown("[Go to Amazon Seller Page](https://sellercentral.amazon.in)")



# AIzaSyDJgHXJYX3cnUEoE3al73QARTYrIXLSSoc


# import streamlit as st
# import firebase_admin
# from firebase_admin import credentials, firestore
# import google.generativeai as genai

# # Firebase Setup
# if not firebase_admin._apps:
#     cred = credentials.Certificate("meesho-round-2-firebase-adminsdk-fbsvc-15b34b9e02.json")
#     firebase_admin.initialize_app(cred)

# db = firestore.client()

# # Gemini Setup
# genai.configure(api_key="API")
# model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

# st.set_page_config(page_title="AI Platform Recommendation", layout="centered")
# st.title("AI Platform Recommendation")
# st.markdown("---")

# # Fetch Latest Product Entry
# docs = db.collection("products").order_by("Date", direction=firestore.Query.DESCENDING).limit(1).stream()

# latest_data = None
# for doc in docs:
#     latest_data = doc.to_dict()

# if latest_data:
#     category = latest_data.get("Category")
#     product_name = latest_data.get("Product Name")
#     product_description = latest_data.get("Product Description")
#     cost_price = latest_data.get("Cost Price")

#     st.subheader(f"Product: {product_name}")
#     st.subheader(f"Category: {category}")
#     st.subheader(f"Cost Price: ₹{cost_price}")

#     prompt = (
#         f"Suggest the top 3 Indian e-commerce platforms for the following product details:\n"
#         f"Category: {category}\n"
#         f"Product Description: {product_description}\n"
#         f"Cost Price: ₹{cost_price}\n"
#         f"Provide only each platform name, its seller registration link, and a 1-line reason why it's suitable. Do not include any extra notes or considerations."
#     )

#     tip_prompt = "Give me one funny yet useful business tip for selling products online in one line."

#     with st.spinner("Getting Gemini's recommendation..."):
#         try:
#             response = model.generate_content(prompt)
#             tip_response = model.generate_content(tip_prompt)
#             st.success("Recommended Platforms:")
#             st.write(response.text.strip())
#             st.info(f"💡 Business Tip: {tip_response.text.strip()}")
#         except Exception as e:
#             st.error(f"Gemini API Error: {e}")
# else:
#     st.error("No product data found. Please fill the product form first!")

    


import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
import re

# Firebase Setup
if not firebase_admin._apps:
    cred = credentials.Certificate("meesho-round-2-firebase-adminsdk-fbsvc-15b34b9e02.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Gemini Setup
genai.configure(api_key="AIzaSyDJgHXJYX3cnUEoE3al73QARTYrIXLSSoc")  # Replace with your actual API key
model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

st.set_page_config(page_title="AI Platform Recommendation", layout="centered")
st.title("AI Platform Recommendation")
st.markdown("---")

# Fetch latest product entry
docs = db.collection("products").order_by("Date", direction=firestore.Query.DESCENDING).limit(1).stream()

latest_data = None
for doc in docs:
    latest_data = doc.to_dict()

if latest_data:
    category = latest_data.get("Category")
    product_name = latest_data.get("Product Name")
    product_description = latest_data.get("Product Description")
    cost_price = latest_data.get("Cost Price")

    st.subheader(f"Product: {product_name}")
    st.subheader(f"Category: {category}")
    st.subheader(f"Cost Price: ₹{cost_price}")

    # Gemini prompt setup
    prompt = (
        f"Suggest the top 3 Indian e-commerce platforms for the following product details:\n"
        f"Category: {category}\n"
        f"Product Description: {product_description}\n"
        f"Cost Price: ₹{cost_price}\n"
        f"Provide only each platform name, its seller registration link, and a 1-line reason why it's suitable. "
        f"Do not include any introduction or ending note."
    )
    tip_prompt = "Give me one funny yet useful business tip for selling products online in one line."

    # Only generate once and freeze using session state
    if "platform_text_displayed" not in st.session_state:
        with st.spinner("Getting Gemini's recommendation..."):
            try:
                response = model.generate_content(prompt)
                tip_response = model.generate_content(tip_prompt)
                st.session_state.platform_text_displayed = response.text.strip()
                st.session_state.tip_text = tip_response.text.strip()
            except Exception as e:
                st.error(f"Gemini API Error: {e}")
                st.stop()

    # Show saved Gemini content
    st.success("Recommended Platforms:")
    st.markdown(st.session_state.platform_text_displayed)

    # Ask user to choose a platform
    st.markdown("### 👉 Please choose one of the platforms based on your choice:")

    # Extract platform names
    platform_names = re.findall(r"\d+\.\s*(.*)", st.session_state.platform_text_displayed)
    selected = None

    # Only show buttons if list is non-empty
    if platform_names:
        cols = st.columns(len(platform_names))
        for i, platform_name in enumerate(platform_names):
            with cols[i]:
                if st.button(platform_name.strip()):
                    selected = platform_name.strip()
    else:
        st.warning("⚠️ No platform names could be extracted from the response.")

    # Save selected platform
    if selected:
        try:
            db.collection("selections").add({
                "product_name": product_name,
                "selected_platform": selected,
                "timestamp": firestore.SERVER_TIMESTAMP
            })
            st.success(f"✅ You selected: {selected}")
        except Exception as e:
            st.error(f"❌ Failed to store selection: {e}")

    # Show frozen tip
    st.info(f"💡 Business Tip: {st.session_state.tip_text}")

else:
    st.error("No product data found. Please fill the product form first!")
