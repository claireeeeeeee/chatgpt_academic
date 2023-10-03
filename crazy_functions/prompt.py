for entry in jsonl_data:
    task_id = entry["task_id"]
    prompt = entry["prompt"]
    entry_point = entry["entry_point"]

    # project leader for developer
    # System input, list, used to enter prerequisite prompts for GPT, such as what if you are a translator...
    project_leader1_sys_prompt='Our development team consists of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Every role has distinct responsibilities that need to be diligently executed for the successful completion of the project. I would like for you to take on the role of a project leader, your goal being to devise a high-level plan to manage. When you, as a project leader, develop a plan, you need to break it down into easy-to-solvable subtasks for functional units and develop a high-level plan outlining the major steps to implement. This plan will be handed over to developers so the output I need is just the plan, no actual code or anything else.'
    plan_say = f"""
When you, as the project leader, generate a report to guide the development of programmers, you should make the requirements in the report as detailed as possible to let the programmer know what he needs to do. Your plan will guide programmers in developing Python functions (rather than delving into implementation details) based on the requirement. Given a requirement as follows: 
```{prompt}```
This requirement itself is the header of the program that the programmer needs to generate. What the programmer needs to do is to continue writing according to this requirement. It includes function signatures, NL descriptions, unit tests, and possibly import declarations. Here is what you need to include (not the format or steps you have to follow):
1. Import Statement:
You need to specify in the plan the packages that the developer-generated function needs to import, according to the import statement in the requirement.
2. Function Signature:
The function signature contains the function name and the type and number of parameters it accepts. The function signature specifies the name of the function that developers need to develop.The function name should be 
```{entry_point}```.
3. NL Description:
Use the NL description to determine and devise a high-level plan for the development of function. You should guide the developers based on this description, ensuring they understand the context and direction and pay attention to every detail of the requirements. Your role here is to provide oversight and guidance without immersing yourself in the intricacies of the code. 
4. Test cases:
Please do not provide test cases directly to developers. Regarding the testing requirements for developers, please let him generate test cases and test them himself.
"""
    # project leader for tester
    project_leader2_sys_prompt='Our development team consists of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Every role has distinct responsibilities that need to be diligently executed for the successful completion of the project. I would like for you to take on the role of a project leader, your goal being to devise a high-level plan to manage. When you, as a project leader, develop a plan, you need to break it down into easy-to-solvable subtasks for functional units and develop a high-level plan outlining the major steps to implement. This plan will be handed over to developers so the output I need is just the plan, no actual code or anything else.'
    tester_say = f"""
As a project leader, your goal is to devise a high-level plan to manage and direct the quality assurance testers. This plan is designed to verify that the function is robust, effective, and aligns with the requirements.
Given a requirement as follows: 
```{prompt}```
The requirement includes function signatures, NL descriptions, unit tests, and possibly import declarations. This is the plan given to the developer by the project leader: ```{plan_say}```
Please first let the tester check whether the code meets the plan given to him by the project leader. You instruct the quality assurance testers to test whether the developers use the function name and other requirements required in the requirements and guide quality assurance testers to utilize these unit tests in the requirements to validate the developed function. Their objective will be to ensure that the function works correctly as per the given specifications and the code from the developer is free of any bugs.
"""
    # developer
    dev_sys_prompt='Our development team consists of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Every role has distinct responsibilities that need to be diligently executed for the successful completion of the project. I would like for you to take on the role of a project leader, your goal being to devise a high-level plan to manage. When you, as a project leader, develop a plan, you need to break it down into easy-to-solvable subtasks for functional units and develop a high-level plan outlining the major steps to implement. This plan will be handed over to developers so the output I need is just the plan, no actual code or anything else.'
    code_say = f"""
The plan of Project Leader is 
```{plan_say}```.
This plan will outline:
1. The package/module you expect to use may contain.
2. The name of function you must follow. The function name should be ```{entry_point}```.
3. The type and number of parameters the function should accept.
4. The requirements in detail.
5. Test cases.
Your goal is to follow the requirements and write Python code to satisfy its requirements and generate your own test cases to test whether your function is accurate. It is crucial to follow the function names and packages required in it. You also need to check the code to ensure it meets all the criteria specified in the requirement. Make sure to look for edge cases and try to break the code to ensure it's robust. This ensures consistency and a unified direction in the development process. When you write code, ensure your Python code:
1. Is efficient in terms of algorithmic complexity.
2. Is readable, making it easier for other team members to understand and, if necessary, modify.
3. Adheres to best practices of Python, including PEP 8 style guidelines.
"""
    # tester
    tester_sys_prompt='There is a development team composed of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Each role has its unique responsibilities and requires collaboration for successful execution. When you test the code as a tester on the development team, I want you to make suggestions on the code and record test reports covering various aspects such as functionality, readability, maintainability, etc. Your role involves not just identifying and reporting errors but also ensuring that the code aligns perfectly with our standards and requirements. Note that you need to check not only these but also other criteria that you feel need to be tested.'
    tester_say="""
As part of our development team, we are entrusting you with the crucial responsibility of a quality assurance tester.  You hold the keys to the final gate through which our code must pass before being deployed. Below is a comprehensive guide on what your responsibilities entail. This is not necessarily a strict sequence, but it should cover all the key points:
1. Code Inspection and Compliance Check:
Provided Code and Requirements:
You will receive code as outlined in 
```{code_say}```
Once you receive the code from the developers, carefully go through it. Please verify that the function names specified in the development requirements are correctly used. Ensure that all required functionalities are fully implemented, per the development plan. Validate that all necessary packages are correctly imported as specified in the development plan.
2. Unit Test Execution and Validation:
Unit Test Execution: 
The tests are outlined in: 
```{test_say}```
Use the provided unit tests to validate the functionality of the code. Verify that the program works as expected and returns the correct results. Make sure your program handles unexpected input or error conditions gracefully. If there are any differences, please improve the code.
Exception Handling:
Test how the program handles unexpected input or error conditions. Make sure it fails gracefully without sudden crashes. At this step, you should generate your own test cases. The test cases provided in the requirements may not fully cover all situations. To ensure exception handling, you need to account for as many exception inputs as possible in advance. If there are any errors, please improve the code.
3. Detailed Analysis: Beyond just the functionality, assess the code for readability. A clear and understandable code will be crucial for future maintenance and updates.You need to gauge the maintainability of the code. Consider factors like modularity, scalability, and whether best coding practices have been followed.
4. Final result: Based on your report, improve the code and output the final version of the code that can finally pass the test.
"""
    # Extract
    sys_prompt='Only output the final version of the code, and only the code(no any descriptions).'
    output_say = f"""
Your objective is to extract the final version of the code for me, by reading the final report. Here is the final report from Quality assurance: 
```{code_say}``` 
Please remember to remove the code used by the test as well, and only keep the Python functions needed in the requirements(mentioned in the function signature.). Please remember to provide only the final version of the code.
"""

    # pair programming
    sys_prompt='Pair programming is a software development approach in which two programmers collaborate at the same computer. The driver writes code, while the observer analyses each line of code as it is entered. Now you need to act as a driver, write a program according to the requirement, and then hand it over to the observer for inspection.'
    plan_say = f"""
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

    sys_prompt='Pair programming is a software development approach in which two programmers collaborate at the same computer. The driver writes code, while the observer analyses each line of code as it is entered. Now you need to act as an observer, review each line of code. When you test the code, I want you to make suggestions on the code and record test reports covering various aspects such as functionality, readability, maintainability, etc. Your role involves not just identifying and reporting errors but also ensuring that the code aligns perfectly with our standards and requirements. Note that you need to check not only these but also other criteria that you feel need to be tested.'
    code_say = f"""
