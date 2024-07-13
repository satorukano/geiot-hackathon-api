from PIL import Image

def adjust_hue_for_colorblind(image_path, angle):
    image = Image.open(image_path)
    
    # 色相を調整
    image = image.convert('HSV')
    data = image.getdata()
    new_data = []
    for item in data:
        h, s, v = item
        new_h = (h + angle) % 256  # 色相を調整
        new_data.append((new_h, s, v))
    
    image.putdata(new_data)
    image = image.convert('RGB')
    
    return image

# 使用例
adjusted_image = adjust_hue_for_colorblind("sample.png", 45)  # 色相を45度回転
adjusted_image.save("output_image.png", "PNG")  # 変換後の画像をPNG形式で保存
