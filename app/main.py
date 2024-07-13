from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from io import BytesIO
import base64
import logging
import color_blindness_simulation as cbs
import color_blindness_correction as cbc
import saliency_map_generation as smg
from PIL import Image

# ロガーを設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,   # 追記により追加
    allow_methods=["*"],      # 追記により追加
    allow_headers=["*"]       # 追記により追加
)

# モックの関数
def process_image(image):
    logger.debug("Processing image")

    # バイナリデータをPIL.Imageオブジェクトに変換
    image_pil = Image.open(BytesIO(image))

    # 色覚特性シミュレーション画像を生成
    blindness_image = cbs.create_blindness_image(image_pil, color_blindness_type='deuteranopia')

    # 色相調整画像を生成
    adjusted_image = cbc.adjust_hue_for_colorblind(image_pil, 45)

    # 注視マップ画像を生成
    saliency_map_image = smg.generate_saliency_maps(image_pil)

    return [blindness_image, adjusted_image, saliency_map_image]


# 処理状態と結果を格納する辞書
execution_status = {}
execution_results = {}

@app.get("/")
async def root():
    logger.debug("Root endpoint called")
    return {"message": "Hello World"}

@app.post("/upload")
async def upload_image(file: UploadFile = File(...), execution_id: str = Form(...)):
    logger.debug(f"Upload endpoint called with execution_id: {execution_id}")
    # ファイルの取得
    image_data = await file.read()
    logger.debug(f"File received with size: {len(image_data)} bytes")
    # 処理状態を更新
    execution_status[execution_id] = "processing"

    try:
        # 画像処理
        processed_images = process_image(image_data)
        encoded_images = [base64.b64encode(img).decode('utf-8') for img in processed_images]
        execution_results[execution_id] = encoded_images
        # 処理状態を更新
        execution_status[execution_id] = "completed"
        logger.debug(f"Processing completed for execution_id: {execution_id}")
    except Exception as e:
        execution_status[execution_id] = "failed"
        logger.error(f"Processing failed for execution_id: {execution_id}, error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse(content={"message": f"Image uploaded and processing started for execution_id: {execution_id}"})

@app.get("/status")
async def get_status(execution_id: str):
    logger.debug(f"Querying status for execution_id: {execution_id}")
    status = execution_status.get(execution_id)
    if status is None:
        logger.debug(f"Execution ID {execution_id} not found")
        return JSONResponse(content={"error": "Execution ID not found"}, status_code=404)
    return JSONResponse(content={"status": status})

@app.get("/results")
async def get_results(execution_id: str):
    logger.debug(f"Querying results for execution_id: {execution_id}")
    if execution_status.get(execution_id) != "completed":
        logger.debug(f"Processing not completed or execution ID {execution_id} not found")
        return JSONResponse(content={"error": "Processing not completed or execution ID not found"}, status_code=404)

    results = execution_results.get(execution_id)
    if results is None:
        logger.debug(f"Results not found for execution_id: {execution_id}")
        return JSONResponse(content={"error": "Results not found"}, status_code=404)
    return JSONResponse(content={"results": results})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug", reload=True)
