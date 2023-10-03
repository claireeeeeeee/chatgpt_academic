from toolbox import CatchException, update_ui
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from .crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
import re
import os

@CatchException
def code_generation_en(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
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
    
    i_say = f'Separate the tasks of the {txt} website by function in the format 1.a, 1.b, 2.a, 2.b, 3.a, 3.b...\n\n'
    inputs_show_user = f'Here is the possible functions of your website:'
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=i_say, inputs_show_user=inputs_show_user, 
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
        sys_prompt="Separate the tasks of the website by function in the format 1.a, 1.b, 2.a, 2.b, 3.a, 3.b...\n\n"
    )

    # history.append(gpt_say)
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新

    i_say = f'To reclassify these functions on different web pages, all the above functions need to be included, that is, to reclassify the functions by page, the format must be the same, here is one example: 1. Home page: login function, sign in function... \n\n'
    inputs_show_user = f'Reclassify them:'
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=i_say, inputs_show_user=inputs_show_user, 
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
        sys_prompt="To reclassify these functions on different web pages, all the above functions need to be included, that is, to reclassify the functions by page, the format must be the same, here is one example: 1. Home page: login function, sign in function...\n\n"
    )
    
    history.append(gpt_say)
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新

    function_list = extract_function_descriptions(history[0])
    
    for function in function_list:
        i_say = f'The website will have {function[0]} page html, css code, containing function {function[1:]} in the format: HTML code: ..., CSS code: ...Note: Whenever I ask you to write code, I want you to write code in a way that separates functions with side-effects, such as file system, database, or network access, from the functions without side- effects.\n\n'
        inputs_show_user = f'{function[0]} Page:'
        gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
            inputs=i_say, inputs_show_user=inputs_show_user, 
            llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
            sys_prompt="The website will have {function[0]} page html, css code, containing function {function[1:]} in the format: HTML code: ..., CSS code: ...Note: Whenever I ask you to write code, I want you to write code in a way that separates functions with side-effects, such as file system, database, or network access, from the functions without side- effects.\n\n"
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


 
def code_generation_eng(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
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
    import re

    i_say = f"""Separate the tasks of building the {txt} website by function, then reclassify these functions on different web pages, that is, to reclassify the functions by page, the format must be the same as my example, here is my example: 
1. Home Page:
Login Function: Allow users to log in to their accounts.
Sign Up Function: Provide a registration form for new users to create an account.
Product Display: Display featured products or product categories.

2. Product Listing Page:
Product Listing: Show a list of products with their details, such as name, price, and image.
Sorting and Filtering: Allow users to sort and filter products based on different criteria (e.g., price, popularity, category).

3. Product Detail Page:
Product Information: Display detailed information about a specific product, including description, specifications, and reviews.
Add to Cart: Enable users to add the product to their shopping cart.

4. Shopping Cart Page:
Cart Summary: Show a summary of the products in the user's shopping cart.
Update Quantity: Allow users to update the quantity of each item in the cart.
Remove Items: Enable users to remove items from the cart.
Proceed to Checkout: Redirect users to the checkout page to complete their purchase.

5. Checkout Page:
Shipping Address: Collect the user's shipping address information.
Payment Options: Provide different payment methods for users to choose from.
Order Summary: Display a summary of the order before finalizing the purchase.
Place Order: Allow users to confirm and place the order.

6. User Profile Page:
User Information: Display and allow users to edit their profile details, such as name, email, and password.
Order History: Show a list of the user's previous orders and their details.

7. Admin Dashboard:
Product Management: Enable administrators to add, edit, or remove products from the inventory.
Order Management: Allow administrators to view and manage orders placed by customers.
User Management: Provide functionality to manage user accounts, such as creating or deleting accounts and changing user permissions.\n\n"""
    inputs_show_user = f'Here is the possible functions of your website:'
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=i_say, inputs_show_user=inputs_show_user, 
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
        sys_prompt="Separate the tasks of the website by function in the format.\n\n"
    )

    # history.append(gpt_say)
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新
    function_list = extract_function_descriptions(gpt_say)
    #function_list = extract_function_descriptions(history[0])
    
    for function in function_list:
        i_say = f'The website will have {function[0]} page html, css code, containing function {function[1:]} in the format: HTML code: ..., CSS code: ...Note: Whenever I ask you to write code, I want you to write code in a way that separates functions with side-effects, such as file system, database, or network access, from the functions without side- effects.\n\n'
        inputs_show_user = f'{function[0]} Page:'
        gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
            inputs=i_say, inputs_show_user=inputs_show_user, 
            llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
            sys_prompt="The website will have {function[0]} page html, css code, containing function {function[1:]} in the format: HTML code: ..., CSS code: ...Note: Whenever I ask you to write code, I want you to write code in a way that separates functions with side-effects, such as file system, database, or network access, from the functions without side- effects.\n\n"
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
    # 使用换行符和冒号分割字符串为子段落
    sections = string.split("\n\n")

    # 初始化输出列表
    output_list = []

    # 遍历子段落，提取关键信息并添加到输出列表
    for section in sections:
        # 分割子段落的第一行为页面名称和说明
        lines = section.split(":\n")
        page_name = re.sub(r'^\d+\.\s', '', lines[0])  # 去除页面名称前的数字
        page_info = lines[1]
        # 提取页面功能并添加到输出列表
        page_functions = page_info.split("\n")
        page_functions.pop(0)  # 移除页面说明
        page_functions = [page_name] + page_functions  # 添加页面名称到列表开头
        output_list.append(page_functions)
    return output_list

def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder {folder_path} created successfully")
    else:
        print(f"Folder {folder_path} already exists")

def save_html_css_code(input_string, html_filename, css_filename):
    html_start = "HTML code：\n\n```"
    html_end = "```\n"
    css_start = "CSS code：\n\n```"
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

    print("HTML and CSS code saved to file!")
