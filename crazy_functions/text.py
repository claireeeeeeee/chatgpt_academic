import json

def read_jsonl(file_path):
    data = []
    with open(file_path, "r") as file:
        for line in file:
            # Parse each line as a JSON object and append it to the list
            data.append(json.loads(line.strip()))
    return data

# Example usage:
file_path = "/home/cli776/1/HumanEval.jsonl"
jsonl_data = read_jsonl(file_path)

# Access the elements of each JSON object in the list
entry=jsonl_data[0]
task_id = entry["task_id"]
prompt = entry["prompt"]
entry_point = entry["entry_point"]
canonical_solution = entry["canonical_solution"]
test = entry["test"]

# Do whatever you need with the extracted elements
print("Task ID:", type(task_id), task_id)
print("Prompt:", type(prompt), prompt)
#print("Entry Point:", type(), entry_point)
#print("Canonical Solution:", type(), canonical_solution)
#print("Test:", type(), test)