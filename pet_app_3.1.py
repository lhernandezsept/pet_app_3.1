#!/usr/bin/env python
# coding: utf-8

# In[29]:


import streamlit as st
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz
import base64
from PIL import Image
import os


st.write("__file__ is:", __file__ if '__file__' in globals() else "No __file__ in this environment")
st.write("Current working directory is:", os.getcwd())

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Load credentials from Streamlit secrets
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)

# Authorize the gspread client
client = gspread.authorize(creds)

SPREADSHEET_ID = "1UNo82AyTd07v_z1AytJpsPG5HO7xun9KyGsHSJ5QcqE"
spreadsheet = client.open_by_key(SPREADSHEET_ID)
worksheet = spreadsheet.worksheet("Data")

# virtual clock
def show_clock():
    now = datetime.now(pytz.timezone("America/Chicago"))
    clock_html = f"<div class='clock'>{now.strftime('%A, %B %d, %Y %I:%M:%S %p')}</div>"
    clock_css = """
    <style>
        .clock {
            font-size: 4em;
            font-weight: bold;
            color: #39ff14;
            text-shadow: 0 0 5px #ff00ff, 0 0 10px #ff00ff, 0 0 20px #ff00ff;
            background-color: rgba(173, 216, 230, 0.3);
            backdrop-filter: blur(5px);
            padding: 20px 40px;
            border-radius: 20px;
            margin-bottom: 10px;
            display: inline-block;
            text-align: center;
            font-family: 'Orbitron', sans-serif;
        }
    </style>
    """
    st.markdown(clock_html + clock_css, unsafe_allow_html=True)
def get_base_dir():
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        return os.getcwd()

BASE_DIR = get_base_dir()
st.write("BASE_DIR is:", BASE_DIR)

image_path = os.path.join(BASE_DIR, "assets", "boston.jpg")
st.write("Image path is:", image_path)
st.write("Does image exist?", os.path.exists(image_path))

