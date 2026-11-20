# -*- coding: utf-8 -*-
"""photo_sanitize.py —— 批量压缩 / 转 WebP / 剥离 EXIF（手机原图入公开仓库前用）

为什么要有这个脚本（三条血泪教训，别删）：
1. 必须先做 EXIF 方向修正（ImageOps.exif_transpose）再缩放。手机竖拍的照片
   像素是横着存的、靠 EXIF Orientation=6 让看图软件转正；一旦剥掉 EXIF 而不
   转置像素，输出图会横躺着。原始脚本就栽在这，测试里 3000x4000 竖拍输出成
   1200x1600 横图。
2. 不能在 PowerShell 里用 Set-Content / 重定向写含中文的 .py 或 .js，默认编码
   会破坏 UTF-8，直接 SyntaxError 或乱码。脚本一律存成 .py 文件、读写都显式
   encoding='utf-8'。
3. 只传 exif=b"" 不够保险——不同 Pillow 版本对 WebP 的处理不一致；正确做法是
   不把 exif 传进 save()，并在 --verify 时用 getexif() 复核 GPS/Make/Model。

用法:
  python photo_sanitize.py --src "D:\\素材\\班级活动原图" --dst ".\\site\\assets\\photos"
  python photo_sanitize.py --src ... --dst ... --max-width 1600 --quality 85 --recursive
  python photo_sanitize.py --src ... --dst ... --verify      # 只核验已有输出
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:  # pragma: no cover
    sys.exit("需要 Pillow：pip install Pillow")

EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
SENSITIVE_TAGS = {0x010F: "Make", 0x0110: "Model", 0x8825: "GPSInfo", 0x0112: "Orientation"}


def iter_images(src: Path, recursive: bool):
    it = src.rglob("*") if recursive else src.glob("*")
    for p in sorted(it):
        if p.is_file() and p.suffix.lower() in EXTS:
            yield p


def convert_one(path: Path, dst: Path, max_width: int, quality: int, keep_icc: bool, skip_existing: bool):
    """返回 (状态, 说明)。状态 ∈ ok / skip / error"""
    out = dst / (path.stem + ".webp")
    if skip_existing and out.exists() and out.stat().st_mtime >= path.stat().st_mtime:
        return "skip", "已是最新"
    try:
        with Image.open(path) as raw:
            # ① 方向修正：把 EXIF Orientation 落实到像素上，之后才安全丢 EXIF
            img = ImageOps.exif_transpose(raw)
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA" if "A" in img.getbands() else "RGB")
            if img.width > max_width:
                h = round(img.height * max_width / img.width)
                img = img.resize((max_width, h), Image.Resampling.LANCZOS)
            kwargs = {"quality": quality, "method": 6}
            if keep_icc and raw.info.get("icc_profile"):
                kwargs["icc_profile"] = raw.info["icc_profile"]
            # ② 故意不传 exif → 输出文件不带任何元数据
            img.save(out, "WEBP", **kwargs)
        return "ok", "%dx%d -> %s" % (img.width, img.height, out.name)
    except Exception as exc:  # 单张失败不中断整批
        return "error", "%s: %s" % (path.name, exc)


def verify(dst: Path, max_width: int) -> int:
    bad = 0
    files = sorted(dst.glob("*.webp"))
    for p in files:
        with Image.open(p) as im:
            ex = im.getexif()
            hits = [name for tag, name in SENSITIVE_TAGS.items() if tag in ex]
            if im.width > max_width:
                hits.append("超宽 %d>%d" % (im.width, max_width))
        if hits:
            bad += 1
            print("  ✗ %-40s %s" % (p.name, ", ".join(hits)))
    print("核验 %d 张，残留敏感字段 %d 张" % (len(files), bad))
    return bad


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="批量压缩、转 WebP 并剥离 EXIF")
    ap.add_argument("--src", required=True, help="源目录（手机原图）")
    ap.add_argument("--dst", required=True, help="输出目录（站点 photos）")
    ap.add_argument("--max-width", type=int, default=1200)
    ap.add_argument("--quality", type=int, default=82)
    ap.add_argument("--recursive", action="store_true")
    ap.add_argument("--keep-icc", action="store_true", help="保留色彩配置文件（不影响 GPS 隐私）")
    ap.add_argument("--skip-existing", action="store_true", help="跳过比源文件新的输出")
    ap.add_argument("--verify", action="store_true", help="只核验输出目录，不处理")
    args = ap.parse_args(argv)

    dst = Path(args.dst)
    dst.mkdir(parents=True, exist_ok=True)

    if args.verify:
        return 1 if verify(dst, args.max_width) else 0

    src = Path(args.src)
    if not src.is_dir():
        sys.exit("源目录不存在：%s" % src)

    counts = {"ok": 0, "skip": 0, "error": 0}
    for p in iter_images(src, args.recursive):
        status, msg = convert_one(p, dst, args.max_width, args.quality, args.keep_icc, args.skip_existing)
        counts[status] += 1
        if status != "skip":
            print("[%s] %s" % (status, msg))

    print("\n完成：成功 %d / 跳过 %d / 失败 %d，输出目录 %s" % (counts["ok"], counts["skip"], counts["error"], dst))
    if counts["error"]:
        return 2
    return 1 if verify(dst, args.max_width) else 0


if __name__ == "__main__":
    sys.exit(main())
