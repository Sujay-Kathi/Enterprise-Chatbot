"""RAG service: query → FAISS retrieval → emotion detection → NVIDIA NIM → answer."""

from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from loguru import logger

from app.core.config import get_settings
from app.core.embeddings import get_vector_store
from app.services import cache_service, response_cache_service

settings = get_settings()

# ── Emotion Detection ──────────────────────────────────────────────────────────

_EMOTION_KEYWORDS: dict[str, list[str]] = {
    "frustrated": ["frustrated", "angry", "annoyed", "stupid", "useless", "terrible", "awful", "hate", "error", "broken", "fix"],
    "confused": ["confused", "don't understand", "unclear", "what is", "explain", "help", "lost", "unsure", "how does"],
    "curious": ["interesting", "wonder", "curious", "explore", "learn", "tell me more", "what about"],
    "happy": ["great", "thanks", "thank you", "awesome", "perfect", "love", "excellent", "wonderful"],
    "neutral": [],
}

_HIDDEN_SOURCES: list[str] = ["custom_facts.txt"]

_TONE_INSTRUCTIONS: dict[str, str] = {
    "frustrated": (
        "The user seems frustrated or upset. Respond with empathy and patience. "
        "Acknowledge their difficulty first, then provide a clear, calm, step-by-step answer."
    ),
    "confused": (
        "The user seems confused. Use simple language, short sentences, and helpful analogies. "
        "Break down the concept clearly before giving the full answer."
    ),
    "curious": (
        "The user is curious and engaged. Match their enthusiasm! Provide a thorough, "
        "insightful answer and optionally suggest related topics they might enjoy."
    ),
    "happy": (
        "The user is in a positive mood. Maintain a warm, friendly, and encouraging tone "
        "in your response."
    ),
    "neutral": (
        "Respond in a professional, clear, and helpful manner."
    ),
}


def detect_emotion(query: str) -> str:
    query_lower = query.lower()
    for emotion, keywords in _EMOTION_KEYWORDS.items():
        if emotion == "neutral":
            continue
        if any(kw in query_lower for kw in keywords):
            return emotion
    return "neutral"


# ── System Prompt Template ────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are an intelligent, empathetic Enterprise AI Assistant for internal company use.
Your primary purpose is to help employees find information from company documents, but you can also hold polite conversation.

TONE INSTRUCTION:
{tone_instruction}

PINNED HIGH-PRIORITY CONTEXT (CAG):
{pinned_context}

RETRIEVED DOCUMENT SNIPPETS (RAG):
{context}

