from toolbox import CatchException, report_execption, write_results_to_file
from toolbox import update_ui
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from .crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
from colorful import *
import re
import os

@CatchException
def code_generation_multi1(txt, llm_kwargs, plugin_kwargs, chatbot, history, sys_prompt, web_port):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数，如温度和top_p等，一般原样传递下去就行
    plugin_kwargs   插件模型的参数，暂时没有用武之地
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    web_port        当前软件运行的端口号
    """
        # 基本信息：功能、贡献者
    chatbot.append([
        "函数插件功能？",
        "批量翻译PDF文档。函数插件贡献者: Binary-Husky"])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # 清空历史，以免输入溢出
    history = []

    i_say = f"""
Separate the tasks of building the {txt} website by function, then reclassify these functions on different web pages, that is, to reclassify the functions by page, the format must be the same as my example, here is my example: 
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
        inputs=i_say,
        inputs_show_user=inputs_show_user, 
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
        sys_prompt="Separate the tasks of the website by function in the format.\n\n"
    )

    print('gpt_say',gpt_say)
    function_list = extract_function_descriptions(gpt_say)

    # 多线，翻译
    gpt_response_collection = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
        inputs_array=[
                f'The website will have {function[0]} page html, css code, containing function {function[1:]} in the format: HTML code: ..., CSS code: ...Note: Whenever I ask you to write code, I want you to write code in a way that separates functions with side-effects, such as file system, database, or network access, from the functions without side- effects.\n\n' for function in function_list],
            inputs_show_user_array=[f'{function[0]} Page: ' for function in function_list],
            llm_kwargs=llm_kwargs,
            chatbot=chatbot,
            history_array=[],
            sys_prompt_array=[
                'You, as a programmer, are responsible for writing the sample website as required. Feel free to assume functions not mentioned, as long as your assumptions make the site complete. Note: Whenever I ask you to write code, I want you to write code in a way that separates functions with side-effects, such as file system, database, or network access, from the functions without side- effects.\n\n' for function in function_list],
            # max_workers=5  # OpenAI所允许的最大并行过载
    )
    
    print(gpt_response_collection)

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