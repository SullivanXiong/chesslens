class ContextBuilder:
    """Build RAG context for Claude chat prompts."""

    def build_context(
        self,
        retrieved_chunks: list,
        pinned_chunks: list | None = None,
    ) -> str:
        parts = []

        if pinned_chunks:
            parts.append("### Pinned Game Context")
            for chunk in pinned_chunks:
                text = (
                    chunk.chunk_text if hasattr(chunk, "chunk_text") else str(chunk)
                )
                parts.append(f"- {text}")
            parts.append("")

        if retrieved_chunks:
            parts.append("### Related Games & Patterns")
            for chunk in retrieved_chunks:
                text = (
                    chunk.chunk_text if hasattr(chunk, "chunk_text") else str(chunk)
                )
                parts.append(f"- {text}")
            parts.append("")

        return "\n".join(parts)
