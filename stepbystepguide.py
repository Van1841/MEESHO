# AIzaSyDJgHXJYX3cnUEoE3al73QARTYrIXLSSoc
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
from fpdf import FPDF

# Firebase Setup
if not firebase_admin._apps:
    cred = credentials.Certificate("meesho-round-2-firebase-adminsdk-fbsvc-15b34b9e02.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Gemini Setup
genai.configure(api_key="AIzaSyDJgHXJYX3cnUEoE3al73QARTYrIXLSSoc")
model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

# Streamlit Setup
st.set_page_config(page_title="Your Business Roadmap", layout="centered")
st.title("Your Step-by-Step Business Roadmap")
st.markdown("## Choose your next step to grow your business")

# Fetch platform
docs = db.collection("selections").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(1).stream()
selected_platform = ""
product_name = ""

for doc in docs:
    data = doc.to_dict()
    selected_platform = data.get("selected_platform", "").strip()
    product_name = data.get("product_name", "")

# Generate AI roadmap
if selected_platform:
    guide_prompt = f"""
    Create a friendly, beginner-focused, 3-step roadmap to help a new seller launch their product on {selected_platform}.
    Make each step detailed, clear, and visually structured.
    Start with a motivating 1-liner intro.
    Do NOT include steps for price setup, listing, or ad content — we’ll add them after.
    """

    with st.spinner("Generating your personalized selling guide..."):
        try:
            guide_response = model.generate_content(guide_prompt)
            guide_text = guide_response.text.strip()

            st.success(f"Here’s your AI-powered roadmap for selling on {selected_platform}!")

            # Show roadmap in styled card
            st.subheader("Step-by-Step Guide:")
            st.markdown(
                f"""
                <div style='background-color: #f0f4ff; padding: 20px; border-radius: 12px;'>
                    <div style='white-space: pre-wrap;'>{guide_text}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Final 3 Steps section (styled like card)
            st.subheader("🚀 Final 3 Steps to Launch Your Product:")
            with st.container():
                st.markdown(
                    """
                    <div style='background-color: #f0f4ff; padding: 20px; border-radius: 12px;'>
                        <div style='display: flex; gap: 20px; flex-wrap: wrap;'>
                            <div style='flex: 1; min-width: 250px; background-color: #eef6ff; padding: 16px; border-radius: 10px;'>
                                <b>🧮 Price Calculator</b><br>
                                <form action='/price' target='_self'>
                                    <button style='margin-top: 10px; padding: 8px 16px; background-color: #dceeff; border-radius: 8px;'>Go to Calculator</button>
                                </form>
                            </div>
                            <div style='flex: 1; min-width: 250px; background-color: #eef6ff; padding: 16px; border-radius: 10px;'>
                                <b>📋 Product Listing</b><br>
                                <form action='/productlisting' target='_self'>
                                    <button style='margin-top: 10px; padding: 8px 16px; background-color: #dceeff; border-radius: 8px;'>Add Listing</button>
                                </form>
                            </div>
                            <div style='flex: 1; min-width: 250px; background-color: #eef6ff; padding: 16px; border-radius: 10px;'>
                                <b>🎯 Create Ad Content</b><br>
                                <form action='/adcontent' target='_self'>
                                    <button style='margin-top: 10px; padding: 8px 16px; background-color: #dceeff; border-radius: 8px;'>Create Ad</button>
                                </form>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Create clean version of guide for PDF (no emojis)
            clean_guide = guide_text.encode('ascii', 'ignore').decode('ascii')
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            for line in clean_guide.split('\n'):
                pdf.multi_cell(0, 10, txt=line)

            pdf.multi_cell(0, 10, txt="\nFinal 3 Steps:")
            pdf.multi_cell(0, 10, txt="1. Set Your Price")
            pdf.multi_cell(0, 10, txt="2. Add Product Listing")
            pdf.multi_cell(0, 10, txt="3. Create Ad Content")

            pdf_output = pdf.output(dest='S').encode('latin1')

            st.download_button(
                label="⬇️ Download Guide as PDF",
                data=pdf_output,
                file_name=f"{selected_platform}_selling_guide.pdf",
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"Gemini API Error: {e}")

else:
    st.error("No platform selected. Please select a platform first.")
