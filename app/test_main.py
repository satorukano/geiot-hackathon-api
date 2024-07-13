import pytest
from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_upload_and_process_image():
    # テスト用の画像ファイルを作成
    with open("test_image.jpg", "wb") as f:
        f.write(os.urandom(1024))  # ランダムなバイトデータを書き込む

    execution_id = "test123"

    # 画像をアップロード
    with open("test_image.jpg", "rb") as f:
        response = client.post("/upload", files={"file": f}, data={"execution_id": execution_id})

    assert response.status_code == 200
    assert response.json()["message"] == f"Image uploaded and processing started for execution_id: {execution_id}"

    # ステータスを確認
    response = client.get(f"/status?execution_id={execution_id}")
    assert response.status_code == 200
    status = response.json()
    assert status["status"] in ["processing", "completed"]

    # 処理完了を待つ（本来は非同期で待つが、ここでは単純なsleepを使用）
    import time
    time.sleep(1)

    # 結果を確認
    response = client.get(f"/results?execution_id={execution_id}")
    assert response.status_code == 200
    results = response.json()
    assert "processed_image" in results

    # テスト画像ファイルを削除
    os.remove("test_image.jpg")


if __name__ == "__main__":
    pytest.main()
