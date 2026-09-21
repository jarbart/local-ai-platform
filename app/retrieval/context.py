from typing import Any


class ContextBuilder:
    def build(
        self,
        results: list[dict[str, Any]],
    ) -> str:
        sections = []

        for index, result in enumerate(results, start=1):
            filename = result.get("filename") or "unknown"
            page_number = result.get("page_number")
            score = result.get("score")
            text = result.get("text", "")

            sections.append(
                f"[Source {index}]\n"
                f"Document: {filename}\n"
                f"Page: {page_number}\n"
                f"Relevance: {score:.4f}\n\n"
                f"{text}"
            )

        return "\n\n".join(sections)