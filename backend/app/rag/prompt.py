from __future__ import annotations

from typing import Any


def build_prompt(question: str, context_chunks: list[dict[str, Any]]) -> str:
    """Construct a grounded prompt for the RAG answer generator."""
    context_text = "\n\n".join(
        f"Source: {chunk.get('filename', 'unknown')}\n{chunk.get('text', '')}" for chunk in context_chunks
    )

    return f"""You are a grounded assistant.
Use only the retrieved context below to answer the user's question.
If the answer is not present in the retrieved context, say exactly:
\"I could not find this information in the uploaded documents.\"
Do not hallucinate or invent facts.

Question: {question}

Retrieved context:
{context_text or 'No relevant context found.'}

Answer in 1-3 concise sentences and cite the source filenames when possible."""
