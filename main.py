import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import time
import asyncio 
import uuid 
from app import process_the_document, mongo_db 

# ------ Initial Settings ------ #
PAGE_ICON = "https://img.icons8.com/ios-filled/50/000000/parthenon.png"
TITLE = "Wayback Tweets"
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
    page_title="Wayback Tweets",
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
        /* Set the background color to white */
        .main {
            background-color: #FFFFFF;
            color: #000000;
        }
        /* Set the header background color to white and text color to black */
        header[data-testid="stHeader"] {
            background-color: #FFFFFF;
            color: #000000;
            opacity: 1.0;
        }
        /* Adjust input fields and button colors */
        .stTextInput input, .stFileUploader, .stSelectbox {
            background-color: #E0E0E0;
            color: #000000;
        }
        .stCheckbox span {
            color: #000000;
        }
        .stButton button {
            background-color: #000000;
            color: #FFFFFF;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ------ User Interface ------ #
st.title(TITLE)
st.caption(
    "[![GitHub release](https://img.shields.io/github/v/release/claromes/waybacktweets)](https://github.com/claromes/waybacktweets/releases) "
    "[![Read the documentation](https://img.shields.io/badge/read_the-documentation-0a507a?logo=sphinx)](https://claromes.github.io/waybacktweets) "
    "[![Donate via sponsors](https://img.shields.io/badge/donate-via%20sponsors-ff69b4.svg?logo=github)](https://github.com/sponsors/claromes)"
)

st.write("Retrieves archived tweets CDX data in HTML (for easy viewing of the tweets), CSV, and JSON formats.")
st.write("For better performance, use the CLI version, available on [PyPI](https://pypi.org/project/waybacktweets).")
st.write("To access the legacy version of Wayback Tweets, [click here](https://waybacktweets-legacy.streamlit.app).")
st.divider()

# ------ File Upload Option ------ #
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

mail_id = st.text_input("Enter Your Email ID")  # Corrected to be a simple text input for email

# ------ Model Providers and Models Selection ------ #
model_provider = st.selectbox("Select Model Provider", options=["AIML API", "Groq", "Together AI"])
if model_provider:
    models_list = models_data.get(model_provider, [])
    model_names = [model["name"] for model in models_list]
    selected_model_name = st.selectbox("Select Model", options=model_names)

    # Find and store the model_id for the selected model
    selected_model_id = next((model["model_id"] for model in models_list if model["name"] == selected_model_name), None)

    if selected_model_id:
        st.write(f"Selected Model ID: {selected_model_id}")

if model_provider == "AIML API":
    model_provider = "aimlapi"
elif model_provider == "Groq":
    model_provider = "groq"
elif model_provider == "Together AI":
    model_provider = "together_ai"

# ------ Output Format Selection ------ #
output_format = st.selectbox("Select Output Format", options=["CSV", "Excel"])

# ------ Query Button ------ #
query = st.button("Query")

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





































































# from fastapi import FastAPI, Form, File, UploadFile, HTTPException
# from fastapi.responses import FileResponse, JSONResponse
# from fastapi.middleware.cors import CORSMiddleware
# import time, os
# from fastapi.responses import StreamingResponse
# import pandas as pd
# import io, uuid
# from src.synthetic_data_genration import mongo_db
# from app import *
# import xlsxwriter

# # Initialize MongoDB connection
# cosmosdb_connection_string = os.getenv("cosmosdb_connection_string")
# if not cosmosdb_connection_string:
#     raise RuntimeError("COSMOSDB_CONNECTION_STRING environment variable not set")

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], 
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# @app.post("/upload-file/")
# async def handle_file(
#     file: UploadFile = File(...),
#     output_format : str= Form(...),
#     user_id: str = Form(...),
#     model_providers: str = Form(...),
#     model: str = Form(...)
# ):
#     if file.content_type not in ["text/csv", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
#         raise HTTPException(status_code=400, detail="Unsupported file type")
    
