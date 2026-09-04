import os
import requests
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env file immediately on import
load_dotenv()


class FDAClient:
    """Handles interactions with the openFDA REST API."""

    def __init__(self):
        self.base_url = "https://api.fda.gov/drug/label.json"
        self.recall_url = "https://api.fda.gov/drug/enforcement.json"

    def fetch_drug_info(self, med_name: str) -> dict:
        """Fetches medication label info with a strict 5-second timeout."""
        query_url = (
            f'{self.base_url}?search=openfda.brand_name:"{med_name}"'
            f'+openfda.generic_name:"{med_name}"&limit=1'
        )

        try:
            response = requests.get(query_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])[0]

                return {
                    "usage": " ".join(
                        results.get("indications_and_usage", ["N/A"])
                    ),
                    "warnings": " ".join(results.get("warnings", ["N/A"])),
                    "side_effects": " ".join(
                        results.get("adverse_reactions", ["N/A"])
                    ),
                    "found_in_fda": True,
                }
        except Exception:
            pass

        return {
            "usage": f"Information for {med_name}",
            "warnings": "Consult a healthcare professional.",
            "side_effects": "Consult a healthcare professional.",
            "found_in_fda": False,
        }

    def check_recalls(self, med_name: str) -> tuple[bool, str]:
        """Checks active FDA recalls with a strict 5-second timeout."""
        query_url = (
            f'{self.recall_url}?search=product_description:"{med_name}"&limit=1'
        )

        try:
            response = requests.get(query_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                if results:
                    reason = results[0].get(
                        "reason_for_recall", "Recall reason not specified."
                    )
                    return True, reason
        except Exception:
            pass

        return False, "No active recall records found or service offline."


class AITranslator:
    """Translates clinical medication descriptions into 5th-grade plain English."""

    def __init__(self):
        api_key = (
            os.getenv("GEMINI_API_KEY")
            or os.getenv("PillSpeak")
            or os.getenv("API_KEY")
        )

        if not api_key:
            raise ValueError(
                "API Key missing. Please ensure your .env file contains GEMINI_API_KEY."
            )

        self.client = genai.Client(api_key=api_key)

    def translate(
        self,
        med_name: str,
        usage: str,
        warnings: str,
        side_effects: str,
        found_in_fda: bool,
    ) -> str:
        prompt = f"""
        You are PillSpeak, an AI Medical Information Assistant developed for NCAIR.
        Translate the following clinical information for the medication '{med_name}' into clear, simple 5th-grade English.

        Medication: {med_name}
        FDA Data Available: {found_in_fda}
        Usage Context: {usage[:1000]}
        Warnings Context: {warnings[:1000]}
        Side Effects Context: {side_effects[:1000]}

        Structure your response clearly with markdown headings:
        ### 🎯 What is it used for?
        ### ⚠️ Important Safety Warnings
        ### 🤒 Common Side Effects
        ### 💡 Safe Usage Tips
        """

        # Using Google's active standard model string
        for model_id in ["gemini-3.6-flash", "gemini-2.5-flash"]:
            try:
                response = self.client.models.generate_content(
                    model=model_id, contents=prompt
                )
                return response.text
            except Exception as err:
                print(f"[PillSpeak Debug] Model {model_id} failed: {err}")
                continue

        return "Error: Unable to connect to Gemini API. Please check your API key."