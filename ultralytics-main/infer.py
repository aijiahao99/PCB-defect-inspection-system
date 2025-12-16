# API调用接口文件
import ast

from openai import OpenAI
import os
# token
content = 'This is the result after the PCB inspection. Please analyze the result and provide suggestions for improvement. '

# 初始化OpenAI客户端
client = OpenAI(
    # 如果没有配置环境变量，请用阿里云百炼API Key替换：api_key="sk-xxx"
    api_key="sk-a7119b13a51241db98a387ccf4f46d6a",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 聊天机器人功能
def call_aliyun_model(question = "",model = ''):
    try:
        # 初始化消息
        messages = [{"role": "user", "content": question}]
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            # 通过 extra_body 设置 enable_thinking 开启思考模式
            extra_body={"enable_thinking": False},
            stream=True,
            stream_options={
                "include_usage": True
            },
        )

        #reasoning_content = ""  # 完整思考过程
        answer_content = ""  # 完整回复
        is_answering = False  # 是否进入回复阶段
        #print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")

        for chunk in completion:
            if not chunk.choices:
                #print("\n" + "=" * 20 + "Token 消耗" + "=" * 20 + "\n")
                #print(chunk.usage)
                continue

            delta = chunk.choices[0].delta
            '''
            # 只收集思考内容
            if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
                if not is_answering:
                    print(delta.reasoning_content, end="", flush=True)
                reasoning_content += delta.reasoning_content
            '''

            # 收到content，开始进行回复
            if hasattr(delta, "content") and delta.content:
                if not is_answering:
                    #print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                    is_answering = True
                #print(delta.content, end="", flush=True)
                answer_content += delta.content
        return answer_content
    except Exception as e:
        print("Error:", e)
# 分析PCB结果功能
def call_aliyun_api_assessment(model = '',set = None):
    global content
    set = ast.literal_eval(set)
    result = [["Detect item", "Quantities", "Result"],
              ["Missing hole", "0", "Pass"],
              ["Mouse bite", "0", "Pass"],
              ["Open circuit", "0", "Pass"],
              ["Short", "0", "Pass"],
              ["Spur", "0", "Pass"],
              ["Spurious copper", "0", "Pass"]]
    print(set)
    i = 0
    for _ in range(1,len(result)):
        if eval(set[i]) > 0:
            result[_][2] = 'Fail'
        result[_][1] = set[i]
        i += 1
    content += str(result)
    # 初始化消息
    messages = [{"role": "user", "content": content}]
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            # 通过 extra_body 设置 enable_thinking 开启思考模式
            extra_body={"enable_thinking": False},
            stream=True,
            stream_options={
                "include_usage": True
            },
        )

        answer_content = ""  # 完整回复
        is_answering = False  # 是否进入回复阶段

        for chunk in completion:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            # 收到content，开始进行回复
            if hasattr(delta, "content") and delta.content:
                if not is_answering:
                    is_answering = True
                answer_content += delta.content
        return answer_content
    except Exception as e:
        print("Error:", e)

