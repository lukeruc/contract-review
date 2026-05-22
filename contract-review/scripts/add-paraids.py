#!/usr/bin/env python3
"""
Add w14:paraId attributes to all paragraphs in a .docx file.

Usage:
    python add-paraids.py input.docx

Modifies the file in place. docx-mcp requires w14:paraId on every <w:p>
to locate paragraphs — older Word versions often omit these attributes.
"""

import zipfile
import hashlib
import os
import io
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W14 = "http://schemas.microsoft.com/office/word/2010/wordml"


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Add w14:paraId attributes to all paragraphs in a .docx"
    )
    parser.add_argument("input", help="Input .docx path (modified in place)")
    args = parser.parse_args()

    path = args.input

    # Read entire zip into memory
    with zipfile.ZipFile(path, "r") as zf:
        data = {name: zf.read(name) for name in zf.namelist()}

    tree = etree.fromstring(data["word/document.xml"])

    count = 0
    for p in tree.iter(f"{{{W}}}p"):
        if p.get(f"{{{W14}}}paraId"):
            continue
        text = "".join(p.itertext()).strip()[:100]
        h = hashlib.md5(f"{count}:{text}".encode()).hexdigest()[:8]
        pid = format(int(h, 16) & 0x7FFFFFFF, "08X")
        p.set(f"{{{W14}}}paraId", pid)
        count += 1

    if count == 0:
        print("All paragraphs already have w14:paraId — nothing to do.")
        return

    data["word/document.xml"] = etree.tostring(
        tree, xml_declaration=True, encoding="UTF-8", standalone=True
    )

    # Write back
    tmp = path + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in data.items():
            zf.writestr(name, content)
    os.replace(tmp, path)

    print(f"Added w14:paraId to {count} paragraphs in {os.path.basename(path)}")


if __name__ == "__main__":
    main()
