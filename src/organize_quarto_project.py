from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "markdown"


def read_title(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def quote_yaml(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def md_to_qmd(md_path: Path) -> tuple[Path, str]:
    markdown = md_path.read_text(encoding="utf-8")
    title = read_title(markdown, md_path.stem)
    qmd_path = md_path.with_suffix(".qmd")

    body = re.sub(r"^# .+\n+", "", markdown, count=1)
    front_matter = [
        "---",
        f"title: {quote_yaml(title)}",
        "toc: true",
        "---",
        "",
    ]
    qmd_path.write_text("\n".join(front_matter) + body.rstrip() + "\n", encoding="utf-8")
    return qmd_path, title


def build_index(entries: list[tuple[Path, str]]) -> None:
    lines = [
        "---",
        'title: "Curso Java - Slides Convertidos"',
        "toc: false",
        "---",
        "",
        "# Curso Java - Slides Convertidos",
        "",
        "Este projeto Quarto foi gerado a partir dos PDFs da pasta original.",
        "Cada aula foi organizada como um capítulo, mantendo a imagem de cada página e o texto extraído logo abaixo.",
        "",
        "## Aulas",
        "",
    ]
    for qmd_path, title in entries:
        lines.append(f"- [{title}]({qmd_path.name})")
    (SOURCE_DIR / "index.qmd").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_quarto_config(entries: list[tuple[Path, str]]) -> None:
    lines = [
        "project:",
        "  type: book",
        "  output-dir: _book",
        "",
        "book:",
        '  title: "Curso Java - Slides Convertidos"',
        '  language: "pt-BR"',
        "  chapters:",
        "    - index.qmd",
    ]
    for qmd_path, _ in entries:
        lines.append(f"    - {qmd_path.name}")

    lines.extend(
        [
            "",
            "format:",
            "  html:",
            "    theme: cosmo",
            "    toc: true",
            "    number-sections: false",
            "    fig-responsive: true",
            "    code-copy: true",
            "",
            "execute:",
            "  freeze: auto",
            "",
            "lang: pt-BR",
        ]
    )
    (SOURCE_DIR / "_quarto.yml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    md_files = sorted(
        [path for path in SOURCE_DIR.glob("*.md") if path.name != "index.md"],
        key=lambda path: path.name.lower(),
    )
    entries = [md_to_qmd(path) for path in md_files]
    build_index(entries)
    build_quarto_config(entries)
    print(f"Projeto Quarto criado em: {SOURCE_DIR}")
    print(f"Arquivos QMD gerados: {len(entries) + 1}")


if __name__ == "__main__":
    main()
