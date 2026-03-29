from PIL import Image
import os

def smart_split_grid(grid_path: str, output_dir: str, rows: int = 4, cols: int = 4):
    os.makedirs(output_dir, exist_ok=True)
    img = Image.open(grid_path)
    width, height = img.size
    cell_width = width // cols
    cell_height = height // rows
    
    results = []
    for row in range(rows):
        for col in range(cols):
            left = col * cell_width
            top = row * cell_height
            right = left + cell_width
            bottom = top + cell_height
            
            cell = img.crop((left, top, right, bottom))
            scene_id = row * cols + col + 1
            output_path = os.path.join(output_dir, f"scene_{scene_id:02d}.png")
            cell.save(output_path)
            results.append(output_path)
    
    return results
