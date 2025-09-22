import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.title("Nutrition & Hydration")

DATA_DIR = "data"
csv_file = os.path.join(DATA_DIR, "nutrition_and_hydration.csv")

# Create CSV if doesn't exist
if not os.path.exists(csv_file):
    df = pd.DataFrame(columns=["date", "breakfast", "lunch", "dinner", "snacks", "water_ml"])
    df.to_csv(csv_file, index=False)
else:
    df = pd.read_csv(csv_file)

st.dataframe(df)
