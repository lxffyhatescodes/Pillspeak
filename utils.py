import re


class TextSanitizer:
    """Helper class containing regex utilities for validation and text processing."""

    @staticmethod
    def validate_med_name(name: str) -> str:
        """Validates medication input and strips leading/trailing spaces.

        Raises ValueError if empty or containing invalid characters.
        """
        cleaned = name.strip()
        if not cleaned:
            raise ValueError("Medication name cannot be empty.")

        # Allows letters, numbers, spaces, and hyphens (e.g., "Tylenol-Extra")
        if not re.match(r"^[a-zA-Z0-9\s\-]+$", cleaned):
            raise ValueError(
                "Invalid medication name. Avoid special characters (e.g., @, #, $, !)."
            )

        return cleaned

    @staticmethod
    def clean_text(text: str) -> str:
        """Strips HTML tags, redundant white spaces, and common disclaimer headers using regex."""
        if not text:
            return ""

        # Remove HTML tags if present (e.g., <p>, <br>)
        cleaned = re.sub(r"<[^>]+>", " ", text)

        # Replace multiple spaces, tabs, or newlines with a single space
        cleaned = re.sub(r"\s+", " ", cleaned)

        # Remove repetitive FDA boilerplate phrases
        cleaned = re.sub(
            r"(?i)see package insert for full prescribing information",
            "",
            cleaned,
        )

        return cleaned.strip()

    @staticmethod
    def extract_critical_keywords(text: str) -> list[str]:
        """Uses regex to identify high-risk safety keywords in medication text."""
        # Pattern matching critical warning words (case-insensitive)
        pattern = r"\b(fatal|death|liver failure|anaphylaxis|addiction|black box|stroke|heart attack)\b"
        matches = re.findall(pattern, text, flags=re.IGNORECASE)

        # Return unique lowercase keywords found
        return sorted(list(set(word.lower() for word in matches)))