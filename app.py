import streamlit as st
import pandas as pd
import base64

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set the page configuration
st.set_page_config(
    page_title="Patient Details Lookup",
    page_icon=":hospital:",
    layout="centered",
    initial_sidebar_state="auto"
)

# Configuration for the PostgreSQL connection
DATABASE_URI = 'postgresql://adithya14255:1Wg3FwivuZDU@ep-twilight-mode-70634399-pooler.ap-southeast-1.aws.neon.tech/medical?sslmode=require'

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URI)

# Function to load patient data from the database
@st.cache_data(ttl=60)
def load_data():
    query = "SELECT * FROM patients"
    return pd.read_sql(query, engine)

# Function to save patient data back to the database
def save_data(df):
    df.to_sql('patients', engine, if_exists='replace', index=False)

# Load the patient data
df_patients = load_data()

def add_bg_from_url(image_url):
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url({image_url});
             background-size: cover;
         }}
         .tick-mark {{
             color: green;
             font-size: 2em;
             display: flex;
             justify-content: center;
             align-items: center;
             height: 100px;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

# Add background image
add_bg_from_url("https://4kwallpapers.com/images/walls/thumbs_3t/8324.png")

# Set the title and header
st.title('Patient Details Lookup')
st.subheader('Find and update patient details')

# Input for patient's name, ID, and editor's name
col1, col2 = st.columns(2)
with col1:
    patient_name = st.text_input('Enter Patient Name')
with col2:
    patient_id = st.number_input('Enter Patient ID', min_value=1)

editor_name = st.text_input('Enter Your Name')

# Search for patient
if st.button('Search'):
    patient = df_patients[(df_patients['Name'].str.lower() == patient_name.lower()) & (df_patients['ID'] == patient_id)]

    if not patient.empty:
        st.subheader('Patient Details (Editable):')
        
        # Ensure the DataFrame has an 'Edited_By' column
        if 'Edited_By' not in patient.columns:
            patient['Edited_By'] = ""

        edited_patient = st.data_editor(patient, use_container_width=True, key='data_editor')

        if st.button('Save Changes'):
            # Update the original dataframe with the edited rows
            edited_rows = st.session_state['data_editor']['edited_rows']
            for row_idx, updates in edited_rows.items():
                for col, new_value in updates.items():
                    df_patients.at[row_idx, col] = new_value
                # Mark the editor's name for the edited row
                df_patients.at[row_idx, 'Edited_By'] = editor_name

            save_data(df_patients)
            st.success('Patient details updated successfully!')

            # Show confirmation tick
            st.markdown('<div class="tick-mark">✔</div>', unsafe_allow_html=True)

        # Download link for the searched patient's details
        csv = edited_patient.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="patient_details.csv" style="color: #007bff; text-decoration: underline;">Download Patient Details</a>'
        st.markdown(href, unsafe_allow_html=True)
    else:
        st.error('No patient found with the provided details.')
