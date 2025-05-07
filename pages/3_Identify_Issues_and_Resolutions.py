import streamlit as st
import os
import subprocess
import pandas as pd

# Define the folder to save the files
save_folder = "public/data/input/usecase3"
processed_folder = "public/data/output"

if not os.path.exists(save_folder):
    os.makedirs(save_folder)
if not os.path.exists(processed_folder):
    os.makedirs(processed_folder)

# Store processed file path in session state
if "processed_3" not in st.session_state:
    st.session_state["processed_3"] = None


# Function to save the uploaded file with a specific name
def save_file(uploaded_file, filename):
    with open(os.path.join(save_folder, filename), "wb") as f:
        f.write(uploaded_file.getbuffer())

# Function to run the external Python script
def run_processing_script():
    python_env = "C:/atul/poc1/DQM_GenAI_Usecases/.venv/Scripts/python.exe"
    try:
        with st.spinner("Processing data... Please wait.") :
            subprocess.run([python_env, "usecase3_potential_issue.py"], check=True)
        st.success("Data processed successfully!")
        st.session_state["processed_3"] = True
        return True  # Indicate successful processing
    except subprocess.CalledProcessError as e:
        st.error(f"Error during processing: {e}")
        return False
    
st.title("Identify Issues and Resolutions")

col1,col2 =st.columns(2)
col3,col4 =st.columns(2)
col5,col6 = st.columns(2)
c1,c2,c3 = st.columns(3)


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


with col1:
    file1 = st.file_uploader("Upload Data test file", type=["json"])
with col2:
    file2 = st.file_uploader("Upload Metadata file", type=["json"])
with col3:
    file3 = st.file_uploader("Upload dq_rules file", type=["json"])
with col4:
    file4 = st.file_uploader("Upload Issues file", type=["json"])
with col5:
    file5 = st.file_uploader("Upload dataset file", type=["json"])

if "files_uploaded_3" not in st.session_state:
    st.session_state["files_uploaded_3"] = False


# Check if all files have been uploaded
if file1 and file2 and file3 and file4 and file5:
    # Create the submit button
    with c1:
        submit_button = st.button("Submit")

    # When submit button is pressed, save the files
    if submit_button:
        save_file(file1, "data_test.json")
        save_file(file2, "metadata.json")
        save_file(file3, "dq_rules.json")
        save_file(file4, "issues.json")
        save_file(file5, "dataset.json")
        st.success("All files have been successfully submitted!")

        st.session_state["files_uploaded_3"] = True


# Store processed file path in session state
if "processed_file_path_3" not in st.session_state:
    st.session_state["processed_file_path_3"] = None


if "first_5_rows_3" not in st.session_state:
    st.session_state["first_5_rows_3"] = None


# Process button logic, only visible when files are uploaded
if st.session_state["files_uploaded_3"]:
    with c2:
        process_button = st.button("Process Data")
    
    if process_button:
        try:
            if run_processing_script():
                processed_file_path_3 = os.path.join(processed_folder, "potential_issues.csv")  
                st.session_state["processed_file_path_3"] = processed_file_path_3
            try:
                # Load the processed file into a DataFrame
                df = pd.read_csv(processed_file_path_3)
                st.session_state["first_5_rows_3"] = df.head()
            except Exception as e:
                st.error(f"Error displaying processed data: {e}")

        except Exception as e:
            st.error(f"please click on process data button again")
    #code to display the output
    processed_file_path_3 = os.path.join(processed_folder, "potential_issues.csv")  
    st.session_state["processed_file_path_3"] = processed_file_path_3
    
    if st.session_state["processed_3"] is not None:
        download_file(processed_file_path_3, "potential_issues.csv")

    if st.session_state["first_5_rows_3"] is not None:
        st.write("First 5 rows of the processed data:")
        st.write(st.session_state["first_5_rows_3"])
else:
    # Display message if not all files are uploaded
    st.warning("Please upload all 5 files before submitting.")
