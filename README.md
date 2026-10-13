# AI Quest — DSC401-6 Artificial Intelligence Quiz

Interactive quiz for Units I and II of Artificial Intelligence.

## Files
- `app.py`: Streamlit user interface, quiz flow, scoring and review.
- `questions.json`: 50 questions with answer keys and explanations.
- `requirements.txt`: required Python package.

## Run locally
1. Install Python 3.10 or later.
2. Open a terminal in this folder.
3. Create and activate a virtual environment (recommended).
4. Install dependencies:
   `python -m pip install -r requirements.txt`
5. Start the app:
   `streamlit run app.py`
6. Open the local URL printed by Streamlit.

## Features
- 50-question bank with multiple question formats
- Topic and difficulty labels
- Randomized question order
- Configurable quiz length
- Immediate feedback and explanations
- Progress bar and final score
- Answer review
- Marks converted to a score out of 25

## Notes
The quiz is a practice/educational application. Results are stored in the current browser session and are not persisted to a database.
