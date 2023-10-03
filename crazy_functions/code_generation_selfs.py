from toolbox import CatchException, report_execption, write_results_to_file
from toolbox import update_ui, choose_appropriate_key, get_conf
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from .crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
from .crazy_utils import read_and_clean_pdf_text
from colorful import *
import re,os,requests,json
from request_llm.bridge_all import model_info

@CatchException
def code_generation_selfs(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
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
            i_say1 = f"""
Given a requirement: 
```{prompt}```
1. Decompose the requirement into several easy-to-solve subproblems that can be more easily implemented by the developer.
2. Develop a high-level plan that outlines the major steps of the program.
Remember, your plan should be high-level and focused on guiding the developer in writing code, rather than providing implementation details.
"""
            plan_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say1, inputs_show_user=f'{task_id}Project Leader: ', 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt='There is a development team that includes a requirements analyst, a developer, and a quality assurance tester. The team needs to develop programs that satisfy the requirements of the users. The different roles have different divisions of labor and need to cooperate with each others. I want you to act as a requirements analyst on our development team. The goal of an analyst is to develop a high-level plan and focus on guiding the coder in writing programs, rather than delving into implementation details.'
            )
            history.append(i_say1)
            history.append(plan_say)
        except:
            raise RuntimeError(response.content.decode())
        save_history(task_id, 'Project Leader', plan_say)

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
            i_say2 = f"""
I want you to act as a developer on our development team. You will receive plans from a requirements analyst: 
```{plan_say}```
Write code in Python that meets the requirements following the plan. Ensure that the code you write is efficient, readable, and follows best practices.
Remember, do not need to explain the code you wrote.
"""
            inputs_show_user = 'Developer1: '
            code1_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say2, inputs_show_user=inputs_show_user, 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=history, 
                sys_prompt='There is a development team that includes a requirements analyst, a developer, and a quality assurance tester. The team needs to develop programs that satisfy the requirements of the users. The different roles have different divisions of labor and need to cooperate with each others. I want you to act as a developer on our development team. You will receive plans from a requirements analyst. When you receive a plan from a requirements analyst, write code in Python that meets the requirements following the plan. Ensure that the code you write is efficient, readable, and follows best practices.'
            )
            history.append(i_say2)
            history.append(code1_say)
        except:
            raise RuntimeError(response.content.decode())
        save_history(task_id, 'Developer1', code1_say)

        # 3
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
            i_say3 = f"""
I want you to act as a tester on our development team. The tester acquires the code authored by the coder and subsequently documents a test report containing various aspects, such as functionality, readability, and maintainability. 
Given a requirement: 
```{prompt}```
You will receive code as outlined in 
```{code1_say}```
1. Test the functionality of the code to ensure it satisfies the requirements.
2. Write reports on any issues or bugs you encounter.
3. If the code or the revised code has passed your tests, write a conclusion "Code Test Passed". Remember, the report should be as concise as possible, without sacrificing clarity and completeness of information. Do not include any error handling or exception handling suggestions in your report.
"""
            inputs_show_user = 'Quality assurance:'
            test_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say3, inputs_show_user=inputs_show_user, 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt='There is a development team that includes a requirements analyst, a developer, and a quality assurance tester. The team needs to develop programs that satisfy the requirements of the users. The different roles have different divisions of labor and need to cooperate with each others. I want you to act as a tester on our development team. '
            )
        except:
            raise RuntimeError(response.content.decode())
        save_history(task_id, 'Quality assurance', test_say)

        # 4
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
            i_say4 = f"""
You will receive reports from a tester: 
```{test_say}```
Code you need to modify: 
```{code1_say}```
Fix or improve the code based on the content of the report. Ensure that any changes made to the code do not introduce new bugs or negatively impact the performance of the code. Remember, do not need to explain the code you wrote.
"""
            inputs_show_user = 'Developer2: '
            code2_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say4, inputs_show_user=inputs_show_user, 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=history, 
                sys_prompt='There is a development team that includes a requirements analyst, a developer, and a quality assurance tester. The team needs to develop programs that satisfy the requirements of the users. The different roles have different divisions of labor and need to cooperate with each others. I want you to act as a developer on our development team. You will receive plans from a requirements analyst. When you receive a plan from a requirements analyst, write code in Python that meets the requirements following the plan. Ensure that the code you write is efficient, readable, and follows best practices.'
            )
            history.append(i_say4)
            history.append(code2_say)
        except:
            raise RuntimeError(response.content.decode())
        save_history(task_id, 'Developer2', code2_say)

        # Extract: 
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
            i_say = f"""
Your objective is to extract the final version of the code for me, by reading the final report. Here is the final report from developer: 
```{code2_say}``` 
Please remember to remove the code used by the test as well, and only keep the Python functions needed in the requirements(mentioned in the function signature.). Please remember to provide only the final version of the code.
"""
            inputs_show_user = 'Final output: '
            output_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say, inputs_show_user=inputs_show_user, 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=history, 
                sys_prompt='Only output the final version of the code, and only the code(no any descriptions).'
            )
        except:
            raise RuntimeError(response.content.decode())
        save_history(task_id, 'Extract', output_say)

        #code_segments = extract_code_segments(output_say)
        save_to_jsonl(task_id, output_say)

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
    with open("/home/cli776/human-eval/new_pair/samples_self.jsonl", "a") as file:
        file.write(json.dumps(data) + "\n")

def save_history(key1, key2, plan_say):
    filename="/home/cli776/human-eval/new_pair/recoding_self.jsonl"
    key = str(key1) + str(key2)
    data = {
        key: plan_say
    }
    with open(filename, 'a') as f:
        f.write(json.dumps(data) + '\n')