RULES:
- If there is relevant information in PINNED HIGH-PRIORITY CONTEXT, treat it as the "Golden Truth".
- Use the RETRIEVED SNIPPETS to supplement specific figures or details not in the pinned context.
- Weave source citations naturally into your response if needed.
- If the user is just saying hello, asking general questions, or if documents haven't been uploaded yet, respond naturally.
- If the user asks for specific company information that is NOT in the context, politely inform them.
- Do NOT fabricate information. Keep answers concise but complete.
"""


def _build_llm() -> ChatNVIDIA:
    return ChatNVIDIA(
        model=settings.nim_model,
        api_key=settings.nvidia_api_key,
        temperature=0.3,
        max_tokens=1024,
    )


def answer_query(
    query: str,
    history: Optional[list[dict]] = None,
) -> dict:
    """
    Full RAG pipeline:
    1. Emotion detection
    2. FAISS retrieval (top-4 chunks)
    3. Prompt construction with history + context + tone
    4. NVIDIA NIM LLM generation

    Returns: { "answer": str, "emotion": str, "sources": list[str] }
    """
    emotion = detect_emotion(query)
    tone_instruction = _TONE_INSTRUCTIONS[emotion]
    logger.info(f"[RAG] Detected emotion: {emotion}")

    # 0. Check Response Cache (Semantic)
    cached = response_cache_service.check_cache(query)
    if cached:
        return cached

    # Retrieval
    vector_store = get_vector_store()
    context_text = ""
    sources: list[str] = []

    if vector_store is None:
        context_text = "No documents have been uploaded yet."
        logger.warning("[RAG] No FAISS index found — answering without context.")
    else:
        # Skip retrieval for casual greetings to avoid irrelevant sources
        casual_greetings = ["hi","yo","hoi", "hello", "hey", "who are you?", "who are you", "how are you?", "how are you", "thanks", "thank you", "roshni?", "roshni"]
        if query.strip().lower() in casual_greetings:
            docs = []
            context_text = "No context needed for this greeting."
        else:
            docs = vector_store.similarity_search(query, k=4)
            
        if docs:
            context_parts = []
            for doc in docs:
                source = doc.metadata.get("source", "Unknown")
                if source not in sources and source not in _HIDDEN_SOURCES:
                    sources.append(source)
                    # Notify CAG Heat Map
                    cache_service.record_access(source)
                context_parts.append(f"[Source: {source}]\n{doc.page_content}")
            context_text = "\n\n---\n\n".join(context_parts)
        else:
            context_text = "No relevant sections found in the uploaded documents."

    # PINNED CONTEXT (CAG)
    pinned_context = cache_service.get_pinned_context()

    # Build messages
    system_content = _SYSTEM_PROMPT.format(
        tone_instruction=tone_instruction,
        pinned_context=pinned_context if pinned_context else "No high-priority documents pinned.",
        context=context_text,
    )
    messages = [SystemMessage(content=system_content)]

    # Add conversation history
    if history:
        for msg in history[-6:]:  # last 3 exchanges (6 messages)
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))

    messages.append(HumanMessage(content=query))

    # LLM call
    llm = _build_llm()
    response = llm.invoke(messages)
    answer = response.content.strip()

    # 5. Save to Response Cache
    response_cache_service.save_cache(query, answer, emotion, sources)

    logger.success(f"[RAG] Answer generated ({len(answer)} chars)")
    return {"answer": answer, "emotion": emotion, "sources": sources}


def stream_answer_query(
    query: str,
    history: Optional[list[dict]] = None,
):
    """
    Streaming RAG pipeline:
    Yields chunks of the answer as they are generated.
    The first yield contains metadata (emotion, sources).
    Subsequent yields contain text chunks.
    """
    emotion = detect_emotion(query)
    tone_instruction = _TONE_INSTRUCTIONS[emotion]
    logger.info(f"[RAG-Stream] Detected emotion: {emotion}")

    # 0. Check Response Cache
    cached = response_cache_service.check_cache(query)
    if cached:
        import json
        yield f"__METADATA__:{json.dumps({'emotion': cached['emotion'], 'sources': cached['sources'], 'cached': True})}\n"
        yield cached['answer']
        return

    # Retrieval
    vector_store = get_vector_store()
    context_text = ""
    sources: list[str] = []

    if vector_store is None:
        context_text = "No documents have been uploaded yet."
    else:
        # Skip retrieval for casual greetings
        casual_greetings = ["hi", "hello", "hey", "who are you?", "who are you", "how are you?", "how are you", "thanks", "thank you", "roshni?", "roshni"]
        if query.strip().lower() in casual_greetings:
            docs = []
            context_text = "No context needed for this greeting."
        else:
            docs = vector_store.similarity_search(query, k=4)
            
        if docs:
            context_parts = []
            for doc in docs:
                source = doc.metadata.get("source", "Unknown")
                if source not in sources and source not in _HIDDEN_SOURCES:
                    sources.append(source)
                    # Notify CAG Heat Map
                    cache_service.record_access(source)
                context_parts.append(f"[Source: {source}]\n{doc.page_content}")
            context_text = "\n\n---\n\n".join(context_parts)
        else:
            context_text = "No relevant sections found in the uploaded documents."

    # First yield: Metadata
    import json
    yield f"__METADATA__:{json.dumps({'emotion': emotion, 'sources': sources})}\n"

    # PINNED CONTEXT (CAG)
    pinned_context = cache_service.get_pinned_context()

    # Build messages
    system_content = _SYSTEM_PROMPT.format(
        tone_instruction=tone_instruction,
        pinned_context=pinned_context if pinned_context else "No high-priority documents pinned.",
        context=context_text,
    )
    messages = [SystemMessage(content=system_content)]

    if history:
        for msg in history[-6:]:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))

    messages.append(HumanMessage(content=query))

    # Streaming LLM call
    llm = _build_llm()
    full_answer = ""
    for chunk in llm.stream(messages):
        if chunk.content:
            full_answer += chunk.content
            yield chunk.content
            
    # Save to Cache
    response_cache_service.save_cache(query, full_answer.strip(), emotion, sources)


def summarize_document(file_bytes: bytes, filename: str) -> str:
    """
    Summarize a document by chunking it and passing to the LLM.
    Uses a map-reduce style: summarize chunks, then combine.
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from app.core.embeddings import get_embeddings
    from app.services.ingestion_service import _extract_text

    raw_text = _extract_text(file_bytes, filename)
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
    chunks = splitter.split_text(raw_text)

    llm = _build_llm()

    # Summarize each chunk
    chunk_summaries: list[str] = []
    for i, chunk in enumerate(chunks[:8]):  # cap at 8 chunks to avoid token overflow
        prompt = f"Summarize the following section from '{filename}' in 3-5 sentences:\n\n{chunk}"
        resp = llm.invoke([HumanMessage(content=prompt)])
        chunk_summaries.append(resp.content.strip())

    # Final combine pass
    combined = "\n\n".join(chunk_summaries)
    final_prompt = (
        f"Here are section summaries from '{filename}'. "
        f"Write a single cohesive summary of the entire document in a professional tone:\n\n{combined}"
    )
    final_resp = llm.invoke([HumanMessage(content=final_prompt)])
    return final_resp.content.strip()
