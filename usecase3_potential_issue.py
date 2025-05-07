from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import AzureChatOpenAI
import json
import os
import pandas as pd
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_api_base = os.getenv("OPENAI_API_BASE")
openai_api_version = os.getenv("OPENAI_API_VERSION")
openai_api_type = os.getenv("OPENAI_API_TYPE")
openai_api_endpoint = os.getenv("OPENAI_API_BASE")

DEPLOYMENT_NAME = "gpt-4" 

llm = AzureChatOpenAI(
    deployment_name=DEPLOYMENT_NAME,
    model_name="gpt-4",
    openai_api_key=openai_api_key,
    openai_api_base=openai_api_endpoint,
    api_version=openai_api_version
)

prompt_template1 = """ 
f"Dataset: {dataset}\nTestdata: {testdata}\nMetadata: {metadata}\nDq_rules: {dq_rules}\nIssues: {issues}\n
Based on the provided dataset, metadata, existing data quality rules, and detected issues, generate and suggest a new set of resolutions for the test data. 
Additionally, predict potential data quality issues using the historical ingestion errors, where the "issues dataset" refers to these errors. 
Identify and report every issue from the test data, ensuring no issue is missed. 
Provide multiple possible resolutions for each issue.
Respond in a detailed JSON format, clearly listing every identified issue and providing as many expert-level resolutions as possible.
Give response in this format , donot provide any extra text. 

Give the response in the json, as shown format 
"potential_issues": [
        [
            "issue_id":1,
            "issue_description": " ",
            "affected_records": [
                "CustomerID: ",
                "CustomerID: "
            ],
            "date_reported": " ",
            "resolution": [
                " ",
                " ",
                " "
            ]
        ]
    ]

"
"""

prompt = PromptTemplate(template=prompt_template1, input_variables=["dataset", "metadata","dq_rules", "issues","testdata"])
llm_chain = LLMChain(llm=llm, prompt=prompt)

data_path ="public/data/input/usecase3"
def read_json_file(file_name):
    with open(os.path.join(data_path, file_name), 'r') as f:
        return json.load(f)
    

def save_json_to_local(data_dict, json_path):
    try:
        with open(json_path, "w") as json_file:
            json.dump(data_dict, json_file, indent=4)
        print(f"JSON file saved successfully at {json_path}")
    except Exception as e:
        print(f"An error occurred while saving the JSON file: {e}")
    
dataset = read_json_file('dataset.json')
metadata = read_json_file('metadata.json')
dq_rules = read_json_file('dq_rules.json')
issues = read_json_file('issues.json')
test_data = read_json_file('data_test.json')

json_path = "public/data/input/usecase3"
csv_path = "public/data/input/usecase3"
def main():
    response = llm_chain.run({
    "dataset": dataset,
    "metadata": metadata,
    "dq_rules": dq_rules,
    "issues": issues,
    "testdata" : test_data
    })
    print(response)
    data_dict = json.loads(response)
    df = pd.DataFrame(data_dict)
    df.to_csv("public/data/output/potential_issues.csv", index=False)
    print(df)
    # save_json_to_local(data_dict, json_path)
    


if __name__ == "__main__":
    main()