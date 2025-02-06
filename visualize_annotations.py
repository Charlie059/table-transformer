import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import os

def visualize_single_type(img, objects, obj_type, color, alpha, output_path):
    plt.figure(figsize=(20, 15))
    plt.imshow(img)
    plt.title(f"Table {obj_type}", pad=20, fontsize=14)
    
    for obj in objects:
        if obj.find('name').text == obj_type:
            bbox = obj.find('bndbox')
            xmin = float(bbox.find('xmin').text)
            ymin = float(bbox.find('ymin').text)
            xmax = float(bbox.find('xmax').text)
            ymax = float(bbox.find('ymax').text)
            
            # 填充
            rect = patches.Rectangle(
                (xmin, ymin), 
                xmax - xmin, 
                ymax - ymin, 
                linewidth=0,
                facecolor=color,
                alpha=alpha
            )
            plt.gca().add_patch(rect)
            # 边框
            rect = patches.Rectangle(
                (xmin, ymin), 
                xmax - xmin, 
                ymax - ymin, 
                linewidth=2,
                edgecolor=color,
                facecolor='none',
                alpha=1.0
            )
            plt.gca().add_patch(rect)
    
    plt.axis('off')
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()

def visualize_table_annotations(image_path, xml_path, output_dir):
    # 读取图片
    img = Image.open(image_path)
    
    # 读取XML标注
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # 定义每种类型的颜色
    type_colors = {
        'table': ('red', 0.2),
        'table row': ('blue', 0.2),
        'table column': ('lime', 0.2),
        'table column header': ('purple', 0.3),
        'table spanning cell': ('orange', 0.3)
    }
    
    # 为每种类型生成单独的图
    for obj_type, (color, alpha) in type_colors.items():
        output_path = os.path.join(output_dir, f"table_{obj_type.replace(' ', '_')}.png")
        visualize_single_type(img, root.findall('object'), obj_type, color, alpha, output_path)
        print(f"Saved {obj_type} visualization to {output_path}")
    
    # 生成一个包含所有类型的图
    plt.figure(figsize=(20, 15))
    plt.imshow(img)
    plt.title("All Table Components", pad=20, fontsize=14)
    
    for obj in root.findall('object'):
        name = obj.find('name').text
        if name in type_colors:
            bbox = obj.find('bndbox')
            xmin = float(bbox.find('xmin').text)
            ymin = float(bbox.find('ymin').text)
            xmax = float(bbox.find('xmax').text)
            ymax = float(bbox.find('ymax').text)
            
            color, alpha = type_colors[name]
            # 填充
            rect = patches.Rectangle(
                (xmin, ymin), 
                xmax - xmin, 
                ymax - ymin, 
                linewidth=0,
                facecolor=color,
                alpha=alpha
            )
            plt.gca().add_patch(rect)
            # 边框
            rect = patches.Rectangle(
                (xmin, ymin), 
                xmax - xmin, 
                ymax - ymin, 
                linewidth=2,
                edgecolor=color,
                facecolor='none',
                alpha=1.0
            )
            plt.gca().add_patch(rect)
    
    # 添加图例
    legend_elements = [patches.Patch(facecolor=color, edgecolor=color,
                                   linewidth=2, alpha=alpha, label=name)
                      for name, (color, alpha) in type_colors.items()]
    plt.legend(handles=legend_elements, loc='upper center',
              bbox_to_anchor=(0.5, -0.05), ncol=3, fontsize=12)
    
    plt.axis('off')
    all_components_path = os.path.join(output_dir, "table_all_components.png")
    plt.savefig(all_components_path, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Saved combined visualization to {all_components_path}")

if __name__ == "__main__":
    base_dir = "/mnt/c/Users/XG/Documents/GitHub/table-transformer"
    image_path = os.path.join(base_dir, "PubTables-1M-Structure_Images_Val", "PMC493285_table_0.jpg")
    xml_path = os.path.join(base_dir, "converted_annotations", "table_0.xml")
    output_dir = os.path.join(base_dir, "visualizations")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成可视化
    visualize_table_annotations(image_path, xml_path, output_dir) 