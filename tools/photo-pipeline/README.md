# photo-pipeline

手机原图 → WebP 入库前的脱敏工具。`photo_sanitize.py` 是本目录唯一入口，其余是复盘记录。

## 用法

```powershell
# 处理：缩放 + 转 WebP + 清空 EXIF（含 GPS 与机型）
python photo_sanitize.py --src "D:\素材\班级活动原图" --dst "E:\启蒙_大学纪念站\site\assets\photos"

# 常用参数
--max-width 1200     最大宽度，只缩不放
--quality 82         WebP 质量
--recursive          递归子目录
--keep-icc           保留色彩配置文件（不影响定位隐私）
--skip-existing      只处理新增/改过的源图，可反复跑

# 只核验：不处理，检查目标目录里还有没有残留敏感字段
python photo_sanitize.py --src X --dst Y --verify
```

退出码：0 全部通过；1 核验发现残留；2 有源文件处理失败。

## 为什么不是"三行 Pillow"

| 坑 | 后果 | 处理 |
|---|---|---|
| 只剥 EXIF 不转置像素 | 手机竖拍照片横躺（EXIF Orientation=6 被删，像素没转） | 先 `ImageOps.exif_transpose()` 再 `resize()` |
| `save(exif=b"")` 当作万能 | 不同 Pillow 版本对 WebP 处理不一致，可能残留 | 不把 exif 传进 `save()`，再用 `--verify` 复核 |
| 在 PowerShell 里写含中文的 .py/.js | 默认非 UTF-8，SyntaxError 或全文件乱码 | 脚本存成 .py 文件，读写显式 `encoding='utf-8'` |
| 没指定 quality | WebP 默认 80，合照细节糊 | 显式 `quality=82`（可按需调到 88） |

## 实测记录（2026-11-20）

- 3000×4000、Orientation=6 的手机竖拍：未修正时输出 1200×1600（横躺），修正后 1200×900（正确）。
- 4000×3000 横拍：1200×900，EXIF 键为空，GPS IFD 为空。
- 800×600 小图：不放大，原尺寸输出。
- 混入一个非图片文件：不中断整批，报错后继续，退出码 2。
- 幂等：`--skip-existing` 二次运行，跳过 4 张、重复处理 0 张。
- `--verify`：4 张输出残留敏感字段 0 张。

## 不做什么

- 不做 AI 超分。240px 级别的微信缩略图没有高频信息，超分只会造幻觉纹理；这类图应走 CSS 滤镜 + 文本索引。
- 不直接改 `site/assets/data.js` 这类构建产物。照片挂载的映射必须写进上游 `build.py`，否则下次构建会把手工改动冲掉。
