# 💊 PillSpeak: Patient Medication Translator

PillSpeak is a command-line tool that looks up medications, pulls official data from the FDA's [openFDA](https://open.fda.gov/) API, checks for active recalls, and uses Google's Gemini AI to translate dense clinical drug labels into clear, 5th-grade-level plain English.

> ⚠️ **Disclaimer**: PillSpeak is an informational tool, not a substitute for professional medical advice. Always consult a doctor or pharmacist before making decisions about medication.

## Features

- 🔍 **Medication lookup** — search by brand name, generic name, or common regional/international names
- 📋 **Official FDA data** — pulls usage, warnings, and side effect information directly from openFDA drug labels
- 🚨 **Recall checks** — flags active FDA enforcement/recall notices for the searched medication
- 🤖 **AI translation** — converts clinical language into simple, everyday English using Gemini, with a fallback to general AI knowledge when a drug isn't found in the FDA database
- 💾 **Local history** — saves each lookup to a local `history.json` file so you can revisit past searches
- 🧹 **History management** — view or clear your saved search history from the menu
- ✅ **Input validation** — sanitizes and validates medication name input before searching
- 🔁 **Retry logic** — automatically retries AI translation requests on transient (503) errors

## How It Works

1. You enter a medication name.
2. `FDAClient` queries openFDA's label and enforcement endpoints for usage, warnings, side effects, and recall status.
3. `AITranslator` sends the raw clinical text to Gemini, which rewrites it into a plain-language summary under three sections: **What It's For**, **Important Warnings**, and **Possible Side Effects**.
4. The result is displayed in the terminal and saved to `history.json` via `HistoryManager`.

## Requirements

- Python 3.10+
- A Google Gemini API key ([Google AI Studio](https://aistudio.google.com/))

### Dependencies

```bash
pip install requests google-genai
```

## Setup

1. Clone the repository and navigate into it:
   ```bash
   git clone <your-repo-url>
   cd pillspeak
   ```
2. Install dependencies (see above).
3. Set your Gemini API key as an environment variable. Either name works:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   # or
   export PillSpeak="your-api-key-here"
   ```

## Usage

Run the app from the terminal:

```bash
python main.py
```

You'll see a menu:

```
--- MAIN MENU ---
1. Look up a Medication
2. View Search History
3. Clear History
4. Exit
```

- **Option 1** — enter a medication name to fetch its FDA info, recall status, and AI-simplified summary
- **Option 2** — view a list of your past lookups
- **Option 3** — clear all saved history
- **Option 4** — exit the program

## Project Structure

```
pillspeak/
├── main.py             # CLI entry point and menu loop
├── models.py            # Medication dataclass (to_dict / from_dict for JSON storage)
├── services.py           # FDAClient (openFDA lookups) and AITranslator (Gemini integration)
├── storage.py            # HistoryManager for reading/writing history.json
├── utils.py              # TextSanitizer for input validation and text cleanup
├── history.json           # Local storage of past medication lookups (generated at runtime)
├── test_services.py         # Manual script to verify FDA + AI translation calls
└── test_storage.py          # Manual script to verify history save/load/clear
```

## Testing

`test_services.py` and `test_storage.py` are standalone verification scripts (not a pytest assertion suite) — running them prints step-by-step output so you can confirm the FDA lookup, AI translation, and history storage are working end-to-end:

```bash
python test_services.py
python test_storage.py
```

## Data Storage

Search history is stored locally in `history.json` in the project directory. Each entry includes the medication name, AI-generated summary, recall status, recall reason, and a timestamp. No data is sent anywhere other than the openFDA and Gemini APIs needed to process your search.

## License

Add your license of choice here (e.g., MIT).