def set_background(image_file, overlay="rgba(255, 255, 255, 0.6)"):
    with open(image_file, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()

    # Properly escaped curly braces for f-string
    css = f"""
    <style>
        .stApp {{
            background: 
                linear-gradient({overlay}, {overlay}),
                url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)

if os.path.exists(image_path):
    set_background(image_path)
else:
    st.error(f"Image not found at: {image_path}")    





# Fetch the latest activity records
def get_latest_submission_summaries(n=5):
    rows = worksheet.get_all_values()
    if len(rows) < 2:
        return [{"Message": "No records found yet!"}]

    header = rows[0]
    data_rows = rows[1:]
    latest_activities = []

    for row in data_rows[-n:]:
        activity = {"Timestamp": row[0]}
        for col_name, val in zip(header[1:], row[1:]):
            if val not in ["Not Provided", ""]:
                activity[col_name] = val
        latest_activities.append(activity)

    return latest_activities


# Styling and defining main page
def main_page():
    if os.path.exists(image_path):
        set_background(image_path)
    else:
        st.error(f"Image not found at: {image_path}")
    show_clock()

    st.markdown('<h2>📝 Latest Activity</h2>', unsafe_allow_html=True)
    latest_activities = get_latest_submission_summaries(5)

    if latest_activities and "Message" in latest_activities[0]:
      st.markdown(
    '<div style="color: black;" class="card">No records found yet!</div>',
    unsafe_allow_html=True
)
    else:
        for activity in latest_activities:
            timestamp = activity.get("Timestamp", "")
            st.markdown(f"<p style='font-weight:bold; color:#2E86C1;'>{timestamp}</p>", unsafe_allow_html=True)
            for key, val in activity.items():
                if key != "Timestamp":
                    st.markdown(f"• {key}: {val}")
            st.markdown("<hr>", unsafe_allow_html=True)


    # Dashboard Header
    st.markdown("""
        <div class="dashboard-header">
            <h1>🐾 Pet Care Dashboard</h1>
            <p>Choose a section to log activities:</p>
        </div>
    """, unsafe_allow_html=True)

    
    # Navigation Buttons
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        st.button("🥩 Feeding", key="feeding_button", on_click=lambda: st.session_state.update({"page": "feeding"}))

    with col2:
        st.button("🩺 Wellness", key="wellness_button", on_click=lambda: st.session_state.update({"page": "wellness"}))

    with col3:
        st.button("🎾 Enrichment", key="enrichment_button", on_click=lambda: st.session_state.update({"page": "enrichment"}))

    with col4:
        st.button("📜 Past Records", key="past_records_button", on_click=lambda: st.session_state.update({"page": "past_records"}))

    # CSS styles for main page elements
    st.markdown("""
    <style>
        /* --- General page background --- */
        .main {
            background-color: transparent;
        }

        /* --- Card styling --- */
        .card {
            background-color: rgba(255, 255, 255, 0.85);
            padding: 20px;
            border-radius: 20px;
            box-shadow: 2px 2px 12px rgba(0,0,0,0.15);
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
        /* --- Section headers --- */
        h2 {
            color: navy;
            font-weight: bold;
            margin-bottom: 15px;
        }

        /* --- Dashboard header --- */
        .dashboard-header {
            text-align: center;
            padding: 30px 0 20px 0;
            background: linear-gradient(to right, #74ebd5, #ACB6E5);
            border-radius: 16px;
            margin-bottom: 30px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        .dashboard-header h1 {
            color: #0F2027;
            font-size: 40px;
            margin: 0;
            font-weight: 800;
        }
        .dashboard-header p {
            font-size: 18px;
            color: #333;
            margin-top: 10px;
        }
        /* --- Base button style (applies to all buttons) --- */
        div.stButton > button {
            width: 100%;
            height: 60px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 12px;
            border: none;
            padding: 10px 20px;
            margin: 5px;
            color: white;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            transition: all 0.2s ease-in-out;
        }

        div.stButton > button[key="feeding_button"] {
            background: linear-gradient(to right, #FF416C, #FF4B2B);
        }

        div.stButton > button[key="wellness_button"] {
            background: linear-gradient(to right, #00b09b, #96c93d);
        }

        div.stButton > button[key="enrichment_button"] {
            background: linear-gradient(to right, #f7971e, #ffd200);
            color: #333;
        }

        div.stButton > button[key="past_records_button"] {
            background: linear-gradient(to right, #654ea3, #eaafc8);
        }

        div.stButton > button:hover {
            background-color: white !important;
            background-image: none !important;
            color: black !important;
            transform: scale(1.03);
            cursor: pointer;
        }

        div.stButton > button:active {
            transform: scale(0.97);
        }
        
        /* --- Submit button --- */
        div.stButton > button[key="submit_feeding"],
        div.stButton > button[key="submit_wellness"],
        div.stButton > button[key="submit_enrichment"],
        div.stButton > button[key="submit_past_records"] {
            background-color: #28a745;
            color: white;
        }

        /* --- Back button --- */
        div.stButton > button[key="back_feeding"],
        div.stButton > button[key="back_wellness"],
        div.stButton > button[key="back_enrichment"],
        div.stButton > button[key="back_past_records"] {
            background-color: #003366;
            color: white;
        }

    </style>
    """, unsafe_allow_html=True)
        
        



# ------------------------------
# Utility Functions
# ------------------------------
ALL_COLUMNS = [
    "Timestamp", "Kibble", "Toppers", "Treats",
    "Dental Chew", "Teeth Cleaning", "Teeth Cleaning Notes",
    "Nail Trim", "Nail Trim Notes", "Medication",
    "Walk", "Park", "Played Ball", "Proofing Commands", "Love & Praise"
]
DEFAULT_VALUES = {col: "Not Provided" for col in ALL_COLUMNS if col != "Timestamp"}

def not_provided(val):
    return val if val not in ["Choose option", "", None] else "Not Provided"

def append_submission(submission_data):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [timestamp] + [not_provided(submission_data.get(col, DEFAULT_VALUES[col]))
                         for col in ALL_COLUMNS if col != "Timestamp"]
    worksheet.append_row(row)



# ------------------------------
# Page Definitions
# ------------------------------
def feeding_page():
    show_clock()
    base_dir = get_base_dir()
    image_path = os.path.join(base_dir, "assets", "smile.jpg")  # adjust if image is in a subfolder
    if os.path.exists(image_path):
        st.image(image_path, use_column_width=True)
    else:
        st.error(f"Image not found at {image_path}")    
    st.title("🥩 Feeding Section")

    kibble = st.selectbox("Kibble?", ["Choose option", "Yes", "No"])
    toppers = st.selectbox("Toppers?", ["Choose option", "Yes", "No"])
    treats = st.multiselect("Treats", ["Raw Chews", "Training", "Hemp Chews", "Kong (Filling)"])

    feeding_data = {
        "Kibble": not_provided(kibble),
        "Toppers": not_provided(toppers),
        "Treats": ", ".join(treats) if treats else "Not Provided"
    }

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Submit", key="submit_feeding"):
            append_submission(feeding_data)
            st.session_state.page = "main"

    with col2:
        st.button(
            "🔙 to main page",
            key="back_feeding",
            on_click=lambda: st.session_state.update({"page": "main"})
        )

def wellness_page():
    show_clock()
    base_dir = get_base_dir()
    image_path = os.path.join(base_dir, "assets", "meme.jpg")  # adjust if image is in a subfolder
    if os.path.exists(image_path):
        st.image(image, use_container_width=True)
    else:
        st.error(f"Image not found at {image_path}") 
    st.title("🩺 Wellness Section")

    dental_chew = st.selectbox("Dental Chew?", ["Choose option", "Yes", "No"])
    teeth_cleaning = st.selectbox("Teeth Cleaning?", ["Choose option", "Yes", "No"])
    teeth_notes = st.text_input("Teeth Cleaning Notes") if teeth_cleaning == "Yes" else "Not Provided"
    nail_trim = st.selectbox("Nail Trim?", ["Choose option", "Yes", "No"])
    nail_notes = st.text_input("Nail Trim Notes") if nail_trim == "Yes" else "Not Provided"
    meds = st.text_input("Medication Notes") or "Not Provided"

    wellness_data = {
        "Dental Chew": not_provided(dental_chew),
        "Teeth Cleaning": not_provided(teeth_cleaning),
        "Teeth Cleaning Notes": teeth_notes,
        "Nail Trim": not_provided(nail_trim),
        "Nail Trim Notes": nail_notes,
        "Medication": meds
    }

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Submit", key="submit_wellness"):
            append_submission(wellness_data)
            st.session_state.page = "main"

    with col2:
        st.button(
            "🔙 to main page",
            key="back_wellness",
            on_click=lambda: st.session_state.update({"page": "main"})
        )



def enrichment_page():
    show_clock()
    col1, col2 = st.columns(2)
    with col1:
        base_dir = get_base_dir()
    image_path = os.path.join(base_dir, "assets", "friends.jpg")  # adjust if image is in a subfolder
    if os.path.exists(image_path):
        st.image(image_path, use_column_width=True)
    else:
        st.error(f"Image not found at {image_path}") 
        base_dir = get_base_dir()
    image_path = os.path.join(base_dir,"assets", "rope.jpg")  # adjust if image is in a subfolder
    if os.path.exists(image_path):
        st.image(image_path, use_column_width=True)
    else:
        st.error(f"Image not found at {image_path}") 

    st.title("🎾 Enrichment Section")
    walk = st.text_input("Walk Distance (e.g., 1 mile)")
    park = st.selectbox("Park?", ["Choose option", "Yes", "No"])
    played_ball = st.selectbox("Played Ball?", ["Choose option", "Yes", "No"])
    proofing_commands = st.text_input("Proofing Commands")
    love_praise = st.selectbox("Love & Praise?", ["Choose option", "Yes", "No"])

    enrichment_data = {
        "Walk": walk.strip() if walk.strip() else "Not Provided",
        "Park": not_provided(park),
        "Played Ball": not_provided(played_ball),
        "Proofing Commands": proofing_commands.strip() if proofing_commands.strip() else "Not Provided",
        "Love & Praise": not_provided(love_praise)
    }

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Submit", key="submit_enrichment"):
            append_submission(enrichment_data)
            st.session_state.page = "main"

    with col2:
        st.button(
            "🔙 to main page",
            key="back_enrichment",
            on_click=lambda: st.session_state.update({"page": "main"})
        )

# ------------------------------
# Past Records Page
# ------------------------------
def past_records_page():
    show_clock()
    base_dir = get_base_dir()
    image_path = os.path.join(base_dir, "assets", "relax.jpg")  # adjust if image is in a subfolder
    if os.path.exists(image_path):
        st.image(image_path, use_column_width=True)
    else:
        st.error(f"Image not found at {image_path}") 
    st.title("📜 Past Records")
    
    df = fetch_records()

    if df.empty:
        st.info("Chispa's care journal is empty. Track her care by submitting logs!")

    else:
        # Filter by section
        sections = ["All"] + sorted(df['Section'].unique())
        section_filter = st.selectbox("Filter by Section:", sections)
        if section_filter != "All":
            df = df[df['Section'] == section_filter]

        # Filter by date range
        if 'Date' in df.columns:
            min_date = df['Date'].min()
            max_date = df['Date'].max()
            date_filter = st.date_input("Filter by Date:", value=(min_date, max_date))
            if isinstance(date_filter, tuple) and len(date_filter) == 2:
                start_date, end_date = date_filter
                df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]

        st.dataframe(df.sort_values(by='Date', ascending=False))
    
    col1, col2 = st.columns(2)

    with col2:
        st.button(
            "🔙 to main page",
            key="back_past_records",
            on_click=lambda: st.session_state.update({"page": "main"})
        )



# ------------------------------
# Fetch Records Function
# ------------------------------
def fetch_records():
    rows = worksheet.get_all_values()
    if not rows or len(rows) < 2:
        return pd.DataFrame()  # No data yet

    header = rows[0]
    data_rows = rows[1:]
    df = pd.DataFrame(data_rows, columns=header)
    
    # Optional: Add a 'Section' column based on which fields are filled
    def determine_section(row):
        if row["Kibble"] != "Not Provided" or row["Toppers"] != "Not Provided" or row["Treats"] != "Not Provided":
            return "Feeding"
        elif row["Dental Chew"] != "Not Provided" or row["Teeth Cleaning"] != "Not Provided" or row["Medication"] != "Not Provided":
            return "Wellness"
        elif row["Walk"] != "Not Provided" or row["Park"] != "Not Provided" or row["Played Ball"] != "Not Provided":
            return "Enrichment"
        else:
            return "Unknown"

    df["Section"] = df.apply(determine_section, axis=1)
    
    # Convert timestamp to datetime for filtering
    df["Date"] = pd.to_datetime(df["Timestamp"])
    return df





      
 
# ------------------------------
# App Runner
# ------------------------------
if "page" not in st.session_state:
    st.session_state.page = "main"

page = st.session_state.page

if page == "main":
    main_page()
elif page == "feeding":
    feeding_page()
elif page == "wellness":
    wellness_page()
elif page == "enrichment":
    enrichment_page()
elif page == "past_records":
    past_records_page()



# In[ ]:





# In[ ]:




