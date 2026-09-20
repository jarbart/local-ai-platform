from pathlib import Path
from uuid import uuid4

import pymupdf

from app.documents.models import NormalizedDocument


class DocumentService:
    def extract_text(
        self,
        file_path: Path,
        filename: str,
        content_type: str,
    ) -> NormalizedDocument:
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
            document_id=str(uuid4()),
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