#     tokens_used, document_id = None, str(uuid.uuid4())
#     try:
#         if file.content_type == "text/csv":
#             df = pd.read_csv(file.file)
#             response = await process_the_document(user_id=user_id, document_id=document_id , document=df, client=model_providers, model=model, file_output_format=output_format)
#             return {
#                 "user_id" : user_id,
#                 "document_id" : document_id,
#                 "output_format" : output_format,
#                 "tokens_used" : tokens_used
#             }
        
#         elif file.content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
#             df = pd.read_excel(file.file)
#             response = await process_the_document(user_id=user_id, document_id=document_id , document=df, client=model_providers, model=model, file_output_format=output_format)
#             return {
#                 "user_id" : user_id,
#                 "document_id" : document_id,
#                 "output_format" : output_format,
#                 "tokens_used" : tokens_used
#             }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

#     raise HTTPException(status_code=500, detail="Unexpected error")

# @app.get("/get_model_card/")
# async def get_model():
#     try:
#         documents = mongo_db.find_many("SDG_model_cards", {}, 10)
#         documents = mongo_db.find_with_projection("SDG_model_cards", {}, {"_id": 0})
#         response = [doc for doc in documents]
#         return response
#     except Exception as e:
#         return JSONResponse(status_code=500, content={"detail": f"Error retrieving model cards: {str(e)}"})
    
# @app.get("/get_demo_csv/")
# async def get_model():
#     try:
#         data = {
#             'scenerio': [
#                 'Smita ordered a portable power bank for an upcoming birthday. However, after receiving the product, they faced issues with the product installation. Now, Smita is worried about finding a solution before the birthday.',
#                 'Harsh ordered a smart doorbell for an upcoming fitness challenge. However, after receiving the product, they had trouble with the payment process. Now, Harsh is worried about finding a solution before the fitness challenge.',
#                 'Ajay ordered a tablet for an upcoming long weekend. However, after receiving the product, they received a notification that the product is delayed. Now, Ajay is worried about finding a solution before the long weekend.',
#                 'Kiran ordered a air purifier for an upcoming anniversary. However, after receiving the product, they faced issues with the product installation. Now, Kiran is worried about finding a solution before the anniversary.',
#                 'Sanjay ordered a electric grill for an upcoming Diwali celebration. However, after receiving the product, they discovered that the product is out of stock after placing the order. Now, Sanjay is worried about finding a solution before the Diwali celebration.']}
        
#         df = pd.DataFrame(data)
#         stream = io.StringIO()
#         df.to_csv(stream, index=False)
#         stream.seek(0)
#         response = StreamingResponse(iter([stream.getvalue()]),
#                                      media_type="text/csv")
#         response.headers["Content-Disposition"] = "attachment; filename=sample.csv"

#         return response
#     except Exception as e:
#         return JSONResponse(status_code=500, content={"detail": f"Error retrieving model cards: {str(e)}"})

# @app.post("/get_documents/") 
# async def get_data(document_id: str = Form(...), output_format: str = Form(...)):
#     try:
#         query = {"document_id": document_id}
#         projection = {"_id": 0, "document_id": 0, "user_id": 0}
#         results = mongo_db.find_with_projection("SDG_synthetic_data", query, projection)
#         all_messages = list(results)
#         df = pd.DataFrame(all_messages)
        
#         if output_format.lower() == "csv":
#             stream = io.StringIO()
#             df.to_csv(stream, index=False)
#             stream.seek(0)
#             response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
#             response.headers["Content-Disposition"] = "attachment; filename=export.csv"
        
#         elif output_format.lower() == "excel":
#             stream = io.BytesIO()
#             with pd.ExcelWriter(stream, engine='xlsxwriter') as writer:
#                 df.to_excel(writer, index=False, sheet_name='Data')
#             stream.seek(0)
#             response = StreamingResponse(iter([stream.getvalue()]), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
#             response.headers["Content-Disposition"] = "attachment; filename=export.xlsx"

#         return response

#     except Exception as e:
#         return JSONResponse(status_code=500, content={"detail": f"Error retrieving documents: {str(e)}"})