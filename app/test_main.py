import shutil

import pytest
from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    # テストの前に実行されるセットアップコード
    os.makedirs("files", exist_ok=True)
    yield
    # テストの後に実行されるクリーンアップコード
    shutil.rmtree("files")


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_upload_and_process_image():
    # アップロード用のテスト画像を作成
    with open("test_image.jpg", "wb") as f:
        f.write(os.urandom(1024))  # ランダムなバイトデータを書き込む

    # 画像をアップロード
    with open("test_image.jpg", "rb") as f:
        response = client.post("/upload", files={"file": f}, data={"execution_id": "test123"})

    assert response.status_code == 200
    assert response.json()["message"] == "Image uploaded and processed successfully"

    # ステータスを確認
    response = client.get("/status?execution_id=test123")
    assert response.status_code == 200
    status = response.json()
    assert status["algorithm_a"] == "completed"
    assert status["algorithm_b"] == "completed"
    assert status["algorithm_c"] == "completed"

    # 結果を確認
    response = client.get("/results?execution_id=test123")
    assert response.status_code == 200
    results = response.json()
    assert "A_image_url" in results
    assert "B_image_url" in results
    assert "C_image_url" in results

    # テスト画像ファイルを削除
    os.remove("test_image.jpg")


if __name__ == "__main__":
    pytest.main()
