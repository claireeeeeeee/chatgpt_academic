from toolbox import CatchException, report_execption, write_results_to_file
from toolbox import update_ui, choose_appropriate_key, get_conf
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from .crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
from .crazy_utils import read_and_clean_pdf_text
from colorful import *
import re,os,requests,json
from request_llm.bridge_all import model_info

@CatchException
def code_generation_pair(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    history = []    # 清空历史，以免输入溢出
    jsonl_data = read_jsonl(txt)

    for chunk in read_three(jsonl_data):
        prompt_array = []
        id_array = []
        for item in chunk:
            prompt_array.append(item["prompt"])
            id_array.append(item["task_id"])

        history_array = [''] * len(prompt_array)
        sys_prompt_array1 = ["Pair programming is a software development approach in which two programmers collaborate at the same computer. The driver writes code, while the observer analyses each line of code as it is entered. Now you need to act as a driver, write a program according to the requirement, and then hand it over to the observer for inspection."] * len(prompt_array)
        sys_prompt_array2 = ["Pair programming is a software development approach in which two programmers collaborate at the same computer. The driver writes code, while the observer analyses each line of code as it is entered. Now you need to act as an observer, review each line of code. When you test the code, I want you to make suggestions on the code and record test reports covering various aspects such as functionality, readability, maintainability, etc. Your role involves not just identifying and reporting errors but also ensuring that the code aligns perfectly with our standards and requirements. Note that you need to check not only these but also other criteria that you feel need to be tested."] * len(prompt_array)
        sys_prompt_array_output = ["Only output the final version of the code, and only the code(no any descriptions)."] * len(prompt_array)
        
        # 1
        history = []    # 清空历史，以免输入溢出
        gpt_collection1 = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
            inputs_array=[
                f"While you as a driver are writing code that meets the requirements of the plan, you need to use Python to complete the requirements, taking care to ensure that the code you write is efficient, readable, and follows best practices. The requirement you need to follow is {prompt}.\nThis requirement will have:\n1. Package/module you expect to use may contain.\n2. Name of function you must follow.\n3. Type and number of parameters the function should accept.\n4. Function you need to achieve.\n5. Test cases.\nYour goal is to follow the requirements and write Python code to satisfy its requirements and generate your own test cases to test whether your function is accurate. It is crucial to follow the function names and packages required in it. You also need to check the code to ensure it meets all the criteria specified in the requirement. Make sure to look for edge cases and try to break the code to ensure it's robust. This ensures consistency and a unified direction in the development process. When you write code, ensure your Python code:\n1. Is efficient in terms of algorithmic complexity.\n2. Is readable, making it easier for other team members to understand and, if necessary, modify.\n3. Adheres to best practices of Python, including PEP 8 style guidelines.\n" for prompt in prompt_array],
            inputs_show_user_array=[f"{task_id}Project Leader for Developers: " for task_id in id_array],
            llm_kwargs=llm_kwargs,
            chatbot=chatbot,
            history_array=history_array,
            sys_prompt_array=sys_prompt_array1,
                # max_workers=5  # OpenAI所允许的最大并行过载
            )
        codes = merge_2_lists(gpt_collection1, prompt_array)

        # 2
        history = []    # 清空历史，以免输入溢出
        gpt_collection2 = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
            inputs_array=[
                f"This is the code of the driver paired with you:{code} and the requirements for it is as follows: {prompt}\nHere is what you need to include (not the format or steps you have to follow):\n1. Code Inspection: Please check the code against the requirements received. Please ensure that the function names and packages required in the requirements are used and that all required functionality is implemented.\n2. Unit Test Execution: Use the provided unit tests from the requirements to validate the functionality of the code. Verify that the program works as expected and returns the correct results. Make sure your program handles unexpected input or error conditions gracefully. Should there be any discrepancies, take note of them for your report.\n3. Detailed Analysis: Beyond just the functionality, assess the code for readability. A clear and understandable code will be crucial for future maintenance and updates.You need to gauge the maintainability of the code. Consider factors like modularity, scalability, and whether best coding practices have been followed.\n4. Code Improvement: Improve the code provided to you, based on your analysis reports." for code,prompt in codes],
            inputs_show_user_array=[f"{task_id}Project Leader for Testers: " for task_id in id_array],
            llm_kwargs=llm_kwargs,
            chatbot=chatbot,
            history_array=history_array,
            sys_prompt_array=sys_prompt_array2,
                # max_workers=5  # OpenAI所允许的最大并行过载
            )
        results = merge_2_lists(gpt_collection2, prompt_array)

        # final
        inputs_show_user_array = ["Final output:"] * len(prompt_array)
        history = []    # 清空历史，以免输入溢出
        gpt_output_collection = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
            inputs_array=[
                f"Here is the final report from the developer: {code} and the requirement: {prompt}. Your objective is to extract the final version of the code for me, by reading the final report from the developer.  Please remember to remove the code used by the test, and only keep the Python functions needed in the requirements(mentioned in the function signature.). Please remember: provide only the final version of the code.\n4. Code Improvement: Improve the code provided to you, based on your analysis reports." for code,prompt in results],
            inputs_show_user_array=inputs_show_user_array,
            llm_kwargs=llm_kwargs,
            chatbot=chatbot,
            history_array=history_array,
            sys_prompt_array=sys_prompt_array_output,
                # max_workers=5  # OpenAI所允许的最大并行过载
            )
        final = clean(gpt_output_collection)
        save_to_jsonl(id_array, final)

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

def save_to_jsonl(id_list, code_list):
    if len(id_list) != len(code_list):
        raise ValueError("The lengths of id_list and code_list must be equal.")
    
    with open("/home/cli776/human-eval/samples_pair1_2.jsonl", "a") as file:
        for task_id, code_segments in zip(id_list, code_list):
            data = {"task_id": task_id, "completion": code_segments}
            file.write(json.dumps(data) + "\n")

def save_history(key, lists):
    filename = "/home/cli776/human-eval/history_pair1_2.jsonl"
    with open(filename, 'a') as f:
        key = key
        data = {
            key: lists
        }
        f.write(json.dumps(data) + '\n')

def read_three(jsonl_data):
    i = 0
    while i < len(jsonl_data):
        yield jsonl_data[i:i+3]
        i += 3

def clean(list1):
    results = []
    for i, item in enumerate(list1):
        if i % 2 != 0:
            results.append(item)
    return results

def merge_2_lists(codes, prompts):
    results = []
    for i,k in enumerate(codes): 
        if i%2==0:
            codes[i] = codes[i]
        else:
            results.append(codes[i])
    save_history("results", results)
    if len(prompts) != len(results):
        raise RuntimeError("The lengths of the lists must be equal.")
    plans = []
    for i, (item1, item2) in enumerate(zip(prompts, codes)):
        plans.append([item1, item2])
    return plans

