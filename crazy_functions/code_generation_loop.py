from toolbox import CatchException, report_execption, write_results_to_file
from toolbox import update_ui, choose_appropriate_key, get_conf
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from .crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
from .crazy_utils import read_and_clean_pdf_text
from colorful import *
import re,os,requests,json
from request_llm.bridge_all import model_info

@CatchException
def code_generation_loop(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
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
While you as a driver are writing code, you need to write a Python function named ```{entry_point}``` that meets a specific requirement (```{prompt}```), taking care to ensure that your code is efficient, readable, and follows best practices. Your goal is to follow the requirements write Python code to satisfy its requirements and generate your own test cases to test whether your function is accurate.  
This requirement will have: 
1. Package/Module: You may use any relevant Python packages or modules as required. 
2. Function Name: You must implement a function named ```{entry_point}```.
3. Parameters: The function should accept specific types and numbers of parameters as indicated in the requirement. 
4. Function Description: Your task is to implement the function according to the provided requirement. Ensure that your code meets the specified criteria, and consider edge cases to ensure its robustness.
5. Attention to details: Please carefully follow every detail in the requirements.
6. Testing: Generate your own test cases to validate the function's accuracy and reliability.
It is crucial to follow the function names and packages required in it. You also need to check the code to ensure it meets all the criteria specified in the requirement. Make sure to look for edge cases and try to break the code to ensure it is robust. When writing your Python code, pay attention to the following: 
1. Efficiency: Optimize your code in terms of algorithmic complexity to ensure it runs efficiently. 
2. Readability: Write code that is easy for your team members to understand and potentially modify in the future.
3. Best Practices: Adhere to the best practices of Python programming, including compliance with PEP 8 style guidelines.
"""
            code_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say1, inputs_show_user=f'{task_id}Driver', 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt='Pair programming is a software development approach in which two programmers collaborate at the same computer. The driver writes code, while the observer analyses each line of code as it is entered. Now you need to act as a driver, write a program according to the requirement, and then hand it over to the observer for inspection.'
            )
        except:
            raise RuntimeError(response.content.decode())
        save_history(task_id, 'Driver', 0, code_say)

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
            i_say = f"""
This is code written by the driver you are paired with:{code_say}. And the requirements for it is as follows: {prompt}
Here is what you need to include (not the format or steps you have to follow): 
1. Code Inspection: Please check the code against the requirements received. Please make sure that the function name used in the code is the same as {entry_point} and that all required functions in the requirements are implemented. 
2. Unit Test Execution: Use the provided unit tests from the requirements to validate the functionality of the code. Verify that the program works as expected and returns the correct results. You should also generate your own test cases to additionally test functions. Make sure your program handles unexpected input or error conditions gracefully. If there are any differences, please modify them in the final code.
3. Detailed Analysis: Beyond just the functionality, assess the code for readability. A clear and understandable code will be crucial for future maintenance and updates.You need to gauge the maintainability of the code. Consider factors like modularity, scalability, and whether best coding practices have been followed. 
4. Code Improvements: Improve the code provided to you based on your analysis reports to provide a final version of the code.
5. If the code has passed your tests, write a conclusion "Code Test Passed".
"""
            test_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say, inputs_show_user=f'{task_id}Observer',
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt='Pair programming is a software development approach in which two programmers collaborate at the same computer. The driver writes code, while the observer analyses each line of code as it is entered. Now you need to act as an observer, review each line of code. When you test the code, I want you to make suggestions on the code and record test reports covering various aspects such as functionality, readability, maintainability, etc. Your role involves not just identifying and reporting errors but also ensuring that the code aligns perfectly with our standards and requirements. Note that you need to check not only these but also other criteria that you feel need to be tested.'
            )
        except:
            raise RuntimeError(response.content.decode())
        save_history(task_id, 'Observer', 0, test_say)
        
        i = 0
        if "Code Test Passed" in test_say:
            i = -1

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
                i_say = f"""
The report after the tester test is:
{test_say}
Your task is to revise or optimize the existing code based on the issues and feedback outlined in the tester's report. Keep the following guidelines in mind:
1. Issue Resolution: Address all concerns and issues identified in the testing report.
2. Code Integrity: Make sure that any changes you make do not introduce new bugs into the system.
3. Performance: Be cautious not to degrade the performance of the code. Optimize where possible but not at the expense of functionality or accuracy.
4. You don't need to provide comments or explanations for the code changes you make.
"""
                inputs_show_user = 'Developer: '
                code_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                    inputs=i_say, inputs_show_user=inputs_show_user, 
                    llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                    sys_prompt=''
                )
            except:
                raise RuntimeError(response.content.decode())
            save_history(task_id, 'Developer', i, code_say)

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
                i_say = f"""
This is code written by the driver you are paired with:{code_say}. And the requirements for it is as follows: {prompt}
Here is what you need to include (not the format or steps you have to follow): 
1. Code Inspection: Please check the code against the requirements received. Please make sure that the function name used in the code is the same as {entry_point} and that all required functions in the requirements are implemented. 
2. Unit Test Execution: Use the provided unit tests from the requirements to validate the functionality of the code. Verify that the program works as expected and returns the correct results. You should also generate your own test cases to additionally test functions. Make sure your program handles unexpected input or error conditions gracefully. If there are any differences, please modify them in the final code.
3. Detailed Analysis: Beyond just the functionality, assess the code for readability. A clear and understandable code will be crucial for future maintenance and updates.You need to gauge the maintainability of the code. Consider factors like modularity, scalability, and whether best coding practices have been followed. 
4. Code Improvements: Improve the code provided to you based on your analysis reports to provide a final version of the code.
5. If the code has passed your tests, write a conclusion "Code Test Passed".
"""
                inputs_show_user = 'Observer:'
                test_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                    inputs=i_say, inputs_show_user=inputs_show_user, 
                    llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                    sys_prompt='Pair programming is a software development approach in which two programmers collaborate at the same computer. The driver writes code, while the observer analyses each line of code as it is entered. Now you need to act as an observer, review each line of code. When you test the code, I want you to make suggestions on the code and record test reports covering various aspects such as functionality, readability, maintainability, etc. Your role involves not just identifying and reporting errors but also ensuring that the code aligns perfectly with our standards and requirements. Note that you need to check not only these but also other criteria that you feel need to be tested.'
                )
            except:
                raise RuntimeError(response.content.decode())
            save_history(task_id, 'Observer', i, test_say)
            if "Code Test Passed" in test_say:
                i = -1
            else: 
                i += 1
        #code_segments = extract_code_segments(output_say)
        
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
        save_history(task_id, 'Extract', '', output_say)

        save_to_jsonl(task_id, code_say)

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
    with open("/home/cli776/human-eval/new_pair/samples_loop2.jsonl", "a") as file:
        file.write(json.dumps(data) + "\n")

def save_history(key1, key2, key3, plan_say):
    filename="/home/cli776/human-eval/new_pair/recoding_loop2.jsonl"
    key = str(key1) + str(key2) + str(key3)
    data = {
        key: plan_say
    }
    with open(filename, 'a') as f:
        f.write(json.dumps(data) + '\n')
