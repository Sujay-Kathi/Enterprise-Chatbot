"""Content moderation service: blocks profanity/bad language before RAG."""

from better_profanity import profanity
from loguru import logger

# Initialise with the default wordlist (loads once at import time)
profanity.load_censor_words()


def is_content_safe(text: str) -> bool:
    """Return True if text contains NO profanity; False otherwise."""
    safe = not profanity.contains_profanity(text)
    if not safe:
        logger.warning(f"[Moderation] Blocked inappropriate content in query.")
    return safe


def get_rejection_message() -> str:
    return (
        "I'm sorry, but I'm unable to process requests containing inappropriate "
        "language. Please rephrase your question respectfully and try again."
    )
