#!/usr/bin/env python3
"""Check that slides.md keeps the Table of Contents consistent.

Slidev's <Toc> lists every slide that isn't marked `hideInToc: true`, using
its first `# ` heading. This deck's convention is that only section slides
(`layout: section`) appear in the TOC, and each one links back to it.

Checks:
  - exactly one slide has `routeAlias: toc` and a <Toc> component
  - every section slide has a `# ` title, is not hidden, and has
    <Link to="toc" .../>
  - every other slide (besides the title and TOC slides) is hidden
  - no slide has frontmatter but no content (a stray `---` block)

Prints the TOC entries in order, and exits non-zero on any problem.
"""
import re
import sys

FRONTMATTER_KEY = re.compile(r"^[A-Za-z][A-Za-z0-9_]*:")


def parse_slides(text):
    """Split a Slidev markdown file into (line_number, frontmatter, body) slides."""
    lines = text.split("\n")
    slides = []
    i = 0
    # The first slide's frontmatter is the headmatter between the first two '---'
    if lines and lines[0] == "---":
        j = 1
        while j < len(lines) and lines[j] != "---":
            j += 1
        start, fm, i = 1, lines[1:j], j + 1
    else:
        start, fm = 1, []
    body, in_code = [], False
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            in_code = not in_code
        if line == "---" and not in_code:
            slides.append((start, fm, body))
            start, fm, body = i + 1, [], []
            # A '---' followed by key: value lines and another '---' is frontmatter
            j = i + 1
            while j < len(lines) and FRONTMATTER_KEY.match(lines[j]):
                j += 1
            if j > i + 1 and j < len(lines) and lines[j] == "---":
                fm = lines[i + 1:j]
                i = j
            i += 1
            continue
        body.append(line)
        i += 1
    slides.append((start, fm, body))
    return slides


def main(path):
    slides = parse_slides(open(path, encoding="utf-8").read())
    errors, toc, toc_slides = [], [], 0

    for n, (line, fm, body) in enumerate(slides, 1):
        keys = dict(l.split(":", 1) for l in fm if ":" in l)
        keys = {k.strip(): v.strip() for k, v in keys.items()}
        text = "\n".join(body)
        title = next((l[2:].strip() for l in body if l.startswith("# ")), None)
        hidden = keys.get("hideInToc") == "true"
        where = f"{path}:{line} (slide {n}, {title or 'untitled'!r})"

        if keys.get("routeAlias") == "toc":
            toc_slides += 1
            if "<Toc" not in text:
                errors.append(f"{where}: routeAlias toc but no <Toc> component")

        if keys.get("layout") == "section":
            if hidden:
                errors.append(f"{where}: section slide is hidden from the TOC")
            if not title:
                errors.append(f"{where}: section slide has no '# ' title")
            if '<Link to="toc"' not in text:
                errors.append(f'{where}: section slide has no <Link to="toc"/> back link')
        elif not hidden:
            errors.append(f"{where}: appears in the TOC but is not a section slide "
                          "(add 'hideInToc: true' or 'layout: section')")

        if fm and not text.strip():
            errors.append(f"{where}: frontmatter with no content (stray '---' block?)")

        if not hidden and title:
            toc.append(title)

    if toc_slides != 1:
        errors.append(f"{path}: expected exactly one slide with 'routeAlias: toc', found {toc_slides}")

    print(f"{len(slides)} slides, {len(toc)} TOC entries:")
    for i, t in enumerate(toc, 1):
        print(f"  {i}. {t}")
    for e in errors:
        print(f"error: {e}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "slides.md"))
