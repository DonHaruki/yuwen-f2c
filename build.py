# -*- coding: utf-8 -*-
"""
build.py — 21语教 F & C 班大学四年纪念站数据构建脚本

只读知识库 E:\\启蒙（不创建、不改写、不删除库内任何文件）。
仅输出：
  - site/assets/data.js
  - 班级站复查清单.txt（仅留本机核对，严禁提交到 GitHub）
"""
from __future__ import annotations

import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VAULT = Path(r"E:\启蒙")
OUT_JS = ROOT / "site" / "assets" / "data.js"
OUT_AUDIT = ROOT / "班级站复查清单.txt"

CHRONICLE_MD = VAULT / "00-归档与记录" / "微信聊天对账分册" / "大学大事记（2021–2025）.md"
INDEX_MD = VAULT / "00-归档与记录" / "微信聊天对账分册" / "大学资料总索引.md"

ESSAY_SPECS = [
    {
        "slug": "xuewei-4years",
        "path": ROOT / "content" / "xuewei-4years.md",
        "tag": "学委后记",
        "badge": "F & C",
        "date": "2025-06-27",
    },
    {
        "slug": "xuewei-zibai",
        "path": VAULT / "03-创作与随笔" / "散文与随笔" / "一名学习委员的自白.md",
        "tag": "致 F 班",
        "badge": "21F",
        "date": "2021-12-15",
    },
    {
        "slug": "suibei-winter",
        "path": VAULT / "03-创作与随笔" / "散文与随笔" / "穗北的冬天.md",
        "tag": "花都纪事",
        "badge": "21F",
        "date": "2021-12-20",
    },
    {
        "slug": "study-review",
        "path": VAULT / "03-创作与随笔" / "散文与随笔" / "对学习的一些清算.md",
        "tag": "大一复盘",
        "badge": "21F",
        "date": "2022-01-06",
    },
    {
        "slug": "ideology-aie",
        "path": VAULT / "03-创作与随笔" / "文艺评论" / "意识形态与意识形态国家机器.md",
        "tag": "文论习作",
        "badge": "21C",
        "date": "2022-04-23",
    },
    {
        "slug": "fujino-reading",
        "path": VAULT / "03-创作与随笔" / "文艺评论" / "《藤野先生》文本细读与分析.md",
        "tag": "专业课习作",
        "badge": "21C",
        "date": "2022-10-25",
    },
    {
        "slug": "lv-shuxiang",
        "path": VAULT / "03-创作与随笔" / "散文与随笔" / "讲稿.md",
        "title_override": "吕叔湘语文教育思想讲稿",
        "tag": "课堂讲稿",
        "badge": "21C",
        "date": "2023-12-21",
    },
    {
        "slug": "sishu-jingdu",
        "path": VAULT / "03-创作与随笔" / "文艺评论" / "四书精读.md",
        "tag": "课程感想",
        "badge": "21C",
        "date": "2024-06-19",
    },
]

BLOCK_FILE_TERMS = (
    "切勿外传", "切勿挂网", "成绩", "补考", "缓考", "重修", "挂科",
    "联系方式", "学号", "名单", "未提交", "检测列表", "报名表",
    "综合测评", "请假", "信息表", "信息修改表", "流水号",
    "是否符合单独指导", "董明康", "梁译尹", "陈永乐", "作业6.1", "作业6.11",
)

VIDEO_META = {
    "BV1D54y1W73h": (
        "知网与读秀文献检索指南",
        "2021-11-07 · 21语教F吹💦群（许雪欣分享）",
    ),
    "BV1Wi4y1Z7Bs": (
        "21语教F班集体生日会 Plog",
        "2021-12-05 · 21语教F吹💦群（杨昕剪辑）",
    ),
    "BV1Jb4y127LC": (
        "大一下班级学习视频分享",
        "2022-05-10 · Confident逢考必过~💯",
    ),
    "BV1qs4y1M7A3": (
        "大三上专业学习视频分享",
        "2023-10-29 · Confident逢考必过~💯",
    ),
}

