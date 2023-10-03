from toolbox import CatchException, update_ui
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
import re
@CatchException
def code_generation_self1(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数，如温度和top_p等，一般原样传递下去就行
    plugin_kwargs   插件模型的参数，暂时没有用武之地
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    web_port        当前软件运行的端口号
    """
    history = []    # 清空历史，以免输入溢出
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 由于请求gpt需要一段时间，我们先及时地做一次界面更新
    i_say = f'There is a development team that includes a requirements analyst, a developer, and a quality assurance tester. The team needs to develop programs that satisfy the requirements of the users. The different roles have different divisions of labor and need to cooperate with each others. I want you to act as a requirement analyst in this team. The goal of an analyst is to develop a high-level plan and focus on guiding the coder in writing programs, rather than delving into implementation details. Given a requirement {txt}, the analyst decomposes it into several easy-to-solve subtasks that facilitate the division of functional units and develops a high-level plan that outlines the major steps of the implementation.'
    inputs_show_user = 'Analyst: '
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=i_say, inputs_show_user=inputs_show_user, 
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
        sys_prompt='When you, as an analyst, develop a plan, you need to break it down into easy-to-solvable subtasks for functional units and develop a high-level plan outlining the major steps to implement. The output I need is just this plan, no actual code or anything else.'
    )
    history.append(gpt_say)

    i_say = f'There is a development team that includes a requirements analyst, a developer, and a quality assurance tester. The team needs to develop programs that satisfy the requirements of the users. The different roles have different divisions of labor and need to cooperate with each others. I want you to act as a developer on our development team. As the central role of this team, the coder receives plans from an analyst throughout the workflow. You will receive plans from a requirements analyst. Plans are {gpt_say}. Your job is: when you receive a plan from a requirements analyst, write code in Python that meets the requirements following the plan. Ensure that the code you write is efficient, readable, and follows best practices.'
    inputs_show_user = 'Coder: '
    gpt_say_code = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=i_say, inputs_show_user=inputs_show_user, 
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
        sys_prompt='While you as a developer are writing code that meets the requirements of the plan, you need to use Python to complete the requirements the plans of analysts, taking care to ensure that the code you write is efficient, readable, and follows best practices. The output I need is just a working code, no need to explain your code or other content.'
    )
    history.append(gpt_say_code)

    i_say = f'There is a development team that includes a requirements analyst, a developer, and a quality assurance tester. The team needs to develop programs that satisfy the requirements of the users. The different roles have different divisions of labor and need to cooperate with each others. I want you to act as a tester on our development team. The tester acquires the code authored by the coder, which is {gpt_say}, and subsequently documents a test report containing various aspects, such as functionality, readability, and maintainability.'
    inputs_show_user = 'Tester: '
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=i_say, inputs_show_user=inputs_show_user, 
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
        sys_prompt='When you test the code as a tester on the development team, I want you to make suggestions on the code and record test reports covering various aspects such as functionality, readability, maintainability, etc. Note that you need to check not only these, but also other criteria that you feel need to be tested.'
    )
    history.append(gpt_say)

    i_say = f'There is a development team that includes a requirements analyst, a developer, and a quality assurance tester. The team needs to develop programs that satisfy the requirements of the users. The different roles have different divisions of labor and need to cooperate with each others. I want you to act as a developer on our development team. As the central role of this team, the coder receives test reports from a tester throughout the workflow. You will receive test reports from a tester, which is {gpt_say}. Your job is: when you receive a test report from a tester, fix or improve the code, which is {gpt_say_code}, based on the content of the report. Ensure that any changes made to the code do not introduce new bugs or negatively impact the performance of the code. Remember, do not need to explain the code you wrote.'
    inputs_show_user = 'Final code: '
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=i_say, inputs_show_user=inputs_show_user, 
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
        sys_prompt='When you, as a developer, write code that meets the requirements of the plan, I want you to change the code I give you based on the test reports from the testers. If the code does not need to be modified, please also output the code that has not been changed.'
    )
    # 提取代码段
    code_segments = extract_code_segments(gpt_say)
    # 将提取的代码保存到文件
    output_file = "code.py"
    save_code_to_file(code_segments, output_file)

    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新

def extract_code_segments(input_string):
    # 使用正则表达式提取代码段
    code_pattern = r'```python(.*?)```'
    code_segments = re.findall(code_pattern, input_string, re.DOTALL)
    return code_segments

def save_code_to_file(code_segments, output_file):
    with open(output_file, 'w') as file:
        for idx, code in enumerate(code_segments, start=1):
            file.write(f"## ==== Code Segment {idx} ====\n")
            file.write(code)
            file.write("\n\n")