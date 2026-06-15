#!/usr/bin/env python3
"""Pre-scan a contract Markdown file to extract clause numbering structure.

Replaces the Structure Agent's first-pass read. Outputs a JSON map of all
clauses with line ranges, hierarchy, and anomaly flags.

Usage:
    python scan-structure.py contract.md [_internal/scan-result.json]
    python scan-structure.py template.md

Supports both Chinese (第X条) and English (ARTICLE/Section/Clause) numbering.
"""

import json
import re
import sys
from pathlib import Path

# ── Chinese numeral conversion ──────────────────────────────────────────

_CN_NUM = {
    "零": 0, "〇": 0, "一": 1, "二": 2, "三": 3, "四": 4,
    "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
    "百": 100, "千": 1000, "万": 10000, "亿": 100000000,
}


def cn2int(s: str) -> int:
    """Convert a Chinese numeral string to integer.  '三百二十五' -> 325."""
    s = s.strip()
    if s.isdigit():
        return int(s)

    result, section, digit = 0, 0, 0
    for ch in s:
        if ch not in _CN_NUM:
            if ch.isdigit():
                digit = int(ch)
            continue
        v = _CN_NUM[ch]
        if v >= 10000:                  # 万、亿
            result = (result + section + digit) * v
            section = digit = 0
        elif v >= 10:                   # 十、百、千
            section += (digit or 1) * v
            digit = 0
        else:
            digit = v
    return result + section + digit


# ── Roman numeral conversion ────────────────────────────────────────────

_ROMAN_VAL = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}


def roman2int(s: str) -> int:
    """Convert Roman numeral string to integer.  'xiv' -> 14."""
    s = s.strip().lower()
    result = 0
    prev = 0
    for ch in reversed(s):
        if ch not in _ROMAN_VAL:
            continue
        cur = _ROMAN_VAL[ch]
        if cur < prev:
            result -= cur
        else:
            result += cur
        prev = cur
    return result


# ── Language detection ──────────────────────────────────────────────────

def detect_language(text: str) -> str:
    """Detect contract language by CJK character proportion in first 100 lines."""
    lines = text.split("\n")[:100]
    sample = "\n".join(lines)
    if not sample.strip():
        return "en"

    cjk = sum(1 for ch in sample if "一" <= ch <= "鿿" or "㐀" <= ch <= "䶿")
    total = len(sample.replace("\n", "").replace(" ", ""))
    if total == 0:
        return "en"
    ratio = cjk / total
    if ratio > 0.3:
        return "zh"
    if ratio < 0.1:
        return "en"
    return "bilingual"


# ── Regex patterns ──────────────────────────────────────────────────────

# Chinese patterns
RE_CN_PART = re.compile(r"^\s*第([一二三四五六七八九十百千\d]+)编\s*")
RE_CN_CHAPTER = re.compile(r"^\s*第([一二三四五六七八九十百千\d]+)章\s*")
RE_CN_SECTION = re.compile(r"^\s*第([一二三四五六七八九十百千\d]+)节\s*")
RE_CN_ARTICLE = re.compile(r"^\s*第([一二三四五六七八九十百千\d]+)条\s*")
RE_CN_SUBITEM = re.compile(r"^\s*[（(]([一二三四五六七八九十\d]+)[）)]\s*")
RE_CN_NUMITEM = re.compile(r"^\s*(\d+)\s*[、,]")
# Inline reference (not a clause start)
RE_CN_INLINE_REF = re.compile(r".{2,}第[一二三四五六七八九十百千\d]+条")

# English patterns
RE_EN_ARTICLE = re.compile(r"^\s*ARTICLE\s+([IVXLCDM\d]+)\b", re.IGNORECASE)
RE_EN_SECTION = re.compile(r"^\s*Section\s+([\d.]+)\b", re.IGNORECASE)
RE_EN_CLAUSE = re.compile(r"^\s*Clause\s+([\d.]+)\b", re.IGNORECASE)
RE_EN_NUMPARA = re.compile(r"^\s*(\d+)\.\s+")
RE_EN_DOTTED = re.compile(r"^\s*(\d+\.\d+)\s+")
RE_EN_LETTER = re.compile(r"^\s*\(([a-zA-Z])\)\s+")
RE_EN_ROMAN = re.compile(r"^\s*\(([ivxlcdm]+)\)\s+", re.IGNORECASE)

