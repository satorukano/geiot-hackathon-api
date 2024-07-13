from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()


# モックの関数
def process_image(image):
    # モックの画像処理関数（適当な処理を行う）
    return {"processed_image": "data"}


# 処理状態と結果を格納する辞書
execution_status = {}
execution_results = {}


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/upload")
async def upload_image(file: UploadFile = File(...), execution_id: str = Form(...)):
    # ファイルの取得
    image_data = await file.read()
    # 処理状態を更新
    execution_status[execution_id] = "processing"

    try:
        # 画像処理
        results = process_image(image_data)
        execution_results[execution_id] = results
        # 処理状態を更新
        execution_status[execution_id] = "completed"
    except Exception as e:
        execution_status[execution_id] = "failed"
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse(content={"message": f"Image uploaded and processing started for execution_id: {execution_id}"})


@app.get("/status")
async def get_status(execution_id: str):
    print(f"Querying status for execution_id: {execution_id}")
    status = execution_status.get(execution_id)
    if status is None:
        return JSONResponse(content={"error": "Execution ID not found"}, status_code=404)
    return JSONResponse(content={"status": status})


@app.get("/results")
async def get_results(execution_id: str):
    print(f"Querying results for execution_id: {execution_id}")
    if execution_status.get(execution_id) != "completed":
        return JSONResponse(content={"error": "Processing not completed or execution ID not found"}, status_code=404)

    results = execution_results.get(execution_id)
    if results is None:
        return JSONResponse(content={"error": "Results not found"}, status_code=404)
    return JSONResponse(content=results)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug", reload=True)
