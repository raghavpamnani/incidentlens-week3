import csv
import hashlib
import re
from pathlib import Path

from incidentlens.models import Chunk


def read_pages(path: Path, pdf_parser: str = "pdfplumber") -> list[tuple[int | None, str, str]]:
    if path.suffix.lower() == ".pdf":
        if pdf_parser == "docling":
            from docling.datamodel.base_models import InputFormat
            from docling.datamodel.pipeline_options import PdfPipelineOptions
            from docling.document_converter import DocumentConverter, PdfFormatOption

            options = PdfPipelineOptions(do_ocr=False)
            doc = (
                DocumentConverter(
                    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
                )
                .convert(path)
                .document
            )
            return [(i, doc.export_to_markdown(page_no=i), "docling") for i in sorted(doc.pages)]
        import pdfplumber

        with pdfplumber.open(path) as doc:
            return [
                (i + 1, p.extract_text(layout=False) or "", "pdfplumber")
                for i, p in enumerate(doc.pages)
            ]
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
                raise ValueError("CSV requires unique headers")
            rows = []
            for row in reader:
                if None in row or any(v is None for v in row.values()):
                    raise ValueError("CSV row does not match header")
                rows.append("; ".join(f"{k}: {v}" for k, v in row.items()))
            return [(None, "\n\n".join(rows), "csv")]
    if path.suffix.lower() in {".md", ".txt"}:
        return [(None, path.read_text(encoding="utf-8-sig"), "markdown")]
    raise ValueError("Supported formats: PDF, Markdown, TXT and CSV")


def chunk_pages(
    path: Path, pages: list[tuple[int | None, str, str]], max_chars: int = 1300, overlap: int = 160
) -> list[Chunk]:
    if max_chars <= overlap or overlap < 0:
        raise ValueError("Overlap must be smaller than chunk size")
    chunks = []
    title = path.stem
    for page, text, parser in pages:
        section = "Overview"
        blocks = re.split(r"(?m)^(#{1,6}\s+.+)$", text)
        for block in blocks:
            if block.startswith("#"):
                section = block.lstrip("# ").strip()
                if block.startswith("# "):
                    title = section
                continue
            block = block.strip()
            if not block:
                continue
            start = 0
            while start < len(block):
                end = min(start + max_chars, len(block))
                if end < len(block):
                    boundary = block.rfind(". ", start + max_chars // 2, end)
                    if boundary > start:
                        end = boundary + 1
                snippet = block[start:end].strip()
                identity = f"{path.name}:{page}:{section}:{start}:{snippet}"
                chunks.append(
                    Chunk(
                        id=hashlib.sha256(identity.encode()).hexdigest()[:24],
                        document=path.name,
                        title=title,
                        section=section,
                        page=page,
                        text=snippet,
                        parser=parser,
                    )
                )
                if end == len(block):
                    break
                start = max(start + 1, end - overlap)
    return chunks