# Continuation words — if text after "ARTICLE X" starts with these, it's inline text
_INLINE_CONTINUATION = {
    "of", "to", "the", "in", "for", "and", "or", "this", "that",
    "such", "herein", "hereby", "hereunder", "thereto", "thereof",
    "shall", "will", "may", "must", "not", "any", "all", "each",
    "is", "be", "are", "was", "were", "has", "have", "had",
    "by", "on", "at", "with", "from", "as", "it", "its",
    "a", "an", "no", "nor", "but", "if", "so", "yet",
}

# Attachment detection (both languages) — standalone header lines only
RE_ATTACHMENT = re.compile(
    r"^\s*(附件[一二三四五六七八九十\d]*|Appendix\s+[IVXLCDM\d]+|"
    r"Exhibit\s+[A-Z\d]+|Schedule\s+[A-Z\d]+|Annex\s+[A-Z\d]+)\s*[:：]?$",
    re.IGNORECASE,
)


def normalize_article_num(raw: str, fmt: str) -> int:
    """Normalize article number to integer for comparison."""
    raw = raw.strip()
    if fmt == "chinese" and not raw.isdigit():
        try:
            return cn2int(raw)
        except (ValueError, KeyError):
            return -1
    elif fmt == "roman":
        try:
            return roman2int(raw)
        except (ValueError, KeyError):
            return -1
    try:
        # "1.1" -> just the first part for ordering
        if "." in raw:
            return int(raw.split(".")[0])
        return int(raw)
    except ValueError:
        return -1


# ── Main scan logic ─────────────────────────────────────────────────────

