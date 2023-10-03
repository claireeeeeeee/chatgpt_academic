from toolbox import CatchException, report_execption, write_results_to_file
from toolbox import update_ui, choose_appropriate_key, get_conf
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from .crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
from .crazy_utils import read_and_clean_pdf_text
from colorful import *
import re,os,requests
import json
from request_llm.bridge_all import model_info

@CatchException
def code_generation_test1(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    history = []    # 清空历史，以免输入溢出
    jsonl_data = read_jsonl(txt)

    for entry in jsonl_data:
        task_id = entry["task_id"]
        prompt = entry["prompt"]

        # 使用特定的方法请求答案
        answer = ask_question(prompt, task_id, llm_kwargs, chatbot)
        
        print('answer:::', answer)

def ask_question(prompt, task_id, llm_kwargs, chatbot):
    i_say = f'There is a development team composed of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Each role has its unique responsibilities and requires collaboration for successful execution. I would like for you to take on the role of a project leader, your goal being to devise a high-level plan and guide programmers in developing the software, rather than delving into the implementation details. The requirement gives the name of the function and specific requirements. Given a requirement as follows: {prompt}'
    inputs_show_user = f'{task_id}Project Leader: '
    plan_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=i_say, inputs_show_user=inputs_show_user, 
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
        sys_prompt='When you, as a project leader, develop a plan, you need to break it down into easy-to-solvable subtasks for functional units and develop a high-level plan outlining the major steps to implement. The output I need is just this plan, no actual code or anything else.'
    )
    # 从 plan_say 中提取答案 (这取决于 request_gpt_model_in_new_thread_with_ui_alive 返回的格式)
    answer = plan_say  # 假设plan_say直接是答案，如果不是，您需要进行必要的处理来提取答案
    return answer

def read_jsonl(file_path):
    data = []
    with open(file_path, "r") as file:
        for line in file:
            # Parse each line as a JSON object and append it to the list
            data.append(json.loads(line.strip()))
    return data