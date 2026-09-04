from models import Medication
from storage import HistoryManager

print("=== TESTING HISTORY STORAGE ===")

storage = HistoryManager("test_history.json")

# Clean up any leftover test file
storage.clear_history()

# Create a sample Medication record using summary
sample_med = Medication(
    name="Ibuprofen",
    summary="• **What It's For**: Minor aches, pain, and fever reduction.\n• **Important Warnings**: Avoid if allergic to aspirin.",
    is_recalled=False,
    recall_reason="No active recall notices found.",
)

# 1. Test Saving
print("\n1. Saving medication record to JSON...")
storage.save_medication(sample_med)
print("   ✅ Record saved.")

# 2. Test Loading
print("\n2. Loading history from JSON...")
records = storage.load_history()
print(f"   ✅ Records retrieved: {len(records)}")

if records:
    print("\n--- RETRIEVED RECORD ---")
    print(f"Name: {records[0]['name']}")
    print(f"Summary: {records[0]['summary'][:60]}...")
    print(f"Recalled: {records[0]['is_recalled']}")
    print(f"Timestamp: {records[0]['timestamp']}")

# Clean up test file after verification
storage.clear_history()