# 修复部分内容错误，移除“大愚治水”的错误描述
# 自动按 theme 归档照片
PHOTOS = [
    # F班影像
    {"id": "ph-f-junxun", "vol": 0, "date": "2021-09-21", "badge": "21F", "name": "21语教F军训", "file": "21语文教育F军训_亮.webp", "src": "assets/photos/21语文教育F军训_亮.webp", "caption": "21语教F军训", "theme": "F班影像"},
    {"id": "ph-f-tuanjian", "vol": 0, "date": "2021-11-08", "badge": "21F", "name": "F班团建", "file": "F班团建.webp", "src": "assets/photos/F班团建.webp", "caption": "F班团建", "theme": "F班影像"},
    {"id": "ph-f-jiaozi", "vol": 0, "date": "2021-12-20", "badge": "21F", "name": "F班包饺子", "file": "F班团建做饺子.webp", "src": "assets/photos/F班团建做饺子.webp", "caption": "F班包饺子", "theme": "F班影像"},
    {"id": "ph-f-banzhuren", "vol": 0, "date": "2021-12", "badge": "21F", "name": "班主任版F班团建", "file": "班主任版F班团建.webp", "src": "assets/photos/班主任版F班团建.webp", "caption": "班主任版F班团建", "theme": "F班影像"},
    {"id": "ph-english", "vol": 0, "date": "2022-01", "badge": "21F", "name": "F班大一英语课合影", "file": "大一英语课大合影.webp", "src": "assets/photos/大一英语课大合影.webp", "caption": "F班大一英语课合影", "theme": "F班影像"},
    # C班影像
    {"id": "ph-group-discuss", "vol": 1, "date": "2022-03", "badge": "21C", "name": "小组作业激情讨论", "file": "小组作业激情讨论.jpg", "src": "assets/photos/小组作业激情讨论.jpg", "caption": "小组作业激情讨论", "theme": "C班影像"},
    {"id": "ph-weige", "vol": 2, "date": "2023", "badge": "21C", "name": "C班微格教学", "file": "微格小组合影.webp", "src": "assets/photos/微格小组合影.webp", "caption": "C班微格教学合影", "theme": "C班影像"},
    {"id": "ph-sizheng", "vol": 1, "date": "2022-05-20", "badge": "21C", "name": "C班思政课合影", "file": "思政课合影.webp", "src": "assets/photos/思政课合影.webp", "caption": "C班思政课合影", "theme": "C班影像"},
    {"id": "ph-shige-stage", "vol": 1, "date": "2022-06-06", "badge": "21C", "name": "C班诗歌朗诵合影", "file": "诗歌朗诵合影.webp", "src": "assets/photos/诗歌朗诵合影.webp", "caption": "C班诗歌朗诵合影", "theme": "C班影像"},
    {"id": "ph-shige-prep", "vol": 1, "date": "2022-04-16", "badge": "21C", "name": "C班诗歌朗诵组队", "file": "诗歌朗诵合影 (2).webp", "src": "assets/photos/诗歌朗诵合影 (2).webp", "caption": "C班诗歌朗诵组队", "theme": "C班影像"},
    {"id": "ph-grad-college", "vol": 4, "date": "2025-05", "badge": "21C", "name": "文学院大合影", "file": "文学院大合影.webp", "src": "assets/photos/文学院大合影.webp", "caption": "文学院大合影", "theme": "C班影像"},
    {"id": "ph-grad-class", "vol": 4, "date": "2025-05-08", "badge": "21C", "name": "C班毕业合影", "file": "2025-05-08_毕业全班正装_C25A0419.webp", "src": "assets/photos/2025-05-08_毕业全班正装_C25A0419.webp", "caption": "C班毕业合影", "theme": "C班影像"},
]



def sanitize_public_text(text: str) -> str:
    """Apply Tier-2 public class-site sanitization rules."""
    def _clean_file_link(m: re.Match) -> str:
        label = re.sub(r"(_含语音转写)?\.txt$", "", m.group(1).strip())
        return label

    text = re.sub(r"\[([^\]]+)\]\(file:///[^)]+\)", _clean_file_link, text)
    text = re.sub(r"!\[\[[^\]]+\]\]", "", text)
    text = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"([\u4e00-\u9fa5]{2,4})\s+\d{1,2}\.\d{1,3}", r"\1", text)
    text = text.replace("阳江市第一中学实验学校", "阳江实习学校")
    text = text.replace("阳江第一中学实验学校", "阳江实习学校")
    return text


