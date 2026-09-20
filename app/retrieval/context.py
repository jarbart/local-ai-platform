from typing import Any


class ContextBuilder:
    def build(
        self,
        results: list[dict[str, Any]],
    ) -> str:
        sections = []

        for index, result in enumerate(results, start=1):
            page_number = result.get("page_number")
            text = result.get("text", "")

            sections.append(
                f"[Source {index} | Page {page_number}]\n"
                f"{text}"
            )

        return "\n\n".join(sections)