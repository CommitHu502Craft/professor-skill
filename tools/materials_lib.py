#!/usr/bin/env python3
"""Shared helpers for professor material extraction and synthesis."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable


MATERIAL_DIRS = [
    "slides",
    "syllabus",
    "exams",
    "assignments",
    "transcripts",
    "chats",
    "notices",
    "misc",
]

CATEGORIES = {
    "slides": {".pdf", ".ppt", ".pptx", ".key"},
    "syllabus": {".md", ".pdf", ".doc", ".docx"},
    "exams": {".pdf", ".doc", ".docx", ".txt", ".md"},
    "assignments": {".pdf", ".doc", ".docx", ".txt", ".md"},
    "transcripts": {".txt", ".md", ".srt"},
    "chats": {".txt", ".md", ".json", ".csv"},
    "notices": {".txt", ".md", ".pdf"},
}

TEXT_SUFFIXES = {".txt", ".md", ".csv", ".json", ".srt"}
EXTRACTABLE_SUFFIXES = TEXT_SUFFIXES | {".pdf", ".pptx", ".docx"}

STOP_WORDS = {
    "the",
    "and",
    "for",
    "that",
    "with",
    "this",
    "from",
    "have",
    "will",
    "your",
    "into",
    "course",
    "老师",
    "这个",
    "一个",
    "不是",
    "我们",
    "你们",
    "以及",
    "如果",
    "内容",
    "重点",
    "考试",
    "课堂",
    "同学",
    "作业",
    "例题",
    "问题",
    "要求",
    "什么",
}


def infer_category(path: Path) -> str:
    lower_parts = {part.lower() for part in path.parts}
    for category in CATEGORIES:
        if category in lower_parts:
            return category

    suffix = path.suffix.lower()
    for category, suffixes in CATEGORIES.items():
        if suffix in suffixes:
            return category
    return "misc"


def read_text_best_effort(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gbk"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return ""


def normalize_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extracted_relative_path(materials_root: Path, source_file: Path) -> Path:
    relative = source_file.relative_to(materials_root)
    return Path("exports") / "extracted" / relative.with_suffix(relative.suffix + ".txt")


def load_extract_index(root: Path) -> list[dict[str, object]]:
    index_path = root / "exports" / "extracted" / "index.json"
    if not index_path.exists():
        return []
    return json.loads(index_path.read_text(encoding="utf-8"))


def save_extract_index(root: Path, records: list[dict[str, object]]) -> None:
    index_path = root / "exports" / "extracted" / "index.json"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def keyword_candidates(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}|[\u4e00-\u9fff]{2,8}", text.lower())


def extract_keywords(texts: Iterable[str], limit: int = 12) -> list[str]:
    counter: Counter[str] = Counter()
    for text in texts:
        for token in keyword_candidates(text):
            if token in STOP_WORDS or token.isdigit():
                continue
            counter[token] += 1
    return [word for word, _ in counter.most_common(limit)]


def split_sentences(text: str) -> list[str]:
    chunks = re.split(r"[。\n!?！？]+", text)
    return [chunk.strip() for chunk in chunks if len(chunk.strip()) >= 6]


def top_sentences(texts: Iterable[str], limit: int = 6) -> list[str]:
    counter: Counter[str] = Counter()
    for text in texts:
        for sentence in split_sentences(text):
            if len(sentence) > 80:
                continue
            counter[sentence] += 1
    return [sentence for sentence, _ in counter.most_common(limit)]


def detect_exam_styles(texts: Iterable[str]) -> list[str]:
    patterns = [
        ("证明题", re.compile(r"证明|充要条件|当且仅当")),
        ("计算题", re.compile(r"计算|求|化为|求出")),
        ("简答题", re.compile(r"简答|说明|解释")),
        ("分析题", re.compile(r"分析|讨论|比较")),
        ("选择/填空", re.compile(r"选择|填空")),
    ]
    joined = "\n".join(texts)
    found = [label for label, pattern in patterns if pattern.search(joined)]
    return found or ["题型信号不足"]


def extract_bullets(text: str) -> list[str]:
    bullets = []
    for line in text.splitlines():
        stripped = line.strip().lstrip("-*0123456789.、）)(").strip()
        if len(stripped) >= 6:
            bullets.append(stripped)
    return bullets

