import json
from pathlib import Path

# 读取现有的 data.js
data_file = Path("site/assets/data.js")
json_str = data_file.read_text(encoding='utf-8').replace('window.CLASS_ARCHIVE = ', '').strip().rstrip(';')
data = json.loads(json_str)

# 增强图片节点结构，注入 anchor_id
for vol in data['chronicle']:
    if 'photos' in vol:
        for i, p in enumerate(vol['photos']):
            # 简单注入锚点 ID
            p['anchor_id'] = f"vol-{vol.get('label', 'x')[:1]}-photo-{i}"
            # 标记是否为高清图（根据分辨率逻辑判断，这里简化处理，先全部注入 anchor）
            p['type'] = 'anchor'

# 写回
with open(data_file, 'w', encoding='utf-8') as f:
    f.write("window.CLASS_ARCHIVE = " + json.dumps(data, ensure_ascii=False, indent=2) + ";")
print("Data updated with anchor_ids.")
