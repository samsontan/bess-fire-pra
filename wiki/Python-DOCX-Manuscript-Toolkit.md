---
tags: [toolkit, python-docx, manuscript, Word, automation, reusable]
date: 2026-05-17
---

# Python-DOCX Manuscript Building Toolkit

Patterns established for BESS paper (v9->v11). Copy for all future journal papers.

## Cross-Run Text Replacement (ALWAYS use this)

Word splits text across multiple `<w:r>` runs at format boundaries. Never replace run-by-run.

```python
def replace_in_para(para, old, new):
    full = ''.join(r.text or '' for r in para.runs)
    if old not in full:
        return False
    replaced = full.replace(old, new, 1)
    if para.runs:
        para.runs[0].text = replaced
        for r in para.runs[1:]:
            r.text = ''
    return True
```

## Caption Guard (ALWAYS add before any figure number replacement)

```python
import re
IS_CAPTION = re.compile(r'^Figure \d+[:\.]', re.IGNORECASE)

for para in all_paragraphs(doc):
    if IS_CAPTION.match(para.text.strip()):
        continue    # never touch caption lines
    replace_in_para(para, old, new)
```

Without this, `('Figure 4', 'Figure 3')` will corrupt caption text.

## All-Paragraphs Iterator (ALWAYS use, not doc.paragraphs)

```python
def all_paragraphs(doc):
    for para in doc.paragraphs:
        yield para
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    yield para
```

## Tracked Changes Stripping (lxml, NOT Word COM)

```python
from docx.oxml.ns import qn

def strip_tracked_changes(doc):
    root = doc.element.body
    changed = True
    while changed:
        changed = False
        for ins in root.findall(f'.//{qn("w:ins")}'):
            parent = ins.getparent()
            idx = list(parent).index(ins)
            for child in list(ins):
                ins.remove(child); parent.insert(idx, child); idx += 1
            parent.remove(ins); changed = True
        for del_elem in root.findall(f'.//{qn("w:del")}'):
            parent = del_elem.getparent()
            if parent is not None:
                parent.remove(del_elem); changed = True
        for tag in ('rPrChange', 'pPrChange', 'sectPrChange'):
            for elem in root.findall(f'.//{qn(f"w:{tag}")}'):
                p2 = elem.getparent()
                if p2 is not None:
                    p2.remove(elem); changed = True
```

## Author Block Rebuild (superscript affiliations)

```python
from docx.oxml.ns import qn

def clear_runs(para):
    for child in list(para._element):
        if child.tag in (qn('w:r'), qn('w:hyperlink'), qn('w:bookmarkStart'), qn('w:bookmarkEnd')):
            para._element.remove(child)

def add_run(para, text, superscript=False, italic=False, bold=False):
    run = para.add_run(text)
    run.font.superscript = superscript
    if italic: run.italic = True
    if bold: run.bold = True
    return run

# Usage:
clear_runs(author_para)
author_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_run(author_para, 'Samson Tan')
add_run(author_para, '1,3', superscript=True)
add_run(author_para, ', Paul Joseph')
add_run(author_para, '1', superscript=True)
```

## Insert Paragraph After Anchor

```python
from docx.oxml import OxmlElement
from copy import deepcopy

def insert_para_after(anchor_elem, style_para):
    new_p = OxmlElement('w:p')
    pPr = style_para._element.find(qn('w:pPr'))
    if pPr is not None:
        new_p.append(deepcopy(pPr))
    anchor_elem.addnext(new_p)   # key: addnext not insert
    return new_p
```

## Paragraph Deletion

```python
para._element.getparent().remove(para._element)
# Never: doc.paragraphs.remove(para)  -- does not exist
```

## Word COM PDF Export

```python
import subprocess, os, win32com.client

subprocess.run(['taskkill', '/F', '/IM', 'WINWORD.EXE'], capture_output=True)

word = win32com.client.Dispatch('Word.Application')
word.Visible = False
try:
    wdoc = word.Documents.Open(os.path.abspath(docx_path))
    wdoc.SaveAs(os.path.abspath(pdf_path), FileFormat=17)
    wdoc.Close(False)
finally:
    try: word.Quit()
    except: pass
```

Always use `os.path.abspath()`. FileFormat=17 = PDF.

## FDS Figure White-Out (remove title strip)

```python
from PIL import Image, ImageDraw

img = Image.open(src_png)
draw = ImageDraw.Draw(img)
draw.rectangle([0, 0, img.width, 40], fill='white')
img.save(dst_png)
```

## Script Template (with dry-run flag)

```python
import sys
sys.stdout.reconfigure(encoding='utf-8')
DRY_RUN = '--execute' not in sys.argv

def act(label, fn, *args):
    tag = '[DRY]' if DRY_RUN else '[DO ]'
    print(f'{tag} {label}')
    if not DRY_RUN:
        fn(*args)

# Usage:
act(f'move {src} -> {dst}', shutil.move, src, dst)
```

## Reference Scripts

| Script | What it shows |
|--------|--------------|
| `08_MANUSCRIPT_Build-Scripts\finalize_manuscript_v9.py` | Figure renumbering + image swap + FDS white-out |
| `08_MANUSCRIPT_Build-Scripts\build_v10_citations.py` | Citation insertion + reference reordering |
| `08_MANUSCRIPT_Build-Scripts\prepare_bess_draft_for_reviewers.py` | Tracked change strip + (EN) removal + 4-author block |
| `08_MANUSCRIPT_Build-Scripts\save_as_v11.py` | Copy canonical + PDF export |
