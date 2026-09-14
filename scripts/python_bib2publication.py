#!/usr/bin/env python3
"""
读取 _bibliography/papers.bib，为每篇论文生成一个 Markdown 文件到 _publications/
支持 @string 宏展开、特殊字符处理、文件名去重
"""

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
import os
import re
import hashlib

BIB_FILE = "_bibliography/groupPapers.bib"
OUTPUT_DIR = "_publications"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def slugify(text, max_len=60):
    """生成文件名安全的 slug"""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')[:max_len]


def format_authors(author_str):
    """把 'Last, First and Last2, First2' 转为 'F. Last, F2. Last2'"""
    if not author_str:
        return ""
    authors = [a.strip() for a in author_str.split(" and ")]
    formatted = []
    for a in authors:
        if "," in a:
            last, first = [x.strip() for x in a.split(",", 1)]
            initials = " ".join([f"{n[0]}." for n in first.split() if n])
            formatted.append(f"{initials} {last}")
        else:
            parts = a.strip().split()
            if len(parts) > 1:
                initials = " ".join([f"{n[0]}." for n in parts[:-1]])
                formatted.append(f"{initials} {parts[-1]}")
            else:
                formatted.append(a.strip())
    return ", ".join(formatted)

def format_authors_long_name(author_str):
    """把 'Last, First and Last2, First2' 转为 'First Last, First2 Last2'"""
    if not author_str:
        return ""
    authors = [a.strip() for a in author_str.split(" and ")]
    formatted = []
    for a in authors:
        if "," in a:
            last, first = [x.strip() for x in a.split(",", 1)]
            formatted.append(f"{first} {last}")
        else:
            formatted.append(a.strip())
    return ", ".join(formatted)


def clean_text(text):
    """清理 BibTeX 特殊字符"""
    if not text:
        return ""
    text = text.replace("{", "").replace("}", "")
    text = text.replace("\\&", "&")
    text = text.replace("\\%", "%")
    text = text.replace("\\_", "_")
    text = text.replace("\\ ", " ")       # ← 新增：处理 \ 空格
    text = re.sub(r'\\[a-zA-Z]+', '', text)  # 去掉 LaTeX 命令
    text = re.sub(r'\s+', ' ', text)          # 合并多余空格
    return text.strip()


def parse_bib():
    """解析 BibTeX 文件，自动展开 @string 宏"""
    parser = BibTexParser(common_strings=True)
    parser.ignore_nonstandard_types = False
    parser.homogenize_fields = False
    parser.customization = convert_to_unicode

    with open(BIB_FILE, "r", encoding="utf-8") as f:
        bib_database = bibtexparser.load(f, parser=parser)

    return bib_database.entries


def generate_markdown(entry):
    """根据 BibTeX 条目生成 Jekyll 的 Markdown 文件"""
    title = clean_text(entry.get("title", "Untitled"))
    authors = format_authors(entry.get("author", ""))
    year = entry.get("year", "n.d.")
    venue = clean_text(
        entry.get("journal")
        or entry.get("booktitle")
        or entry.get("publisher", "")
    )
    doi = entry.get("doi", "")
    url = entry.get("url", "")
    pages = entry.get("pages", "")
    volume = entry.get("volume", "")
    number = entry.get("number", "")

    # 生成唯一文件名，避免同名论文冲突
    slug = slugify(title)
    short_hash = hashlib.md5(title.encode()).hexdigest()[:6]
    filename = f"{year}-{slug}-{short_hash}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)

    # 构建 citation 字符串
    #citation = f'{authors}. "{title}."'
    citation = f'{authors}.'
    if venue:
        citation += f" {venue},"
    if volume:
        citation += f" vol. {volume},"
    if number:
        citation += f" no. {number},"
    if pages:
        citation += f" pp. {pages.replace('--', '–')},"
    citation += f" {year}."
    citation = citation.replace(",,", ",").replace(" ,", ",").strip()

    # 构建链接
    links = []
    if doi:
        links.append(f"[**DOI**](https://doi.org/{doi})")
    if url:
        links.append(f"[**PDF**]({url})")

    content = f"""---
title: "{title}"
collection: publications
category: manuscripts
permalink: /publication/{year}-{slug}-{short_hash}
excerpt: '{venue} ({year})'
date: {year}-01-01
venue: '{venue}'
paperurl: '{url if url else (f"https://doi.org/{doi}" if doi else "")}'
citation: '{citation}'
---

**Authors:** {authors}

**Venue:** {venue} ({year})

{" | ".join(links)}
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filename


def main():
    entries = parse_bib()
    print(f"📚 读取到 {len(entries)} 篇论文，开始生成 Markdown 文件...")

    # 清理旧文件
    for f in os.listdir(OUTPUT_DIR):
        if f.endswith(".md"):
            os.remove(os.path.join(OUTPUT_DIR, f))

    for entry in entries:
        filename = generate_markdown(entry)
        print(f"{filename}")

    print(f"\n 完成！共生成 {len(entries)} 个文件，位于 {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()