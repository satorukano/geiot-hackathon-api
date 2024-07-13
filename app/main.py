from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import shutil
import uvicorn
import os

app = FastAPI()

# mocの関数
def process_image(image):
    #　適当な画像
    return image

# 処理状態
is_processing = True
# 入力データ
image_file = None
id = None
# 処理結果
results = None

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/upload")
async def upload_image(file: UploadFile = File(...), execution_id: str = Form(...)):
    is_processing = True
    # ファイルの取得
    image_file = file
    id = execution_id
    # 画像処理
    results = process_image(image_file)
    is_processing = False
    
@app.get("/status")
async def get_status(execution_id: str):
    status = is_processing
    if status is None:
        return JSONResponse(content={"error": "Execution ID not found"}, status_code=404)
    return JSONResponse(content=status)

@app.get("/results")
async def get_results(execution_id: str):
    if not is_processing:
        if results is None:
            return JSONResponse(content={"error": "Execution ID not found"}, status_code=404)
        return JSONResponse(content=results)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug", reload=True)
