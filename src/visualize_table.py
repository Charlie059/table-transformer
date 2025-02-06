import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import os

def visualize_table_structure(json_file, img_file=None):
    # 读取JSON文件
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # 创建图形
    fig, ax = plt.subplots(1, figsize=(15, 10))
    
    # 设置颜色映射
    color_map = {
        'table spanning cell': 'lightblue',
        'table column header': 'lightgreen',
        'table projected row header': 'lightcoral',
        'table row': 'white',
        'table': 'none'
    }
    
    # 如果提供了图片文件，显示原始图片
    if img_file and os.path.exists(img_file):
        img = Image.open(img_file)
        ax.imshow(img)
    else:
        print(f"Warning: Image file not found at {img_file}")
    
    # 在图片上叠加表格结构
    # 绘制每个元素
    for obj in data:
        bbox = obj['bbox']
        label = obj['label']
        
        # 计算矩形参数
        x = bbox[0]
        y = bbox[1]
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        
        # 创建矩形
        rect = patches.Rectangle(
            (x, y), width, height,
            linewidth=2,
            edgecolor=color_map.get(label, 'white'),
            facecolor=color_map.get(label, 'white'),
            alpha=0.3
        )
        
        # 添加矩形到图形
        ax.add_patch(rect)
        
        # 对于合并单元格，添加行列信息标注
        if label == 'table spanning cell' and 'row_numbers' in obj and 'column_numbers' in obj:
            cell_info = f"R{obj['row_numbers']}\nC{obj['column_numbers']}"
            ax.text(x + width/2, y + height/2, cell_info,
                   horizontalalignment='center',
                   verticalalignment='center',
                   fontsize=8,
                   bbox=dict(facecolor='white', alpha=0.7))
    
    # 设置坐标轴
    ax.set_xlim(min(obj['bbox'][0] for obj in data) - 10,
                max(obj['bbox'][2] for obj in data) + 10)
    ax.set_ylim(min(obj['bbox'][1] for obj in data) - 10,
                max(obj['bbox'][3] for obj in data) + 10)
    
    # 反转Y轴（因为PDF坐标系统从底部开始）
    ax.invert_yaxis()
    
    # 添加图例
    legend_elements = [patches.Patch(facecolor=color, alpha=0.3, label=label)
                      for label, color in color_map.items()]
    ax.legend(handles=legend_elements, loc='upper right')
    
    ax.set_title('Table Structure Visualization')
    
    # 去除坐标轴
    ax.axis('off')
    
    # 调整布局
    plt.tight_layout()
    
    # 显示图形
    plt.show()

if __name__ == "__main__":
    json_file = 'results/srS4l_0_objects.json'
    img_file = 'test_images/srS4l.jpg'
    visualize_table_structure(json_file, img_file) 