def render_inline(t: str) -> str:
    """Render inline Markdown cleanly and safely."""
    t = sanitize_public_text(t)
    links: list[tuple[str, str]] = []

    def _stash_link(m: re.Match) -> str:
        idx = len(links)
        links.append((m.group(1), m.group(2)))
        return f"\x00LNK{idx}\x00"

    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", _stash_link, t)
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)

    for idx, (label, url) in enumerate(links):
        safe_url = html.escape(url, quote=True)
        safe_lbl = html.escape(label, quote=False)
        anchor = f'<a href="{safe_url}" target="_blank" rel="noopener noreferrer">{safe_lbl}</a>'
        t = t.replace(f"\x00LNK{idx}\x00", anchor)
    return t


def _split_pipe_row(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    s = s.replace("\\|", "\x00PIPE\x00")
    return [c.strip().replace("\x00PIPE\x00", "|") for c in s.split("|")]


def _is_table_sep(line: str) -> bool:
    s = line.strip()
    if "|" not in s:
        return False
    cells = _split_pipe_row(s)
    return bool(cells) and all(re.match(r"^:?-{2,}:?$", c) for c in cells)


def md_to_html(lines: list[str]) -> str:
    """Convert rich Markdown (headings, hr, quotes, ul/ol, pipe tables) to HTML."""
    out: list[str] = []
    para: list[str] = []
    quote: list[str] = []
    ul_items: list[str] = []
    ol_items: list[str] = []

    def flush() -> None:
        if para:
            out.append("<p>" + " ".join(para) + "</p>")
            para.clear()
        if quote:
            out.append("<blockquote><p>" + "<br>".join(quote) + "</p></blockquote>")
            quote.clear()
        if ul_items:
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in ul_items) + "</ul>")
            ul_items.clear()
        if ol_items:
            out.append("<ol>" + "".join(f"<li>{x}</li>" for x in ol_items) + "</ol>")
            ol_items.clear()

    i = 0
    n = len(lines)
    while i < n:
        raw = lines[i].rstrip()
        t = raw.strip()
        if not t:
            flush()
            i += 1
            continue
        if re.match(r"^-{3,}$", t):
            flush()
            out.append("<hr>")
            i += 1
            continue
        if t.startswith("|") and i + 1 < n and _is_table_sep(lines[i + 1]):
            flush()
            headers = _split_pipe_row(t)
            i += 2
            rows: list[list[str]] = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(_split_pipe_row(lines[i]))
                i += 1
            th_html = "".join(f"<th>{render_inline(h)}</th>" for h in headers)
            body_html = ""
            for row in rows:
                padded = row + [""] * (len(headers) - len(row))
                tds = "".join(f"<td>{render_inline(c)}</td>" for c in padded[:len(headers)])
                body_html += f"<tr>{tds}</tr>"
            out.append(f'<div class="tbl-wrap"><table><thead><tr>{th_html}</tr></thead><tbody>{body_html}</tbody></table></div>')
            continue
        if t.startswith("### "):
            flush()
            out.append(f"<h4>{render_inline(t[4:])}</h4>")
            i += 1
            continue
        if t.startswith("## "):
            flush()
            out.append(f"<h3>{render_inline(t[3:])}</h3>")
            i += 1
            continue
        if t.startswith("# "):
            flush()
            out.append(f"<h2>{render_inline(t[2:])}</h2>")
            i += 1
            continue
        if t.startswith(">"):
            if para or ul_items or ol_items:
                flush()
            quote.append(render_inline(t.lstrip(">").strip()))
            i += 1
            continue
        if re.match(r"^[-*]\s+", t):
            if para or quote or ol_items:
                flush()
            ul_items.append(render_inline(re.sub(r"^[-*]\s+", "", t)))
            i += 1
            continue
        if re.match(r"^\d+\.\s+", t):
            if para or quote or ul_items:
                flush()
            ol_items.append(render_inline(re.sub(r"^\d+\.\s+", "", t)))
            i += 1
            continue
        if quote or ul_items or ol_items:
            flush()
        para.append(render_inline(t))
        i += 1

    flush()
    return "\n".join(out)


def plain_from_lines(lines: list[str]) -> str:
    buf: list[str] = []
    for ln in lines:
        t = sanitize_public_text(ln.strip())
        t = re.sub(r"^>+ ?", "", t)
        t = re.sub(r"^#{1,6}\s+", "", t)
        t = re.sub(r"^[-*]\s+", "", t)
        t = re.sub(r"^\d+\.\s+", "", t)
        t = re.sub(r"^-{3,}$", "", t)
        t = t.replace("**", "").replace("`", "")
        if t:
            buf.append(t)
    return "\n".join(buf)


