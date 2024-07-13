from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import shutil
import uvicorn
import os

#############################################################
## DB コード
#############################################################
import sqlite3
import pickle

# SQLiteのインメモリデータベースに接続
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# 状態とPythonオブジェクトを管理するテーブルを作成
cursor.execute('''
CREATE TABLE execution_state (
    id INTEGER PRIMARY KEY,
    is_running BOOLEAN,
    obj1 BLOB,
    obj2 BLOB
)
''')

# 初期状態を挿入する関数
def insert_initial_state(id, is_running, obj1, obj2):
    obj1_blob = pickle.dumps(obj1)
    obj2_blob = pickle.dumps(obj2)
    cursor.execute('INSERT INTO execution_state (id, is_running, obj1, obj2) VALUES (?, ?, ?, ?)', 
                   (id, is_running, obj1_blob, obj2_blob))
    conn.commit()

# 実行状態を設定する関数
def set_execution_state(id, state):
    cursor.execute('UPDATE execution_state SET is_running = ? WHERE id = ?', (state, id))
    conn.commit()

# 実行状態を取得する関数
def get_execution_state(id):
    cursor.execute('SELECT is_running FROM execution_state WHERE id = ?', (id,))
    state = cursor.fetchone()[0]
    return bool(state)

# Pythonオブジェクト1を取得する関数
def get_object1(id):
    cursor.execute('SELECT obj1 FROM execution_state WHERE id = ?', (id,))
    obj1_blob = cursor.fetchone()[0]
    return pickle.loads(obj1_blob)

# Pythonオブジェクト2を取得する関数
def get_object2(id):
    cursor.execute('SELECT obj2 FROM execution_state WHERE id = ?', (id,))
    obj2_blob = cursor.fetchone()[0]
    return pickle.loads(obj2_blob)

# Pythonオブジェクト1を更新する関数
def update_object1(id, obj1):
    obj1_blob = pickle.dumps(obj1)
    cursor.execute('UPDATE execution_state SET obj1 = ? WHERE id = ?', (obj1_blob, id))
    conn.commit()

# Pythonオブジェクト2を更新する関数
def update_object2(id, obj2):
    obj2_blob = pickle.dumps(obj2)
    cursor.execute('UPDATE execution_state SET obj2 = ? WHERE id = ?', (obj2_blob, id))
    conn.commit()
############################################################

app = FastAPI()

# mocの関数
def process_image(image):
    #　適当な画像
    return image

@app.get("/")
async def root():
    return {"message": "Hello World"}

# curl -X POST http://localhost:8000/upload -F "file=@path/to/your/image.jpg" -F "executi^C_id=your_execution_id"
# 上、file ... の後ろは画像ファイルへのパス
@app.post("/upload")
async def upload_image(file: UploadFile = File(...), execution_id: str = Form(...)):
    # 初期データを挿入
    insert_initial_state(execution_id, True, file, None)
    # 画像処理
    update_object2(execution_id, process_image(get_object1))
    set_execution_state(execution_id ,False)

# http://localhost:8000/status?execution_id=1234
# 上の?以降がクエリパラメータでつけなとだめ
@app.get("/status")
async def get_status(execution_id: str):
    return JSONResponse(content=get_execution_state(execution_id))

@app.get("/results")
async def get_results(execution_id: str):
    return JSONResponse(content=get_object2(execution_id))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug", reload=True)
