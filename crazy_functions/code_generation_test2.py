from toolbox import CatchException, report_execption, write_results_to_file
from toolbox import update_ui, choose_appropriate_key, get_conf
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from .crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
from .crazy_utils import read_and_clean_pdf_text
from colorful import *
import re,os,requests,json
from request_llm.bridge_all import model_info

@CatchException
def code_generation_test(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    history = []    # 清空历史，以免输入溢出
    jsonl_data = read_jsonl(txt)
    
    for entry in jsonl_data:
        task_id = entry["task_id"]
        prompt = entry["prompt"]

        # Project Leader
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
            i_say = f'There is a development team composed of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Each role has its unique responsibilities and requires collaboration for successful execution. I would like for you to take on the role of a project leader, your goal being to devise a high-level plan and guide programmers in developing the software, rather than delving into the implementation details. The requirement includes a function signature, NL description,  and several unit tests. Please first separate the function signature, NL description and unit test by yourself, use the function signature as the function name, use the NL description to determine the development plan of the function, and finally let the quality assurance tester use the provided unit test to test the function. Given a requirement as follows: {prompt}'
            inputs_show_user = f'{task_id}Project Leader: '
            plan_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say, inputs_show_user=inputs_show_user, 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt='When you, as a project leader, develop a plan, you need to break it down into easy-to-solvable subtasks for functional units and develop a high-level plan outlining the major steps to implement. The output I need is just this plan, no actual code or anything else.'
            )
        except:
            raise RuntimeError(response.content.decode())
        save_history('Project Leader', plan_say)
        
        # Developer
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
            i_say = f'There is a development team composed of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Each role has its unique responsibilities and requires collaboration for successful execution. I would like for you to assume the role of a developer. As a core member of the team, you will receive plans from the analyst during the workflow. You will be given the plan from the Project Leader. Your aim is to write Python code in accordance with this plan to meet its requirements. Ensure that your code is efficient, readable, and adheres to best practices. The plan of Project Leader is {plan_say}.'
            inputs_show_user = 'Developer: '
            code_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say, inputs_show_user=inputs_show_user, 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt='While you as a developer are writing code that meets the requirements of the plan, you need to use Python to complete the requirements the plans of analysts, taking care to ensure that the code you write is efficient, readable, and follows best practices. The output I need is just a working code, no need to explain your code or other content.'
            )
        except:
            raise RuntimeError(response.content.decode())
        save_history('Developer', code_say)

        # Quality assurance: 
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
            i_say = f'There is a development team composed of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Each role has its unique responsibilities and requires collaboration for successful execution. I would like you to assume the role of a quality assurance tester within our development team. After receiving the code written by the developers, your task is to scrutinize it for errors and test the code against the unit tests in the requirements. The code that you need to inspect is: {code_say} and the requirement is: {prompt}. Then record your findings in a test report, covering various aspects such as functionality, readability, and maintainability, for developers to modify.'
            inputs_show_user = 'Quality assurance: '
            tester_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say, inputs_show_user=inputs_show_user, 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt='When you test the code as a tester on the development team, I want you to make suggestions on the code and record test reports covering various aspects such as functionality, readability, maintainability, etc. Note that you need to check not only these, but also other criteria that you feel need to be tested.'
            )
        except:
            raise RuntimeError(response.content.decode())
        save_history('Quality assurance', tester_say)

        # Developer
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
            i_say = f'There is a development team composed of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Each role has its unique responsibilities and requires collaboration for successful execution. Next, I would like you to take on the role of a developer once again. This time, your task is to receive the test report from the quality assurance tester and make revisions to the existing code throughout the workflow. Your aim is to fix or improve the previous code based on the test report. Ensure that any changes made to the code do not introduce new errors or negatively impact the performance of the code. Remember, there is no need to explain the code you have written. The test report you have received is: {tester_say}. The code you need to modify is: {code_say}.'
            inputs_show_user = 'Final code: '
            gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say, inputs_show_user=inputs_show_user, 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt='When you, as a developer, write code that meets the requirements of the plan, I want you to change the code I give you based on the test reports from the testers. If the code does not need to be modified, please also output the code that has not been changed.'
            )
        except:
            raise RuntimeError(response.content.decode())
        save_history('Developer', gpt_say)

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
            i_say = f'Finally, your objective is to extract the final version of the code for me, by reading the final report from the developer. Here is the report from the developer: {gpt_say}. Please remember: provide only the final version of the code.'
            inputs_show_user = 'Final output: '
            output_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say, inputs_show_user=inputs_show_user, 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt='Only output the final version of the code, and only the code(no any descriptions).'
            )
        except:
            raise RuntimeError(response.content.decode())
        save_history('Extract', output_say)

        code_segments = extract_code_segments(output_say)
        save_to_jsonl(task_id, code_segments)

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
    with open("/home/cli776/human-eval/samples.jsonl", "a") as file:
        file.write(json.dumps(data) + "\n")

def save_history(key, values):
    with open("/home/cli776/human-eval/recoding.jsonl", "w") as f:
        for idx, value in enumerate(values, 1):  # 从1开始计数
            key = f"{idx}_{key}"
            data = {key: value}
            json_str = json.dumps(data)
            f.write(json_str + '\n')
