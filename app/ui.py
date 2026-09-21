import requests
import streamlit as st


API_URL = "http://localhost:8000"


st.set_page_config(
    page_title="Local AI Platform",
    page_icon="🤖",
    layout="wide",
)


def get_documents() -> list[dict]:
    response = requests.get(
        f"{API_URL}/documents",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def upload_document(file) -> dict:
    response = requests.post(
        f"{API_URL}/documents/upload",
        files={
            "file": (
                file.name,
                file.getvalue(),
                file.type,
            )
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json()


def delete_document(document_id: str) -> dict:
    response = requests.delete(
        f"{API_URL}/documents/{document_id}",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def ask_question(question: str) -> dict:
    response = requests.post(
        f"{API_URL}/chat",
        json={
            "question": question,
        },
        timeout=180,
    )

    response.raise_for_status()

    return response.json()


def initialize_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []


def render_sources(sources):
    if not sources:
        st.info("No sources returned.")
        return

    for index, source in enumerate(sources, start=1):
        filename = source.get("filename") or "Unknown"
        page = source.get("page_number")
        score = source.get("score")

        if score is None:
            relevance = "N/A"
        else:
            relevance = f"{score:.4f}"

        with st.expander(
            f"📄 Source {index} · {filename}",
        ):
            col1, col2 = st.columns(2)

            with col1:
                st.caption("Document")
                st.write(filename)

            with col2:
                st.caption("Page")
                st.write(
                    page if page is not None else "N/A"
                )

            st.caption("Relevance")
            st.progress(
                min(max(float(score or 0), 0.0), 1.0),
                text=relevance,
            )


def render_documents():
    try:
        documents = get_documents()
    except requests.RequestException as exc:
        st.error(
            f"Could not load documents: {exc}"
        )
        return

    if not documents:
        st.info("No documents indexed.")
        return

    for document in documents:
        document_id = document["document_id"]
        filename = document.get("filename") or "Unknown"
        content_type = (
            document.get("content_type") or "Unknown"
        )
        chunk_count = document["chunk_count"]

        st.markdown(
            f"""
            **📄 {filename}**

            `{content_type}` · {chunk_count} chunk(s)
            """
        )

        if st.button(
            "Delete",
            key=f"delete_{document_id}",
            use_container_width=True,
        ):
            try:
                delete_document(document_id)

                st.success(
                    f"Deleted {filename}."
                )

                st.rerun()

            except requests.HTTPError as exc:
                if exc.response is not None:
                    try:
                        detail = exc.response.json().get(
                            "detail",
                            exc.response.text,
                        )
                    except ValueError:
                        detail = exc.response.text

                    st.error(
                        f"API error: {detail}"
                    )
                else:
                    st.error(
                        "Could not delete document."
                    )

            except requests.RequestException as exc:
                st.error(
                    f"API request failed: {exc}"
                )

        st.divider()


initialize_state()


st.title("🤖 Local AI Platform")
st.caption(
    "Local-first document intelligence platform"
)


with st.sidebar:
    st.header("📚 Documents")

    uploaded_file = st.file_uploader(
        "Upload a document",
        type=["pdf", "txt"],
        help="Supported formats: PDF and TXT",
    )

    if uploaded_file is not None:
        st.caption(
            f"Selected: **{uploaded_file.name}**"
        )

        if st.button(
            "Process document",
            type="primary",
            use_container_width=True,
        ):
            try:
                with st.spinner(
                    "Extracting, chunking and indexing document..."
                ):
                    result = upload_document(
                        uploaded_file
                    )

                if result["duplicate"]:
                    st.warning(
                        "This document is already indexed."
                    )
                else:
                    st.success(
                        "Document indexed successfully."
                    )

                st.rerun()

            except requests.HTTPError as exc:
                if exc.response is not None:
                    try:
                        detail = exc.response.json().get(
                            "detail",
                            exc.response.text,
                        )
                    except ValueError:
                        detail = exc.response.text

                    st.error(
                        f"API error: {detail}"
                    )
                else:
                    st.error(
                        "API request failed."
                    )

            except requests.RequestException as exc:
                st.error(
                    f"API request failed: {exc}"
                )

    st.divider()

    st.subheader("Indexed documents")

    render_documents()

    st.divider()

    st.subheader("Session")

    st.caption(
        f"Questions: {len(st.session_state.messages)}"
    )

    if st.button(
        "Clear conversation",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.rerun()


st.subheader("💬 Chat")


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant":
            sources = message.get("sources", [])

            if sources:
                st.markdown("**Sources**")
                render_sources(sources)


question = st.chat_input(
    "Ask a question about your documents..."
)


if question:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner(
                "Searching documents and generating answer..."
            ):
                result = ask_question(question)

            answer = result["answer"]
            sources = result.get("sources", [])

            st.markdown(answer)

            if sources:
                st.markdown("**Sources**")
                render_sources(sources)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                }
            )

        except requests.HTTPError as exc:
            if exc.response is not None:
                try:
                    detail = exc.response.json().get(
                        "detail",
                        exc.response.text,
                    )
                except ValueError:
                    detail = exc.response.text

                error_message = (
                    f"API error: {detail}"
                )
            else:
                error_message = (
                    "API request failed."
                )

            st.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                    "sources": [],
                }
            )

        except requests.RequestException as exc:
            error_message = (
                f"API request failed: {exc}"
            )

            st.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                    "sources": [],
                }
            )