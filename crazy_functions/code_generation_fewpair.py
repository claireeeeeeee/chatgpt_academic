from toolbox import CatchException, report_execption, write_results_to_file
from toolbox import update_ui, choose_appropriate_key, get_conf
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from .crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
from .crazy_utils import read_and_clean_pdf_text
from colorful import *
import re,os,requests,json
from request_llm.bridge_all import model_info

@CatchException
def code_generation_fewpair(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    history = []    # 清空历史，以免输入溢出
    jsonl_data = read_jsonl(txt)
    
    for entry in jsonl_data:
        task_id = entry["task_id"]
        prompt = entry["prompt"]
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
Requirement: prime_fib returns n-th number that is a Fibonacci number and it’s also prime.
Driver:
def is_prime(n: int):
    if n < 2:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True
fib_seq = [1, 1]
counter = n
while counter > 0:
    fib_seq.append(fib_seq[-1] + fib_seq[-2])
    if is_prime(fib_seq[-1]):
        counter -= 1
return fib_seq[-1]
<end>
Requirement: Create a function that takes integers, floats, or strings representing real numbers, and returns the larger variable in its given variable type. Return None if the values are equal. Note: If a real number is represented as a string, the floating point might be . or ,
Driver:
def compare_one(a, b):
    a_original = a
    b_original = b
    if isinstance(a, str):
        a = float(a.replace(’,’, ’.’))
    if isinstance(b, str):
        b = float(b.replace(’,’, ’.’))
    if a > b:
        return a_original
    elif b > a:
        return b_original
    else:
        return None
<end>
Requirement: Create a function which takes a string representing a file’s name, and returns ’Yes’ if the the file’s name is valid, and returns ’No’ otherwise. A file’s name is considered to be valid if and only if all the following conditions are met: - There should not be more than three digits (’0’-’9’) in the file’s name. - The file’s name contains exactly one dot ’.’ - The substring before the dot should not be empty, and it starts with a letter from the latin alphapet (’a’-’z’ and ’A’-’Z’). - The substring after the dot should be one of these: [’txt’, ’exe’, ’dll’]
Driver:
def file_name_check(file_name):
    if len(re.findall(r’\\d’, file_name)) > 3:
        return ’No’
    if len(re.findall(r’\\.’, file_name)) != 1:
        return ’No’
    if not re.match(r’[a-zA-Z]’, file_name.split(’.’)[0]):
        return ’No’
    if file_name.split(’.’)[1] not in [’txt’, ’exe’, ’dll’]:
        return ’No’
    return ’Yes’
<end>
Requirement: This function takes a list l and returns a list l’ such that l’ is identical to l in the odd indicies, while its values at the even indicies are equal to the values of the even indicies of l, but sorted.
Driver:
def sort_even(l: list):
    even_indices = [x for x in range(len(l)) if x % 2 == 0]
    sorted_even_indices = sorted(l[i] for i in even_indices)
    result = []
    for i in range(len(l)):
        if i % 2 == 0:
            result.append(sorted_even_indices.pop(0))
        else:
            result.append(l[i])
    return result
<end>
Requirement: {prompt}
Driver: 
"""
            code1_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say1, inputs_show_user=f'{task_id}Driver', 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt=""
            )
            history.append(i_say1)
            history.append(code1_say)
        except:
            raise RuntimeError(response.content.decode())
        save_history(task_id, 'Driver', code1_say)

        # 2
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
            i_say2 = f"""
Requirement: prime_fib returns n-th number that is a Fibonacci number and it’s also prime.
Driver:
def is_prime(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False 
    i=5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True
def prime_fib(n):
    if n <= 0:
        raise ValueError("n must be a positive integer.")
    fib = [0, 1]  # Initial Fibonacci sequence
    count = 0  # Count of prime Fibonacci numbers
    while count < n:
        # Generate the next Fibonacci number
        next_fib = fib[-1] + fib[-2]
        # Check if the new Fibonacci number is prime
        if is_prime(next_fib):
            count += 1
        # Append the new Fibonacci number to the list
        fib.append(next_fib)
    return fib[-2]  # The last prime Fibonacci number
Observer: 
After rigorous testing and inspection of the provided code, several issues have been identified that affect the correct functionality of the program: The function is_prime checks for prime numbers, but it returns True for 1 and this behavior deviates from the standard definition where 1 is not considered a prime number. In the function prime_fib, the starting Fibonacci sequence is [0, 1]. While technically correct, this could result in the function considering 0 as a potential prime Fibonacci number, which is incorrect. In the same function, the return statement returns the second-to-last element of the Fibonacci sequence (fib[-2]), which is not necessarily the nth prime Fibonacci number the function is supposed to return. The above-mentioned issues need to be addressed to ensure the correct execution of the program. After these issues are fixed, the code should correctly return the nth prime number in the Fibonacci sequence.
Modified Code:
def is_prime(n: int):
    if n < 2:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True
fib_seq = [1, 1]
counter = n
while counter > 0:
    fib_seq.append(fib_seq[-1] + fib_seq[-2])
    if is_prime(fib_seq[-1]):
        counter -= 1
return fib_seq[-1]
<end>
Requirement: Create a function that takes integers, floats, or strings representing real numbers, and returns the larger variable in its given variable type. Return None if the values are equal. Note: If a real number is represented as a string, the floating point might be . or ,
Driver:
def compare_one(a, b):
    if a == b:
        return None
    if isinstance(a, str):
        a = float(a.replace(’,’, ’.’))
    if isinstance(b, str):
        b = float(b.replace(’,’, ’.’))
    if isinstance(a, int) and isinstance(b, int):
        return max(a, b)
    else:
        return float(max(a, b))
Observer: 
The testing of the function ‘compare_one‘ in the provided code has revealed several significant issues: 1. The function does not appropriately handle the case where both inputs are equal. It returns ‘None‘ instead of returning the equal values. 2. The function doesn’t retain the original type of the inputs when they are both integers. It converts the maximum value to a float before returning, which could lead to incorrect type handling in further operations. 3. If the larger value was originally a string, the function returns a float or int rather than the original string. Fixing these issues should result in a function that correctly compares two values, converting strings to floats for comparison if necessary, and returning the larger value in its original form, or ‘None‘ if they are equal.
Modified Code:
def compare_one(a, b):
    a_original = a
    b_original = b
    if isinstance(a, str):
        a = float(a.replace(’,’, ’.’))
    if isinstance(b, str):
        b = float(b.replace(’,’, ’.’))
    if a > b:
        return a_original
    elif b > a:
        return b_original
    else:
        return None
<end>
Requirement: This function takes a list l and returns a list l’ such that l’ is identical to l in the odd indicies, while its values at the even indicies are equal to the values of the even indicies of l, but sorted.
Driver:
def file_name_check(file_name):
    if len(re.findall(r’\\d’, file_name)) > 3:
        return ’No’
    if len(re.findall(r’\\.’, file_name)) != 1:
        return ’No’
    if not re.match(r’[a-zA-Z]’, file_name.split(’.’)[0]):
        return ’No’
    if file_name.split(’.’)[1] not in [’txt’, ’exe’, ’dll’]:
        return ’No’
    return ’Yes’
Observer: 
Upon careful examination and testing of the ‘file_name_check‘ function, it was found to perform as expected. The function successfully verifies whether a file name meets certain criteria: - It contains no more than three digits. - It has exactly one period. - It starts with a letter before the period. - The extension after the period is one of ’txt’, ’exe’, or ’dll’. If the file name meets all of these conditions, the function returns ’Yes’. Otherwise, it returns ’No’. In conclusion, no issues were found during testing. The ‘file_name_check‘ function has passed all tests and is working as expected. Code Test Passed
Modified Code: ’file_name_check’ function passed all tests and is working as expected. So the code has no need to change.
def file_name_check(file_name):
    if len(re.findall(r’\\d’, file_name)) > 3:
        return ’No’
    if len(re.findall(r’\\.’, file_name)) != 1:
        return ’No’
    if not re.match(r’[a-zA-Z]’, file_name.split(’.’)[0]):
        return ’No’
    if file_name.split(’.’)[1] not in [’txt’, ’exe’, ’dll’]:
        return ’No’
    return ’Yes’
<end>
Requirement: This function takes a list l and returns a list l’ such that l’ is identical to l in the odd indicies, while its values at the even indicies are equal to the values of the even indicies of l, but sorted.
Driver:
def sort_even(l: list):
    even_indices = [l[i] for i in range(len(l)) if i % 2 == 0]
    sorted_even_indices = sorted(even_indices)
    l_prime = l.copy()
    for i in range(len(l_prime)):
        if i % 2 == 0:
            l_prime[i] = sorted_even_indices.pop(0)
    return l_prime
Observer: 
Upon careful examination and testing of the ‘sort_even‘ function in the provided code, the following issues were discovered: 1. The function sorts elements at even indices in the list, rather than sorting even numbers themselves. Addressing these issues will result in a function that correctly sorts all even numbers in the input list while maintaining the order and position of odd numbers.
Modified Code:
def sort_even(l: list):
    even_indices = [x for x in range(len(l)) if x % 2 == 0]
    sorted_even_indices = sorted(l[i] for i in even_indices)
    result = []
    for i in range(len(l)):
        if i % 2 == 0:
            result.append(sorted_even_indices.pop(0))
        else:
            result.append(l[i])
    return result
<end>
Requirement: {prompt}
Driver: {code1_say}
Observer: "
"""
            code2_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say2, inputs_show_user=f'{task_id}Observer', 
                llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
                sys_prompt=""
            )
            history.append(i_say2)
            history.append(code2_say)
        except:
            raise RuntimeError(response.content.decode())
        save_history(task_id, 'Observer', code2_say)

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
            i_say = f'Here is the requirement: {prompt} and the report from the developer: {code2_say}. Your objective is to extract the final version of the code for me, by reading the final report from the developer.  Please remember to remove the code used by the test, and only keep the Python functions needed in the requirements(mentioned in the function signature.). Please remember: provide only the final version of the code.'
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
    with open("/home/cli776/human-eval/new_pair/samples4.jsonl", "a") as file:
        file.write(json.dumps(data) + "\n")

def save_history(key1, key2, plan_say):
    filename="/home/cli776/human-eval/new_pair/recoding4.jsonl"
    key = str(key1) + str(key2)
    data = {
        key: plan_say
    }
    with open(filename, 'a') as f:
        f.write(json.dumps(data) + '\n')
