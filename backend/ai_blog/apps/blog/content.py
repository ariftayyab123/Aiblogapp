"""
Markdown content analysis helpers.

Single source of truth for word count / reading time / heading extraction,
shared by the generation service, the model properties, and the API layer.
"""
import re

WORDS_PER_MINUTE = 200

# Fenced code blocks are stripped before heading detection so that a commented
# line inside ``` ... ``` is not mistaken for a markdown heading.
_FENCE_RE = re.compile(r'^(?:```|~~~).*?(?:^(?:```|~~~)[^\n]*$|\Z)', re.MULTILINE | re.DOTALL)
_HEADING_RE = re.compile(r'^(#{1,3})\s+(.+)$', re.MULTILINE)
# Words are alphanumeric runs, so markdown syntax (#, **, -, |) is not counted.
_WORD_RE = re.compile(r"[^\W_]+(?:['’-][^\W_]+)*", re.UNICODE)


def count_words(markdown: str) -> int:
    """Count prose words in a markdown body, ignoring markdown syntax."""
    return len(_WORD_RE.findall(markdown or ''))


def reading_time_minutes(word_count: int) -> int:
    """Reading time in whole minutes, rounded up, minimum 1."""
    return max(1, -(-max(word_count, 0) // WORDS_PER_MINUTE))


def compute_content_structure(markdown: str) -> dict:
    """Compute word/heading/reading-time metadata for a markdown body."""
    markdown = markdown or ''
    headings = _HEADING_RE.findall(_FENCE_RE.sub('', markdown))
    word_count = count_words(markdown)

    return {
        'word_count': word_count,
        'heading_count': len(headings),
        'reading_time_minutes': reading_time_minutes(word_count),
        'headings': [{'level': level, 'text': text.strip()} for level, text in headings],
    }
