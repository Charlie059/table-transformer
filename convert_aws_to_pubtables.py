import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
from PIL import Image

def create_xml_object(name, bbox):
    """创建一个XML对象元素"""
    obj = ET.Element('object')
    
    name_elem = ET.SubElement(obj, 'name')
    name_elem.text = name
    
    pose = ET.SubElement(obj, 'pose')
    pose.text = 'Frontal'
    
    truncated = ET.SubElement(obj, 'truncated')
    truncated.text = '0'
    
    difficult = ET.SubElement(obj, 'difficult')
    difficult.text = '0'
    
    occluded = ET.SubElement(obj, 'occluded')
    occluded.text = '0'
    
    bndbox = ET.SubElement(obj, 'bndbox')
    xmin = ET.SubElement(bndbox, 'xmin')
    ymin = ET.SubElement(bndbox, 'ymin')
    xmax = ET.SubElement(bndbox, 'xmax')
    ymax = ET.SubElement(bndbox, 'ymax')
    
    xmin.text = f"{bbox['xmin']:.4f}"
    ymin.text = f"{bbox['ymin']:.4f}"
    xmax.text = f"{bbox['xmax']:.4f}"
    ymax.text = f"{bbox['ymax']:.4f}"
    
    return obj

def get_image_size(image_path):
    """获取图片实际尺寸"""
    with Image.open(image_path) as img:
        return img.size

def convert_bbox(aws_bbox, image_width, image_height):
    """将AWS的相对坐标转换为绝对像素坐标"""
    # AWS的坐标是相对的(0-1)，需要乘以图片尺寸
    # 注意：AWS使用左上角作为原点
    return {
        'xmin': aws_bbox['Left'] * image_width,
        'ymin': aws_bbox['Top'] * image_height,
        'xmax': (aws_bbox['Left'] + aws_bbox['Width']) * image_width,
        'ymax': (aws_bbox['Top'] + aws_bbox['Height']) * image_height
    }

def get_table_structure(blocks):
    """从AWS blocks中提取表格结构"""
    table_blocks = []
    cells = []
    rows = {}
    columns = {}
    headers = []
    spanning_cells = []
    
    # 找到表格块和MERGED_CELL
    for block in blocks:
        if block['BlockType'] == 'TABLE':
            table_blocks.append(block)
        elif block['BlockType'] in ['CELL', 'MERGED_CELL']:
            cells.append(block)
            
            # 收集行信息
            row_idx = block['RowIndex']
            if row_idx not in rows:
                rows[row_idx] = []
            rows[row_idx].append(block)
            
            # 收集列信息
            col_idx = block['ColumnIndex']
            if col_idx not in columns:
                columns[col_idx] = []
            columns[col_idx].append(block)
            
            # 识别表头
            if row_idx == 1:
                headers.append(block)
            
            # 识别跨单元格
            if block['BlockType'] == 'MERGED_CELL' or \
               block.get('RowSpan', 1) > 1 or block.get('ColumnSpan', 1) > 1:
                spanning_cells.append(block)
    
    return {
        'tables': table_blocks,
        'cells': cells,
        'rows': rows,
        'columns': columns,
        'headers': headers,
        'spanning_cells': spanning_cells
    }

