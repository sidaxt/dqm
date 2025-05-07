import json
import os
import pandas as pd
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import AzureChatOpenAI
# from langchain.chains import RunnableSequence
from dotenv import load_dotenv
import openai
from pprint import pprint

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_api_base = os.getenv("OPENAI_API_BASE")
openai_api_version = os.getenv("OPENAI_API_VERSION")
openai_api_type = os.getenv("OPENAI_API_TYPE")
openai_api_endpoint = os.getenv("OPENAI_API_BASE")

# Set up the OpenAI API
# openai.api_key = openai_api_key
# openai.api_base = openai_api_base
# openai.api_version = openai_api_version
# openai.api_type = openai_api_type
DEPLOYMENT_NAME = "gpt-4" 

llm = AzureChatOpenAI(
    deployment_name=DEPLOYMENT_NAME,
    model_name="gpt-4",
    openai_api_key=openai_api_key,
    openai_api_base=openai_api_endpoint,
    api_version=openai_api_version
)
# Define the prompt template
prompt_template1 = """
You are tasked with analyzing a dataset and its associated data quality rules. Based on the dataset, metadata, historical data quality issues, and existing rules:

1. Identify any new patterns or anomalies in the dataset.
2. Suggest new, **unique** data quality rules that improve data integrity, addressing both historical issues and emerging trends.
3. Ensure that the new rules are **non-redundant** and do not replicate or overlap with the previously existing rules.


Dataset: {dataset}
Metadata: {metadata}
Existing DQ Rules: {dq_rules}
Historical Issues: {issues}

Please provide only the following response, no extra explanation or words.
Please provide the response IN JSON format, with dict name new_dq_rules. 


"""

prompt = PromptTemplate(template=prompt_template1, input_variables=["dataset","metadata" "dq_rules", "issues"])

# Load the data from CSV and JSON files
def load_data():
    # Load dataset (customer.csv)
    dataset = pd.read_csv('public/data/input/usecase2/customers.csv').to_json()  # Convert to JSON for easier usage
    
    with open('public/data/input/usecase2/metadata.json', 'r') as metadata_file:
        metadata = json.load(metadata_file)
    
    # Load metadata (dq_rules.json and historical_issues.json)
    with open('public/data/input/usecase2/customers_dq_rules.json', 'r') as dq_file:
        dq_rules = json.load(dq_file)
    
    with open('public/data/input/usecase2/issues.json', 'r') as issues_file:
        issues = json.load(issues_file)

    

    return dataset,metadata,dq_rules, issues

# Define the LLM chain for generating new DQ rules
llm_chain = LLMChain(llm=llm, prompt=prompt)

# # Generate new DQ rules
# def generate_new_dq_rules():
#     dataset,metadata, dq_rules, issues = load_data()
    
#     # Call the LLM with the data
#     response = llm_chain.run({
#         "dataset": dataset,
#         "metadata" : metadata,
#         "dq_rules": dq_rules,
#         "issues": issues
#     })

#     # Save the new rules in a JSON file
#     # new_dq_rules = response.strip()

#     data_dict = json.loads(response)
    
#     with open('new_dq_rules.json', 'w') as new_dq_file:
#         json.dump({"generated_dq_rules": data_dict}, new_dq_file, indent=4)
        

#     print("New DQ rules saved in new_dq_rules.json")


# Generate new DQ rules
def generate_new_dq_rules():
    dataset, metadata, dq_rules, issues = load_data()

    # Call the LLM with the data
    response = llm_chain.run({
        "dataset": dataset,
        "metadata": metadata,
        "dq_rules": dq_rules,
        "issues": issues
    })

    # Debugging: Print the raw response to inspect it
    print("Raw LLM response:", response)
    
    try:
        # Directly parse the response JSON
        data_dict = json.loads(response)

        # Convert the dq_rules to a DataFrame
        df = pd.DataFrame(data_dict["new_dq_rules"])

        # Save the DataFrame to a CSV file
        df.to_csv('public/data/output/new_dq_rules.csv', index=False)
        print("New DQ rules saved in new_dq_rules.csv")

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print("LLM Response was:", response)

if __name__ == "__main__":
    generate_new_dq_rules()
