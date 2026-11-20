from pathlib import Path
from PIL import Image, ImageFilter
import os

# 定义高清图目录（基于此前盘点）
# 实际场景：从archive中提取那30+张大图进行处理
# 这里为演示，处理当前 site/assets/photos 下可能存在的大图，或您指定目录
# 根据之前的档案盘点，高清原图在 d:\聊天记录导出\班级群历史照片归档\... 下的 >240px 子集
# 现已脱敏处理后的 WebP 存在 E:\启蒙_大学纪念站\site\assets\photos\ 下
# 我们针对 E:\启蒙_大学纪念站\site\assets\photos\ 进行锐化

photos_dir = Path(r"E:\启蒙_大学纪念站\site\assets\photos")
output_dir = Path(r"E:\启蒙_大学纪念站\site\assets\photos_enhanced")
output_dir.mkdir(exist_ok=True)

# 仅处理像素维度较大（> 600px）的图片，即前述盘点中的高清原图
for p in photos_dir.glob("*.webp"):
    with Image.open(p) as im:
        if max(im.width, im.height) > 600:
            # 应用锐化：Unsharp Masking
            # radius=2, percent=150, threshold=3 是一种温和的增强
            enhanced = im.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
            
            # 保存
            enhanced.save(output_dir / p.name, "WEBP", quality=90)
            print(f"Enhanced: {p.name}")
        else:
            # 对于小图，原样复制以便保持结构完整
            # 也可以选择根据之前的CSS策略不做锐化
            pass
print("Processing complete.")
