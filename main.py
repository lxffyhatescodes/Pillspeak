import os
from models import Medication
from services import FDAClient, AITranslator
from storage import HistoryManager
from utils import TextSanitizer


def main():
    print("==================================================")
    print("          PILLSPEAK: Patient Medication Translator")
    print("==================================================")

    # Initialize core services and storage
    try:
        fda_client = FDAClient()
        ai_translator = AITranslator()
        storage = HistoryManager("history.json")
    except Exception as e:
        print(f"\n❌ Initialization Error: {e}")
        return

    while True:
        print("\n--- MAIN MENU ---")
        print("1. Look up a Medication")
        print("2. View Search History")
        print("3. Clear History")
        print("4. Exit")

        choice = input("\nSelect an option (1-4): ").strip()

        if choice == "1":
            raw_name = input(
                "\nEnter drug name (e.g., Paracetamol, Amoxicillin, Albenol, Aspirin): "
            )
            try:
                # 1. Validate name input using TextSanitizer regex
                med_name = TextSanitizer.validate_med_name(raw_name)
            except ValueError as ve:
                print(f"❌ Input Error: {ve}")
                continue

            print(f"\n🔍 Searching records for '{med_name}'...")
            try:
                # 2. Fetch FDA Data & Active Recalls
                raw_data = fda_client.fetch_drug_info(med_name)
                is_recalled, recall_msg = fda_client.check_recalls(med_name)

                if is_recalled:
                    print(
                        f"⚠️ WARNING: Active recall notice found! Reason: {recall_msg}"
                    )
                else:
                    print("✅ No active recall notices found.")

                if raw_data["found_in_fda"]:
                    print(
                        "🤖 Translating openFDA clinical label into 5th-grade plain English via Gemini..."
                    )
                else:
                    print(
                        "🌐 Generating medical info via Gemini AI Knowledge Base..."
                    )

                # 3. Translate via Gemini AI Core
                summary = ai_translator.translate(
                    med_name=med_name,
                    usage=raw_data["usage"],
                    warnings=raw_data["warnings"],
                    side_effects=raw_data["side_effects"],
                    found_in_fda=raw_data["found_in_fda"],
                )

                print("\n==================================================")
                print(f"         PILLSPEAK SUMMARY FOR {med_name.upper()}")
                print("==================================================")
                print(summary)
                if is_recalled:
                    print(f"\n⚠️ RECALL ALERT: {recall_msg}")
                print("==================================================")

                # 4. Save record to local JSON history
                med_record = Medication(
                    name=med_name,
                    summary=summary,
                    is_recalled=is_recalled,
                    recall_reason=recall_msg,
                )
                storage.save_medication(med_record)
                print("\n💾 Medication lookup saved to local history.")

            except Exception as e:
                print(f"\n❌ Error processing medication lookup: {e}")

        elif choice == "2":
            records = storage.load_history()
            if not records:
                print("\n📭 No past search history found.")
            else:
                print(f"\n=== PAST LOOKUPS ({len(records)} recorded) ===")
                for i, rec in enumerate(records, 1):
                    print(
                        f"\n{i}. Medication: {rec['name']} (Searched: {rec['timestamp']})"
                    )
                    print(
                        f"   Recalled: {rec['is_recalled']} | Recall Reason: {rec['recall_reason'][:60]}..."
                    )
                    print(f"   Summary Snippet: {rec['summary'][:90]}...")

        elif choice == "3":
            confirm = (
                input("\nAre you sure you want to clear all history? (y/n): ")
                .strip()
                .lower()
            )
            if confirm in ["y", "yes"]:
                storage.clear_history()
                print("🗑️ History cleared successfully.")
            else:
                print("Action cancelled.")

        elif choice == "4":
            print("\nThank you for using PillSpeak! Stay safe and informed.")
            break
        else:
            print("❌ Invalid option. Please choose a number between 1 and 4.")


if __name__ == "__main__":
    main()
