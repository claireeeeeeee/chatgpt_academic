from toolbox import CatchException, report_execption, write_results_to_file
from toolbox import update_ui, choose_appropriate_key, get_conf
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from .crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
from .crazy_utils import read_and_clean_pdf_text
from colorful import *
import re,os,requests,json
from request_llm.bridge_all import model_info

@CatchException
def code_generation_multi(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    history = []    # 清空历史，以免输入溢出
    jsonl_data = read_jsonl(txt)

    for chunk in read_three(jsonl_data):
        prompt_array = []
        id_array = []
        for item in chunk:
            prompt_array.append(item["prompt"])
            id_array.append(item["task_id"])

        history_array = [''] * len(prompt_array)
        sys_prompt_array_leader1 = ["Our development team consists of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Every role has distinct responsibilities that need to be diligently executed for the successful completion of the project. I would like for you to take on the role of a project leader, your goal being to devise a high-level plan to manage. When you, as a project leader, develop a plan, you need to break it down into easy-to-solvable subtasks for functional units and develop a high-level plan outlining the major steps to implement. This plan will be handed over to developers so the output I need is just the plan, no actual code or anything else."] * len(prompt_array)
        sys_prompt_array_leader2 = ["Our development team consists of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Every role has distinct responsibilities that need to be diligently executed for the successful completion of the project. I would like for you to take on the role of a project leader, your goal being to devise a high-level plan to manage. When you, as a project leader, develop a plan, you need to break it down into easy-to-solvable subtasks for functional units and develop a high-level plan outlining the major steps to implement. This plan will be handed over to quality assurance testers so the output I need is just the plan, no actual code or anything else."] * len(prompt_array)
        sys_prompt_array_dev1 = ["Our development team consists of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Every role has distinct responsibilities that need to be diligently executed for the successful completion of the project. I would like for you to assume the role of a developer. As a core member of the team, you will receive detailed plans from the project leader during the workflow. While you as a developer are writing code that meets the requirements of the plan, you need to use Python to complete the requirements the plans of analysts, taking care to ensure that the code you write is efficient, readable, and follows best practices. The output I need is just a working code, no need to explain your code or other content."] * len(prompt_array)
        sys_prompt_array_test = ["There is a development team composed of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Each role has its unique responsibilities and requires collaboration for successful execution. When you test the code as a tester on the development team, I want you to make suggestions on the code and record test reports covering various aspects such as functionality, readability, maintainability, etc. Your role involves not just identifying and reporting errors but also ensuring that the code aligns perfectly with our standards and requirements. Note that you need to check not only these but also other criteria that you feel need to be tested."] * len(prompt_array)
        sys_prompt_array_dev2 = ["There is a development team composed of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Each role has its unique responsibilities and requires collaboration for successful execution. Next, I would like you to take on the role of a developer once again.  When you, as a developer, write code that meets the requirements of the plan, I want you to change the code I give you based on the test reports from the testers. If the code does not need to be modified, please also output the code that has not been changed."] * len(prompt_array)
        sys_prompt_array_output = ["Only output the final version of the code, and only the code(no any descriptions)."] * len(prompt_array)
        
        # Project Leader 1
        history = []    # 清空历史，以免输入溢出
        gpt_plans_collection = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
            inputs_array=[
                f"Given a requirement as follows: {prompt}\nI would like for you to take on the role of a project leader, your goal being to devise a high-level plan to manage and direct the developers. Your plan will guide programmers in developing Python functions (rather than delving into implementation details) based on the requirement. The requirement includes function signatures, NL descriptions, unit tests, and possibly import declarations. Here is what you need to include (not the format or steps you have to follow):\n1. Import Statement:\nYou need to specify in the plan the packages that the developer-generated function needs to import, according to the import statement in the requirement.\n2. Function Signature:\nThe function signature contains the function name and the type and number of parameters it accepts. The developer must use this function signature to generate subsequent functions.\n3. NL Description:\nUse the NL description to determine and devise a high-level plan for the development of function. You should guide the developers based on this description, ensuring they understand the context and direction. Your role here is to provide oversight and guidance without immersing yourself in the intricacies of the code. \n4. Test cases:\nPlease do not provide test cases directly to developers. Regarding the testing requirements for developers, please let him generate test cases and test them himself.\n" for prompt in prompt_array],
            inputs_show_user_array=[f"{task_id}Project Leader for Developers: " for task_id in id_array],
            llm_kwargs=llm_kwargs,
            chatbot=chatbot,
            history_array=history_array,
            sys_prompt_array=sys_prompt_array_leader1,
                # max_workers=5  # OpenAI所允许的最大并行过载
            )

        # Project Leader 2
        history = []    # 清空历史，以免输入溢出
        gpt_testers_collection = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
            inputs_array=[
                f"Given a requirement as follows: {prompt}\nI would like for you to take on the role of a project leader, your goal being to devise a high-level plan to manage and direct the quality assurance testers. Your plan will guide quality assurance testers in testing functions. The requirement includes function signatures, NL descriptions, unit tests, and possibly import declarations. You instruct the quality assurance testers to test whether the developers use the function name and other requirements required in the requirements and guide quality assurance testers to utilize these unit tests to validate the developed function. Their objective will be to ensure that the function works correctly as per the given specifications and is free of any bugs.\n" for prompt in prompt_array],
            inputs_show_user_array=[f"{task_id}Project Leader for Testers: " for task_id in id_array],
            llm_kwargs=llm_kwargs,
            chatbot=chatbot,
            history_array=history_array,
            sys_prompt_array=sys_prompt_array_leader2,
                # max_workers=5  # OpenAI所允许的最大并行过载
            )

        # Developer1
        codes_plan = []
        for i,k in enumerate(gpt_plans_collection): 
            if i%2==0:
                gpt_plans_collection[i] = gpt_plans_collection[i]
            else:
                codes_plan.append(gpt_plans_collection[i])
        
        save_history("Project Leader for Developers: ", codes_plan)
        inputs_show_user_array = ["Developer:"] * len(prompt_array)
        history = []    # 清空历史，以免输入溢出
        gpt_code_collection = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
            inputs_array=[
                f"The plan of Project Leader is {plan_say}./nThis plan will outline:/n1. The package/module you expect to use may contain./n2. The name of function you must follow./n3. The type and number of parameters the function should accept./n4. The requirement in detail./nYour goal is to follow this plan and write Python code to satisfy its requirements and generate your own test cases to test whether your function is accurate. It is paramount that you follow the plan provided by the Project Leader. This ensures consistency and a unified direction in the development process. When you write code, ensure your Python code:/n1. Is efficient in terms of algorithmic complexity./n2. Is readable, making it easier for other team members to understand and, if necessary, modify./n3. Adheres to best practices of Python, including PEP 8 style guidelines." for plan_say in codes_plan],
            inputs_show_user_array=inputs_show_user_array,
            llm_kwargs=llm_kwargs,
            chatbot=chatbot,
            history_array=history_array,
            sys_prompt_array=sys_prompt_array_dev1,
                # max_workers=5  # OpenAI所允许的最大并行过载
            )
        
        # Quality assurance tester
        plans = merge_3_lists(gpt_code_collection, gpt_plans_collection, gpt_testers_collection)
        save_history("Project Leader for Testers: ", plans)

        inputs_show_user_array = ["Quality assurance:"] * len(prompt_array)
        history = []    # 清空历史，以免输入溢出
        gpt_testers_collection = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
            inputs_array=[
                f"As part of our development team, we are entrusting you with the crucial responsibility of a quality assurance tester.  Here is what you need to include (not the format or steps you have to follow):/n1. Code Inspection: Once you receive the code from the developers, carefully go through it. The code for your review is as follows: {code_say} and the requirements for developers are as follows: {plan_say} Please ensure that the function names required in the requirements are used and that all required functionality is implemented./n2. Unit Test Execution: The tests are outlined in: {tester_say} Use the provided unit tests from the requirements to validate the functionality of the code. Verify that the program works as expected and returns the correct results. Make sure your program handles unexpected input or error conditions gracefully. Should there be any discrepancies, take note of them for your report./n3. Detailed Analysis: Beyond just the functionality, assess the code for readability. A clear and understandable code will be crucial for future maintenance and updates.You need to gauge the maintainability of the code. Consider factors like modularity, scalability, and whether best coding practices have been followed./n" for code_say,plan_say,tester_say in plans],
            inputs_show_user_array=inputs_show_user_array,
            llm_kwargs=llm_kwargs,
            chatbot=chatbot,
            history_array=history_array,
            sys_prompt_array=sys_prompt_array_test,
                # max_workers=5  # OpenAI所允许的最大并行过载
            )

        # Developer2
        plans2 = merge_2_lists(gpt_testers_collection, gpt_code_collection)
        save_history("Developer2use", plans2)

        inputs_show_user_array = ["Final code:"] * len(prompt_array)
        history = []    # 清空历史，以免输入溢出
        gpt_code_collection = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
            inputs_array=[
                f"Your task is to receive the test report from the quality assurance tester and make revisions to the existing code throughout the workflow. Your aim is to fix or improve the previous code based on the test report. Ensure that any changes made to the code do not introduce new errors or negatively impact the performance of the code. Remember, there is no need to explain the code you have written. The test report you have received is: {tester_say}. The code you need to modify is: {code_say}./nWhen you write code, ensure your Python code:/n1. Is efficient in terms of algorithmic complexity./n2. Is readable, making it easier for other team members to understand and, if necessary, modify./n3. Adheres to best practices of Python, including PEP 8 style guidelines./n" for tester_say, code_say in plans2],
            inputs_show_user_array=inputs_show_user_array,
            llm_kwargs=llm_kwargs,
            chatbot=chatbot,
            history_array=history_array,
            sys_prompt_array=sys_prompt_array_dev2,
                # max_workers=5  # OpenAI所允许的最大并行过载
            )
        
        # Quality assurance tester2
        plans = merge_3_lists(gpt_code_collection, gpt_plans_collection, gpt_testers_collection)
        save_history("Tester 2 use: ", plans)

        inputs_show_user_array = ["Quality assurance:"] * len(prompt_array)
        history = []    # 清空历史，以免输入溢出
        gpt_testers_collection = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
            inputs_array=[
                f"As part of our development team, we are entrusting you with the crucial responsibility of a quality assurance tester.  Here is what you need to include (not the format or steps you have to follow):/n1. Code Inspection: Once you receive the code from the developers, carefully go through it. The code for your review is as follows: {code_say} and the requirements for developers are as follows: {plan_say} Please ensure that the function names required in the requirements are used and that all required functionality is implemented./n2. Unit Test Execution: The tests are outlined in: {tester_say} Use the provided unit tests from the requirements to validate the functionality of the code. Verify that the program works as expected and returns the correct results. Make sure your program handles unexpected input or error conditions gracefully. Should there be any discrepancies, take note of them for your report./n3. Detailed Analysis: Beyond just the functionality, assess the code for readability. A clear and understandable code will be crucial for future maintenance and updates.You need to gauge the maintainability of the code. Consider factors like modularity, scalability, and whether best coding practices have been followed./n" for code_say,plan_say,tester_say in plans],
            inputs_show_user_array=inputs_show_user_array,
            llm_kwargs=llm_kwargs,
            chatbot=chatbot,
            history_array=history_array,
            sys_prompt_array=sys_prompt_array_test,
                # max_workers=5  # OpenAI所允许的最大并行过载
            )
        
        # Developer3
        plans2 = merge_2_lists(gpt_testers_collection, gpt_code_collection)
        save_history("Developer3use", plans2)

        inputs_show_user_array = ["Final code:"] * len(prompt_array)
        history = []    # 清空历史，以免输入溢出
        gpt_code_collection = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
            inputs_array=[
                f"Your task is to receive the test report from the quality assurance tester and make revisions to the existing code throughout the workflow. Your aim is to fix or improve the previous code based on the test report. Ensure that any changes made to the code do not introduce new errors or negatively impact the performance of the code. Remember, there is no need to explain the code you have written. The test report you have received is: {tester_say}. The code you need to modify is: {code_say}./nWhen you write code, ensure your Python code:/n1. Is efficient in terms of algorithmic complexity./n2. Is readable, making it easier for other team members to understand and, if necessary, modify./n3. Adheres to best practices of Python, including PEP 8 style guidelines./n" for tester_say, code_say in plans2],
            inputs_show_user_array=inputs_show_user_array,
            llm_kwargs=llm_kwargs,
            chatbot=chatbot,
            history_array=history_array,
            sys_prompt_array=sys_prompt_array_dev2,
                # max_workers=5  # OpenAI所允许的最大并行过载
            )
        
        # Final output: 
        final_codes = []
        for i,k in enumerate(gpt_code_collection): 
            if i%2==0:
                gpt_code_collection[i] = gpt_code_collection[i]
            else:
                final_codes.append(gpt_code_collection[i])
        save_history("Dev2", final_codes)

        if len(prompt_array) != len(final_codes):
            raise RuntimeError("The lengths of the lists must be equal.")
        plans3 = []
        for i, (item1, item2) in enumerate(zip(prompt_array, final_codes)):
            plans3.append([item1, item2])

        inputs_show_user_array = ["Final output:"] * len(prompt_array)
        history = []    # 清空历史，以免输入溢出
        gpt_output_collection = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
            inputs_array=[
                f"Here is the requirement: {prompt} and the report from the developer: {gpt_say}. Your objective is to extract the final version of the code for me, by reading the final report from the developer.  Please remember to remove the code used by the test, and only keep the Python functions needed in the requirements(mentioned in the function signature.). Please remember: provide only the final version of the code." for prompt, gpt_say in plans3],
            inputs_show_user_array=inputs_show_user_array,
            llm_kwargs=llm_kwargs,
            chatbot=chatbot,
            history_array=history_array,
            sys_prompt_array=sys_prompt_array_output,
                # max_workers=5  # OpenAI所允许的最大并行过载
            )
        outputs = clean(gpt_output_collection)
        save_to_jsonl(id_array, outputs)

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
    
    with open("/home/cli776/human-eval/samples_multi_2.jsonl", "a") as file:
        for task_id, code_segments in zip(id_list, code_list):
            data = {"task_id": task_id, "completion": code_segments}
            file.write(json.dumps(data) + "\n")

def save_history(key1, key2, plan_say):
    filename="/home/cli776/human-eval/recoding_multi_2.jsonl"
    key = str(key1) + str(key2)
    data = {
        key: plan_say
    }
    with open(filename, 'a') as f:
        f.write(json.dumps(data) + '\n')
   
def save_history(key, lists):
    filename = "/home/cli776/human-eval/multi_2.jsonl"
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

def merge_3_lists(list1, list2, list3):
    if len(list1) != len(list2) or len(list2) != len(list3):
        raise RuntimeError("The lengths of the lists must be equal.")
    
    results = []
    for i, (item1, item2, item3) in enumerate(zip(list1, list2, list3)):
        if i%2!=0:
            results.append([item1, item2, item3])
    return results

def merge_2_lists(list1, list2):
    if len(list1) != len(list2):
        raise RuntimeError("The lengths of the lists must be equal.")
    
    results = []
    for i, (item1, item2) in enumerate(zip(list1, list2)):
        if i%2!=0:
            results.append([item1, item2])
    return results

def clean(list1):
    results = []
    for i, item in enumerate(list1):
        if i % 2 != 0:
            results.append(item)
    return results