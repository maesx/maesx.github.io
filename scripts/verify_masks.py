#!/usr/bin/env python3
"""
验证和修复mask文件
检查所有mask文件是否可读,并移除损坏的文件
"""
import os
import cv2
from pathlib import Path
from tqdm import tqdm

def verify_masks(masks_dir):
    """验证mask文件完整性"""
    masks_path = Path(masks_dir)
    splits = ['train', 'val', 'test']
    
    total_files = 0
    corrupted_files = []
    
    for split in splits:
        split_dir = masks_path / split
        if not split_dir.exists():
            print(f"跳过不存在的目录: {split_dir}")
            continue
        
        print(f"\n检查 {split} 数据集...")
        mask_files = list(split_dir.glob('*.png'))
        
        for mask_file in tqdm(mask_files, desc=f"检查{split}"):
            total_files += 1
            try:
                mask = cv2.imread(str(mask_file), cv2.IMREAD_GRAYSCALE)
                if mask is None:
                    corrupted_files.append(mask_file)
                    print(f"  ✗ 无法读取: {mask_file.name}")
            except Exception as e:
                corrupted_files.append(mask_file)
                print(f"  ✗ 读取错误: {mask_file.name} - {e}")
    
    print(f"\n{'='*60}")
    print(f"检查完成!")
    print(f"总文件数: {total_files}")
    print(f"损坏文件数: {len(corrupted_files)}")
    
    if corrupted_files:
        print(f"\n损坏的文件列表:")
        for f in corrupted_files:
            print(f"  - {f}")
        
        # 询问是否删除
        response = input(f"\n是否删除这 {len(corrupted_files)} 个损坏的文件? (yes/no): ")
        if response.lower() == 'yes':
            for f in corrupted_files:
                try:
                    os.remove(f)
                    print(f"  ✓ 已删除: {f.name}")
                except Exception as e:
                    print(f"  ✗ 删除失败: {f.name} - {e}")
            print(f"\n删除完成!")
        else:
            print("取消删除操作")
    else:
        print("所有文件完整!")
    
    return corrupted_files

def check_image_mask_pairs(data_dir, masks_dir):
    """检查图像和mask是否一一对应"""
    images_path = Path(data_dir) / 'images'
    masks_path = Path(masks_dir)
    splits = ['train', 'val', 'test']
    
    missing_masks = []
    missing_images = []
    
    for split in splits:
        img_dir = images_path / split
        mask_dir = masks_path / split
        
        if not img_dir.exists() or not mask_dir.exists():
            continue
        
        print(f"\n检查 {split} 数据集的图像-mask配对...")
        
        # 检查图像
        img_files = list(img_dir.glob('*.jpg')) + list(img_dir.glob('*.png'))
        for img_file in tqdm(img_files, desc="检查图像"):
            mask_file = mask_dir / (img_file.stem + '.png')
            if not mask_file.exists():
                missing_masks.append((img_file, mask_file))
        
        # 检查mask
        mask_files = list(mask_dir.glob('*.png'))
        for mask_file in tqdm(mask_files, desc="检查mask"):
            img_file_jpg = img_dir / (mask_file.stem + '.jpg')
            img_file_png = img_dir / (mask_file.stem + '.png')
            if not img_file_jpg.exists() and not img_file_png.exists():
                missing_images.append((mask_file, img_file_jpg))
    
    print(f"\n{'='*60}")
    print(f"配对检查完成!")
    print(f"缺失mask的图像: {len(missing_masks)}")
    print(f"缺失图像的mask: {len(missing_images)}")
    
    if missing_masks:
        print(f"\n缺失mask的图像 (前10个):")
        for img_file, mask_file in missing_masks[:10]:
            print(f"  图像: {img_file.name} -> 缺失mask: {mask_file.name}")
    
    if missing_images:
        print(f"\n缺失图像的mask (前10个):")
        for mask_file, img_file in missing_images[:10]:
            print(f"  mask: {mask_file.name} -> 缺失图像: {img_file.name}")
    
    return missing_masks, missing_images

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='验证和修复mask文件')
    parser.add_argument('--data_dir', type=str, default='road_vehicle_pedestrian_det_datasets',
                        help='数据集根目录')
    parser.add_argument('--masks_dir', type=str, default='outputs/masks_car',
                        help='mask文件目录')
    parser.add_argument('--check_pairs', action='store_true',
                        help='检查图像和mask是否配对')
    
    args = parser.parse_args()
    
    print("="*60)
    print("Mask文件验证工具")
    print("="*60)
    
    # 验证mask文件
    corrupted = verify_masks(args.masks_dir)
    
    # 检查图像-mask配对
    if args.check_pairs:
        check_image_mask_pairs(args.data_dir, args.masks_dir)
