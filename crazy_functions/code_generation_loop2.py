from toolbox import CatchException, report_execption, write_results_to_file
from toolbox import update_ui, choose_appropriate_key, get_conf
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from .crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
from .crazy_utils import read_and_clean_pdf_text
from colorful import *
import re,os,requests,json
from request_llm.bridge_all import model_info

@CatchException
def code_generation_loop2(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    history = []    # 清空历史，以免输入溢出
    jsonl_data = read_jsonl(txt)
    
    for entry in jsonl_data:
        task_id = entry["task_id"]
        prompt = entry["prompt"]
        entry_point = entry["entry_point"]

        system_message = f"""There is a development team that \ 
includes a requirement analyst, a coder, and a quality tester. \
The team needs to develop programs that satisfy the requirements of \
the users. The different roles have different divisions of \
labor and need to cooperate with each others"""
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
            analyst_description = f""" I want you to act as an analyst \
on our development team. Analyze a user requirement.\
The user requirement will be provided between triple backticks (```),

Your role involves two primary responsibilities: \
1:Decompose User Requirements: decomposes the requirement x into \
several easy-to-solve subtasks that facilitate the division \
of functional units.

2:Develop High-Level Implementation Plan: Then, develops a high-level plan \
that outlines the major steps of the implementation.

The requirement from users is ```{prompt}```.
"""
            analyst_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=analyst_description, inputs_show_user=f'{task_id}Analyst', 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt=system_message
            )
        except:
            raise RuntimeError(response.content.decode())
        save_history(task_id, 'Analyst', 0, analyst_say)

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
            coder_description = f"""
You are taking on the role of a coder \
within our development team. Depending on the input you receive, \
your task is distinct:

Task Based on Input:
# Requirement Analyst Plan:
If you receive a plan from a requirement analyst, \
develop Python code in line with the plan. \
Ensure your code is efficient, adheres to \
readability standards, and follows coding best practices.

# Tester's Test Report:
If you receive a detailed test report and its accompanying \
Python code from a tester, \
your main task is to revise the code by incorporating \
the feedback from the test report. \

Your main objectives are:
1. You adhere strictly to the feedback given in the test report.
2. The modifications do not change the core functionality of the code.
3. You provide an improved version of the provided code that \
considers the feedback on readability and maintainability.

Note: No need for explanations or comments on the code you develop.

The requirement from users is ```{analyst_say}```. Output in Python code format.
"""
            code_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=coder_description, inputs_show_user=f'{task_id}Coder',
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt=system_message
            )
        except:
            raise RuntimeError(response.content.decode())
        save_history(task_id, 'Coder', 0, code_say)

        # 3
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
            tester_description = f"""
I'd like you to assume the role of a tester within \
our development team. When you receive code from a coder, \
you are responsible for the following three steps:

Step 1: Document Test Report
Generate a comprehensive test report assessing various code aspects, \
including but not limited to functionality, readability, and maintainability.

Step 2: Advocate for Model-Simulated Testing
Promote the use of a process where our machine learning model \
simulates the testing phase and produces test reports, \
thereby automating quality assessment.

Step 3: Issue Reporting in JSON Format
List all identified issues in a JSON formatted document. \
Each issue entry should contain three key-value pairs: \
'description' for issue details, 'severity' to indicate \
the level of urgency, and 'suggested_fix' to propose a solution.

All parts of your response should be separated by \
triple backticks to denote different sections.

The code from the coder is {code_say}.
"""
            test_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=tester_description, inputs_show_user=f'{task_id}Test',
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt=system_message
            )
        except:
            raise RuntimeError(response.content.decode())
        save_history(task_id, 'Test', 0, test_say)
        test_results = extract_text(test_say)
        save_history(task_id, 'Test Report', 0, test_results)
        i = 0

        while i >= 0:
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
                coder_description = f"""
You are taking on the role of a coder \
within our development team. Depending on the input you receive, \
your task is distinct:

Task Based on Input:
# Requirement Analyst Plan:
If you receive a plan from a requirement analyst, \
develop Python code in line with the plan. \
Ensure your code is efficient, adheres to \
readability standards, and follows coding best practices.

# Tester's Test Report:
If you receive a detailed test report and its accompanying \
Python code from a tester, \
your main task is to revise the code by incorporating \
the feedback from the test report. \

Your main objectives are:
1. You adhere strictly to the feedback given in the test report.
2. The modifications do not change the core functionality of the code.
3. You provide an improved version of the provided code that \
considers the feedback on readability and maintainability.

Note: No need for explanations or comments on the code you develop.

The requirement from users is ```{test_results}```. Output in Python code format.
"""
                code_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                    inputs=coder_description, inputs_show_user=f'{task_id}Coder',
                    llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                    sys_prompt=system_message
                )
            except:
                raise RuntimeError(response.content.decode())
            save_history(task_id, 'Coder', i, code_say)

            # tester
            history = []    # 清空历史，以免输入溢出
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
                tester_description = f"""
I'd like you to assume the role of a tester within \
our development team. When you receive code from a coder, \
you are responsible for the following three steps:

Step 1: Document Test Report
Generate a comprehensive test report assessing various code aspects, \
including but not limited to functionality, readability, and maintainability.

Step 2: Advocate for Model-Simulated Testing
Promote the use of a process where our machine learning model \
simulates the testing phase and produces test reports, \
thereby automating quality assessment.

Step 3: Issue Reporting in JSON Format
List all identified issues in a JSON formatted document. \
Each issue entry should contain three key-value pairs: \
'description' for issue details, 'severity' to indicate \
the level of urgency, and 'suggested_fix' to propose a solution.

All parts of your response should be separated by \
triple backticks to denote different sections.

If the code or the revised code has passed your tests, \
write a conclusion "Code Test Passed".

The code from the coder is {code_say}.
"""
                test_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                    inputs=tester_description, inputs_show_user=f'{task_id}Test',
                    llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                    sys_prompt=system_message
                )
            except:
                raise RuntimeError(response.content.decode())
            save_history(task_id, 'Test', i, test_say)
            test_results = extract_text(test_say)
            save_history(task_id, 'Test Report', i, test_results)
            if "Code Test Passed" in test_results:
                i = -1
            else: 
                i += 1

        save_history(task_id, 'Result', i, test_say)
        result_code = extract_python_code(code_say)
        save_to_jsonl(task_id, result_code)

        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新

