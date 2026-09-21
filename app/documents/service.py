from hashlib import sha256
from pathlib import Path

import pymupdf

from app.documents.models import NormalizedDocument


class DocumentService:
    def extract_text(
        self,
        file_path: Path,
        filename: str,
        content_type: str,
    ) -> NormalizedDocument:
        document_id = self._calculate_document_id(file_path)

        document = pymupdf.open(file_path)

        pages = []

        for page_number, page in enumerate(document, start=1):
            pages.append(
                {
                    "page_number": page_number,
                    "text": page.get_text(),
                }
            )

        document.close()

        text = "\n".join(page["text"] for page in pages)

        return NormalizedDocument(
            document_id=document_id,
            filename=filename,
            content_type=content_type,
            text=text,
            metadata={
                "page_count": len(pages),
                "pages": pages,
                "character_count": len(text),
                "extraction_method": "pymupdf",
            },
        )

    @staticmethod
    def _calculate_document_id(file_path: Path) -> str:
        hasher = sha256()

        with file_path.open("rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                hasher.update(chunk)

        return hasher.hexdigest()