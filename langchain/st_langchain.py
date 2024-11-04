import boto3
import streamlit as st
# For Claude 3, use BedrockChat instead of Bedrock
from langchain_aws import ChatBedrock
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

# Bedrock 클라이언트 설정
bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name="ap-northeast-2")

# Claude 3.5 파라미터 설정
model_kwargs =  { 
    "max_tokens": 1000,
    "temperature": 0.01,
    "top_p": 0.01,
}

# Bedrock LLM 설정
llm = ChatBedrock(
    client=bedrock_runtime,
    model_id="anthropic.claude-3-haiku-20240307-v1:0",
    model_kwargs=model_kwargs,
    streaming=True
)

# Streamlit 앱 설정
st.title("Chatbot powered by Bedrock and LangChain")

# Streamlit 채팅 메시지 히스토리 설정
message_history = StreamlitChatMessageHistory(key="chat_messages")

# 프롬프트 템플릿 설정
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an AI chatbot having a conversation with a human."),
        MessagesPlaceholder(variable_name="message_history"),
        ("human", "{query}"),
    ]
)

# 대화 체인 설정
chain_with_history = RunnableWithMessageHistory(
    prompt | llm,
    lambda session_id: message_history,  # 항상 이전 대화를 리턴
    input_messages_key="query",
    history_messages_key="message_history",
)

# 채팅 인터페이스
for msg in message_history.messages:
    st.chat_message(msg.type).write(msg.content)

# 사용자 입력 처리
if query := st.chat_input("Message Bedrock..."):
    st.chat_message("human").write(query)

    # chain이 호출되면 새 메시지가 자동으로 StreamlitChatMessageHistory에 저장됨
    config = {"configurable": {"session_id": "any"}}
    response_stream = chain_with_history.stream({"query": query},config=config)
    st.chat_message("ai").write_stream(response_stream)

    #LangChain 기반 관리:

#이 코드에서는 LangChain의 RunnableWithMessageHistory, StreamlitChatMessageHistory, ChatPromptTemplate 등의 객체를 활용하여 대화 흐름과 히스토리를 효율적으로 관리합니다. 이전 코드에서는 st.session_state와 수동 관리로 대화 히스토리를 다뤘지만, LangChain을 사용하면 세션을 더욱 직관적으로 관리할 수 있습니다.
#프롬프트 템플릿 활용:

#LangChain의 ChatPromptTemplate와 MessagesPlaceholder를 사용하여 프롬프트 내에서 대화 히스토리를 자동으로 불러옵니다. 기존 코드에 비해 프롬프트 설정이 유연해지고, 새로운 대화 패턴에 쉽게 맞출 수 있습니다.
#실시간 스트리밍 처리:

#이 코드에서는 write_stream을 사용해 실시간으로 Claude의 응답을 표시할 수 있어 사용자 경험이 더 자연스러워집니다.
#모듈화 및 유연성 향상:

#LangChain의 구성 요소를 사용해 코드가 모듈화되었고, 다양한 대화 흐름을 쉽게 변경할 수 있게 되었습니다.