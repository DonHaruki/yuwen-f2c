# 检查 data.js 内容：
# 打印所有 chronicle 对象中的 photos 字段。
import json
from pathlib import Path

# 修正：直接写入本地脚本，不再需要 justification 和 sandbox_permissions
data_file = Path("site/assets/data.js")
content = data_file.read_text(encoding='utf-8')
# 确保数据被正确读取
json_str = content.replace('window.CLASS_ARCHIVE = ', '').strip().rstrip(';')
data = json.loads(json_str)

# 打印所有 chronicle 卷的内容以便调试
for i, vol in enumerate(data['chronicle']):
    if 'photos' in vol:
        print(f"卷 {i} ({vol['label']}) 包含 {len(vol['photos'])} 张照片")
        # 顺便打印照片文件名验证是否正确写入
        for p in vol['photos']:
            print(f"  - {p['src']}")
    else:
        print(f"卷 {i} ({vol['label']}) 不包含 photos 字段")
