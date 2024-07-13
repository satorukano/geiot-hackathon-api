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

# curl -X POST http://localhost:8000/upload -F "file=@path/to/your/image.jpg" -F "executi^C_id=your_execution_id"
# 上、file ... の後ろは画像ファイルへのパス
@app.post("/upload")
async def upload_image(file: UploadFile = File(...), execution_id: str = Form(...)):
    is_processing = True
    # ファイルの取得
    image_file = file
    id = execution_id
    # 画像処理
    results = process_image(image_file)
    is_processing = False

# http://localhost:8000/status?execution_id=1234
# 上の?以降がクエリパラメータでつけなとだめ
@app.get("/status")
async def get_status(execution_id: str):
    return JSONResponse(content=is_processing)

@app.get("/results")
async def get_results(execution_id: str):
    if not is_processing:
        if results:
            return JSONResponse(content=results)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug", reload=True)