def read_jsonl(file_path):
    data = []
    with open(file_path, "r") as file:
        for line in file:
            # Parse each line as a JSON object and append it to the list
            data.append(json.loads(line.strip()))
    return data

def extract_after_step3(text):
    # Find the start position of "Step 3:"
    step3_start = text.find("Step 3:")

    # Check if "Step 3:" was found
    if step3_start != -1:
        # Extract the text after "Step 3:"
        step3_text = text[step3_start + len("Step 3:"):].strip()
        return step3_text
    else:
        return None

def extract_jsonl(text):
    # 分割文本到行
    lines = text.strip().split('\n')
    # 初始化一个空的列表来保存 JSON 对象
    json_objects = []
    # 遍历每一行
    for line in lines:
        try:
            # 尝试解析行为一个 JSON 对象
            json_object = json.loads(line)
            # 如果成功，添加到列表中
            json_objects.append(json_object)
        except json.JSONDecodeError:
            # 如果解析失败，打印错误并继续
            json_objects = []
    return None

def extract_python_code(input_string):
    # Use regular expressions to find Python code within triple backticks (```)
    code_blocks = re.findall(r'```python(.*?)```', input_string, re.DOTALL)

    # Join the code blocks into a single string
    python_code = '\n'.join(code_blocks)

    python_code = re.sub(r'# Developer.*\n', '', python_code)

    if python_code.startswith('\n'):
        python_code = python_code[1:]

    return python_code

def extract_text(input_text):
    # First, try to extract text after "Step 3:"
    extracted_text = extract_after_step3(input_text)
    if extracted_text is not None:
        return extracted_text

    # If that fails, try to extract JSONL data
    extracted_jsonl = extract_jsonl(input_text)
    if extracted_jsonl is not None:
        return extracted_jsonl

    # If both attempts fail, return the original input text
    return input_text

def save_to_jsonl(task_id, code_segments):
    data = {"task_id": task_id, "completion": code_segments}
    with open("/home/cli776/human-eval/loop/samples_loop4.jsonl", "a") as file:
        file.write(json.dumps(data) + "\n")

def save_history(key1, key2, key3, plan_say):
    filename="/home/cli776/human-eval/loop/recoding_loop4.jsonl"
    key = str(key1) + str(key2) + str(key3)
    data = {
        key: plan_say
    }
    with open(filename, 'a') as f:
        f.write(json.dumps(data) + '\n')
