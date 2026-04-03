#!/usr/bin/env python3
"""Generate professor persona, course brain, and review guide from extracted materials."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from materials_lib import (
    detect_exam_styles,
    extract_bullets,
    extract_keywords,
    load_extract_index,
    normalize_text,
    split_sentences,
    top_sentences,
)


CONFIDENCE_NOTE = "> 注意：当前材料不足，以下结论含推断成分，请优先补充历年题、讲课转写或聊天答疑。"


def read_text(path: Path) -> str:
    return normalize_text(path.read_text(encoding="utf-8"))


def load_texts(root: Path) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for record in load_extract_index(root):
        extracted_path = record.get("extracted_path")
        if record.get("extract_status") != "ok" or not extracted_path:
            continue
        text_path = root / str(extracted_path)
        if text_path.exists():
            grouped[str(record["category"])].append(read_text(text_path))
    return grouped


def take_top(items: list[str], limit: int = 5) -> list[str]:
    seen = set()
    result = []
    for item in items:
        cleaned = item.strip(" -")
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        result.append(cleaned)
        if len(result) >= limit:
            break
    return result


def normalize_line(text: str) -> str:
    text = re.sub(r"^(?:[0-9]+[.)、]|[一二三四五六七八九十]+[、.)）])\s*", "", text).strip()
    text = text.replace("：", ":")
    if ":" in text and len(text.split(":", 1)[0]) <= 6:
        text = text.split(":", 1)[1].strip()
    return text.strip(" -。！？?")


def infer_topics(primary_texts: list[str], support_texts: list[str], fallback: str) -> list[str]:
    bullets = []
    for text in primary_texts:
        bullets.extend(extract_bullets(text))
    cleaned = []
    for bullet in bullets:
        line = normalize_line(bullet)
        if not line or len(line) < 4 or len(line) > 26:
            continue
        if line.startswith("#") or "%" in line:
            continue
        if any(flag in line for flag in ("考核方式", "教学目标", "说明", "课程大纲", "平时作业", "期中测试", "期末考试", "重点章节", "课程强调")):
            continue
        cleaned.append(line)
    if cleaned:
        return take_top(cleaned, limit=6)

    keywords = extract_keywords(primary_texts + support_texts, limit=8)
    return keywords or [fallback]


def infer_traps(texts: list[str]) -> list[str]:
    traps = []
    patterns = [
        r"不得满分[^。\n]*",
        r"酌情扣分[^。\n]*",
        r"不行[^。\n]*",
        r"不要[^。\n]*",
        r"不会[^。\n]*",
        r"条件[^。\n]*",
    ]
    for text in texts:
        for pattern in patterns:
            traps.extend(re.findall(pattern, text))
        for sentence in split_sentences(text):
            if len(sentence) < 7:
                continue
            if "学生" in sentence and "老师" in sentence:
                continue
            if any(flag in sentence for flag in ("扣分", "条件", "依据", "不要", "不会", "先")):
                traps.append(sentence)
    cleaned = [normalize_line(item) for item in traps]
    cleaned = [item for item in cleaned if len(item) >= 6]
    return take_top(cleaned, limit=6)


def infer_catchphrases(texts: list[str]) -> list[str]:
    sentences = top_sentences(texts, limit=10)
    quotes = [normalize_line(sentence) for sentence in sentences if any(flag in sentence for flag in ("要", "不要", "先", "看", "讲过", "重复", "定义"))]
    return take_top(quotes or sentences, limit=5)


def infer_style(persona_texts: list[str]) -> list[str]:
    joined = "\n".join(persona_texts)
    style = []
    if re.search(r"先[^。\n]{0,18}(看|讲|写|说)", joined):
        style.append("喜欢先把前提、定义或背景说清楚，再进入计算或结论。")
    if re.search(r"不要|不行|先", joined):
        style.append("会直接指出学生的偷懒做法，语气克制但不纵容。")
    if re.search(r"重复|每年|讲过", joined):
        style.append("会通过重复强调来暗示重要性，而不是直接说“这题必考”。")
    if not style:
        style.append("表达风格偏规则化，重视步骤依据和解题路径。")
    return take_top(style, limit=4)


def build_persona(meta: dict[str, object], texts: dict[str, list[str]]) -> str:
    persona_sources = texts.get("transcripts", []) + texts.get("chats", []) + texts.get("notices", [])
    catchphrases = infer_catchphrases(persona_sources)
    style = infer_style(persona_sources)
    reactions = []
    for text in texts.get("chats", []):
        for sentence in split_sentences(text):
            if any(flag in sentence for flag in ("不直接回答", "先看", "课堂例", "依据")):
                reactions.append(normalize_line(sentence))
    signals = []
    for text in texts.get("transcripts", []):
        for sentence in split_sentences(text):
            if any(flag in sentence for flag in ("一定", "每年", "这一步", "重点", "自己推")):
                signals.append(normalize_line(sentence))

    low_confidence = not persona_sources
    lines = [f"# {meta['name']} - Persona", ""]
    if low_confidence:
        lines.extend([CONFIDENCE_NOTE, ""])
    lines.extend(
        [
            "## Identity",
            "",
            f"- School: {meta['profile'].get('school') or 'unknown'}",
            f"- Department: {meta['profile'].get('department') or 'unknown'}",
            f"- Course: {meta['profile'].get('course') or 'unknown'}",
            "",
            "## Catchphrases",
            "",
        ]
    )
    lines.extend(f'- "{item}"' for item in (catchphrases or ["人格证据不足，建议补充讲课转写或群聊记录。"]))
    lines.extend(["", "## Speaking Style", ""])
    lines.extend(f"- {item}" for item in style)
    lines.extend(["", "## How This Professor Answers Students", ""])
    lines.extend(f'- "{item}"' for item in (take_top(reactions, 4) or ["材料不足，无法稳定判断答疑风格。"]))
    lines.extend(["", "## How Importance Is Signaled", ""])
    lines.extend(f'- "{item}"' for item in (take_top(signals, 4) or ["更常通过重复、强调条件或纠错来暗示重要性。"]))
    return "\n".join(lines).rstrip() + "\n"


def build_course(meta: dict[str, object], texts: dict[str, list[str]]) -> str:
    course_sources = texts.get("exams", []) + texts.get("assignments", []) + texts.get("syllabus", []) + texts.get("slides", [])
    transcript_sources = texts.get("transcripts", [])
    topics = infer_topics(texts.get("syllabus", []) + texts.get("slides", []), course_sources + transcript_sources, fallback="待补充课程材料")
    exam_styles = detect_exam_styles(texts.get("exams", []) + texts.get("assignments", []))
    traps = infer_traps(texts.get("exams", []) + texts.get("assignments", []) + texts.get("chats", []) + transcript_sources)
    low_confidence = not texts.get("exams")

    lines = [f"# {meta['profile'].get('course', 'Course')} - Course Brain", ""]
    if low_confidence:
        lines.extend([CONFIDENCE_NOTE, ""])
    lines.extend(["## Course Overview", "", f"{meta['profile'].get('course', '这门课')} 的高频信号来自现有材料，而不是通用教材目录。", ""])
    lines.extend(["## Core Topics", ""])
    lines.extend(f"- {item}" for item in topics)
    lines.extend(["", "## Exam Signals", ""])
    lines.extend(f"- {item}" for item in exam_styles)
    lines.extend(["", "## Common Traps", ""])
    lines.extend(f"- {item}" for item in (traps or ["当前材料里没有足够明确的扣分信号。"]))
    return "\n".join(lines).rstrip() + "\n"


def build_review(meta: dict[str, object], texts: dict[str, list[str]]) -> str:
    review_texts = texts.get("exams", []) + texts.get("assignments", []) + texts.get("transcripts", []) + texts.get("syllabus", [])
    topics = infer_topics(texts.get("syllabus", []) + texts.get("slides", []), review_texts, fallback="建议先补充至少一份考试题或课堂转写")
    traps = infer_traps(review_texts + texts.get("chats", []))
    likely_questions = []
    for text in texts.get("exams", []) + texts.get("assignments", []):
        for sentence in split_sentences(text):
            if any(flag in sentence for flag in ("求", "证明", "说明", "判断", "分析")):
                likely_questions.append(normalize_line(sentence))
    if not likely_questions:
        likely_questions = [f"围绕 `{topic}` 组织一道计算、解释或证明类题目。" for topic in topics[:3]]
    low_confidence = not texts.get("exams")

    lines = [f"# {meta['profile'].get('course', 'Course')} - Review Guide", ""]
    if low_confidence:
        lines.extend([CONFIDENCE_NOTE, ""])
    lines.extend(["## 30 秒总结", "", f"先抓 `{', '.join(topics[:3])}`，再回看材料里反复出现的条件、步骤和扣分点。", ""])
    lines.extend(["## Must Know", ""])
    lines.extend(f"- {item}" for item in topics)
    lines.extend(["", "## 老师可能会这么问", ""])
    lines.extend(f'- "{item}"' for item in take_top(likely_questions, 5))
    lines.extend(["", "## 高频扣分点", ""])
    lines.extend(f"- {item}" for item in (traps or ["材料不足，建议先查看作业批注、试题说明或答疑记录。"]))
    lines.extend(["", "## 考前一晚清单", ""])
    last_night = [
        f"先复盘 `{topics[0]}` 相关题型，再看老师反复强调的依据和条件。",
        "把不会的题分成：定义不会、步骤不会、条件不会，分别补。",
        "优先重做历年题和作业最后的大题，不要只看 PPT 标题。",
    ]
    lines.extend(f"- {item}" for item in last_night)
    return "\n".join(lines).rstrip() + "\n"


def update_meta(root: Path, status: str) -> None:
    meta_path = root / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta.setdefault("artifacts", {})
    meta["artifacts"]["build_status"] = status
    meta["artifacts"]["last_built_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("professor_dir", help="Professor workspace directory")
    args = parser.parse_args(argv)

    root = Path(args.professor_dir).resolve()
    meta_path = root / "meta.json"
    if not meta_path.exists():
        raise SystemExit(f"meta.json not found: {meta_path}")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    texts = load_texts(root)

    (root / "persona.md").write_text(build_persona(meta, texts), encoding="utf-8")
    (root / "course.md").write_text(build_course(meta, texts), encoding="utf-8")
    (root / "review_guide.md").write_text(build_review(meta, texts), encoding="utf-8")
    update_meta(root, "generated")

    print("generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
