from toolbox import CatchException, report_execption, write_results_to_file
from toolbox import update_ui, choose_appropriate_key, get_conf
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from .crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
from .crazy_utils import read_and_clean_pdf_text
from colorful import *
import re,os,requests,json
from request_llm.bridge_all import model_info

@CatchException
def code_generation_new1(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
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
When you, as the project leader, generate a report to guide the development of programmers, you should make the requirements in the report as detailed as possible to let the programmer know what he needs to do. Your plan will guide programmers in developing Python functions (rather than delving into implementation details) based on the requirement. Given a requirement as follows: 
{prompt}
This requirement itself is the header of the program that the programmer needs to generate. What the programmer needs to do is to continue writing according to this requirement. It includes function signatures, NL descriptions, unit tests, and possibly import declarations. Here is what you need to include (not the format or steps you have to follow):
1. Import Statement:
You need to specify in the plan the packages that the developer-generated function needs to import, according to the import statement in the requirement.
2. Function Signature:
The function signature contains the function name and the type and number of parameters it accepts. The function signature specifies the name of the function that developers need to develop.The function name should be {entry_point}.
3. NL Description:
Use the NL description to determine and devise a high-level plan for the development of function. You should guide the developers based on this description, ensuring they understand the context and direction and pay attention to every detail of the requirements. Your role here is to provide oversight and guidance without immersing yourself in the intricacies of the code. 
4. Test cases:
Please do not provide test cases directly to developers. Regarding the testing requirements for developers, please let him generate test cases and test them himself.
"""
            inputs_show_user = f'{task_id}Project Leader'
            plan_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say1, inputs_show_user=inputs_show_user, 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt='Our development team consists of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Every role has distinct responsibilities that need to be diligently executed for the successful completion of the project. I would like for you to take on the role of a project leader, your goal being to devise a high-level plan to manage. When you, as a project leader, develop a plan, you need to break it down into easy-to-solvable subtasks for functional units and develop a high-level plan outlining the major steps to implement. This plan will be handed over to developers so the output I need is just the plan, no actual code or anything else.'
            )
        except:
            raise RuntimeError(response.content.decode())
        save_history(task_id, 'Project Leader', "", plan_say)

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
The plan of Project Leader is: 
{plan_say}
This plan will outline:
1. The package/module you expect to use may contain.
2. The name of function you must follow. The function name should be {entry_point}.
3. The type and number of parameters the function should accept.
4. The requirements in detail.
Your goal is to follow the requirements and write Python code to satisfy its requirements and generate your own test cases to test whether your function is accurate. Please continue writing code after this header of function: ```{prompt}```. It is crucial to follow the function names and packages required in it. You also need to check the code to ensure it meets all the criteria specified in the requirement. Make sure to look for edge cases and try to break the code to ensure it's robust. This ensures consistency and a unified direction in the development process. When you write code, ensure your Python code:
1. Is efficient in terms of algorithmic complexity.
2. Is readable, making it easier for other team members to understand and, if necessary, modify.
3. Adheres to best practices of Python, including PEP 8 style guidelines.
"""
            inputs_show_user = 'Developer: '
            code_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say, inputs_show_user=inputs_show_user, 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt='Our development team consists of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Every role has distinct responsibilities that need to be diligently executed for the successful completion of the project. I would like for you to assume the role of a developer. As a core member of the team, you will receive detailed plans from the project leader during the workflow. While you as a developer are writing code that meets the requirements of the plan, you need to use Python to complete the requirements the plans of analysts, taking care to ensure that the code you write is efficient, readable, and follows best practices. The output I need is just a working code, no need to explain your code or other content.'
            )
        except:
            raise RuntimeError(response.content.decode())
        save_history(task_id, 'Developer', "", code_say)

        # first tester
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
As part of our development team, we are entrusting you with the crucial responsibility of a quality assurance tester.  You hold the keys to the final gate through which our code must pass before being deployed. 
The requirement you need to follow is:
{prompt}
The code you need to modify is: 
{code_say}
Below is a comprehensive guide on what your responsibilities entail. 
1. Function Names and Signatures Check: Verify that the function names specified in the development requirements are correctly used.
2. Import Statements: Validate that all necessary packages are correctly imported as specified in the development plan.
3. Implementation Completeness: Ensure that all required functionalities are fully implemented, per the development plan.
4. Unit Test Execution: 
Use the unit tests provided in the requirements to verify the functionality of the code. Verify that the program works as expected and returns the correct results. Make sure your program handles unexpected input or error conditions gracefully. If there are any errors, please write them in your report.
5. Exception Handling:
Test how the program handles unexpected input or error conditions. Make sure it fails gracefully without sudden crashes. At this step, you can generate your own test cases. The test cases provided in the requirements may not fully cover all situations. To ensure exception handling, you need to account for as many exception inputs as possible in advance. If there are any errors, please write them in your report.
6. Detailed Code Quality Analysis:
Readability: Review the code for readability. Simple, clear code is easier to maintain and update in the future. Assess whether comments and documentation are sufficient and clear.
Maintainability: Gauge how maintainable the code is. Is it modular? Could it be easily extended or modified?
Scalability and Performance: Test the scalability of your code. How it performs under different conditions and it should be able to handle larger scales if needed.
Best Practices: Determine whether the code adheres to industry best practices. This includes the use of design patterns, following naming conventions, and efficient resource management.
7. If the code or the revised code has passed your tests, write a conclusion "Code Test Passed".
"""
            inputs_show_user = 'Quality assurance:'
            test_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say, inputs_show_user=inputs_show_user, 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt='There is a development team composed of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Each role has its unique responsibilities and requires collaboration for successful execution. When you test the code as a tester on the development team, I want you to make suggestions on the code and record test reports covering various aspects such as functionality, readability, maintainability, etc. Your role involves not just identifying and reporting errors but also ensuring that the code aligns perfectly with our standards and requirements. Note that you need to check not only these but also other criteria that you feel need to be tested.'
            )
        except:
            raise RuntimeError(response.content.decode())
        save_history(task_id, 'Quality assurance', "", test_say)

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
                    sys_prompt='As a core member of the team, you will receive the test report from tester during the workflow. When you as a developer make changes to your code, you use Python to make the changes requested by the tester, taking care to ensure that the code you write is efficient, readable, and follows best practices. The output I need is just a working code, no need to explain your code or anything.'
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
As part of our development team, we are entrusting you with the crucial responsibility of a quality assurance tester.  You hold the keys to the final gate through which our code must pass before being deployed. 
The requirement you need to follow is:
{prompt}
The code you need to modify is: 
{code_say}
Below is a comprehensive guide on what your responsibilities entail. 
1. Function Names and Signatures Check: Verify that the function names specified in the development requirements are correctly used.
2. Import Statements: Validate that all necessary packages are correctly imported as specified in the development plan.
3. Implementation Completeness: Ensure that all required functionalities are fully implemented, per the development plan.
4. Unit Test Execution: 
Use the unit tests provided in the requirements to verify the functionality of the code. Verify that the program works as expected and returns the correct results. Make sure your program handles unexpected input or error conditions gracefully. If there are any errors, please write them in your report.
5. Exception Handling:
Test how the program handles unexpected input or error conditions. Make sure it fails gracefully without sudden crashes. At this step, you can generate your own test cases. The test cases provided in the requirements may not fully cover all situations. To ensure exception handling, you need to account for as many exception inputs as possible in advance. If there are any errors, please write them in your report.
6. Detailed Code Quality Analysis:
Readability: Review the code for readability. Simple, clear code is easier to maintain and update in the future. Assess whether comments and documentation are sufficient and clear.
Maintainability: Gauge how maintainable the code is. Is it modular? Could it be easily extended or modified?
Scalability and Performance: Test the scalability of your code. How it performs under different conditions and it should be able to handle larger scales if needed.
Best Practices: Determine whether the code adheres to industry best practices. This includes the use of design patterns, following naming conventions, and efficient resource management.
7. If the code or the revised code has passed your tests, write a conclusion "Code Test Passed".
"""
                inputs_show_user = 'Quality assurance:'
                test_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                    inputs=i_say, inputs_show_user=inputs_show_user, 
                    llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                    sys_prompt='There is a development team composed of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Each role has its unique responsibilities and requires collaboration for successful execution. When you test the code as a tester on the development team, I want you to make suggestions on the code and record test reports covering various aspects such as functionality, readability, maintainability, etc. Your role involves not just identifying and reporting errors but also ensuring that the code aligns perfectly with our standards and requirements. Note that you need to check not only these but also other criteria that you feel need to be tested.'
                )
            except:
                raise RuntimeError(response.content.decode())
            save_history(task_id, 'Quality assurance', i, test_say)
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
        save_history(task_id, 'Extract', "", output_say)

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
    with open("/home/cli776/human-eval/new_pair/samples_loop3.jsonl", "a") as file:
        file.write(json.dumps(data) + "\n")

def save_history(key1, key2, key3, plan_say):
    filename="/home/cli776/human-eval/new_pair/recoding_loop3.jsonl"
    key = str(key1) + str(key2) + str(key3)
    data = {
        key: plan_say
    }
    with open(filename, 'a') as f:
        f.write(json.dumps(data) + '\n')
