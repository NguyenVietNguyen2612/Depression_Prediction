import streamlit as st
import pandas as pd
from catboost import CatBoostClassifier
import time

# Custom CSS with fixed quote-box styling
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff !important;
    }
    .main {
        background-color: #e6f0fa;
        padding: 20px;
        border-radius: 10px;
        min-height: 80vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }
    .stSlider .st-bq {
        background-color: #d1e0ff;
        border-radius: 8px;
    }
    .stSelectbox, .stNumberInput {
        background-color: #f5faff;
        border-radius: 8px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stCheckbox {
        margin-top: 10px;
    }
    h1 {
        color: #1e3a8a;
        font-family: 'Arial', sans-serif;
        text-align: center;
    }
    .result-box, .quote-box {
        background-color: #F5ECE0;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin: 20px auto;
        text-align: center;
        max-width: 600px;
        width: 90%;
    }
    .quote-text {
        font-style: italic;
        font-size: 18px;
        color: #2c5282;
        margin-bottom: 10px;
    }
    .quote-author {
        font-weight: bold;
        font-size: 16px;
        color: #1a4971;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for navigation
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# Function to display the homepage
def show_homepage():
    st.title("Welcome to the Depression Risk Predictor 🧠")
    st.markdown("""
    This tool helps you assess your risk of depression based on various lifestyle and personal factors. 
    By answering a few questions, you can gain insights into your mental health and take proactive steps if needed.
    All inputs are confidential and used solely for prediction purposes.
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='quote-box'>
        <p class='quote-text'>“You don’t have to control your thoughts. You just have to stop letting them control you.”</p>
        <p class='quote-author'>— Dan Millman</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Get Started 🔍"):
        st.session_state.page = 'predictor'

# Function to display the prediction tool
def show_predictor():
    # Load model
    model = CatBoostClassifier()
    model.load_model("catboost_tuned_model.cbm")

    # Define fixed category lists based on training data
    suicidal_thoughts_cat = ['No', 'Yes']
    status_cat = ['Student', 'Working Professional']
    diet_cat = ['Healthy', 'Moderate', 'Unhealthy']
    profession_cat = [
        'Chef', 'Teacher', 'Business Analyst', 'Financial Analyst', 'Chemist',
        'Electrician', 'Software Engineer', 'Data Scientist', 'Plumber',
        'Marketing Manager', 'Accountant', 'Entrepreneur', 'HR Manager',
        'UX/UI Designer', 'Content Writer', 'Educational Consultant',
        'Civil Engineer', 'Manager', 'Pharmacist', 'Architect',
        'Mechanical Engineer', 'Customer Support', 'Consultant',
        'Judge', 'Researcher', 'Pilot', 'Graphic Designer', 'Travel Consultant',
        'Digital Marketer', 'Lawyer', 'Research Analyst', 'Sales Executive',
        'Doctor', 'Investment Banker', 'missing'
    ]

    st.title("🧠 Depression Risk Predictor")
    st.markdown("Fill in the details below to assess your depression risk.", unsafe_allow_html=True)
    
    if st.button("Back to Home"):
        st.session_state.page = 'home'
        st.rerun()

    with st.expander("Personal Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=10, max_value=100, step=1, help="Enter your age (10–100 years).")
            suicidal_thoughts = st.selectbox("Have you ever had suicidal thoughts?", suicidal_thoughts_cat, help="Select 'Yes' or 'No'.")
        with col2:
            status = st.selectbox("Student or Working Professional?", status_cat, help="Choose your current status.")

    with st.expander("Academic/Work and Financial Details"):
        col1, col2 = st.columns(2)
        with col1:
            aca_pressure = st.slider("Academic/Work Pressure", 1, 5, help="Rate from 1 (Low) to 5 (High).")
            financial_stress = st.slider("Financial Stress", 1, 5, help="Rate from 1 (Low) to 5 (High).")
        with col2:
            aca_satisfaction = st.slider("Academic/Work Satisfaction", 1, 5, help="Rate from 1 (Low) to 5 (High).")
            hours = st.slider("Work/Study Hours per Day", 0, 18, help="Average hours spent daily.")

    with st.expander("Education and Profession"):
        col1, col2 = st.columns(2)
        with col1:
            cgpa_option = st.checkbox("No CGPA (not applicable)", help="Check if CGPA is not relevant (e.g., not a student).")
            if cgpa_option:
                cgpa = 'NaN'
            else:
                cgpa = st.number_input("CGPA (0.00–10.00)", min_value=0.00, max_value=10.00, step=0.01, format="%.2f", help="Enter your CGPA with two decimal places (0.00–10.00).")
                cgpa = f"{cgpa:.2f}"  # Ensure CGPA is formatted as a string with 2 decimal places
        with col2:
            no_job = st.checkbox("No job (i.e., not working currently)", help="Check if you are not currently employed.")
            profession = 'missing' if no_job else st.selectbox("Profession", profession_cat[:-1], help="Select your profession or leave as 'missing' if not applicable.")

    with st.expander("Lifestyle"):
        col1, col2 = st.columns(2)
        with col1:
            diet = st.selectbox("Dietary Habits", diet_cat, help="Choose your dietary pattern.")
        with col2:
            sleep_duration = st.slider("Sleep Duration (hours)", 0, 12, help="Average hours of sleep per night.")

    if st.button("🔍 Predict Depression Risk"):
        if age < 10 or age > 100:
            st.error("Please enter a valid age between 10 and 100.")
        elif not cgpa_option and (float(cgpa) < 0.00 or float(cgpa) > 10.00):
            st.error("Please enter a valid CGPA between 0.00 and 10.00.")
        else:
            input_df = pd.DataFrame({
                "Age": [age],
                "Have you ever had suicidal thoughts ?": [suicidal_thoughts],
                "Aca/Work Pressure": [aca_pressure],
                "Financial Stress": [financial_stress],
                "Aca/Work Satisfaction": [aca_satisfaction],
                "Working Professional or Student": [status],
                "CGPA": [cgpa],
                "Work/Study Hours": [hours],
                "Dietary Habits": [diet],
                "Profession": [profession],
                "Sleep Duration": [sleep_duration]
            })

            print(f"Input DataFrame:\n{input_df}")
            input_df.to_csv("input_data.csv", index=False)

            with st.spinner("Analyzing your inputs..."):
                time.sleep(1)
                prob = model.predict_proba(input_df)[0][1]

            st.markdown("<div class='result-box'>", unsafe_allow_html=True)
            st.success(f"🧪 Predicted Probability of Depression: **{prob:.2%}**")
            st.progress(prob)
            if prob > 0.7:
                st.warning("This indicates a higher risk. Consider consulting a mental health professional.")
            elif prob > 0.3:
                st.info("Moderate risk. Monitoring your mental health is recommended.")
            else:
                st.success("Low risk. Keep maintaining a healthy lifestyle!")
            st.markdown("</div>", unsafe_allow_html=True)

# Navigation logic
if st.session_state.page == 'home':
    show_homepage()
else:
    show_predictor()