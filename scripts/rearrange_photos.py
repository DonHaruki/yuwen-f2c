import json
from pathlib import Path

# 1. 更新 build.py 中的 PHOTOS 定义，按班级归类
photos_config = [
    # F班照片
    {"file": "21语文教育F军训.webp", "caption": "F班军训", "theme": "F班影像"},
    {"file": "F班团建.webp", "caption": "F班团建", "theme": "F班影像"},
    {"file": "F班团建做饺子.webp", "caption": "F班包饺子", "theme": "F班影像"},
    {"file": "F班团日活动.webp", "caption": "F班团日活动", "theme": "F班影像"},
    {"file": "班主任版F班团建.webp", "caption": "班主任版F班团建", "theme": "F班影像"},
    # C班照片
    {"file": "大一英语课大合影.webp", "caption": "C班大一英语课合影", "theme": "C班影像"},
    {"file": "微格小组合影.webp", "caption": "C班微格教学合影", "theme": "C班影像"},
    {"file": "思政课合影.webp", "caption": "C班思政课合影", "theme": "C班影像"},
    {"file": "诗歌朗诵合影.webp", "caption": "C班诗歌朗诵合影", "theme": "C班影像"},
    {"file": "诗歌朗诵合影 (2).webp", "caption": "C班诗歌朗诵组队", "theme": "C班影像"},
    {"file": "文学院大合影.webp", "caption": "文学院大合影", "theme": "C班影像"},
    {"file": "2025-05-08_毕业全班正装_C25A0419.webp", "caption": "C班毕业合影", "theme": "C班影像"},
]

# 注入必要的结构元数据
for p in photos_config:
    p.update({
        "name": p["caption"],
        "src": f"assets/photos/{p['file']}",
        "id": p["file"].split('.')[0]
    })

# 更新 build.py 中的 PHOTOS 列表内容
# 这里的实现逻辑是：直接用这段代码替换 build.py 中现有的 PHOTOS 列表
# 然后在渲染时，让前端根据 theme 自动分组，或者在 build.py 预处理分组
