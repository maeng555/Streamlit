import json  # JSON 파싱
import boto3
import Streamlit.streamlit as st

bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name="ap-northeast-2")

# 웹 앱 제목 설정
st.title("Chatbot powered by Bedrock")

# 세션 상태에 메시지 없으면 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 세션 상태에 저장된 메시지 순회하며 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):  # 채팅 메시지 버블 생성
        st.markdown(message["content"])  # 메시지 내용 마크다운으로 렌더링

def get_response(prompt):
    try:
        body = json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt}],
                    }
                ],
            }
        )

        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body=body,
        )
        response_body = json.loads(response.get("body").read())
        output_text = response_body["content"][0]["text"]
        return output_text
    except Exception as e:
        print(e)

# 사용자로부터 입력 받음
if prompt := st.chat_input("Message Bedrock..."):
    # 사용자 메시지를 세션 상태에 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):  # 사용자 메시지 채팅 메시지 버블 생성
        st.markdown(prompt)  # 사용자 메시지 표시
    
    # 보조 응답을 세션 상태에 추가
    output_text = get_response(prompt)
    st.session_state.messages.append({"role": "assistant", "content": output_text}) # 보조 메시지 채팅 메시지 버블 생성
    with st.chat_message("assistant"):
        st.markdown(output_text)