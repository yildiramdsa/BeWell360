# BeWell360: Your Daily Holistic Wellness Log

![BeWell360](https://github.com/yildiramdsa/BeWell360/blob/main/images/BeWell360-github.png)

BeWell360 is a modular, AI-driven platform that turns users’ daily holistic wellness logs into personalized, goal-focused guidance.

## Run locally with Streamlit (virtualenvwrapper)

### Prerequisites

- Python 3
- `virtualenvwrapper` installed and initialized in your shell

### Create a new virtualenv, install deps, run the app

From the repo root:

```bash
mkvirtualenv bewell
pip install -r requirements.txt
streamlit run app.py
```

### Re-use an existing virtualenv

If you already created the env earlier:

```bash
workon bewell
pip install -r requirements.txt
streamlit run app.py
```
