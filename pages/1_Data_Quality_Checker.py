import streamlit as st
import os
import subprocess
import pandas as pd


# Define the folder to save the files
save_folder = "public/data/input/usecase1"
# Define the folder for output files
processed_folder = "public/data/output"

if not os.path.exists(save_folder):
    os.makedirs(save_folder)
if not os.path.exists(processed_folder):
    os.makedirs(processed_folder)



# Function to save the uploaded files
def save_file(uploaded_file, filename):
    with open(os.path.join(save_folder, filename), "wb") as f:
        f.write(uploaded_file.getbuffer())

# Store processed file path in session state
if "processed_1" not in st.session_state:
    st.session_state["processed_1"] = None

# Function to run the external Python script
def run_processing_script():
    #address to your envirnoment specific interprator
    python_env = "C:/atul/poc1/DQM_GenAI_Usecases/.venv/Scripts/python.exe"
    try:
        with st.spinner("Processing data... Please wait.") :
            subprocess.run([python_env, "usecase1_dq_score.py"], check=True)
        st.success("Data processed successfully!")
        st.session_state["processed_1"] = True
        return True  # Indicate successful processing
    except subprocess.CalledProcessError as e:
        st.error(f"Error during processing: {e}")
        return False
#function to provide file download functionality
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

# Title
st.title("Data Quality Checker")
# st.markdown("""
# In this page, you can upload your dataset in **JSON format** along with the corresponding **metadata** and **Data Quality rules** that you want to apply. The dataset will be evaluated against the **data quality rules** to calculate individual **data quality (DQ) scores** for each record. Ensure your dataset and metadata are in the correct format to avoid errors.
# """)
st.text("Please Upload Required Files")

#columns for file uploads
col1, col2 = st.columns(2)

with col1:
    file1 = st.file_uploader("Upload Customer Data file", type=["csv"])
with col2:
    file2 = st.file_uploader("Upload Metadata file", type=["json"])
file3 = st.file_uploader("Upload dq_rules file", type=["json"])

#session state to keep track of file uploads
if "files_uploaded_1" not in st.session_state:
    st.session_state["files_uploaded_1"] = False

#column definetion for Buttons
c1,c2,c3 = st.columns(3)


# Check if all files have been uploaded
if file1 and file2 and file3:
    # Create the submit button
    with c1:
        submit_button = st.button("Submit")

    # When submit button is pressed, save the files
    if submit_button:
        save_file(file1, "customers.csv")
        save_file(file2, "metadata.json")
        save_file(file3, "dq_rules_for_dqscore.json")
        st.success("All files have been successfully submitted!")

        st.session_state["files_uploaded_1"] = True



# Store processed file path in session state
if "processed_file_path_1" not in st.session_state:
    st.session_state["processed_file_path_1"] = None

# Store DQ score in session state
if "average_dq_score" not in st.session_state:
    st.session_state["average_dq_score"] = None
#store top 5 rows in session state.
if "first_5_rows_1" not in st.session_state:
    st.session_state["first_5_rows_1"] = None



# Process button logic, only visible when files are uploaded
if st.session_state["files_uploaded_1"]:
    with c2:
        process_button = st.button("Process Data")
    
    if process_button:
        if run_processing_script(): #this run_processing_script function will call the external script
            #defining and storing the path of output file/processed file
            processed_file_path_1 = os.path.join(processed_folder, "final_dataset_with_dq_scores.csv")  
            st.session_state["processed_file_path_1"] = processed_file_path_1

        # Load the processed file into a DataFrame
        try:
            df = pd.read_csv(processed_file_path_1)
            
            # Calculate the average DQ score and store it in session state
            if "DQ_Score" in df.columns:
                average_dq_score = df["DQ_Score"].mean()  # Calculate average of the DQ_Score column
                st.session_state["average_dq_score"] = average_dq_score
            else:
                st.error("DQ_Score column not found in the processed data.")
            
            # Store the first 5 rows in session state
            st.session_state["first_5_rows_1"] = df.head()

        except Exception as e:
            st.error(f"Error displaying processed data: {e}")

    #below is code for displaying the avrage score and top 5 rows.
    processed_file_path_1 = os.path.join(processed_folder, "final_dataset_with_dq_scores.csv")  # Example processed file
    st.session_state["processed_file_path_1"] = processed_file_path_1
    
    if st.session_state["processed_1"] is not None:
        download_file(processed_file_path_1, "final_dataset_with_dq_scores.csv")
    # Display average DQ score and the first 5 rows, if available
    if st.session_state["average_dq_score"] is not None:
        st.write(f"Average Data Quality Score: {st.session_state['average_dq_score']:.2f}")

    if st.session_state["first_5_rows_1"] is not None:
        st.write("First 5 rows of the processed data:")
        st.write(st.session_state["first_5_rows_1"])


       
else:
    # Display message if not all files are uploaded
    st.warning("Please upload all 3 files before submitting.")