This is code written by the driver you are paired with:{plan_say}. And the requirements for it is as follows: {prompt}
Here is what you need to include (not the format or steps you have to follow): 
1. Code Inspection: Please check the code against the requirements received. Please make sure that the function name used in the code is the same as {entry_point} and that all required functions in the requirements are implemented. 
2. Unit Test Execution: Use the provided unit tests from the requirements to validate the functionality of the code. Verify that the program works as expected and returns the correct results. You should also generate your own test cases to additionally test functions. Make sure your program handles unexpected input or error conditions gracefully. If there are any differences, please modify them in the final code.
3. Detailed Analysis: Beyond just the functionality, assess the code for readability. A clear and understandable code will be crucial for future maintenance and updates.You need to gauge the maintainability of the code. Consider factors like modularity, scalability, and whether best coding practices have been followed. 
4. Code Improvements: Improve the code provided to you based on your analysis reports to provide a final version of the code.
"""
    # pair programming with few shots
    addition1 = f"""
Here is an example to illustrate this process you can follow: 
EXAMPLE PROBLEM: \n\ndef subarray_sum_to_k(l: list, k: int):\n    \"\"\"\n    subarray_sum_to_k takes a list of integers and an integer k as its parameters.\n    it returns all distinct subarrays whose elements sum to k.\n    A subarray is defined as a contiguous part of an array.\n     >>> subarray_sum_to_k([1, 2, 3, 4, 5], 9)\n    [[4, 5], [2, 3, 4]]\n    >>> subarray_sum_to_k([1, 3, 2, 1, 4, 1, 3], 6)\n    [[1, 3, 2], [3, 2, 1], [1, 4, 1]]\n    >>> subarray_sum_to_k([1, 2], 5)\n    []\n    \"\"\"\n\n
ITS EXAMPLE ANSWER FOR THE PROBLEM: \n\ndef subarray_sum_to_k(l: list, k: int):\n    result = []\n    for i in range(len(l)):\n        for j in range(i, len(l)):\n            if sum(l[i:j+1]) == k:\n                result.append(l[i:j+1])\n    return result\nprint(subarray_sum_to_k([1, 2, 3, 4, 5], 9))  # Output should be [[4, 5], [2, 3, 4]]\nprint(subarray_sum_to_k([1, 3, 2, 1, 4, 1, 3], 6))  # Output should be [[1, 2, 3], [3, 2, 1], [2, 1, 3], [1, 3, 2], [1, 4, 1]]\nprint(subarray_sum_to_k([1, 2], 5))  # Output should be []\nprint(subarray_sum_to_k([], 5))  # Edge case: Output should be []\nprint(subarray_sum_to_k([5], 5))\n\n
"""