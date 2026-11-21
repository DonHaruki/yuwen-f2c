# -*- coding: utf-8 -*-
"""
audit.py — 21语教 F & C 班纪念站安全与去幻觉检查脚本

用法：
    python audit.py --site
"""
from __future__ import annotations

import base64
import json
import re
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_JS = ROOT / "site" / "assets" / "data.js"
SCHED_JS = ROOT / "site" / "assets" / "schedule_data.js"

# 压缩编码存储的脱敏规则集（避免在公开仓库源码中明文暴露隐私特征词）
_PACKED_FORBIDDEN = (
    "c-noD-%{E@6vki0;i{csK)^`lw(T4Au67&>v_&n{(pD~mML@#<N}2H=Aca&#LV`g_6VP|*<m_(VqS+-%z3J8dzHiU@_U!I!m*2;"
    "6^MQGvpIdaf=UkiVcyxsV7Daq~Ohz&lR!fK55fpXkoRJ-7eF`T$Z^QBES5GAQks8rtB<0!IxR+~8M-nV_HSJL3LpYg^C*I#zr8i@?^=0K<d_9(;2FdI~="
    "YsSVnAAWXLtdvY-41!ZUdk^*%gc0q>8#NZvt!f6IxN6R8}ThF{-N>>;_EQ!P%$IeR&o6f@7=H)KM?wvfqb16<m(QZhDc;K3@!;)RYJWsJMV#rP$s)0Ct*g`"
    "fr<uA(6(@|XKK8uNg(}#e#7b(Z9u23S<(M0$WTGeedx1Hb5cc`{YY%b)Vijwn_3Bd-$vP{sTo+mW3%&3Xsh^AAo?YX=%0f)frj8*k;r?X{I+}X&V}7h-$FH@"
    "kVB0MYtM{uS7ZZCJCq+}XeX#xY%qPDvBm~z@zdg?x#zDQ1;c*PoSd=;GsaLUplgB1S!`5M;{*-zh_`#spZK17((BWo7Y0O@Q0<UxT{+qo?8k9gVuvVYbWj5R"
    "mfo~B#FZR%eeT7jXH($(3<7Q+7o^}{a0iz-O2LHyOX!@T>=C*$kTRtDPfksJ`y7vkTyOpYF$a5g"
)
_PACKED_RESTRICTED = (
    "c-k$@K?=e!5CzbyNY>s+yi2P>f;A+f){P5`t*D?~h!jnvm&r`xEo_GD{+mDi2?N2Q=%Fs1J+kpA8CNs^T}OLkK?{5pp<PgaKZEL"
    "G3RM%bIsMp8N<S`L|DZPC`lrG24OT_t;f6}PPfa*w!y<@%s4nDX16n2w3FMB>LVI(iwYGztv*{nxvRwr"
)


def _unpack(s: str) -> tuple[str, ...]:
    return tuple(json.loads(zlib.decompress(base64.b85decode(s)).decode("utf-8")))


FORBIDDEN_ALL_TOKENS = _unpack(_PACKED_FORBIDDEN)
RESTRICTED_FILE_TOKENS = _unpack(_PACKED_RESTRICTED)
# 课讯正文中允许保留历史网课直播通知原链接（chaoxing.com / wjx.cn），其余敏感词一律禁止
SCHED_ALLOWED_DOMAINS = {"chaoxing.com", "wjx.cn"}

BIRTHDAY_NAME_RE = re.compile(r"[\u4e00-\u9fa5]{2,4}\s+\d{1,2}\.\d{1,3}")
SCHED_NON_NAME_PREFIXES = {"作微小说", "诗歌鉴赏", "机测试题", "通客观题"}


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

    flat = json.dumps(data, ensure_ascii=False)
    violations: list[str] = []

    for tok in FORBIDDEN_ALL_TOKENS:
        idx = flat.find(tok)
        if idx >= 0:
            snippet = flat[max(0, idx - 24):idx + len(tok) + 24]
            violations.append(f"[data.js 禁词] {tok!r} -> …{snippet}…")

    for m in BIRTHDAY_NAME_RE.finditer(flat):
        snippet = flat[max(0, m.start() - 16):m.end() + 16]
        violations.append(f"[data.js 姓名生日后缀] {m.group(0)!r} -> …{snippet}…")

    for fitem in data.get("archive", {}).get("files", []):
        fn = fitem.get("filename", "")
        for tok in RESTRICTED_FILE_TOKENS:
            if tok in fn:
                violations.append(f"[受限文件名] {tok!r} in {fn!r}")

    sched_count = 0
    if SCHED_JS.exists():
        sraw = SCHED_JS.read_text(encoding="utf-8")
        sm = re.search(r"window\.COURSE_NOTICES\s*=\s*(\{.*\})\s*;?\s*$", sraw, re.S)
        if not sm:
            violations.append("[schedule_data.js] 格式不符合预期")
        else:
            sdata = json.loads(sm.group(1))
            sched_count = len(sdata.get("entries", []))
            sflat = json.dumps(sdata, ensure_ascii=False)
            for tok in FORBIDDEN_ALL_TOKENS:
                if tok in SCHED_ALLOWED_DOMAINS:
                    continue
                idx = sflat.find(tok)
                if idx >= 0:
                    snippet = sflat[max(0, idx - 24):idx + len(tok) + 24]
                    violations.append(f"[schedule_data.js 禁词] {tok!r} -> …{snippet}…")
            for m in BIRTHDAY_NAME_RE.finditer(sflat):
                prefix_word = m.group(0).split()[0]
                if prefix_word in SCHED_NON_NAME_PREFIXES:
                    continue
                snippet = sflat[max(0, m.start() - 16):m.end() + 16]
                violations.append(f"[schedule_data.js 姓名生日后缀] {m.group(0)!r} -> …{snippet}…")

    if violations:
        for v in violations:
            print("FAIL:", v)
        print(f"站点审计未通过：违规命中 {len(violations)} 项")
        return 1

    print(
        f"站点审计通过：文存 {len(data.get('essays', []))} 篇、"
        f"编年 {len(data.get('chronicle', []))} 卷、"
        f"群聊 {len(data.get('archive', {}).get('groups', []))} 个、"
        f"课程文件 {len(data.get('archive', {}).get('files', []))} 条、"
        f"课讯 {sched_count} 条 | 违规命中 0 项"
    )
    return 0


if __name__ == "__main__":
    sys.exit(audit_site())
