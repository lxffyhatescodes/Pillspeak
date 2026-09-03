import os
import time
import warnings
import requests
from google import genai

# Suppress SDK deprecation/info warnings in CLI output
warnings.filterwarnings("ignore")


class FDAClient:
    """Handles data retrieval from the official openFDA API endpoints."""

    BASE_LABEL_URL = "https://api.fda.gov/drug/label.json"
    BASE_RECALL_URL = "https://api.fda.gov/drug/enforcement.json"

    def fetch_drug_info(self, med_name: str) -> dict:
        """Fetch brand/generic drug label details from openFDA with flexible search."""
        search_queries = [
            f'openfda.brand_name:"{med_name}" OR openfda.generic_name:"{med_name}"',
            f'openfda.brand_name:*{med_name}* OR openfda.generic_name:*{med_name}*',
            f'substance_name:*{med_name}* OR active_ingredient:*{med_name}*',
        ]

        for query in search_queries:
            try:
                params = {"search": query, "limit": 1}
                response = requests.get(
                    self.BASE_LABEL_URL, params=params, timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    if results:
                        raw = results[0]
                        usage = raw.get(
                            "indications_and_usage",
                            ["No usage info provided."],
                        )[0]
                        warnings_text = raw.get(
                            "warnings", ["No warnings provided."]
                        )[0]
                        side_effects = raw.get(
                            "adverse_reactions",
                            ["No side effects info provided."],
                        )[0]

                        return {
                            "usage": usage,
                            "warnings": warnings_text,
                            "side_effects": side_effects,
                            "found_in_fda": True,
                        }
            except requests.exceptions.RequestException:
                continue

        return {
            "usage": "",
            "warnings": "",
            "side_effects": "",
            "found_in_fda": False,
        }

    def check_recalls(self, med_name: str) -> tuple[bool, str]:
        """Check openFDA enforcement listings for recall alerts."""
        params = {"search": f'product_description:"{med_name}"', "limit": 1}

        try:
            response = requests.get(
                self.BASE_RECALL_URL, params=params, timeout=10
            )

            if response.status_code == 200:
                results = response.json().get("results", [])
                if results:
                    reason = results[0].get(
                        "reason_for_recall", "No specific reason provided."
                    )
                    return True, reason

            return False, "No active recall notices found."

        except requests.exceptions.RequestException:
            return False, "Could not verify recall status due to network error."


class AITranslator:
    """Uses Gemini API to simplify medical text into plain English for PillSpeak."""

    def __init__(self):
        api_key = os.getenv("PillSpeak") or os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "API Key missing. Please ensure environment variable 'PillSpeak' "
                "is configured in PyCharm's Run/Debug Configurations."
            )
        self.client = genai.Client(api_key=api_key)

    def translate(
        self,
        med_name: str,
        usage: str = "",
        warnings: str = "",
        side_effects: str = "",
        found_in_fda: bool = True,
    ) -> str:
        """Sends medical text or drug query to Gemini with automatic retry logic for 503 errors."""
        if found_in_fda and (usage or warnings or side_effects):
            prompt = f"""
            You are the AI core for PillSpeak, an expert patient-education medical translator.
            Translate the following clinical drug information for '{med_name}' into clear, simple, 5th-grade level everyday English.

            Format the response clearly with bullet points under these three bold section titles:
            • **What It's For**:
            • **Important Warnings**:
            • **Possible Side Effects**:

            Raw Usage Data:
            {usage[:1500]}

            Raw Warnings Data:
            {warnings[:1500]}

            Raw Side Effects Data:
            {side_effects[:1500]}
            """
        else:
            prompt = f"""
            You are the AI core for PillSpeak, an expert patient-education medical translator.
            The user searched for the medication '{med_name}' (which may be an international name, generic term, regional brand, or minor spelling variation like Paracetamol, Albenol, or Amoxicilin).

            Provide an accurate, clear, 5th-grade level patient explanation for '{med_name}'. 
            If '{med_name}' is a regional/international name (e.g., Paracetamol = Acetaminophen, Albenol = Albendazole), briefly note that alias.

            Format the response clearly with bullet points under these three bold section titles:
            • **What It's For**:
            • **Important Warnings**:
            • **Possible Side Effects**:
            """

        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt,
                )
                return response.text
            except Exception as e:
                err_msg = str(e)
                if "503" in err_msg or "UNAVAILABLE" in err_msg:
                    if attempt < max_retries:
                        time.sleep(2)  # Wait 2 seconds before retrying
                        continue
                raise RuntimeError(f"AI Translation request failed: {e}")