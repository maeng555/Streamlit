import json
import boto3

# Bedrock runtime
bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
#모델을 호출하기위한 클라이언트 설정 

#api 응답을 생성하는 역할  에러 400코드 ,성공 200 반환 응답본문은 json형식으로 변환 
#ensure_ascii 은 한글이 깨지지않게 false 
def done(err, res):
    if err:
        print(f"!!!!!!!!!!!!{err}")

    return {
        "statusCode": "400" if err else "200",
        # 한글 깨짐을 방지하기 위해 ensure_ascii 옵션 추가
        "body": json.dumps(res, ensure_ascii=False),
        "headers": {"Content-Type": "application/json"},
    }

#람다함수 진입점 api gateway 를 통해 http용청을 처리 (event)
def lambda_handler(event, context):
    print(f">>>>>>>>>>>> ${event}")

    # Bedrock version check
    boto3_version = boto3.__version__
    print(f">>>>>>>>>>>> boto3 version: {boto3_version}")
    #get요청 처리
    try:
        if event["requestContext"]["http"]["method"] == "GET":
            return done(None, "'/' path로 GET 요청을 하셨군요.")
            # post 요청 및 프로픔프 파싱 
        request_body = json.loads(event.get("body"))
        prompt = (
            request_body.get("prompt")
            if "prompt" in request_body
            else "Amazon Bedrock이 뭐야? 3문장 이내로 답변해"
        )
        print(f">>>>>>>>>>>> prompt: {prompt}")

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

        # buffered
        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body=body,
        )
        response_body = json.loads(response.get("body").read())

        input_tokens = response_body["usage"]["input_tokens"]
        output_tokens = response_body["usage"]["output_tokens"]
        output_text = response_body["content"][0]["text"]
        print(f">>>>>>>>>>>> model output: {output_text}")

        print("Invocation details:")
        print(f"- The input length is {input_tokens} tokens.")
        print(f"- The output length is {output_tokens} tokens.")

        return done(None, {"output": output_text})
    except Exception as e:
        return done(e, "Error occured!")