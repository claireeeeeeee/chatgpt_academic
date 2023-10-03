from toolbox import CatchException, update_ui
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from .crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
import re
import os

@CatchException
def code_generation(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
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
        # 基本信息：功能、贡献者
    chatbot.append([
        "函数插件功能？",
        "理解需要生成的代码的功能，将生成的代码下载至html，css文件中"])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
    
    i_say = f'将{txt}网站的任务按功能分开，格式为1.a, 1.b, 2.a, 2.b, 3.a, 3.b...\n\n'
    inputs_show_user = f'Here is the possible functions of your website:'
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=i_say, inputs_show_user=inputs_show_user, 
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
        sys_prompt="将网站的任务按功能分开，格式为1.a, 1.b, 2.a, 2.b, 3.a, 3.b\n\n"
    )

    # history.append(gpt_say)
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新

    i_say = f'将这些功能在不同的网页页面上重新分类，需要包含上面所有功能，即按页面将功能重新分类，实例格式：1. 首页：功能1，功能2，功能3...\n\n'
    inputs_show_user = f'Here is the 大框架代码:'
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=i_say, inputs_show_user=inputs_show_user, 
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
        sys_prompt="将这些功能在不同的网页页面上重新分类，需要包含上面所有功能，即按页面将功能重新分类，实例格式：1. 首页：功能1，功能2，功能3...\n\n"
    )
    
    history.append(gpt_say)
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新

    function_list = extract_function_descriptions(history[0])
    
    for function in function_list:
        i_say = f'该网站将有{function[0]}页面html，css代码，包含功能{function[1:]}\n\n'
        inputs_show_user = f'{function[0]}页面:'
        gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
            inputs=i_say, inputs_show_user=inputs_show_user, 
            llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
            sys_prompt="该网站将有{function[0]}页面html，css代码，包含功能{function[1:]}，格式为：HTML代码：...，CSS代码：...\n\n"
            )
        history.append(gpt_say)
        if '/' in function[0]: 
            function[0] = function[0].replace('/', '')      # 有些功能名字中有/，会导致文件夹创建失败
        file = f'/home/cli776/{txt}{txt}'
        create_folder(file)
        html_file = f'/home/cli776/{txt}{txt}/{function[0]}.html'
        css_file = f'/home/cli776/{txt}{txt}/{function[0]}.css'
        print('!!!', gpt_say, html_file, css_file)
        save_html_css_code(gpt_say, html_file, css_file)

# string = ['1. 首页：搜索功能，最新产品展示，热门商品推荐，个人账户登录/注册，购物车。\n\n2. 产品页面：产品分类展示，商品详细信息，评论区，加入购物车/立即购买。\n\n3. 购物车页面：商品清单，商品总价计算器，商品修改/删除，结算。\n\n4. 支付页面：订单信息，支付方式选择，确认支付。\n\n5. 个人账户页面：个人信息管理，订单查看/修改，收货地址管理，购物历史记录。\n\n6. 帮助页面：常见问题解答，联系客服，商家服务条款，退换货政策。']
# 提取string中的功能描述，return [[1: A, B, C], [2: D, E]]list
def extract_function_descriptions(string):
    lines = string.split('\n')
    lines = [line for line in lines if line]

    result = []
    for line in lines:
        line_parts = line.split('：')
        title = line_parts[0].split('. ')[1]
        items = [item.strip('。，') for item in line_parts[1].split('，')]
        line_list = [title] + items
        result.append(line_list)
    return result

def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"文件夹 {folder_path} 创建成功")
    else:
        print(f"文件夹 {folder_path} 已经存在")

def save_html_css_code(input_string, html_filename, css_filename):
    html_start = "HTML代码：\n\n```"
    html_end = "```\n"
    css_start = "CSS代码：\n\n```"
    css_end = "```\n"
    
    html_code = ""
    css_code = ""
    
    if html_start in input_string and html_end in input_string:
        html_code = input_string.split(html_start)[1].split(html_end)[0]
    
    if css_start in input_string and css_end in input_string:
        css_code = input_string.split(css_start)[1].split(css_end)[0]
    
    html_start = "```html"
    html_end = "```\n"
    css_start = "```css"
    css_end = "```\n"

    if html_start in input_string and html_end in input_string:
        html_code = input_string.split(html_start)[1].split(html_end)[0]

    if html_start in input_string and html_end in input_string:
        css_code = input_string.split(css_start)[1].split(css_end)[0]

    html_code = html_code.replace('```', '')
    css_code = css_code.replace('```', '')

    # 将HTML代码保存到文件
    with open(html_filename, "w") as html_file:
        html_file.write(html_code)

    # 将CSS代码保存到文件
    with open(css_filename, "w") as css_file:
        css_file.write(css_code)

    print("HTML和CSS代码已保存到文件！")