def build_chronicle() -> tuple[list[dict], list[dict]]:
    """Parse 5 volumes + 4 collective themes from 大学大事记（2021–2025）.md."""
    raw = CHRONICLE_MD.read_text(encoding="utf-8-sig")
    lines = raw.splitlines()

    volumes: list[dict] = []
    themes: list[dict] = []
    cur_vol: dict | None = None
    in_themes = False

    vol_re = re.compile(r"^###\s+第([一二三四五])卷\s*·\s*(.+?)\s*（([^）]+)）")
    ev_re = re.compile(r"^-\s+\*\*`([^`]+)`｜(.+?)\*\*：(.*)$")

    i = 0
    while i < len(lines):
        s = lines[i].rstrip()
        t = s.strip()

        if t.startswith("## 二、"):
            in_themes = True
            cur_vol = None
            i += 1
            continue

        if not in_themes:
            vm = vol_re.match(t)
            if vm:
                v_num = vm.group(1)
                v_stage = vm.group(2).strip()
                v_meta = vm.group(3).strip()
                parts = [p.strip() for p in v_meta.split("·")]
                period = parts[0] if parts else v_meta
                class_part = parts[1] if len(parts) > 1 else ""
                badge = "21F" if "F班" in class_part else "21C"
                cur_vol = {
                    "id": f"vol-{len(volumes) + 1}",
                    "label": f"第{v_num}卷 · {v_stage}",
                    "title": f"{v_stage}（{class_part}）" if class_part else v_stage,
                    "period": period,
                    "badge": badge,
                    "keywords": [],
                    "events": [],
                }
                volumes.append(cur_vol)
                i += 1
                continue

            if cur_vol and t.startswith("> **关键词**："):
                kw_str = t.split("：", 1)[1].strip()
                kw_str = kw_str.replace("狮岭代课与39℃高烧、", "").replace("、狮岭代课与39℃高烧", "")
                kw_str = sanitize_public_text(kw_str)
                cur_vol["keywords"] = [k.strip() for k in kw_str.split("、") if k.strip()]
                i += 1
                continue

            if cur_vol and ev_re.match(t):
                block = [t]
                i += 1
                while i < len(lines):
                    nxt = lines[i]
                    nt = nxt.strip()
                    if not nt or nt.startswith("- **") or nt.startswith("### ") or nt.startswith("## ") or nt == "---":
                        break
                    block.append(nxt.rstrip())
                    i += 1
                full_block = "\n".join(block)

                if "寒冬代课与 39℃ 高烧体温计" in full_block:
                    continue

                full_block = full_block.replace("（“这个群以后就是我们两个人的啦”）", "")
                full_block = full_block.replace("也在你流鼻血赴院做 CT 排查期间互相叮嘱照应", "也在身体不适就医排查期间互相叮嘱照应")
                full_block = full_block.replace(
                    "吸纳张羽丹、冼业银、朱依琳、吴欣颐、余家欢、陈志茵、董明康与双学委（梁译尹和你）组成专项审核团",
                    "吸纳张羽丹、冼业银、朱依琳、吴欣颐、余家欢、陈志茵与双学委（梁译尹与你）组成专项审核团",
                )
                full_block = full_block.replace(
                    "逐项交叉审核蔡晓琦、李丽珊、梁译尹、吴欣颐、陈永乐、钟秀芬等同学打包提交的 11 份压缩包佐证",
                    "逐项交叉审核同学们打包提交的 11 份佐证压缩包",
                )
                full_block = full_block.replace("董明康厘清志愿工时截止口径", "同步厘清志愿工时截止口径")
                full_block = full_block.replace("《23年21语文教育C班综合测评结果汇总表(1).xls》范本", "综合测评汇总表范本")
                full_block = full_block.replace("，你与梁译尹选课斗嘴、饭堂聚餐", "，同学们重聚核对选课")
                full_block = full_block.replace("；当晚你与梁译尹约好次日午饭并一起去给学生证盖章", "")
                full_block = full_block.replace(
                    "，前一天（`05-07`）梁译尹头晕问起那支体温计时，你还在坐一个半小时地铁赶回学校（最终仍未归还，成了毕业后还欠着她的一个小念想）",
                    "",
                )

                first_line = block[0]
                if "大愚治水" in full_block:
                    continue
                em = ev_re.match(full_block.splitlines()[0].strip())
                if not em:
                    continue
                ev_date = em.group(1).strip()
                ev_title = sanitize_public_text(em.group(2).strip())
                rest_first = em.group(3).strip()
                body_lines: list[str] = []
                if rest_first:
                    body_lines.append(rest_first)
                for sub in full_block.splitlines()[1:]:
                    sub_t = sub.strip()
                    if sub_t.startswith("- "):
                        body_lines.append(sub_t)
                    elif sub_t:
                        body_lines.append(sub_t)
                ev_obj: dict = {
                    "date": ev_date,
                    "title": ev_title,
                    "html": md_to_html(body_lines),
                }
                if "双学委并肩护航“网课通知群”" in ev_title:
                    ev_obj["link"] = {
                        "label": "翻看 2022 春《给暂未返校的你们》38 条全班寄语墙与 5 张原件 →",
                        "url": "https://donharuki.github.io/xiaoming/university-memories/",
                    }
                cur_vol["events"].append(ev_obj)
                continue
        else:
            if t.startswith("| **") and not _is_table_sep(t):
                cells = _split_pipe_row(t)
                if len(cells) >= 3:
                    raw_name = cells[0].replace("**", "").strip()
                    if "个人与情感主线" in raw_name:
                        i += 1
                        continue
                    clean_name = re.sub(r"^\d+\.\s*", "", raw_name)
                    themes.append({
                        "title": clean_name,
                        "span": cells[1].strip("` "),
                        "html": render_inline(cells[2]),
                    })
        i += 1

    return volumes, themes


