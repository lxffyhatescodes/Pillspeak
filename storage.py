import json
import os
from models import Medication


class HistoryManager:
    """Handles loading and saving medication lookup history to a local JSON file."""

    def __init__(self, filename: str = "history.json"):
        self.filename = filename

    def save_medication(self, med: Medication) -> None:
        """Appends a new Medication record to local history JSON."""
        history = self.load_history()
        history.append(med.to_dict())

        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=4)
        except IOError as e:
            print(f"Warning: Failed to save search history to disk: {e}")

    def load_history(self) -> list[dict]:
        """Loads and returns past search records from JSON file."""
        if not os.path.exists(self.filename):
            return []

        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            # If the file is corrupted or unreadable, fall back to an empty list
            return []

    def clear_history(self) -> None:
        """Clears all stored history by resetting the JSON file."""
        if os.path.exists(self.filename):
            try:
                os.remove(self.filename)
            except OSError as e:
                print(f"Warning: Failed to clear history file: {e}")