def convert_aws_to_pubtables(aws_json, image_width, image_height, output_path):
    """将AWS Textract输出转换为PubTables-1M格式"""
    # 创建根元素
    root = ET.Element('annotation')
    
    # 添加基本信息
    folder = ET.SubElement(root, 'folder')
    filename = ET.SubElement(root, 'filename')
    filename.text = os.path.basename(output_path).replace('.xml', '.jpg')
    
    path = ET.SubElement(root, 'path')
    path.text = filename.text
    
    source = ET.SubElement(root, 'source')
    database = ET.SubElement(source, 'database')
    database.text = 'AWS-Textract-Converted'
    
    size = ET.SubElement(root, 'size')
    width = ET.SubElement(size, 'width')
    height = ET.SubElement(size, 'height')
    depth = ET.SubElement(size, 'depth')
    width.text = str(image_width)
    height.text = str(image_height)
    depth.text = '3'
    
    segmented = ET.SubElement(root, 'segmented')
    segmented.text = '0'
    
    # 提取表格结构
    structure = get_table_structure(aws_json['Blocks'])
    
    # 添加表格对象
    for table in structure['tables']:
        bbox = convert_bbox(table['Geometry']['BoundingBox'], image_width, image_height)
        obj = create_xml_object('table', bbox)
        root.append(obj)
    
    # 添加行对象
    for row_idx, row_cells in structure['rows'].items():
        # 计算行的边界框
        left = min(cell['Geometry']['BoundingBox']['Left'] for cell in row_cells)
        top = min(cell['Geometry']['BoundingBox']['Top'] for cell in row_cells)
        right = max(cell['Geometry']['BoundingBox']['Left'] + cell['Geometry']['BoundingBox']['Width'] 
                   for cell in row_cells)
        bottom = max(cell['Geometry']['BoundingBox']['Top'] + cell['Geometry']['BoundingBox']['Height'] 
                    for cell in row_cells)
        
        bbox = {
            'xmin': left * image_width,
            'ymin': top * image_height,
            'xmax': right * image_width,
            'ymax': bottom * image_height
        }
        obj = create_xml_object('table row', bbox)
        root.append(obj)
    
    # 添加列对象
    for col_idx, col_cells in structure['columns'].items():
        # 计算列的边界框
        left = min(cell['Geometry']['BoundingBox']['Left'] for cell in col_cells)
        top = min(cell['Geometry']['BoundingBox']['Top'] for cell in col_cells)
        right = max(cell['Geometry']['BoundingBox']['Left'] + cell['Geometry']['BoundingBox']['Width'] 
                   for cell in col_cells)
        bottom = max(cell['Geometry']['BoundingBox']['Top'] + cell['Geometry']['BoundingBox']['Height'] 
                    for cell in col_cells)
        
        bbox = {
            'xmin': left * image_width,
            'ymin': top * image_height,
            'xmax': right * image_width,
            'ymax': bottom * image_height
        }
        obj = create_xml_object('table column', bbox)
        root.append(obj)
    
    # 添加表头对象
    if structure['headers']:
        # 计算表头的边界框
        left = min(cell['Geometry']['BoundingBox']['Left'] for cell in structure['headers'])
        top = min(cell['Geometry']['BoundingBox']['Top'] for cell in structure['headers'])
        right = max(cell['Geometry']['BoundingBox']['Left'] + cell['Geometry']['BoundingBox']['Width'] 
                   for cell in structure['headers'])
        bottom = max(cell['Geometry']['BoundingBox']['Top'] + cell['Geometry']['BoundingBox']['Height'] 
                    for cell in structure['headers'])
        
        bbox = {
            'xmin': left * image_width,
            'ymin': top * image_height,
            'xmax': right * image_width,
            'ymax': bottom * image_height
        }
        obj = create_xml_object('table column header', bbox)
        root.append(obj)
    
    # 添加跨单元格对象
    for cell in structure['spanning_cells']:
        bbox = convert_bbox(cell['Geometry']['BoundingBox'], image_width, image_height)
        obj = create_xml_object('table spanning cell', bbox)
        root.append(obj)
    
    # 格式化XML并保存
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xmlstr)

if __name__ == "__main__":
    base_dir = "/mnt/c/Users/XG/Documents/GitHub/table-transformer"
    
    # 读取AWS Textract输出
    aws_json_path = os.path.join(base_dir, "analyzeDocResponse.json")
    with open(aws_json_path, 'r') as f:
        aws_json = json.load(f)
    
    # 获取原始图片尺寸
    image_path = os.path.join(base_dir, "test_images", "table_0.jpg")
    if os.path.exists(image_path):
        image_width, image_height = get_image_size(image_path)
        print(f"Using actual image size: {image_width}x{image_height}")
    else:
        print(f"Warning: Image not found at {image_path}")
        print("Using default size 1000x1000")
        image_width = image_height = 1000
    
    # 转换并保存
    output_path = os.path.join(base_dir, "converted_annotations", "table_0.xml")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    convert_aws_to_pubtables(aws_json, image_width, image_height, output_path)
    print(f"Converted annotation saved to {output_path}") 