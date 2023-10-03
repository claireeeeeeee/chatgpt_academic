from toolbox import CatchException, report_execption, write_results_to_file
from toolbox import update_ui, choose_appropriate_key, get_conf
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from .crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
from .crazy_utils import read_and_clean_pdf_text
from colorful import *
import re,os,requests,json
from request_llm.bridge_all import model_info

@CatchException
def code_generation_new_pair(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    history = []    # 清空历史，以免输入溢出
    jsonl_data = read_jsonl(txt)
    
    for entry in jsonl_data:
        task_id = entry["task_id"]
        prompt = entry["prompt"]
        entry_point = entry["entry_point"]
        # 1
        history = []    # 清空历史，以免输入溢出
        proxies, = get_conf('proxies')
        api_key = choose_appropriate_key(llm_kwargs['api_key'], llm_kwargs['llm_model'], 0)
        print('api_key: ', api_key)
        chat_endpoint = model_info[llm_kwargs['llm_model']]['endpoint']
        headers = {
            'Authorization': f"Bearer {api_key}",
            'Content-Type': 'application/json'
        }
        data = {
            'prompt': prompt
        }
        response = requests.post(chat_endpoint, headers=headers, json=data, proxies=proxies)
        try:
            i_say = f'While you as a driver are writing code that meets the requirements of the plan, you need to use Python to complete the requirements, taking care to ensure that the code you write is efficient, readable, and follows best practices. Your goal is to follow the requirements and write Python code to satisfy its requirements and generate your own test cases to test whether your function is accurate. The requirement you need to follow is {prompt} and {entry_point} is the name of the function.This requirement will have: 1. Package/Module: You may use any relevant Python packages or modules as required. 2. Function Name: You must implement a function named {entry_point} to meet the specified requirement. 3. Parameters: The function should accept specific types and numbers of parameters as indicated in the requirement. 4. Function Description: Your task is to implement the function according to the provided requirement. Ensure that your code meets the specified criteria, and consider edge cases to ensure its robustness. 5. Generate your own test cases to verify the accuracy and reliability of your function. Test cases are crucial for ensuring that your code behaves as expected under various scenarios. It is crucial to follow the function names and packages required in it. You also need to check the code to ensure it meets all the criteria specified in the requirement. Make sure to look for edge cases and try to break the code to ensure it is robust. When writing your Python code, pay attention to the following: 1. Efficiency: Optimize your code in terms of algorithmic complexity to ensure it runs efficiently. 2. Readability: Write code that is easy for your team members to understand and potentially modify in the future. 3. Best Practices: Adhere to the best practices of Python programming, including compliance with PEP 8 style guidelines. Here is an example to illustrate this process you can follow: EXAMPLE PROBLEM: \n\ndef subarray_sum_to_k(l: list, k: int):\n    \"\"\"\n    subarray_sum_to_k takes a list of integers and an integer k as its parameters.\n    it returns all distinct subarrays whose elements sum to k.\n    A subarray is defined as a contiguous part of an array.\n     >>> subarray_sum_to_k([1, 2, 3, 4, 5], 9)\n    [[4, 5], [2, 3, 4]]\n    >>> subarray_sum_to_k([1, 3, 2, 1, 4, 1, 3], 6)\n    [[1, 3, 2], [3, 2, 1], [1, 4, 1]]\n    >>> subarray_sum_to_k([1, 2], 5)\n    []\n    \"\"\"\n\nITS EXAMPLE ANSWER FOR THE PROBLEM: \n\ndef subarray_sum_to_k(l: list, k: int):\n    result = []\n    for i in range(len(l)):\n        for j in range(i, len(l)):\n            if sum(l[i:j+1]) == k:\n                result.append(l[i:j+1])\n    return result\nprint(subarray_sum_to_k([1, 2, 3, 4, 5], 9))  # Output should be [[4, 5], [2, 3, 4]]\nprint(subarray_sum_to_k([1, 3, 2, 1, 4, 1, 3], 6))  # Output should be [[1, 2, 3], [3, 2, 1], [2, 1, 3], [1, 3, 2], [1, 4, 1]]\nprint(subarray_sum_to_k([1, 2], 5))  # Output should be []\nprint(subarray_sum_to_k([], 5))  # Edge case: Output should be []\nprint(subarray_sum_to_k([5], 5))\n\n'
            inputs_show_user = f'{task_id}Developer1'
            plan_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say, inputs_show_user=inputs_show_user, 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt='Pair programming is a software development approach in which two programmers collaborate at the same computer. The driver writes code, while the observer analyses each line of code as it is entered. Now you need to act as a driver, write a program according to the requirement, and then hand it over to the observer for inspection.'
            )
        except:
            raise RuntimeError(response.content.decode())
        save_history(task_id, 'Developer1', plan_say)

        # 2
        history = []    # 清空历史，以免输入溢出
        proxies, = get_conf('proxies')
        api_key = choose_appropriate_key(llm_kwargs['api_key'], llm_kwargs['llm_model'], 1)
        print('api_key: ', api_key)
        chat_endpoint = model_info[llm_kwargs['llm_model']]['endpoint']
        headers = {
            'Authorization': f"Bearer {api_key}",
            'Content-Type': 'application/json'
        }
        data = {
            'prompt': prompt
        }
        response = requests.post(chat_endpoint, headers=headers, json=data, proxies=proxies)
        try:
            i_say = f'This is code written by the programmer you are paired with:{plan_say}. And the requirements for it is as follows: {prompt}Here is what you need to include (not the format or steps you have to follow): 1. Code Inspection: Please check the code against the requirements received. Please make sure that the function name used in the code is the same as {entry_point} and that all required functions are implemented. 2. Unit Test Execution: Use the provided unit tests from the requirements to validate the functionality of the code. Verify that the program works as expected and returns the correct results. Make sure your program handles unexpected input or error conditions gracefully. Should there be any discrepancies, take note of them for your report. 3. Detailed Analysis: Beyond just the functionality, assess the code for readability. A clear and understandable code will be crucial for future maintenance and updates.You need to gauge the maintainability of the code. Consider factors like modularity, scalability, and whether best coding practices have been followed. 4. Code Improvements: Improve the code provided to you based on your analysis reports to provide a final version of the code.Here is the example you can follow: Code Inspection\n\nRequirements Verification\n- Function Name: The function name `subarray_sum_to_k` is the same as that specified in the requirements.\n- Input Parameters: The function takes a list `l` and an integer `k` as input parameters, which is in line with the requirements.\n- Output: The function returns a list of lists, each containing integers. This appears to conform to the requirements.\n- Distinct Subarrays: The requirements mention that the function should return all \"distinct\" subarrays whose sum is `k`. The current implementation does not ensure that the subarrays are distinct.\n\nAdditional Observations\n- Type Hints: The function uses type hints, which is good for readability and maintainability.\n\nUnit Test Execution\nThe code was tested using the sample test cases. Here are the results:\n- `subarray_sum_to_k([1, 2, 3, 4, 5], 9)` returns `[[4, 5], [2, 3, 4]]`. This is correct.\n- `subarray_sum_to_k([1, 3, 2, 1, 4, 1, 3], 6)` returns `[[1, 2, 3], [3, 2, 1], [2, 1, 3], [1, 3, 2], [1, 4, 1]]`. This violates the requirement of distinct subarrays as `[1, 2, 3]` and `[3, 2, 1]` are essentially the same subarray in different orders.\n- `subarray_sum_to_k([1, 2], 5)` returns `[]`. This is correct.\n- `subarray_sum_to_k([], 5)` returns `[]`. This is correct and handles the edge case well.\n- `subarray_sum_to_k([5], 5)` returns `[[5]]`. This is correct.\n\nDetailed Analysis\nReadability\n- Indentation and Spacing: The code is well-indented and spaces are used appropriately.\n- Variable Names: The variable names are concise and to the point, but they could be more descriptive. For instance, `l` could be `input_list`.\nMaintainability\n- Type hints: The type hints make the code easier to maintain.\n- Nested loops: The function currently employs two nested for-loops, which make the function O(n^2) in terms of time complexity. This might not be scalable for larger inputs.\n\nModularity and Scalability\n- The code is not very modular. The logic for finding the subarray could potentially be separated into a helper function.\n- The current algorithm is not highly scalable due to its O(n^2) time complexity.\n\nBest Practices\n- Error Handling: There is no error handling to check if the inputs are valid (i.e., if the first input is indeed a list of integers and the second input is an integer).\n\nRecommendations\n- Implement logic to ensure that the subarrays are distinct as per the requirement.\n- Consider renaming variables for better readability.\n- Break down the function into smaller, more modular helper functions.\n- Consider optimizing the function to handle larger lists more efficiently.\n- Add input validation and error handling.\n\nOverall\nThe code fulfills most of the basic requirements but fails in ensuring that the subarrays are distinct. It is relatively easy to read but could benefit from further modularization and optimizations for better maintainability and scalability.\nFinal Improved Code: \n```Python\ndef subarray_sum_to_k(input_list: list, k: int):\n      if not isinstance(input_list, list) or not all(isinstance(i, int) for i in input_list) or not isinstance(k, int):\n        return \"Invalid input\"\n\n    result_set = set()\n    for i in range(len(input_list)):\n        current_sum = 0\n        for j in range(i, len(input_list)):\n            current_sum += input_list[j]\n            if current_sum == k:\n                result_set.add(tuple(input_list[i:j+1]))\n                \n    return [list(item) for item in result_set]\nBy implementing these changes, the code should now be more readable, maintainable, and closer to fulfilling the requirements.\n'
            inputs_show_user = 'Developer2: '
            code_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say, inputs_show_user=inputs_show_user, 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt='Pair programming is a software development approach in which two programmers collaborate at the same computer. The driver writes code, while the observer analyses each line of code as it is entered. Now you need to act as an observer, review each line of code. When you test the code, I want you to make suggestions on the code and record test reports covering various aspects such as functionality, readability, maintainability, etc. Your role involves not just identifying and reporting errors but also ensuring that the code aligns perfectly with our standards and requirements. Note that you need to check not only these but also other criteria that you feel need to be tested.'
            )
        except:
            raise RuntimeError(response.content.decode())
        save_history(task_id, 'Developer2', code_say)

        # Extract: 
        proxies, = get_conf('proxies')
        api_key = choose_appropriate_key(llm_kwargs['api_key'], llm_kwargs['llm_model'], 2)
        print('api_key: ', api_key)
        chat_endpoint = model_info[llm_kwargs['llm_model']]['endpoint']
        headers = {
            'Authorization': f"Bearer {api_key}",
            'Content-Type': 'application/json'
        }
        data = {
            'prompt': prompt
        }
        response = requests.post(chat_endpoint, headers=headers, json=data, proxies=proxies)
        try:
            i_say = f'Here is the requirement: {prompt} and the report from the developer: {code_say}. Your objective is to extract the final version of the code for me, by reading the final report from the developer.  Please remember to remove the code used by the test, and only keep the Python functions needed in the requirements(mentioned in the function signature.). Please remember: provide only the final version of the code.'
            inputs_show_user = 'Final output: '
            output_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say, inputs_show_user=inputs_show_user, 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt='Only output the final version of the code, and only the code(no any descriptions).'
            )
        except:
            raise RuntimeError(response.content.decode())
        save_history(task_id, 'Extract', output_say)

        #code_segments = extract_code_segments(output_say)
        save_to_jsonl(task_id, output_say)

        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新

