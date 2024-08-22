from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time, os
from fastapi.responses import StreamingResponse
import pandas as pd
import io, uuid
from src.synthetic_data_genration import mongo_db
from app import *
import xlsxwriter

# Initialize MongoDB connection
cosmosdb_connection_string = os.getenv("cosmosdb_connection_string")
if not cosmosdb_connection_string:
    raise RuntimeError("COSMOSDB_CONNECTION_STRING environment variable not set")

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
    user_id: str = Form(...),
    model_providers: str = Form(...),
    model: str = Form(...)
):
    if file.content_type not in ["text/csv", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    tokens_used, document_id = None, str(uuid.uuid4())
    try:
        if file.content_type == "text/csv":
            df = pd.read_csv(file.file)
            response = await process_the_document(user_id=user_id, document_id=document_id , document=df, client=model_providers, model=model, file_output_format=output_format)
            return {
                "user_id" : user_id,
                "document_id" : document_id,
                "output_format" : output_format,
                "tokens_used" : tokens_used
            }
        
        elif file.content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            df = pd.read_excel(file.file)
            response = await process_the_document(user_id=user_id, document_id=document_id , document=df, client=model_providers, model=model, file_output_format=output_format)
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
        documents = mongo_db.find_many("SDG_model_cards", {}, 10)
        documents = mongo_db.find_with_projection("SDG_model_cards", {}, {"_id": 0})
        response = [doc for doc in documents]
        return response
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Error retrieving model cards: {str(e)}"})
    
@app.get("/get_demo_csv/")
async def get_model():
    try:
        data = {
            'scenerio': [
                'Smita ordered a portable power bank for an upcoming birthday. However, after receiving the product, they faced issues with the product installation. Now, Smita is worried about finding a solution before the birthday.',
                'Harsh ordered a smart doorbell for an upcoming fitness challenge. However, after receiving the product, they had trouble with the payment process. Now, Harsh is worried about finding a solution before the fitness challenge.',
                'Ajay ordered a tablet for an upcoming long weekend. However, after receiving the product, they received a notification that the product is delayed. Now, Ajay is worried about finding a solution before the long weekend.',
                'Kiran ordered a air purifier for an upcoming anniversary. However, after receiving the product, they faced issues with the product installation. Now, Kiran is worried about finding a solution before the anniversary.',
                'Sanjay ordered a electric grill for an upcoming Diwali celebration. However, after receiving the product, they discovered that the product is out of stock after placing the order. Now, Sanjay is worried about finding a solution before the Diwali celebration.']}
        
        df = pd.DataFrame(data)
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        stream.seek(0)
        response = StreamingResponse(iter([stream.getvalue()]),
                                     media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=sample.csv"

        return response
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Error retrieving model cards: {str(e)}"})

@app.post("/get_documents/") 
async def get_data(document_id: str = Form(...), output_format: str = Form(...)):
    try:
        query = {"document_id": document_id}
        projection = {"_id": 0, "document_id": 0, "user_id": 0}
        results = mongo_db.find_with_projection("SDG_synthetic_data", query, projection)
        all_messages = list(results)
        df = pd.DataFrame(all_messages)
        
        if output_format.lower() == "csv":
            stream = io.StringIO()
            df.to_csv(stream, index=False)
            stream.seek(0)
            response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
            response.headers["Content-Disposition"] = "attachment; filename=export.csv"
        
        elif output_format.lower() == "excel":
            stream = io.BytesIO()
            with pd.ExcelWriter(stream, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')
            stream.seek(0)
            response = StreamingResponse(iter([stream.getvalue()]), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response.headers["Content-Disposition"] = "attachment; filename=export.xlsx"

        return response

    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Error retrieving documents: {str(e)}"})