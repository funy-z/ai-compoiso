
from fastapi import Body, APIRouter
from typing import Annotated

from fastapi.responses import StreamingResponse
from ai_services.custom_types import AIDocBodyType, OpTypeEnum, OpSubTypeEnum
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama

from ai_services.utils import stream_response, astream_response

router = APIRouter(
    prefix="/ai_docs",
    tags=["ai_docs"],
    responses={404: {"description": "Not found"}}
)

system_prompt_text = "你是一位著名的作家，名字叫做'费小V'。如果问你'你是谁',请不要回答任何其他内容，直接回答'费小V'即可。现在的任务是帮助用户将文章的内容进行处理，续写文章、缩短文章篇幅或者扩充文章篇幅。"
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt_text),
    ("human", "请对如下内容进行{action}: '{content}'")
])

prompt_free = ChatPromptTemplate.from_messages([
    ("system", system_prompt_text),
    ("human", '根据用户的问题，对用户的内容进行处理。\
     问题="{question}" \
     内容="{content}"')
])


@router.post("/generate")
async def get_ai_docs(params: Annotated[AIDocBodyType, ...] = Body()):
    """
      1. 润色
        1.1 口语化
        1.2 更活泼
        1.3 更正式
      2. 续写
      3. 缩短篇幅
      4. 扩充篇幅
    """
    content = params.content
    question = params.question
    op_type = params.op_type
    op_sub_type = params.op_sub_type

    exec_prompt = None
    action = ""
    if question:
        # 1. 处理自由问题
        exec_prompt = prompt_free
    else:
        # 2. 处理定制问题
        action_dict = {
            "polish": "润色",
            "continue_writing": "续写",
            "shorten": "缩短篇幅",
            "expand": "扩充篇幅",
        }
        sub_action_dict = {
            "colloquial": "更口语化",
            "lively": "更活泼",
            "formal": "更正式",
        }

        action = action_dict[op_type]
        if op_type == OpTypeEnum.polish:
            action = f"{action},让内容{
                sub_action_dict[op_sub_type or OpSubTypeEnum.colloquial.value]}"
        exec_prompt = prompt

    # prompt_text = exec_prompt.invoke({
    #     "question": question,
    #     "action": action,
    #     "content": content,
    # })
    llm = ChatOllama(model="qwen2")
    chain = exec_prompt | llm
    # 1. invoke()方法
    # result = chain.invoke({
    #     "question": question,
    #     "action": action,
    #     "content": content,
    # })
    # print(result.content)
    # return {"data": result.content}

    # 2. ainvoke()方法
    # result = await chain.ainvoke({
    #     "question": question,
    #     "action": action,
    #     "content": content,
    # })
    # print(result.content)
    # return {"data": result.content}

    # 3. stream()方法
    # result = chain.stream({
    #     "question": question,
    #     "action": action,
    #     "content": content,
    # })
    # return StreamingResponse(stream_response(result))

    # 4. astream()方法
    result = chain.astream({
        "question": question,
        "action": action,
        "content": content,
    })
    return StreamingResponse(astream_response(result))