from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import shutil
import uvicorn
import os

app = FastAPI()

# モックされたステータスと結果のデータベース
status_db = {}
results_db = {}

# 画像保存用のディレクトリ
UPLOAD_DIR = "files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/upload")
async def upload_image(file: UploadFile = File(...), execution_id: str = Form(...)):
    file_location = f"{UPLOAD_DIR}/{execution_id}_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 初期ステータス設定
    status_db[execution_id] = {"algorithm_a": "pending", "algorithm_b": "pending", "algorithm_c": "pending"}

    # アルゴリズムAを適用
    status_db[execution_id]["algorithm_a"] = "in-progress"
    # モック処理
    a_image_url = f"{UPLOAD_DIR}/{execution_id}_A_{file.filename}"
    shutil.copy(file_location, a_image_url)
    status_db[execution_id]["algorithm_a"] = "completed"

    # アルゴリズムBを適用
    status_db[execution_id]["algorithm_b"] = "in-progress"
    # モック処理
    b_image_url = f"{UPLOAD_DIR}/{execution_id}_B_{file.filename}"
    shutil.copy(file_location, b_image_url)
    status_db[execution_id]["algorithm_b"] = "completed"

    # アルゴリズムCを適用
    status_db[execution_id]["algorithm_c"] = "in-progress"
    # モック処理
    c_image_url = f"{UPLOAD_DIR}/{execution_id}_C_{file.filename}"
    shutil.copy(file_location, c_image_url)
    status_db[execution_id]["algorithm_c"] = "completed"

    # 結果の保存
    results_db[execution_id] = {
        "A_image_url": a_image_url,
        "B_image_url": b_image_url,
        "C_image_url": c_image_url
    }

    return JSONResponse(content={"message": "Image uploaded and processed successfully", "status": "completed"})

@app.get("/status")
async def get_status(execution_id: str):
    status = status_db.get(execution_id, None)
    if status is None:
        return JSONResponse(content={"error": "Execution ID not found"}, status_code=404)
    return JSONResponse(content=status)

@app.get("/results")
async def get_results(execution_id: str):
    results = results_db.get(execution_id, None)
    if results is None:
        return JSONResponse(content={"error": "Execution ID not found"}, status_code=404)
    return JSONResponse(content=results)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug", reload=True)
