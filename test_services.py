from services import FDAClient, AITranslator

print("=== TESTING PILLSPEAK SERVICES ===")

# 1. Initialize FDA Client
fda = FDAClient()
med_name = "Ibuprofen"

print(f"\n1. Fetching FDA info for '{med_name}'...")
try:
    data = fda.fetch_drug_info(med_name)
    print("   ✅ Success! Retrieved drug data.")
    print(f"   Usage Preview: {data['usage'][:120]}...")

    print(f"\n2. Checking recall list for '{med_name}'...")
    is_recalled, recall_msg = fda.check_recalls(med_name)
    print(f"   Recalled: {is_recalled}")
    print(f"   Details: {recall_msg}")

    # 2. Initialize AI Translator
    print("\n3. Testing Gemini AI Translation...")
    translator = AITranslator()
    summary = translator.translate(
        med_name, data["usage"], data["warnings"], data["side_effects"]
    )

    print("\n==================================")
    print("      AI TRANSLATED SUMMARY       ")
    print("==================================")
    print(summary)

except Exception as e:
    print(f"\n❌ An error occurred during testing: {e}")