from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time, os
from fastapi.responses import StreamingResponse
import pandas as pd
import io, uuid
from src.synthetic_data_genration import mongo_db
from app import *
# Initialize MongoDB connection
cosmosdb_connection_string = os.getenv("cosmosdb_connection_string")
if not cosmosdb_connection_string:
    raise RuntimeError("COSMOSDB_CONNECTION_STRING environment variable not set")

mongo_db_instance = mongo_db(cosmosdb_connection_string, "incle")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload-file/")
async def handle_file(
    file: UploadFile = File(...),
    output_format : str= Form(...),
    user_id: int = Form(...),
    model_providers: str = Form(...),
    model: str = Form(...)
):
    if file.content_type not in ["text/csv", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/parquet"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    tokens_used, document_id = None, uuid.uuid4()
    try:
        if file.content_type == "text/csv":
            # df = pd.read_csv(file.file)
            return {
                "user_id" : user_id,
                "document_id" : document_id,
                "output_format" : output_format,
                "tokens_used" : tokens_used

            }
        
        elif file.content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            # df = pd.read_excel(file.file)
            return {
                "user_id" : user_id,
                "document_id" : document_id,
                "output_format" : output_format,
                "tokens_used" : tokens_used
            }
        elif file.content_type == "application/parquet":
            # df = pd.read_parquet(file.file)
        
            return {
                "user_id" : user_id,
                "document_id" : document_id,
                "output_format" : output_format,
                "tokens_used" : tokens_used
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    raise HTTPException(status_code=500, detail="Unexpected error")

@app.get("/get_model_card/")
async def get_model():
    try:
        documents = mongo_db_instance.find_many("SDG_model_cards", {}, 10)
        documents = mongo_db_instance.find_with_projection("SDG_model_cards", {}, {"_id": 0})
        response = [doc for doc in documents]
        return response
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Error retrieving model cards: {str(e)}"})


@app.post("/get_documents/")  # Changed to POST
async def get_data(document_id: str = Form(...), output_format: str = Form(...)):
    try:
        # Fetch or generate DataFrame based on document_id
        data = {
            'Column1': [1, 2, 3],
            'Column2': ['A', 'B', 'C']
        }
        df = pd.DataFrame(data)

        # Convert DataFrame to CSV
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        stream.seek(0)

        # Streaming response setup
        response = StreamingResponse(iter([stream.getvalue()]),
                                     media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=export.csv"

        return response

    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Error retrieving documents: {str(e)}"})