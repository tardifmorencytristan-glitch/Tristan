from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unicodedata
import xml.etree.ElementTree as ET

from .loss_tensor import LossObservation, LossTensor
from .pdf_ir import PDFBlockObservation, PDFDocumentObservation, PDFPageObservation
from .provenance import BoundingBox
from .representation_ir import ConfidenceVector


@dataclass(frozen=True)
class ParserRun:
    parser: str
    parser_version: str
    observation: PDFDocumentObservation
    text: str


@dataclass(frozen=True)
class ParserComparison:
    parser_a: str
    parser_b: str
    exact_normalized_text_equal: bool
    sequence_similarity: float
    token_set_jaccard: float


def normalize_text(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).split())


def _selected_pages(total_pages: int, pages: tuple[int, ...] | None) -> tuple[int, ...]:
    if pages is None:
        return tuple(range(1, total_pages + 1))
    if not pages:
        raise ValueError("pages must be non-empty when provided")
    selected = tuple(sorted(set(pages)))
    if selected[0] < 1 or selected[-1] > total_pages:
        raise ValueError("selected page outside PDF bounds")
    return selected


class PyPDFAdapter:
    name = "pypdf"

    @staticmethod
    def available() -> bool:
        try:
            import pypdf  # noqa: F401
            return True
        except ImportError:
            return False

    def parse_bytes(self, pdf_bytes: bytes, source_artifact_id: str, pages: tuple[int, ...] | None = None) -> ParserRun:
        try:
            import pypdf
        except ImportError as exc:
            raise RuntimeError("pypdf adapter unavailable") from exc

        digest = sha256(pdf_bytes).hexdigest()
        reader = pypdf.PdfReader(BytesIO(pdf_bytes))
        selected = _selected_pages(len(reader.pages), pages)
        observations: list[PDFPageObservation] = []
        text_parts: list[str] = []

        for page_number in selected:
            page = reader.pages[page_number - 1]
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)
            text = page.extract_text() or ""
            text_parts.append(text)
            blocks = ()
            if text.strip():
                blocks = (
                    PDFBlockObservation(
                        id="page-text",
                        kind="TEXT",
                        bbox=BoundingBox(0.0, 0.0, width, height),
                        content=text,
                        reading_order=0,
                        confidence=ConfidenceVector(provenance=1.0),
                        metadata=(("geometry_semantics", "PAGE_ENVELOPE_NOT_TEXT_BBOX"),),
                    ),
                )
            observations.append(PDFPageObservation(page_number, width, height, blocks=blocks))

        observation = PDFDocumentObservation(
            source_artifact_id=source_artifact_id,
            source_sha256=digest,
            parser=self.name,
            parser_version=str(pypdf.__version__),
            pages=tuple(observations),
            observation_status="AUTOMATIC_BYTE_PARSER_OBSERVATION",
        )
        errors = observation.validate()
        if errors:
            raise ValueError(errors)
        return ParserRun(self.name, str(pypdf.__version__), observation, "\n".join(text_parts))