def scan_structure(filepath: str) -> dict:
    text = Path(filepath).read_text(encoding="utf-8")
    lines = text.split("\n")
    lang = detect_language(text)

    articles = []
    chapters = []  # or top-level groupings
    anomalies = []
    preamble = None
    preamble_out = None

    current_chapter = None
    current_chapter_num = None
    preamble_lines = []
    in_preamble = True
    in_attachment = False
    attachment_start = None
    attachment_items = []

    article_idx = 0  # sequential index for tracking

    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue

        # Attachment detection
        if RE_ATTACHMENT.match(stripped):
            if not in_attachment:
                in_attachment = True
                attachment_start = line_no
            attachment_items.append(stripped)
            continue

        if in_attachment:
            # Exit attachment zone if article/clause numbering resumes
            if (RE_CN_ARTICLE.match(stripped) or RE_EN_ARTICLE.match(stripped) or
                RE_EN_SECTION.match(stripped) or RE_EN_CLAUSE.match(stripped)):
                in_attachment = False
            else:
                continue

        if lang in ("zh", "bilingual"):
            # Chinese chapter detection
            ch_match = RE_CN_CHAPTER.match(stripped)
            if ch_match:
                num_raw = ch_match.group(1)
                title = stripped[ch_match.end():].strip()
                num_int = normalize_article_num(num_raw, "chinese")
                current_chapter = {
                    "num": f"第{num_raw}章",
                    "num_int": num_int,
                    "title": title,
                    "line_start": line_no,
                    "article_range_start": None,
                }
                current_chapter_num = num_int
                chapters.append(current_chapter)
                in_preamble = False
                continue

            # Chinese part detection
            part_match = RE_CN_PART.match(stripped)
            if part_match:
                num_raw = part_match.group(1)
                title = stripped[part_match.end():].strip()
                chapters.append({
                    "num": f"第{num_raw}编",
                    "num_int": normalize_article_num(num_raw, "chinese"),
                    "title": title,
                    "line_start": line_no,
                    "article_range_start": None,
                    "is_part": True,
                })
                in_preamble = False
                continue

            # Chinese section detection
            sec_match = RE_CN_SECTION.match(stripped)
            if sec_match:
                num_raw = sec_match.group(1)
                title = stripped[sec_match.end():].strip()
                chapters.append({
                    "num": f"第{num_raw}节",
                    "num_int": normalize_article_num(num_raw, "chinese"),
                    "title": title,
                    "line_start": line_no,
                    "article_range_start": None,
                    "is_section": True,
                })
                in_preamble = False
                continue

            # Chinese article detection
            art_match = RE_CN_ARTICLE.match(stripped)
            if art_match:
                in_preamble = False
                num_raw = art_match.group(1)
                title = stripped[art_match.end():].strip()
                num_int = normalize_article_num(num_raw, "chinese")
                articles.append({
                    "num": f"第{num_raw}条",
                    "num_int": num_int,
                    "num_raw": num_raw,
                    "title": title,
                    "line_start": line_no,
                    "line_end": None,
                    "chapter": current_chapter["num"] if current_chapter else None,
                    "chapter_num_int": current_chapter_num,
                })
                article_idx += 1
                if current_chapter and current_chapter["article_range_start"] is None:
                    current_chapter["article_range_start"] = f"第{num_raw}条"
                if current_chapter:
                    current_chapter["article_range_end"] = f"第{num_raw}条"
                    current_chapter["article_count"] = current_chapter.get("article_count", 0) + 1
                continue

        if lang in ("en", "bilingual"):
            # English ARTICLE detection
            en_art = RE_EN_ARTICLE.match(stripped)
            if en_art:
                num_raw = en_art.group(1)
                after = stripped[en_art.end():].strip()
                # Check not inline: first word after ARTICLE should be a substantive title
                first_word = after.split()[0].strip("—-_.,;:()[]{}").lower() if after else ""
                if first_word not in _INLINE_CONTINUATION:
                    num_int = normalize_article_num(num_raw, "roman" if num_raw.isalpha() else "arabic")
                    current_chapter = {
                        "num": f"ARTICLE {num_raw}",
                        "num_int": num_int,
                        "title": after,
                        "line_start": line_no,
                        "article_range_start": None,
                    }
                    current_chapter_num = num_int
                    chapters.append(current_chapter)
                    in_preamble = False
                    continue

            # English Section detection
            en_sec = RE_EN_SECTION.match(stripped)
            if en_sec:
                num_raw = en_sec.group(1)
                after = stripped[en_sec.end():].strip()
                first_word = after.split()[0].strip("—-_.,;:()[]{}").lower() if after else ""
                # Section heading: followed by substantive text, not inline continuation
                if first_word not in _INLINE_CONTINUATION and after not in ("", ";", "."):
                    num_int = normalize_article_num(num_raw, "arabic")
                    articles.append({
                        "num": f"Section {num_raw}",
                        "num_int": num_int,
                        "num_raw": num_raw,
                        "title": after,
                        "line_start": line_no,
                        "line_end": None,
                        "chapter": current_chapter["num"] if current_chapter else None,
                        "chapter_num_int": current_chapter_num,
                    })
                    article_idx += 1
                    if current_chapter and current_chapter["article_range_start"] is None:
                        current_chapter["article_range_start"] = f"Section {num_raw}"
                    if current_chapter:
                        current_chapter["article_range_end"] = f"Section {num_raw}"
                        current_chapter["article_count"] = current_chapter.get("article_count", 0) + 1
                    in_preamble = False
                continue

            # English Clause detection
            en_cl = RE_EN_CLAUSE.match(stripped)
            if en_cl:
                num_raw = en_cl.group(1)
                after = stripped[en_cl.end():].strip()
                first_word = after.split()[0].strip("—-_.,;:()[]{}").lower() if after else ""
                if first_word not in _INLINE_CONTINUATION and after not in ("", ";", "."):
                    num_int = normalize_article_num(num_raw, "arabic")
                    articles.append({
                        "num": f"Clause {num_raw}",
                        "num_int": num_int,
                        "num_raw": num_raw,
                        "title": after,
                        "line_start": line_no,
                        "line_end": None,
                        "chapter": current_chapter["num"] if current_chapter else None,
                        "chapter_num_int": current_chapter_num,
                    })
                    article_idx += 1
                    if current_chapter and current_chapter["article_range_start"] is None:
                        current_chapter["article_range_start"] = f"Clause {num_raw}"
                    if current_chapter:
                        current_chapter["article_range_end"] = f"Clause {num_raw}"
                        current_chapter["article_count"] = current_chapter.get("article_count", 0) + 1
                    in_preamble = False
                continue

            # English numbered paragraph as clause
            en_np = RE_EN_NUMPARA.match(stripped)
            if en_np and not RE_EN_DOTTED.match(stripped):
                num_raw = en_np.group(1)
                num_int = int(num_raw)
                # Detect clause restart: when numbering drops back to 1 after having seen
                # higher numbers (party listing ends, actual clauses begin). Reset preamble.
                if articles and num_int == 1 and articles[-1]["num_int"] > 3:
                    preamble_lines = list(range(1, line_no))
                    in_preamble = False
                if num_int >= 2 or (articles and num_int == 1):
                    in_preamble = False
                title = stripped[en_np.end():].strip()
                articles.append({
                    "num": f"{num_raw}.",
                    "num_int": num_int,
                    "num_raw": num_raw,
                    "title": title,
                    "line_start": line_no,
                    "line_end": None,
                    "chapter": current_chapter["num"] if current_chapter else None,
                    "chapter_num_int": current_chapter_num,
                })
                article_idx += 1
                if current_chapter:
                    if current_chapter["article_range_start"] is None:
                        current_chapter["article_range_start"] = f"{num_raw}."
                    current_chapter["article_range_end"] = f"{num_raw}."
                    current_chapter["article_count"] = current_chapter.get("article_count", 0) + 1
                continue

        # Track preamble
        if in_preamble and not stripped.startswith("#"):
            preamble_lines.append(line_no)

    # ── Post-process: detect party listing restart ──
    # When numbering restarts from 1 after party listing, move party items to preamble
    if len(articles) >= 4 and articles[0]["num_int"] == 1:
        # Look for a clause restart: 1. after seeing 2., 3., etc.
        clause_keywords = ["confidential", "purpose", "agreement", "project",
                          "definition", "obligation", "term", "condition",
                          "represent", "warrant", "indemnif", "liability",
                          "terminat", "govern", "dispute", "notice", "payment"]
        for i in range(3, len(articles)):
            cur = articles[i]
            prev = articles[i - 1]
            # Restart detected: 1. following a higher number (3+)
            if cur["num_int"] == 1 and prev["num_int"] >= 3:
                title_lower = cur["title"].lower()
                if any(kw in title_lower for kw in clause_keywords):
                    # This is the real clause start. Move prior items to preamble.
                    moved = articles[:i]
                    articles[:] = articles[i:]
                    # Extend preamble (keep existing preamble_lines, add moved items)
                    for m in moved:
                        for ln in range(m["line_start"], (m["line_end"] or m["line_start"]) + 1):
                            if ln not in preamble_lines:
                                preamble_lines.append(ln)
                    preamble_lines.sort()
                    break

    # ── Set article line_end values ──
    for i, art in enumerate(articles):
        if i + 1 < len(articles):
            art["line_end"] = articles[i + 1]["line_start"] - 1
        else:
            # Last article extends to attachment start or end of file
            if attachment_start:
                art["line_end"] = attachment_start - 1
            else:
                art["line_end"] = len(lines)

    # ── Detect anomalies ──
    for i in range(len(articles) - 1):
        cur = articles[i]
        nxt = articles[i + 1]

        same_chapter = cur.get("chapter") == nxt.get("chapter")

        # For dotted numbering (1.1, 1.2), compare segments
        cur_raw = cur.get("num_raw", "")
        nxt_raw = nxt.get("num_raw", "")
        is_dotted = "." in cur_raw and "." in nxt_raw

        if same_chapter and not is_dotted and nxt["num_int"] > 0 and cur["num_int"] > 0:
            gap = nxt["num_int"] - cur["num_int"]
            if gap > 1:
                anomalies.append({
                    "type": "skip",
                    "detail": f'{cur["num"]} → {nxt["num"]}，间隔 {gap - 1} 条，疑似缺失',
                    "after_article": cur["num"],
                    "at_line": cur["line_start"],
                })
            elif gap == 0:
                anomalies.append({
                    "type": "duplicate",
                    "detail": f'{cur["num"]} 重复出现（行 {cur["line_start"]} 和行 {nxt["line_start"]}）',
                    "lines": [cur["line_start"], nxt["line_start"]],
                })
        elif same_chapter and is_dotted:
            # Compare last segment for dotted numbering
            cur_parts = cur_raw.split(".")
            nxt_parts = nxt_raw.split(".")
            if len(cur_parts) == len(nxt_parts):
                try:
                    cur_last = int(cur_parts[-1])
                    nxt_last = int(nxt_parts[-1])
                    gap = nxt_last - cur_last
                    if gap > 1:
                        anomalies.append({
                            "type": "skip",
                            "detail": f'{cur["num"]} → {nxt["num"]}，间隔 {gap - 1} 条，疑似缺失',
                            "after_article": cur["num"],
                            "at_line": cur["line_start"],
                        })
                    elif gap == 0:
                        anomalies.append({
                            "type": "duplicate",
                            "detail": f'{cur["num"]} 重复出现（行 {cur["line_start"]} 和行 {nxt["line_start"]}）',
                            "lines": [cur["line_start"], nxt["line_start"]],
                        })
                except ValueError:
                    pass

    # Detect mixed format within same numbering space
    chinese_articles = [a for a in articles if "条" in a["num"]]
    digit_articles = [a for a in articles if a["num_raw"].isdigit() and "条" not in a["num"]]
    if chinese_articles and digit_articles:
        mid_line = (chinese_articles[-1]["line_start"] + digit_articles[0]["line_start"]) // 2
        anomalies.append({
            "type": "format_mix",
            "detail": f"编号在第{mid_line}行附近从中文格式切换为数字格式",
            "at_line": mid_line,
        })

    # ── Detect numbering space ──
    numbering_space = "global"
    if chapters and len(chapters) > 1:
        # Check if first article in second chapter resets to 1
        ch2_articles = [a for a in articles if a.get("chapter_num_int") == chapters[1].get("num_int")]
        if ch2_articles and ch2_articles[0]["num_int"] <= 5:
            numbering_space = "per_chapter"

    # ── Build result ──
    scheme = {
        "language": lang,
        "numbering_space": numbering_space,
    }
    if lang in ("zh", "bilingual"):
        scheme.update({
            "has_part": any(c.get("is_part") for c in chapters),
            "has_chapter": any(c for c in chapters if not c.get("is_part") and not c.get("is_section")),
            "has_section": any(c.get("is_section") for c in chapters),
            "article_format": "chinese" if chinese_articles else "arabic",
            "sub_item_format": "chinese_paren",
        })
    if lang in ("en", "bilingual"):
        scheme.update({
            "has_article": any("ARTICLE" in c.get("num", "") for c in chapters),
            "section_format": "dotted" if any("." in a.get("num_raw", "") for a in articles) else "numeric",
        })

    preamble_out = None
    if preamble_lines:
        p_start = min(preamble_lines)
        p_end = max(preamble_lines)
        p_text = " ".join(lines[p_start - 1:p_end]).strip()[:200]
        preamble_out = {"line_start": p_start, "line_end": p_end, "preview": p_text}

    attachment_out = None
    if attachment_items:
        attachment_out = {"line_start": attachment_start, "items": attachment_items}

    return {
        "file": Path(filepath).name,
        "total_chars": len(text),
        "total_lines": len(lines),
        "numbering_scheme": scheme,
        "chapters": chapters,
        "articles": articles,
        "total_articles": len(articles),
        "anomalies": anomalies,
        "preamble": preamble_out,
        "attachment_list": attachment_out,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python scan-structure.py <contract.md> [output.json]", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    result = scan_structure(filepath)

    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    json_str = json.dumps(result, ensure_ascii=False, indent=2)

    if output_path:
        Path(output_path).write_text(json_str, encoding="utf-8")
        print(f"Written to {output_path}", file=sys.stderr)
    else:
        print(json_str)


if __name__ == "__main__":
    main()
