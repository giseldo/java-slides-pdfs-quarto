from pathlib import Path
import re
import unicodedata

import fitz


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "markdown"
IMAGE_ZOOM = 2.0


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_text = re.sub(r"[^A-Za-z0-9]+", "-", ascii_text).strip("-").lower()
    return ascii_text or "pdf"


def clean_text(text: str) -> str:
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").split("\n")]
    cleaned = []
    blank = False
    for line in lines:
        if line.strip():
            cleaned.append(line)
            blank = False
        elif not blank:
            cleaned.append("")
            blank = True
    return "\n".join(cleaned).strip()


def unique_slug(base: str, seen: set[str]) -> str:
    slug = base
    index = 2
    while slug in seen:
        slug = f"{base}-{index}"
        index += 1
    seen.add(slug)
    return slug


def convert_pdf(pdf_path: Path, slug: str) -> tuple[Path, int]:
    doc = fitz.open(pdf_path)
    page_count = len(doc)
    image_dir = OUT / f"{slug}_images"
    image_dir.mkdir(parents=True, exist_ok=True)

    md_path = OUT / f"{slug}.md"
    title = pdf_path.stem
    lines = [f"# {title}", "", f"Arquivo original: `{pdf_path.name}`", ""]

    matrix = fitz.Matrix(IMAGE_ZOOM, IMAGE_ZOOM)
    for page_index, page in enumerate(doc, start=1):
        image_name = f"page-{page_index:03d}.png"
        image_path = image_dir / image_name
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        pix.save(image_path)

        rel_image = f"{image_dir.name}/{image_name}"
        page_text = clean_text(page.get_text("text", sort=True))

        lines.extend(
            [
                f"## Página {page_index}",
                "",
                f"![Página {page_index}]({rel_image})",
                "",
            ]
        )
        if page_text:
            lines.extend([page_text, ""])
        else:
            lines.extend(["_Sem texto extraível nesta página._", ""])

    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    doc.close()
    return md_path, page_count


def main() -> None:
    OUT.mkdir(exist_ok=True)
    pdfs = sorted(ROOT.glob("*.pdf"), key=lambda path: path.name.lower())
    seen: set[str] = set()
    index_lines = ["# PDFs convertidos para Markdown", ""]

    for pdf_path in pdfs:
        slug = unique_slug(slugify(pdf_path.stem), seen)
        md_path, page_count = convert_pdf(pdf_path, slug)
        index_lines.append(f"- [{pdf_path.stem}]({md_path.name}) - {page_count} páginas")
        print(f"OK {pdf_path.name} -> {md_path.relative_to(ROOT)}")

    (OUT / "index.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    print(f"\nConvertidos: {len(pdfs)} PDFs")
    print(f"Saida: {OUT}")


if __name__ == "__main__":
    main()