class PopplerBBoxAdapter:
    name = "poppler-pdftotext-bbox-layout"

    @staticmethod
    def available() -> bool:
        return shutil.which("pdftotext") is not None

    @staticmethod
    def version() -> str:
        if not PopplerBBoxAdapter.available():
            raise RuntimeError("pdftotext adapter unavailable")
        result = subprocess.run(["pdftotext", "-v"], capture_output=True, text=True, check=False)
        first_line = (result.stderr or result.stdout).splitlines()[0]
        match = re.search(r"version\s+(.+)$", first_line)
        return match.group(1).strip() if match else first_line.strip()

    def parse_bytes(self, pdf_bytes: bytes, source_artifact_id: str, pages: tuple[int, ...] | None = None) -> ParserRun:
        if not self.available():
            raise RuntimeError("pdftotext adapter unavailable")

        digest = sha256(pdf_bytes).hexdigest()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "input.pdf"
            path.write_bytes(pdf_bytes)
            # pdfinfo is supplied by the same Poppler package and lets us fail closed on page bounds.
            info = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, check=True).stdout
            page_line = next((line for line in info.splitlines() if line.startswith("Pages:")), "")
            if not page_line:
                raise RuntimeError("Poppler did not report page count")
            total_pages = int(page_line.split(":", 1)[1].strip())
            selected = _selected_pages(total_pages, pages)
            if selected != tuple(range(selected[0], selected[-1] + 1)):
                raise ValueError("Poppler adapter currently requires a contiguous page selection")

            result = subprocess.run(
                [
                    "pdftotext", "-f", str(selected[0]), "-l", str(selected[-1]),
                    "-bbox-layout", str(path), "-"
                ],
                capture_output=True,
                text=True,
                check=True,
            )

        root = ET.fromstring(result.stdout)
        ns = {"x": "http://www.w3.org/1999/xhtml"}
        page_elements = root.findall(".//x:page", ns)
        if len(page_elements) != len(selected):
            raise RuntimeError("Poppler page count did not match requested range")

        page_observations: list[PDFPageObservation] = []
        all_text: list[str] = []
        for page_number, page_element in zip(selected, page_elements):
            width = float(page_element.attrib["width"])
            height = float(page_element.attrib["height"])
            blocks: list[PDFBlockObservation] = []
            for order, block in enumerate(page_element.findall(".//x:block", ns)):
                words = [word.text or "" for word in block.findall(".//x:word", ns)]
                text = " ".join(w for w in words if w).strip()
                if not text:
                    continue
                all_text.append(text)
                blocks.append(
                    PDFBlockObservation(
                        id=f"block-{order}",
                        kind="PARAGRAPH",
                        bbox=BoundingBox(
                            float(block.attrib["xMin"]),
                            float(block.attrib["yMin"]),
                            float(block.attrib["xMax"]),
                            float(block.attrib["yMax"]),
                        ),
                        content=text,
                        reading_order=order,
                        confidence=ConfidenceVector(provenance=1.0),
                        metadata=(("geometry_semantics", "POPPLER_REPORTED_BBOX"),),
                    )
                )
            page_observations.append(PDFPageObservation(page_number, width, height, blocks=tuple(blocks)))

        version = self.version()
        observation = PDFDocumentObservation(
            source_artifact_id=source_artifact_id,
            source_sha256=digest,
            parser=self.name,
            parser_version=version,
            pages=tuple(page_observations),
            observation_status="AUTOMATIC_BYTE_PARSER_OBSERVATION",
        )
        errors = observation.validate()
        if errors:
            raise ValueError(errors)
        return ParserRun(self.name, version, observation, "\n".join(all_text))


def compare_texts(parser_a: str, text_a: str, parser_b: str, text_b: str) -> ParserComparison:
    a = normalize_text(text_a)
    b = normalize_text(text_b)
    tokens_a = set(a.split())
    tokens_b = set(b.split())
    union = tokens_a | tokens_b
    jaccard = 1.0 if not union else len(tokens_a & tokens_b) / len(union)
    similarity = SequenceMatcher(None, a, b, autojunk=False).ratio()
    return ParserComparison(parser_a, parser_b, a == b, similarity, jaccard)


def comparison_to_loss_tensor(comparison: ParserComparison, transform_id: str = "parser_crosscheck") -> LossTensor:
    tensor = LossTensor()
    if comparison.exact_normalized_text_equal:
        tensor.add(
            LossObservation(
                transform_id=transform_id,
                item_id=f"{comparison.parser_a}<->{comparison.parser_b}:text",
                dimension="SEMANTIC",
                state="PRESERVED",
                severity=0.0,
                recoverability=1.0,
                cause="exact normalized text equality on compared parser outputs",
            )
        )
    else:
        tensor.add(
            LossObservation(
                transform_id=transform_id,
                item_id=f"{comparison.parser_a}<->{comparison.parser_b}:text",
                dimension="SEMANTIC",
                state="UNKNOWN",
                severity=max(0.0, min(1.0, 1.0 - comparison.sequence_similarity)),
                recoverability=0.0,
                cause="parser disagreement; no independent adjudicator applied",
                detail=f"token_set_jaccard={comparison.token_set_jaccard:.12f}",
            )
        )
    return tensor


def invariant_presence(run: ParserRun, invariants: tuple[str, ...]) -> dict[str, bool]:
    normalized = normalize_text(run.text)
    return {item: normalize_text(item) in normalized for item in invariants}