def build_archive() -> dict:
    """Parse public groups, category overview, filtered 01-09 files, semesters, and Bilibili videos."""
    raw = INDEX_MD.read_text(encoding="utf-8-sig")
    lines = raw.splitlines()

    groups: list[dict] = []
    public_group_names: set[str] = set()
    categories: list[dict] = []
    files: list[dict] = []
    semesters: list[dict] = []
    videos: list[dict] = []

    section = ""
    cur_cat_code = ""
    cur_cat_name = ""

    for ln in lines:
        t = ln.strip()
        if t.startswith("## 一、"):
            section = "groups"
            continue
        if t.startswith("### 核心资料分发者"):
            section = ""
            continue
        if t.startswith("### 分布概览"):
            section = "overview"
            continue
        if t.startswith("## 三、"):
            section = "semesters"
            continue
        if t.startswith("## 四、"):
            section = "urls"
            continue
        if t.startswith("### 4.4 "):
            section = "videos"
            continue
        if t.startswith("## 五、"):
            section = ""
            continue

        cat_m = re.match(r"^###\s+(0[1-9]|1[0-2])\.\s+(.+?)（", t)
        if cat_m:
            code = cat_m.group(1)
            if int(code) >= 10:
                section = "skip_files"
            else:
                section = "files"
                cur_cat_code = code
                cur_cat_name = cat_m.group(2).strip()
            continue

        if section == "groups" and t.startswith("|") and not _is_table_sep(t):
            cells = _split_pipe_row(t)
            if len(cells) >= 6 and cells[0] == "群聊":
                name = cells[1].replace("**", "").strip()
                if name == "大愚治水":
                    continue
                public_group_names.add(name)
                groups.append({
                    "name": name,
                    "role": cells[2].strip(),
                    "span": cells[3].strip(),
                    "messages": int(cells[4].replace(",", "").replace("**", "")),
                    "files": int(cells[5].replace(",", "").replace("**", "")),
                })

        elif section == "overview" and t.startswith("|") and not _is_table_sep(t):
            cells = _split_pipe_row(t)
            if len(cells) >= 4 and cells[0].startswith("**"):
                title_cell = cells[0].replace("**", "").strip()
                cm = re.match(r"^(0[1-9]|1[0-2])\.\s+(.+)$", title_cell)
                if cm:
                    cnt_m = re.match(r"^(\d+)\s*\((\d+)\)$", cells[1].strip())
                    total = int(cnt_m.group(1)) if cnt_m else 0
                    unique = int(cnt_m.group(2)) if cnt_m else total
                    categories.append({
                        "code": cm.group(1),
                        "name": cm.group(2).strip(),
                        "total": total,
                        "unique": unique,
                        "summary": cells[3].strip(),
                    })

        elif section == "files" and t.startswith("|") and not _is_table_sep(t):
            cells = _split_pipe_row(t)
            if len(cells) >= 4 and re.match(r"^\d{4}-\d{2}-\d{2}", cells[0]):
                date_str = cells[0].strip()
                fname = cells[1].strip().strip("`").strip()
                src_raw = cells[3].strip()

                src_parts = [p.strip() for p in src_raw.split("/") if p.strip()]
                pub_parts = [p for p in src_parts if p in public_group_names]
                if not pub_parts:
                    continue

                fname_lower = fname.lower()
                if any(term.lower() in fname_lower for term in BLOCK_FILE_TERMS):
                    continue

                files.append({
                    "cat": cur_cat_code,
                    "catName": cur_cat_name,
                    "date": date_str,
                    "filename": fname,
                    "group": " / ".join(pub_parts),
                })

        elif section == "semesters" and t.startswith("|") and not _is_table_sep(t):
            cells = _split_pipe_row(t)
            if len(cells) >= 4 and cells[0].startswith("**20"):
                stage = cells[0].replace("**", "").strip()
                count = int(cells[1].strip())
                courses = cells[2].strip()
                grp_parts = [g.strip() for g in cells[3].split("、") if g.strip()]
                pub_grp_parts = [
                    g for g in grp_parts
                    if any(g.startswith(pn) for pn in public_group_names)
                ]
                semesters.append({
                    "stage": stage,
                    "files": count,
                    "summary": courses,
                    "groups": "、".join(pub_grp_parts),
                })

        elif section == "videos" and t.startswith("- `"):
            vm = re.search(r"(https://www\.bilibili\.com/video/(BV[0-9A-Za-z]+))", t)
            if vm:
                bv_url = vm.group(1)
                bv_id = vm.group(2)
                title, desc = VIDEO_META.get(bv_id, (f"班级公开视频 {bv_id}", "班级公开B站分享"))
                videos.append({
                    "bvid": bv_id,
                    "url": bv_url,
                    "title": title,
                    "meta": desc,
                })

    return {
        "groups": groups,
        "categories": categories,
        "files": files,
        "semesters": semesters,
        "videos": videos,
    }


