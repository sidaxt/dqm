import streamlit as st
import os
import subprocess
import pandas as pd

# Define the folder to save the files
save_folder = "public/data/input/usecase2"
processed_folder = "public/data/output"

if not os.path.exists(save_folder):
    os.makedirs(save_folder)
if not os.path.exists(processed_folder):
    os.makedirs(processed_folder)

# session state to check wheather the files are procesed or not
if "processed_2" not in st.session_state:
    st.session_state["processed_2"] = None

# Function to save the uploaded file with a specific name
def save_file(uploaded_file, filename):
    with open(os.path.join(save_folder, filename), "wb") as f:
        f.write(uploaded_file.getbuffer())

# Function to run the external Python script
def run_processing_script():
    python_env = "C:/atul/poc1/DQM_GenAI_Usecases/.venv/Scripts/python.exe"
    try:
        with st.spinner("Processing data... Please wait.") :
            subprocess.run([python_env, "usecase2_dq_rule.py"], check=True)
        st.success("Data processed successfully!")
        st.session_state["processed_2"] = True
        return True  # Indicate successful processing
    except subprocess.CalledProcessError as e:
        st.error(f"Error during processing: {e}")
        return False

st.title("Identify Data Quality Rules")
st.text("Please Upload All required files")

#column definations for buttons and input fields
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)
c1,c2,c3 = st.columns(3)

#function to provide download functionality
def download_file(file_path, file_name):
    with open(file_path, "rb") as f:
        file_data = f.read()
    with c3:
        st.download_button(
            label="Download Processed File",
            data=file_data,
            file_name=file_name,
            mime="application/octet-stream"
        )

#Taking File inputs
with col1:
    file1 = st.file_uploader("Upload Customer Data file", type=["csv"])
with col2:
    file2 = st.file_uploader("Upload Metadata file", type=["json"])
with col3:
    file3 = st.file_uploader("Upload dq_rules file", type=["json"])
with col4:
    file4 = st.file_uploader("Upload Issues file", type=["json"])

# session state to verify file upload.
if "files_uploaded_2" not in st.session_state:
    st.session_state["files_uploaded_2"] = False


# Check if all files have been uploaded
if file1 and file2 and file3 and file4:
    # Create the submit button
    with c1:
        submit_button = st.button("Submit")

    # When submit button is pressed, save the files
    if submit_button:
        save_file(file1, "customers.csv")
        save_file(file2, "metadata.json")
        save_file(file3, "customers_dq_rules.json")
        save_file(file4, "issues.json")
        st.success("All files have been successfully submitted!")

        st.session_state["files_uploaded_2"] = True


# Store processed file path in session state
if "processed_file_path_2" not in st.session_state:
    st.session_state["processed_file_path_2"] = None

#session state to store first five rows.
if "first_5_rows_2" not in st.session_state:
    st.session_state["first_5_rows_2"] = None


# Process button logic, only visible when files are uploaded
if st.session_state["files_uploaded_2"]:
    with c2:
        process_button = st.button("Process Data")
    
    if process_button:
        if run_processing_script():
            #loading specified output file path
            processed_file_path_2 = os.path.join(processed_folder, "new_dq_rules.csv")  
            st.session_state["processed_file_path_2"] = processed_file_path_2
        try:
            # Load the processed file into a DataFrame
            df = pd.read_csv(processed_file_path_2)
            st.session_state["first_5_rows_2"] = df.head()

        except Exception as e:
            st.error(f"Error displaying processed data: {e}")
    #code to displaythe output
    processed_file_path_2 = os.path.join(processed_folder, "new_dq_rules.csv")  # Example processed file
    st.session_state["processed_file_path_2"] = processed_file_path_2
    
    if st.session_state["processed_2"] is not None:
        download_file(processed_file_path_2, "new_dq_rules.csv")

    if st.session_state["first_5_rows_2"] is not None:
        st.write("First 5 rows of the processed data:")
        st.write(st.session_state["first_5_rows_2"])
       
else:
    # Display message if not all files are uploaded
    st.warning("Please upload all 4 files before submitting.")
