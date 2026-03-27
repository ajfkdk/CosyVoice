"""
16宫格图片裁剪工具
支持智能检测分隔线和等分裁剪两种模式
"""
import os
from PIL import Image
import numpy as np


def detect_dark_lines(img_array, axis=0, threshold=50, min_line_width=2):
    """
    检测深色分隔线（黑色或深灰色）
    :param img_array: 图像数组
    :param axis: 0=检测水平线, 1=检测垂直线
    :param threshold: 深色阈值（RGB平均值小于此值视为深色）
    :param min_line_width: 最小线宽
    :return: 分隔线位置列表
    """
    # 沿指定轴计算平均亮度
    if axis == 0:  # 水平线，按行求平均
        brightness = img_array.mean(axis=(1, 2))
    else:  # 垂直线，按列求平均
        brightness = img_array.mean(axis=(0, 2))

    # 找出亮度低于阈值的位置
    dark_positions = np.where(brightness < threshold)[0]

    if len(dark_positions) == 0:
        return []

    # 合并连续的深色区域，取中心位置
    lines = []
    start = dark_positions[0]
    for i in range(1, len(dark_positions)):
        if dark_positions[i] - dark_positions[i-1] > 1:
            # 区域结束
            end = dark_positions[i-1]
            if end - start >= min_line_width:
                lines.append((start + end) // 2)
            start = dark_positions[i]

    # 处理最后一个区域
    end = dark_positions[-1]
    if end - start >= min_line_width:
        lines.append((start + end) // 2)

    return lines


def smart_split_grid(img_path, output_dir, rows=4, cols=4):
    """
    智能裁剪16宫格（优先检测分隔线，失败则等分）
    :param img_path: 输入图片路径
    :param output_dir: 输出目录
    :param rows: 行数
    :param cols: 列数
    :return: 裁剪后的文件路径列表
    """
    img = Image.open(img_path)
    img_array = np.array(img)
    h, w = img_array.shape[:2]

    print(f"   图片尺寸: {w}x{h}")

    # 尝试智能检测分隔线
    h_lines = detect_dark_lines(img_array, axis=0)  # 水平线
    v_lines = detect_dark_lines(img_array, axis=1)  # 垂直线

    print(f"   检测到 {len(h_lines)} 条水平线, {len(v_lines)} 条垂直线")

    # 判断是否检测成功（应该有3条水平线和3条垂直线）
    if len(h_lines) == rows - 1 and len(v_lines) == cols - 1:
        print("   ✅ 使用智能检测模式")
        return _split_by_lines(img, h_lines, v_lines, output_dir, rows, cols)
    else:
        print("   ⚠️ 分隔线检测失败，切换到等分模式")
        return _split_evenly(img, output_dir, rows, cols)


def _split_by_lines(img, h_lines, v_lines, output_dir, rows, cols):
    """按检测到的分隔线裁剪"""
    os.makedirs(output_dir, exist_ok=True)
    w, h = img.size

    # 构建切割点（加上边界）
    y_cuts = [0] + h_lines + [h]
    x_cuts = [0] + v_lines + [w]

    results = []
    idx = 1
    for i in range(rows):
        for j in range(cols):
            box = (x_cuts[j], y_cuts[i], x_cuts[j+1], y_cuts[i+1])
            cell = img.crop(box)
            out_path = os.path.join(output_dir, f"scene_{idx:02d}.png")
            cell.save(out_path)
            results.append(out_path)
            idx += 1

    return results


def _split_evenly(img, output_dir, rows, cols):
    """等分裁剪"""
    os.makedirs(output_dir, exist_ok=True)
    w, h = img.size
    cell_w = w // cols
    cell_h = h // rows

    results = []
    idx = 1
    for i in range(rows):
        for j in range(cols):
            box = (j * cell_w, i * cell_h, (j+1) * cell_w, (i+1) * cell_h)
            cell = img.crop(box)
            out_path = os.path.join(output_dir, f"scene_{idx:02d}.png")
            cell.save(out_path)
            results.append(out_path)
            idx += 1

    return results