def _strip_frontmatter(raw: str) -> tuple[list[str], str]:
    lines = raw.splitlines()
    title = ""
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                fm = "\n".join(lines[1:i])
                tm = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', fm, re.M)
                if tm:
                    title = tm.group(1).strip()
                return lines[i + 1:], title
    return lines, title


def build_essays() -> list[dict]:
    """Load, sanitize, and render the 8 curated class/campus essays."""
    essays: list[dict] = []
    for spec in ESSAY_SPECS:
        path: Path = spec["path"]
        raw = path.read_text(encoding="utf-8-sig")
        lines, fm_title = _strip_frontmatter(raw)
        title = spec.get("title_override") or fm_title or path.stem

        cleaned: list[str] = []
        dropped_h1 = False
        dropped_dup_title = False
        for ln in lines:
            t = ln.strip()
            if t.startswith("# ") and not dropped_h1:
                dropped_h1 = True
                continue
            if t.startswith("> *创作日期") or t.startswith(">*创作日期"):
                continue
            if not cleaned and not dropped_dup_title and t in (title, "《藤野先生》文本分析"):
                dropped_dup_title = True
                continue
            if "21550301256" in t:
                continue
            ln = ln.replace(
                "在外面偶尔能够遇到几位女同学，插肩而过、偷窥一下等等，而且二师的美女只让人应接不暇，图书馆自然会有气质女神（雾）。",
                "",
            )
            cleaned.append(ln.rstrip())

        while cleaned and not cleaned[0].strip():
            cleaned.pop(0)
        while cleaned and not cleaned[-1].strip():
            cleaned.pop()

        plain = plain_from_lines(cleaned)
        words = len(re.sub(r"\s+", "", plain))
        excerpt = re.sub(r"\s+", " ", plain)[:88].strip()
        if len(re.sub(r"\s+", " ", plain)) > 88:
            excerpt += "…"

        essays.append({
            "slug": spec["slug"],
            "title": title,
            "date": spec["date"],
            "tag": spec["tag"],
            "badge": spec["badge"],
            "words": words,
            "excerpt": excerpt,
            "body": md_to_html(cleaned),
        })
    return essays


