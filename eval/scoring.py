"""Single correctness rule for ContextMap.

Used by the eval runner and the backend so the rule cannot drift.
A answer is correct when the expected code appears as a whole token in the model output.
"""
import re
import string


def normalize(text: str) -> str:
    return text.strip().strip(string.punctuation + " \n\t").lower()


def is_correct(model_output: str, expected: str) -> bool:
    expected_norm = normalize(expected)
    tokens = re.findall(r"[a-z0-9-]+", model_output.lower())
    return expected_norm in tokens
