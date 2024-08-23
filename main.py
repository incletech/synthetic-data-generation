import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import time
import asyncio 
import uuid 
from app import process_the_document, mongo_db 
import re

# ------ Initial Settings ------ #
PAGE_ICON = "https://img.icons8.com/ios-filled/50/000000/parthenon.png"
TITLE = "LLAMA SDG"
start_date = datetime.now() - timedelta(days=30 * 6)
end_date = datetime.now()
min_date = datetime(2006, 1, 1)

# ------ Model Data ------ #
models_data = {
    "Together AI": [
        {
            "name": "Llama 3.1 70B Instruct Turbo",
            "model_id": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        },
        {
            "name": "Llama 3.1 405B Instruct Turbo",
            "model_id": "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        },
        {
            "name": "Llama 3 70B Instruct Turbo",
            "model_id": "meta-llama/Meta-Llama-3-70B-Instruct-Turbo",
        }
    ],
    "Groq": [
        {
            "name": "Llama 3.1 70B (Preview)",
            "model_id": "llama-3.1-70b-versatile",
        },
        {
            "name": "Llama 3 Groq 70B Tool Use (Preview)",
            "model_id": "llama3-groq-70b-8192-tool-use-preview",
        },
        {
            "name": "Meta Llama 3 70B",
            "model_id": "llama3-70b-8192",

        },
        {
            "name": "Mixtral 8x7B",
            "model_id": "mixtral-8x7b-32768",
        }
    ],
    "AIML API": [
        {
            "name": "Llama 3.1 405B Instruct Turbo",
            "model_id": "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        },
        {
            "name": "Llama 3.1 70B Instruct Turbo",
            "model_id": "meta-llama/Meta-Llama-3-70B-Instruct-Turbo",
        },
        {
            "name": "Llama 3 70B Instruct Lite",
            "model_id": 'meta-llama/Meta-Llama-3-70B-Instruct-Lite',
        },
        {
            "name": "Llama-3 Chat (70B)",
            "model_id": 'meta-llama/Llama-3-70b-chat-hf',
        }
    ]
}

# ------ Page Configuration ------ #
st.set_page_config(
    page_title="LLAMA SDG",
    page_icon=PAGE_ICON,
    layout="centered",
    menu_items={
        "About": """
    This application retrieves archived tweets CDX data in HTML, CSV, and JSON formats.
    For better performance, use the CLI version available on PyPI.
    To access the legacy version of Wayback Tweets, click here.
    """,
        "Report a bug": "https://github.com/claromes/waybacktweets/issues",
    },
)

# ------ Custom CSS for White Background ------ #
st.markdown(
    """
    <style>
        .main {
            background-color: #daf0fc; /* Main background color */
            color: #000000;
        }
        header[data-testid="stHeader"] {
            background-color: #FFFFFF;
            color: #000000;
            opacity: 1.0;
        }
        /* Remove background, borders, and padding from the container around the dropdowns */
        .stSelectbox, .stTextInput input, .stFileUploader {
            background-color: transparent !important; /* Make input background transparent */
            color: #000000;
            border: none; /* Remove border */
            padding: 0; /* Remove padding */
        }
        /* Remove any padding or margin around the overall container */
        .stSelectbox, .stTextInput, .stFileUploader {
            margin-top: 0 !important; 
            margin-bottom: 0 !important; 
            padding-top: 0 !important; 
            padding-bottom: 0 !important; 
        }
        .stCheckbox span {
            color: #000000;
        }
        .stButton button {
            background-color: #000000;
            color: #FFFFFF;
            border-radius: 5px;
        }
        /* Adjust headings to be integrated with the background */
        .selectbox-header {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 5px;
            color: #333333;
            margin-top: 10px; /* Less margin for more compact layout */
            background-color: transparent; /* Transparent background */
        }
        .selectbox-container {
            margin-bottom: 5px; /* Less margin between containers */
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ------ User Interface ------ #
st.markdown('<h1 style="color:blue;">LLAMA SDG</h1>', unsafe_allow_html=True)

# Add a GitHub link
st.caption(
    '[![GitHub](https://img.shields.io/badge/GitHub-incletech/synthetic--data--generation-blue?logo=github)](https://github.com/incletech/synthetic-data-generation)'
)
st.write("Revolutionize Your AI Training with Tailored Synthetic Data!")
st.write("From Scenarios to Solutions: Empower Your LLMs with Our Synthetic Data Generator!")
st.write("Create Realistic Scenarios. Generate High-Quality Data. Train Smarter AI.")


# ------ File Upload Option ------ #
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

def validate_email(email):
    # Define the regex pattern for a valid email address
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_pattern, email)

mail_id = st.text_input("Enter Your Email ID ")  # Corrected to be a simple text input for email

if mail_id:
    if validate_email(mail_id):
        st.success("Valid email address!")
    else:
        st.error("Invalid email address. Please enter a valid email.")

# ------ Model Providers and Models Selection ------ #
st.markdown('<div class="selectbox-container"><div class="selectbox-header">Select Model Provider</div>', unsafe_allow_html=True)
model_provider = st.selectbox("", options=["AIML API", "Groq", "Together AI"])
st.markdown('</div>', unsafe_allow_html=True)

if model_provider:
    models_list = models_data.get(model_provider, [])
    model_names = [model["name"] for model in models_list]
    st.markdown('<div class="selectbox-container"><div class="selectbox-header">Select Model</div>', unsafe_allow_html=True)
    selected_model = st.selectbox("", options=model_names)
    st.markdown('</div>', unsafe_allow_html=True)

    # Find and store the model_id for the selected model
    selected_model_id = next((model["model_id"] for model in models_list if model["name"] == selected_model), None)

    if selected_model_id:
        st.write(f"Selected Model ID: {selected_model_id}")

if model_provider == "AIML API":
    model_provider = "together_ai"
    selected_model_id = "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo"
elif model_provider == "Groq":
    model_provider = "groq"
elif model_provider == "Together AI":
    model_provider = "together_ai"

# ------ Output Format Selection ------ #
st.markdown('<div class="selectbox-container"><div class="selectbox-header">Select Output Format</div>', unsafe_allow_html=True)
output_format = st.selectbox("", options=["CSV", "Excel"])
st.markdown('</div>', unsafe_allow_html=True)
# ------ Query Button ------ #
query = st.button("Generate")

# ------ Results ------ #
if query:
    if uploaded_file is not None:
        try:
            # Determine file type and read accordingly
            if uploaded_file.name.endswith(".csv"):
                data = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".xlsx"):
                data = pd.read_excel(uploaded_file)
            else:
                st.error("Unsupported file format!")

            with st.spinner("Generating data..."):
                user_id = str(uuid.uuid4())  # Generate a unique user ID
                doc_id = str(uuid.uuid4())   # Generate a unique document ID

                # Ensure process_the_document is async, otherwise remove asyncio.run
                data_generation = asyncio.run(process_the_document(user_id, doc_id, mail_id, data, model_provider, selected_model_id, output_format))
                st.write("Token used: ", data_generation["tokens_used"])

                # Query the database to get the generated data
                query = {"document_id": doc_id}
                projection = {"_id": 0, "document_id": 0, "user_id": 0, "mail_id": 0}
                results = mongo_db.find_with_projection("SDG_synthetic_data", query, projection)
                all_messages = list(results)
                df = pd.DataFrame(all_messages)
                if output_format == "CSV":
                    csv_data = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download data as CSV",
                        data=csv_data,
                        file_name='generated_data.csv',
                        mime='text/csv',
                    )
                elif output_format == "Excel":
                    excel_data = df.to_excel(index=False, engine='openpyxl')
                    st.download_button(
                        label="Download data as Excel",
                        data=excel_data,
                        file_name='generated_data.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    )

        except Exception as e:
            st.error(f"Error processing the data: {e}")

    else:
        st.warning("Please upload a CSV or Excel file.")
