import os
from PIL import Image

def convert_images_to_rgb(input_dir, output_dir):
    """
    将输入目录中的所有图片转换为RGB格式并保存到输出目录
    """
    # 获取绝对路径
    input_dir = os.path.abspath(input_dir)
    output_dir = os.path.abspath(output_dir)
    
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 检查输入目录是否存在
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    
    # 遍历输入目录中的所有文件
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + '.jpg')
            
            try:
                # 打开图片并转换为RGB
                with Image.open(input_path) as img:
                    # 转换为RGB模式
                    rgb_img = img.convert('RGB')
                    # 保存为JPG格式
                    rgb_img.save(output_path, 'JPEG')
                print(f"Converted {filename} -> {os.path.basename(output_path)}")
            except Exception as e:
                print(f"Error converting {filename}: {str(e)}")

if __name__ == "__main__":
    # 使用Windows路径
    input_dir = "/mnt/c/Users/XG/Documents/GitHub/table-transformer/test_images"
    output_dir = "/mnt/c/Users/XG/Documents/GitHub/table-transformer/test_images_rgb"
    
    # 转换图片
    convert_images_to_rgb(input_dir, output_dir)
    print("\nConversion complete!") 