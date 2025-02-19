import os
import tempfile
import cv2
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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def __saliency(src):
    saliency = cv2.saliency.StaticSaliencySpectralResidual_create()
    (success, saliemcy_map) = saliency.computeSaliency(src)
    if success is False:
        return (False, None)
    saliemcy_map = (saliemcy_map * 255).astype("uint8")
    heatmap = cv2.applyColorMap(saliemcy_map, cv2.COLORMAP_JET)
    # src1の重み0.7 src2の重み0.5 ガンマ1.0
    weight = cv2.addWeighted(src,0.7, heatmap ,0.5 ,1.0)
    return (success, weight)



def img_saliency(src_file = "sample.png", dst_file = "sample_output.png"):
    image = cv2.imread(src_file)
    (success, saliemcy_map) = __saliency(image)
    if success is True:
        cv2.imwrite(dst_file, saliemcy_map)

# バイナリデータをPNGファイルとして保存する関数
def binary_to_image_file(binary_data, output_file_path):
    with open(output_file_path, 'wb') as file:
        file.write(binary_data)
    im = Image.open(output_file_path)
    img_width, img_height = im.size
    im_crop = im.crop((0, 0, img_width, img_width))
    im_crop.save(output_file_path)

def read_file_as_binary(file_path):
    with open(file_path, 'rb') as file:
        return file.read()

# モックの関数
def process_image(image_path):
    logger.debug("Processing image")

    # 色覚特性シミュレーション画像を生成
    blindness_image_path = './app/image/blindness_image/output.png'
    cbs.create_blindness_image(image_path, color_blindness_type='deuteranopia', save_path=blindness_image_path)

    # 色相調整画像を生成
    adjusted_image_path = "./app/image/blindness_correct/output.png"
    adjusted_image = cbc.adjust_hue_for_colorblind(image_path, 45)
    adjusted_image.save(adjusted_image_path, "PNG")

    # サリエンシーマップ画像を生成
    saliency_map_image_path = "./app/image/saliency_map/saliency.png"
    saliency_map_image = smg.generate_saliency_maps_images(image_path)
    smg.save_image(saliency_map_image[1], saliency_map_image_path)

    saliency_map_blindness_image_path = "./app/image/saliency_map/blindness.png"
    saliency_map_blindness_image = smg.generate_saliency_maps_images(blindness_image_path)
    smg.save_image(saliency_map_blindness_image[1], saliency_map_blindness_image_path)

    saliency_map_adjusted_image_path = "./app/image/saliency_map/adjusted.png"
    saliency_map_adjusted_image = smg.generate_saliency_maps_images(adjusted_image_path)
    smg.save_image(saliency_map_adjusted_image[1], saliency_map_adjusted_image_path)

    return [
        read_file_as_binary(blindness_image_path),
        read_file_as_binary(adjusted_image_path),
        read_file_as_binary(saliency_map_image_path),
        read_file_as_binary(saliency_map_blindness_image_path),
        read_file_as_binary(saliency_map_adjusted_image_path)
    ]

# 処理状態と結果を格納する辞書
execution_status = {}
execution_results = {}

@app.get("/")
async def root():
    logger.debug("Root endpoint called")
    return {"message": "Hello World"}

# @app.post("/upload")
# async def upload_image(file: UploadFile = File(...), execution_id: str = Form(...)):
#     logger.debug(f"Upload endpoint called with execution_id: {execution_id}")
#     # ファイルの取得
#     image_data = await file.read()
#     logger.debug(f"File received with size: {len(image_data)} bytes")
#     # 処理状態を更新
#     execution_status[execution_id] = "processing"

#     try:
#         # バイナリデータをPNGファイルとして保存
#         input_image_path = f"/tmp/{execution_id}.png"
#         binary_to_image_file(image_data, input_image_path)
        
#         # 画像処理
#         processed_images = process_image(input_image_path)
        
#         # 画像をバイナリに変換してエンコード
#         encoded_images = [base64.b64encode(image).decode('utf-8') for image in processed_images]
        
#         execution_results[execution_id] = encoded_images
#         # 処理状態を更新
#         execution_status[execution_id] = "completed"
#         logger.debug(f"Processing completed for execution_id: {execution_id}")
#     except Exception as e:
#         execution_status[execution_id] = "failed"
#         logger.error(f"Processing failed for execution_id: {execution_id}, error: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

#     return JSONResponse(content={"message": f"Image uploaded and processing started for execution_id: {execution_id}"})

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

@app.post("/upload")
async def upload_image(file: UploadFile = File(...), execution_id: str = Form(...)):
    image_data = await file.read()

    # バイナリデータをPNGファイルとして保存
    input_image_path = f"./app/image/normal/input.png"
    binary_to_image_file(image_data, input_image_path)
    normal_saliency_path = './app/image/normal/saliency.png'
    img_saliency(input_image_path, normal_saliency_path)

    blindness_image_path = './app/image/blindness_image/output.png'
    # 色覚特性シミュレーション画像を生成
    cbs.create_blindness_image(input_image_path, color_blindness_type='protanopia', save_path=blindness_image_path)
    blindness_saliency_path = './app/image/blindness_image/saliency.png'
    img_saliency(blindness_image_path, blindness_saliency_path)

    # 色相調整画像を生成
    adjusted_image_path = "./app/image/blindness_correct/output.png"
    adjusted_image = cbc.adjust_hue_for_colorblind(input_image_path, 45)
    adjusted_image.save(adjusted_image_path, "PNG")
    adjusted_salency_path = './app/image/blindness_correct/saliency.png'
    img_saliency(adjusted_image_path, adjusted_salency_path)

    processed_images =  [
        read_file_as_binary(normal_saliency_path),
        read_file_as_binary(blindness_saliency_path),
        read_file_as_binary(adjusted_salency_path)
    ]

    encoded_images = [base64.b64encode(image).decode('utf-8') for image in processed_images]
        
    execution_results[execution_id] = encoded_images
        # 処理状態を更新
    execution_status[execution_id] = "completed"

    return JSONResponse(content={"message": f"Image uploaded and processing started for execution_id: {execution_id}"})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug", reload=True)
