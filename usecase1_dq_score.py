import json
import os
import pandas as pd
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
from pprint import pprint

# Load environment variables
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_api_base = os.getenv("OPENAI_API_BASE")
openai_api_version = os.getenv("OPENAI_API_VERSION")
openai_api_type = os.getenv("OPENAI_API_TYPE")
openai_api_endpoint = os.getenv("OPENAI_API_BASE")

DEPLOYMENT_NAME = "gpt-4"

# Initialize LLM
llm = AzureChatOpenAI(
    deployment_name=DEPLOYMENT_NAME,
    model_name="gpt-4",
    openai_api_key=openai_api_key,
    openai_api_base=openai_api_endpoint,
    api_version=openai_api_version,
    temperature=0,
    model_kwargs={"seed": 42}
)

# Define the prompt template for the LLM
prompt_template = prompt_template = """
You have a dataset in JSON format and a set of data quality (DQ) rules. Your tasks are:

1. Evaluate each data record against the provided DQ rules.
2. Calculate a DQ score for each record: DQ score = (Number of DQ rules passed / Total DQ rules) * 100.
3. Provide the average DQ score for the dataset.

**Note:** Use only the provided DQ rules.Do not use any other DQ rules.

Make sure the length of dq scores is same as number of records in dataset.
Return your response strictly in JSON format with this structure:


    "dq_scores": [DQ score for each record],
    "average_dq_score": average DQ score

( Do not provide explanations or additional comments.)    

Dataset: {dataset}
Metadata: {metadata}
DQ Rules: {dq_rules}
"""

prompt = PromptTemplate(template=prompt_template, input_variables=["dataset", "metadata", "dq_rules"])

# Load dataset and other files
def load_data():
    # Load dataset with the header
    dataset = pd.read_csv('public/data/input/usecase1/customers.csv')  # Retain the header
    # Extract only the data rows (without the header)
    data_rows = dataset.iloc[0:].reset_index(drop=True)  # Skip the header row
    data_rows_json = data_rows.to_json(orient='records')  # Convert the data rows to JSON
    # Load metadata and DQ rules
    with open('public/data/input/usecase1/metadata.json', 'r') as metadata_file:
        metadata = json.load(metadata_file)
    with open('public/data/input/usecase1/dq_rules_for_dqscore.json', 'r') as dq_file:
        dq_rules = json.load(dq_file)

    return dataset, data_rows_json, metadata, dq_rules

# Generate DQ scores for each record
def generate_dq_scores():
    # Load dataset and other files
    dataset_df, data_rows_json, metadata, dq_rules = load_data()

    # Call the LLM with the data rows
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    response = llm_chain.run({
        "dataset": data_rows_json,
        "metadata": metadata,
        "dq_rules": dq_rules
    })

    # Debugging: Print the raw response to inspect it
    print("Raw LLM response:", response)
    # print(data_rows_json[:100])
    # print(data_rows_json[6000:])


    try:
        # Parse the JSON response
        json_start = response.find('{')
        if json_start != -1:
            response_json = response[json_start:].strip()
            data_dict = json.loads(response_json)
        else:
            raise ValueError("No valid JSON found in LLM response.")

        dq_scores = data_dict.get("dq_scores", [])
        average_dq_score = data_dict.get("average_dq_score", None)
        # print(len(dq_scores))
        # print(len(dataset_df))
        # print(dataset_df.head)
        # print(len(data_rows_json))
        print(dq_scores)

        # Ensure that DQ scores and dataset match
        # if len(dq_scores) != len(dataset_df) - 1:
        #     raise ValueError("The number of DQ scores does not match the number of data rows.")

        # Append the DQ scores to the data
        # set (starting from row 2)
        dataset_df['DQ_Score'] = dq_scores  # First row (header) gets None for DQ Score

        # Add a new row with the average DQ score (broadcast it across all columns)
        avg_row = pd.Series(["Average DQ Score"] + [""] * (len(dataset_df.columns) - 2) + [average_dq_score], index=dataset_df.columns)
        dataset_df = dataset_df._append(avg_row, ignore_index=True)

        # Save the final dataset to CSV, including headers
        dataset_df.to_csv('public/data/output/final_dataset_with_dq_scores.csv', index=False, header=True)
        print("Final dataset saved to final_dataset_with_dq_scores.csv")

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print("LLM Response was:", response)

if __name__ == "__main__":
    generate_dq_scores()
