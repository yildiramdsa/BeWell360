# BeWell360: Your Daily Holistic Wellness Log

![BeWell360](https://github.com/yildiramdsa/BeWell360/blob/main/images/BeWell360-github.png)

BeWell360 is a holistic wellness tracker that uses data science and analytics to transform daily logs—nutrition, fitness, sleep, body composition, professional development, and personal growth—into actionable insights for balanced living.

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
