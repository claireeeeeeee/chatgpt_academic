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
            i_say = f'Given a requirement as follows: {prompt}\nI would like for you to take on the role of a project leader, your goal being to devise a high-level plan to manage and direct the developers. Your plan will guide programmers in developing Python functions (rather than delving into implementation details) based on the requirement. The requirement includes function signatures, NL descriptions, unit tests, and possibly import declarations. Here is what you need to include (not the format or steps you have to follow):\n1. Import Statement:\nYou need to specify in the plan the packages that the developer-generated function needs to import, according to the import statement in the requirement.\n2. Function Signature:\nThe function signature contains the function name and the type and number of parameters it accepts. The developer must use this function signature to generate subsequent functions.\n3. NL Description:\nUse the NL description to determine and devise a high-level plan for the development of function. You should guide the developers based on this description, ensuring they understand the context and direction. Your role here is to provide oversight and guidance without immersing yourself in the intricacies of the code. \n4. Test cases:\nPlease do not provide test cases directly to developers. Regarding the testing requirements for developers, please let him generate test cases and test them himself.\n'
            inputs_show_user = f'{task_id}Project Leader for Developer: '
            plan_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say, inputs_show_user=inputs_show_user, 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt='Our development team consists of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Every role has distinct responsibilities that need to be diligently executed for the successful completion of the project. I would like for you to take on the role of a project leader, your goal being to devise a high-level plan to manage. When you, as a project leader, develop a plan, you need to break it down into easy-to-solvable subtasks for functional units and develop a high-level plan outlining the major steps to implement. This plan will be handed over to developers so the output I need is just the plan, no actual code or anything else.'
            )
            
            i_say = f'Given a requirement as follows: {prompt}\nI would like for you to take on the role of a project leader, your goal being to devise a high-level plan to manage and direct the quality assurance testers. Your plan will guide quality assurance testers in testing functions. The requirement includes function signatures, NL descriptions, unit tests, and possibly import declarations. You instruct the quality assurance testers to test whether the developers use the function name and other requirements required in the requirements and guide quality assurance testers to utilize these unit tests to validate the developed function. Their objective will be to ensure that the function works correctly as per the given specifications and is free of any bugs.\n'
            inputs_show_user = f'{task_id}Project Leader for Testers: '
            tester_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say, inputs_show_user=inputs_show_user, 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt='Our development team consists of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Every role has distinct responsibilities that need to be diligently executed for the successful completion of the project. I would like for you to take on the role of a project leader, your goal being to devise a high-level plan to manage. When you, as a project leader, develop a plan, you need to break it down into easy-to-solvable subtasks for functional units and develop a high-level plan outlining the major steps to implement. This plan will be handed over to quality assurance testers so the output I need is just the plan, no actual code or anything else.'
            )
        except:
            raise RuntimeError(response.content.decode())
        save_history(task_id, 'Project Leader1', plan_say)
        save_history(task_id, 'Project Leader2', tester_say)

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
            i_say = f'The plan of Project Leader is {plan_say}./nThis plan will outline:/n1. The package/module you expect to use may contain./n2. The name of function you must follow./n3. The type and number of parameters the function should accept./n4. The requirement in detail./nYour goal is to follow this plan and write Python code to satisfy its requirements and generate your own test cases to test whether your function is accurate. It is paramount that you follow the plan provided by the Project Leader. This ensures consistency and a unified direction in the development process. When you write code, ensure your Python code:/n1. Is efficient in terms of algorithmic complexity./n2. Is readable, making it easier for other team members to understand and, if necessary, modify./n3. Adheres to best practices of Python, including PEP 8 style guidelines.'
            inputs_show_user = 'Developer: '
            code_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say, inputs_show_user=inputs_show_user, 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt='Our development team consists of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Every role has distinct responsibilities that need to be diligently executed for the successful completion of the project. I would like for you to assume the role of a developer. As a core member of the team, you will receive detailed plans from the project leader during the workflow. While you as a developer are writing code that meets the requirements of the plan, you need to use Python to complete the requirements the plans of analysts, taking care to ensure that the code you write is efficient, readable, and follows best practices. The output I need is just a working code, no need to explain your code or other content.'
            )
        except:
            raise RuntimeError(response.content.decode())
        save_history(task_id, 'Developer', code_say)

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
            i_say = f'As part of our development team, we are entrusting you with the crucial responsibility of a quality assurance tester.  Here is what you need to include (not the format or steps you have to follow):/n1. Code Inspection: Once you receive the code from the developers, carefully go through it. The code for your review is as follows: {code_say} and the requirements for developers are as follows: {plan_say} Please ensure that the function names required in the requirements are used and that all required functionality is implemented./n2. Unit Test Execution: The tests are outlined in: {tester_say} Use the provided unit tests from the requirements to validate the functionality of the code. Verify that the program works as expected and returns the correct results. Make sure your program handles unexpected input or error conditions gracefully. Should there be any discrepancies, take note of them for your report./n3. Detailed Analysis: Beyond just the functionality, assess the code for readability. A clear and understandable code will be crucial for future maintenance and updates.You need to gauge the maintainability of the code. Consider factors like modularity, scalability, and whether best coding practices have been followed./n'
            inputs_show_user = 'Quality assurance: '
            tester_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say, inputs_show_user=inputs_show_user, 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt='There is a development team composed of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Each role has its unique responsibilities and requires collaboration for successful execution. When you test the code as a tester on the development team, I want you to make suggestions on the code and record test reports covering various aspects such as functionality, readability, maintainability, etc. Your role involves not just identifying and reporting errors but also ensuring that the code aligns perfectly with our standards and requirements. Note that you need to check not only these but also other criteria that you feel need to be tested.'
            )
        except:
            raise RuntimeError(response.content.decode())
        save_history(task_id, 'Quality assurance', tester_say)

        # Developer2
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
            i_say = f'Your task is to receive the test report from the quality assurance tester and make revisions to the existing code throughout the workflow. Your aim is to fix or improve the previous code based on the test report. Ensure that any changes made to the code do not introduce new errors or negatively impact the performance of the code. Remember, there is no need to explain the code you have written. The test report you have received is: {tester_say}. The code you need to modify is: {code_say}./nWhen you write code, ensure your Python code:/n1. Is efficient in terms of algorithmic complexity./n2. Is readable, making it easier for other team members to understand and, if necessary, modify./n3. Adheres to best practices of Python, including PEP 8 style guidelines./n'
            inputs_show_user = 'Final code: '
            gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say, inputs_show_user=inputs_show_user, 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt='There is a development team composed of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Each role has its unique responsibilities and requires collaboration for successful execution. Next, I would like you to take on the role of a developer once again.  When you, as a developer, write code that meets the requirements of the plan, I want you to change the code I give you based on the test reports from the testers. If the code does not need to be modified, please also output the code that has not been changed.'
            )
        except:
            raise RuntimeError(response.content.decode())
        save_history(task_id, 'Developer', gpt_say)

        # Quality assurance2: 
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
            i_say = f'As part of our development team, we are entrusting you with the crucial responsibility of a quality assurance tester.  Here is what you need to include (not the format or steps you have to follow):/n1. Code Inspection: Once you receive the code from the developers, carefully go through it. The code for your review is as follows: {code_say} and the requirements for developers are as follows: {plan_say} Please ensure that the function names required in the requirements are used and that all required functionality is implemented./n2. Unit Test Execution: The tests are outlined in: {tester_say} Use the provided unit tests from the requirements to validate the functionality of the code. Verify that the program works as expected and returns the correct results. Make sure your program handles unexpected input or error conditions gracefully. Should there be any discrepancies, take note of them for your report./n3. Detailed Analysis: Beyond just the functionality, assess the code for readability. A clear and understandable code will be crucial for future maintenance and updates.You need to gauge the maintainability of the code. Consider factors like modularity, scalability, and whether best coding practices have been followed./n'
            inputs_show_user = 'Quality assurance2: '
            tester_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say, inputs_show_user=inputs_show_user, 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt='There is a development team composed of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Each role has its unique responsibilities and requires collaboration for successful execution. When you test the code as a tester on the development team, I want you to make suggestions on the code and record test reports covering various aspects such as functionality, readability, maintainability, etc. Your role involves not just identifying and reporting errors but also ensuring that the code aligns perfectly with our standards and requirements. Note that you need to check not only these but also other criteria that you feel need to be tested.'
            )
        except:
            raise RuntimeError(response.content.decode())
        save_history(task_id, 'Quality assurance', tester_say)

        # Developer3
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
            i_say = f'Your task is to receive the test report from the quality assurance tester and make revisions to the existing code throughout the workflow. Your aim is to fix or improve the previous code based on the test report. Ensure that any changes made to the code do not introduce new errors or negatively impact the performance of the code. Remember, there is no need to explain the code you have written. The test report you have received is: {tester_say}. The code you need to modify is: {code_say}./nWhen you write code, ensure your Python code:/n1. Is efficient in terms of algorithmic complexity./n2. Is readable, making it easier for other team members to understand and, if necessary, modify./n3. Adheres to best practices of Python, including PEP 8 style guidelines./n'
            inputs_show_user = 'Final code: '
            gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say, inputs_show_user=inputs_show_user, 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt='There is a development team composed of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Each role has its unique responsibilities and requires collaboration for successful execution. Next, I would like you to take on the role of a developer once again.  When you, as a developer, write code that meets the requirements of the plan, I want you to change the code I give you based on the test reports from the testers. If the code does not need to be modified, please also output the code that has not been changed.'
            )
        except:
            raise RuntimeError(response.content.decode())
        save_history(task_id, 'Developer', gpt_say)

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
            i_say = f'Here is the requirement: {prompt} and the report from the developer: {gpt_say}. Your objective is to extract the final version of the code for me, by reading the final report from the developer.  Please remember to remove the code used by the test, and only keep the Python functions needed in the requirements(mentioned in the function signature.). Please remember: provide only the final version of the code.'
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
    with open("/home/cli776/human-eval/samples.jsonl", "a") as file:
        file.write(json.dumps(data) + "\n")

def save_history(key, values):
    with open("/home/cli776/human-eval/recoding.jsonl", "w") as f:
        for idx, value in enumerate(values, 1):  # 从1开始计数
            key = f"{idx}_{key}"
            data = {key: value}
            json_str = json.dumps(data)
            f.write(json_str + '\n')

def save_history(key1, key2, plan_say):
    filename="/home/cli776/human-eval/recoding.jsonl"
    key = str(key1) + str(key2)
    data = {
        key: plan_say
    }
    with open(filename, 'a') as f:
        f.write(json.dumps(data) + '\n')
