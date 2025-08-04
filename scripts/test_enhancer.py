import os
import pandas as pd
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI

define_system_prompt = """
You are an expert in generating runnable Python test cases using `pytest`.

TASK:
Your task is to generate exactly **two** test cases per run:
- **One pass-to-pass (ptp) test** for valid inputs.
- **One fail-to-pass (ftp) test** for invalid inputs and edge cases.

EXPECTED OUTPUT:
1. Each test case must:
   - Be a separate function with a meaningful name prefixed by:
      - `test_ptp_` for pass-to-pass tests.
      - `test_ftp_` for fail-to-pass tests.
   - Contain **one or two assertions** at most.
   - Provide setup code and context before assertions.
2. Use proper `pytest` syntax, such as `pytest.raises` for exceptions.
3. Ensure the test is self-contained and runnable with `pytest`.

Buggy Code:
{buggy_code}

Gold Patch:
{gold_patch}

Original Tests:
{tests}

### OUTPUT FORMAT:
Provide exactly **two** test cases in a Python code block. The test functions should:
1. Begin with `test_ptp_` or `test_ftp_` depending on the category.
2. Include setup code and one or two assertions.
3. only python code (no comments or descriptions)
"""

human_prompt = """
Analyze the following code changes and generate exactly **two** test cases:
- **One pass-to-pass test** for valid inputs.
- **One fail-to-pass test** for invalid inputs and edge cases.

Buggy Code:
{buggy_code}

Gold Patch:
{gold_patch}

Original Tests:
{tests}

Ensure the two test cases follow the required format and are runnable with pytest and only python code (no comments or descriptions)

"""

# Combine into a ChatPromptTemplate
template = ChatPromptTemplate.from_messages(
    messages=[
        SystemMessagePromptTemplate.from_template(define_system_prompt),
        HumanMessagePromptTemplate.from_template(human_prompt),
    ]
)

# Set API key securely
os.environ["OPENAI_API_KEY"] = "your_api_key"

# Initialize the LLM with GPT-4 (enan: or possibly GPT-mini/Gemini)
llm = ChatOpenAI(model_name="gpt-4", temperature=0)

# Create the pipeline
test_case_pipeline = template | llm


def process_project_instances(file_path, project_name, output_file, skipped_instances_file):
    """
    Processes instances related to a specific project and writes all test cases into a single file.

    Each instance runs 20 times, generating one test per run.
    If an instance exceeds the token limit, it is skipped and logged.
    """
    # Load the Excel file
    data = pd.read_csv(file_path)

    # Filter data for the specified project
    project_data = data[data['repo'] == project_name]

    # Open the output file in write mode
    with open(output_file, "w", encoding="utf-8") as consolidated_file, \
         open(skipped_instances_file, "w", encoding="utf-8") as skipped_file:

        consolidated_file.write("import pytest\n\n")  # Ensure pytest is imported

        for idx, row in project_data.iterrows():
            instance_id = row["instance_id"]
            buggy_code = row["buggy_patch"]
            gold_patch = row["patch"]
            tests = row["test_patch"]

            if pd.isna(buggy_code) or pd.isna(gold_patch) or pd.isna(tests):
                print(f"Skipping instance {instance_id} due to missing data.")
                continue

            print(f"Processing instance {instance_id} for project {project_name}...")

            inputs = {
                "buggy_code": buggy_code,
                "gold_patch": gold_patch,
                "tests": tests,
            }

            # Write a section header for this instance
            consolidated_file.write(f"\n### Instance: {instance_id} (Project: {project_name})\n\n")

            try:
                for run in range(1, 21):  # Running the prompt 20 times per instance
                    response = test_case_pipeline.invoke(inputs)
                    output = response.content if hasattr(response, "content") else "No content"

                    # Check for token limit errors
                    if "maximum context length" in output.lower() or "token limit" in output.lower():
                        print(f"Skipping instance {instance_id}: Token limit exceeded.")
                        skipped_file.write(f"{instance_id}\n")
                        break  # Skip further runs for this instance

                    # Ensure proper output is generated
                    if "```python" not in output and "```" not in output:
                        print(f"Skipping instance {instance_id} run {run}: No valid test cases generated.")
                        continue

                    # Clean the output and remove unnecessary formatting
                    output_lines = output.splitlines()
                    cleaned_output = "\n".join(
                        line for line in output_lines if line.strip() not in ["```", "```python"]
                    )

                    # Write a run-specific header
                    consolidated_file.write(f"# --- Run {run} ---\n\n")
                    consolidated_file.write(cleaned_output + "\n\n")

                    print(f"Generated test {run} for instance {instance_id}.")

            except Exception as e:
                print(f"Error processing instance {instance_id}: {e}")
                skipped_file.write(f"{instance_id}\n")  # Log the skipped instance

    print(f"\nAll test cases for {project_name} have been written to {output_file}.")
    print(f"Skipped instances have been logged in {skipped_instances_file}.")


# Run the script for a specific project
if __name__ == "__main__":
    file_path = "verilite.csv"
    selected_project = "astropy/astropy"  # Change this to the desired project
    output_file = f"all_tests_{selected_project.replace('/', '__')}.py"
    skipped_instances_file = "requests_skipped_instances.txt"

    process_project_instances(file_path, selected_project, output_file, skipped_instances_file)
    print(f"\nFinal test cases have been written to {output_file}.")