def read_jsonl(file_path):
    data = []
    with open(file_path, "r") as file:
        for line in file:
            # Parse each line as a JSON object and append it to the list
            data.append(json.loads(line.strip()))
    return data

def extract_code_segments(input_string):
    # 尝试匹配以```python或```开头的代码段
    code_pattern_markdown = r'```(?:python)?(.*?)```'
    code_segments_markdown = re.findall(code_pattern_markdown, input_string, re.DOTALL)
    
    # 如果没有找到以```python或```开头的代码段，尝试匹配以"def"开始的行
    if not code_segments_markdown:
        code_pattern_inline = r'(def .*)'
        code_segments_inline = re.findall(code_pattern_inline, input_string, re.MULTILINE)
    else:
        code_segments_inline = []
    return "\n".join(code_segments_markdown + code_segments_inline)

def save_to_jsonl(task_id, code_segments):
    data = {"task_id": task_id, "completion": code_segments}
    with open("/home/cli776/human-eval/new_pair/samples2.jsonl", "a") as file:
        file.write(json.dumps(data) + "\n")

def save_history(key1, key2, plan_say):
    filename="/home/cli776/human-eval/new_pair/recoding2.jsonl"
    key = str(key1) + str(key2)
    data = {
        key: plan_say
    }
    with open(filename, 'a') as f:
        f.write(json.dumps(data) + '\n')
