import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_JS = ROOT / "site" / "assets" / "data.js"

def build_with_photos():
    content = OUT_JS.read_text(encoding='utf-8')
    json_str = content.replace('window.CLASS_ARCHIVE = ', '').strip().rstrip(';')
    old_data = json.loads(json_str)
    
    photos_map = {
        0: ["21语文教育F军训.webp", "F班团建.webp", "F班团建做饺子.webp"],
        1: ["诗歌朗诵合影 (2).webp", "思政课合影.webp", "诗歌朗诵合影.webp"],
        4: ["2025-05-08_毕业全班正装_C25A0419.webp", "文学院大合影.webp", "微格小组合影.webp", "大一英语课大合影.webp", "F班团日活动.webp", "班主任版F班团建.webp"]
    }
    
    for vol_idx, photo_files in photos_map.items():
        if vol_idx < len(old_data['chronicle']):
            # 修正：每次重新初始化，避免重复
            old_data['chronicle'][vol_idx]['photos'] = []
            for p in photo_files:
                old_data['chronicle'][vol_idx]['photos'].append({"src": f"assets/photos/{p}", "caption": p.replace(".webp", "")})
    
    with open(OUT_JS, 'w', encoding='utf-8') as f:
        f.write('window.CLASS_ARCHIVE = ' + json.dumps(old_data, ensure_ascii=False) + ';')

if __name__ == "__main__":
    build_with_photos()