def write_checklist(
    chronicle: list[dict],
    themes: list[dict],
    archive: dict,
    essays: list[dict],
    specials: list[dict],
) -> None:
    lines = [
        "21语教 F & C 班纪念站 · 本机复查清单（勿随站点发布）",
        f"生成时间：{date.today().isoformat()}",
        f"数据源：{VAULT}（只读）+ {ROOT / 'content' / 'xuewei-4years.md'}",
        "",
        "== 站点规模统计 ==",
        f"  编年卷数：{len(chronicle)} 卷（共 {sum(len(v['events']) for v in chronicle)} 条大事记）",
        f"  集体专题：{len(themes)} 项（已剔除「个人与情感主线」）",
        f"  文存篇目：{len(essays)} 篇",
        f"  公开群聊：{len(archive['groups'])} 个（共 {sum(g['messages'] for g in archive['groups'])} 条消息、{sum(g['files'] for g in archive['groups'])} 份文件，已剔除全部 8 个私聊）",
        f"  学期脉络：{len(archive['semesters'])} 个学期",
        f"  课程分类：{len(archive['categories'])} 个板块（仅展示 01-09 专业课脱敏文件共 {len(archive['files'])} 条）",
        f"  特展入口：{len(specials)} 项（2022 春 21C 寄语墙）",
        f"  公开视频：{len(archive['videos'])} 条 B 站视频（已剔除网盘/超星/协作表/本地路径）",
        "",
        "== 收录文存明细 ==",
    ]
    for e in essays:
        lines.append(f"  [{e['badge']}] {e['slug']:<16} {e['date']}  {e['words']:>4}字  {e['title']}")
    lines += [
        "",
        "== 已按方案排除 ==",
        "  - 毕业典礼.md / 牡丹亭讲稿.md / 原 AI 复盘稿（已用事实修正版 xuewei-4years.md 替代）",
        "  - 全部私聊记录、对账分册、阳实材料、学号、生日后缀、网盘提取码与协作表格链接",
        "  - 10~12 类教务/班务/个人文件明细，及含成绩/补考/名单/切勿挂网字样文件",
        "",
        "核对命令：audit.py --site",
    ]
    OUT_AUDIT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    chronicle, themes = build_chronicle()
    for idx, vol in enumerate(chronicle):
        vol["photos"] = [p for p in PHOTOS if p.get("vol") == idx] if idx == 0 else []
    archive = build_archive()
    essays = build_essays()
    specials = [
        {
            "badge": "2022 春 · 21C 特展",
            "title": "给暂未返校的你们｜21 语教 C 班寄语墙",
            "date": "2022-04-03",
            "meta": "38 条同学寄语 · 5 张手写/便签原件 · 摘自《暖心物语（第五期）》",
            "desc": "2022 年春季四位同学因疫情暂缓返校期间，全班写下的 38 条寄语与 5 份珍贵手写原件（含检索与原件大图）。",
            "url": "https://donharuki.github.io/xiaoming/university-memories/",
        }
    ]

    data = {
        "meta": {
            "title": "文院书简 · 21语教 F & C 班四年纪念册",
            "span": "2021.10 – 2025.06",
            "groupsCount": len(archive["groups"]),
            "totalGroupFiles": sum(g["files"] for g in archive["groups"]),
            "totalGroupMessages": sum(g["messages"] for g in archive["groups"]),
            "shownFilesCount": len(archive["files"]),
        },
        "chronicle": chronicle,
        "themes": themes,
        "specials": specials,
        "essays": essays,
        "archive": archive,
        "photos": PHOTOS,
    }

    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    OUT_JS.parent.mkdir(parents=True, exist_ok=True)
    OUT_JS.write_text("window.CLASS_ARCHIVE = " + payload + ";\n", encoding="utf-8")
    write_checklist(chronicle, themes, archive, essays, specials)

    print(
        f"volumes={len(chronicle)} events={sum(len(v['events']) for v in chronicle)} "
        f"themes={len(themes)} essays={len(essays)} groups={len(archive['groups'])} "
        f"semesters={len(archive['semesters'])} categories={len(archive['categories'])} "
        f"files={len(archive['files'])} videos={len(archive['videos'])} photos={len(data['photos'])}"
    )
    print(f"data.js={OUT_JS.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
