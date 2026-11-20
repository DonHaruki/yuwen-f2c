# -*- coding: utf-8 -*-
"""
audit.py — 21语教 F & C 班纪念站安全与去幻觉检查脚本

用法：
    python audit.py --site
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_JS = ROOT / "site" / "assets" / "data.js"

FORBIDDEN_PRIVACY_TOKENS = (
    "21550301256", "wxid_", "祥盛路", "顺德区大良",
    "pan.baidu.com", "docs.qq.com", "kdocs.cn", "wjx.cn", "chaoxing.com",
    "xwechat_files", "聊天记录导出", "file:///",
    "D:\\", "E:\\", "d:/", "e:/",
)

FORBIDDEN_UNRELATED_TOKENS = (
    "陈圣怡", "圣怡", "叶思彤", "思彤", "关睿瑶", "睿瑶", "梁凝", "凝凝",
    "以诺", "王铭欣", "铭欣", "苏芷瑶", "芷瑶",
    "阳江市第一中学实验学校", "阳江第一中学实验学校",
    "贰柒家", "体温计", "个人与情感主线", "借壳立身", "讨好型",
    "梁译尹人物与关系分析", "偷窥一下", "气质女神",
    "流鼻血", "做 CT", "梁译尹和你", "综合测评结果汇总表(1).xls",
)

FORBIDDEN_HALLUCINATIONS = (
    "英语教育", "英教", "D班", "小明倾情整理",
    "1,698", "1,528", "3,157", "24,795", "743",
)

RESTRICTED_FILE_TOKENS = (
    "切勿外传", "切勿挂网", "综合测评", "学号", "补考", "缓考", "重修",
    "联系方式", "未提交", "检测列表", "报名表", "名单", "成绩", "请假",
)

BIRTHDAY_NAME_RE = re.compile(r"[\u4e00-\u9fa5]{2,4}\s+\d{1,2}\.\d{1,3}")


def audit_site() -> int:
    if not DATA_JS.exists():
        print(f"未找到 {DATA_JS}，请先运行 build.py")
        return 1

    raw = DATA_JS.read_text(encoding="utf-8")
    prefix = "window.CLASS_ARCHIVE = "
    if not raw.startswith(prefix) or not raw.rstrip().endswith(";"):
        print("data.js 格式不符合预期")
        return 1

    json_str = raw[len(prefix):].rstrip()[:-1].replace("<\\/", "</")
    data = json.loads(json_str)

    # Full-text JSON check (excluding legitimate HTML tags / URLs only for d:/ pattern already absent)
    flat = json.dumps(data, ensure_ascii=False)
    violations: list[str] = []

    for tok in FORBIDDEN_PRIVACY_TOKENS + FORBIDDEN_UNRELATED_TOKENS + FORBIDDEN_HALLUCINATIONS:
        idx = flat.find(tok)
        if idx >= 0:
            snippet = flat[max(0, idx - 24):idx + len(tok) + 24]
            violations.append(f"[全站禁词] {tok!r} -> …{snippet}…")

    for m in BIRTHDAY_NAME_RE.finditer(flat):
        snippet = flat[max(0, m.start() - 16):m.end() + 16]
        violations.append(f"[姓名生日后缀] {m.group(0)!r} -> …{snippet}…")

    for fitem in data.get("archive", {}).get("files", []):
        fn = fitem.get("filename", "")
        for tok in RESTRICTED_FILE_TOKENS:
            if tok in fn:
                violations.append(f"[受限文件名] {tok!r} in {fn!r}")

    if violations:
        for v in violations:
            print("FAIL:", v)
        print(f"站点审计未通过：违规命中 {len(violations)} 项")
        return 1

    print(
        f"站点审计通过：文存 {len(data.get('essays', []))} 篇、"
        f"编年 {len(data.get('chronicle', []))} 卷、"
        f"群聊 {len(data.get('archive', {}).get('groups', []))} 个、"
        f"课程文件 {len(data.get('archive', {}).get('files', []))} 条 | 违规命中 0 项"
    )
    return 0


if __name__ == "__main__":
    sys.exit(audit_site())
