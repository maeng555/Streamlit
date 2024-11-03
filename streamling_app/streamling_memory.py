import json  # JSON 파싱
import boto3
import streamlit as st

bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name="ap-northeast-2")

# 웹 앱 제목 설정
st.title("Chatbot powered by Bedrock")

# 세션 상태에 메시지 없으면 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 세션 상태에 저장된 메시지 순회하며 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):  # 채팅 메시지 버블 생성 role이 사용자인지 ai인지 나타냄
        st.markdown(message["content"])  # 메시지 내용 마크다운으로 렌더링 각각 말풍선 맞게 랜더링


def chunk_handler(chunk):
    #  API가 서로 다른 타입을 리턴
    # print(f"\n\n!!!\n{chunk}")
    text = ""
    chunk_type = chunk.get("type")
    # print(f"\n\nchunk type: {chunk_type}")
    if chunk_type == "message_start":
        # 첫 번째 청크는 message role에 대한 정보를 포함
        role = chunk["message"]["role"]
        text = ""
    elif chunk_type == "content_block_start":
        # 응답 텍스트 시작
        text = chunk["content_block"]["text"]
    elif chunk_type == "content_block_delta":
        # 스트리밍 중인 응답 텍스트의 일부
        text = chunk["delta"]["text"]
    elif chunk_type == "message_delta":
        # 응답이 중단되거나 완료된 이유를 포함
        stop_reason = chunk["delta"]["stop_reason"]
        text = ""
    elif chunk_type == "message_stop":
        # 요청에 대한 메트릭을 포함
        metric = chunk["amazon-bedrock-invocationMetrics"]
        inputTokenCount = metric["inputTokenCount"]
        outputTokenCount = metric["outputTokenCount"]
        firstByteLatency = metric["firstByteLatency"]
        invocationLatency = metric["invocationLatency"]
        text = ""

    print(text, end="")
    return text


def get_streaming_response():
    try:
        history = []
        for msg in st.session_state.messages:
            history.append(
                {
                    "role": msg["role"],
                    "content": [{"type": "text", "text": msg["content"]}]
                }
            )
            
        body = json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": history,
            }
        )
    
        # stream
        response = bedrock_runtime.invoke_model_with_response_stream(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            # modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
            body=body,
        )
        stream = response.get("body")

        if stream:
            for event in stream:  # 스트림에서 반환된 각 이벤트 처리
                chunk = event.get("chunk")
                if chunk:
                    chunk_json = json.loads(chunk.get("bytes").decode())
                    yield chunk_handler(chunk_json)
    except Exception as e:
        print(e)


# 사용자로부터 입력 받음
if prompt := st.chat_input("Message Bedrock..."):
    # 사용자 메시지 세션 상태에 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):  # 사용자 메시지 채팅 메시지 버블 생성
        st.markdown(prompt)  # 사용자 메시지 표시
    
    with st.chat_message("assistant"):  # 보조 메시지 채팅 메시지 버블 생성
        model_output = st.write_stream(get_streaming_response)

    # 보조 응답 세션 상태에 추가
    st.session_state.messages.append({"role": "assistant", "content": model_output})