import streamlit as st
import requests
import json
import time

# Streamlit의 세션 상태를 사용하여 대화 내용을 저장
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {'role': 'user', 'content': '당신은 초등학교 과학 교사입니다. 당신은 학생과 토의중입니다. 대화 내용은 오로지 생물과 관련되어야 합니다. 다른 대화 내용은 거부해야합니다. 학생은 다음의 내용을 배웠습니다. 실체 현미경과 광학 현미경의 구조와 사용 방법, 목적. 해캄, 짚신벌레 등의 원생생물을 현미경으로 관찰하고 구조와 특징, 생김새, 사는 곳. 세균의 크기, 생김새, 모양, 번식 방법, 사는 곳, 역할, 좋은 영향, 나쁜 영향. 균류, 원생생물, 세균의 좋은 점, 나쁜 점, 활용되는 분야. 균류, 원생생물, 세균이 활용되는 첨단과학기술 사례. 이 내용들을 이용해서 학생에게 일상 생활 속 문제를 어떻게 해결할 수 있는지를 토의할 수 있는 질문을 하고 학생이 대답을 할 수 있도록 이끌어내시오. 응답은 세 문장 이하로 생성하시오. 응답의 끝에는 질문을 추가해서 대화를 이어가시오. 해당 내용과 관련없는 내용이 입력되면 답변을 거부하고 원래 주제로 토의할 수 있도록 이끌어주세요'}, {'role': 'assistant', 'content':'네'}, {'role': 'assistant', 'content':'어떤 주제로 이야기를 나눠볼까요?'}]

if "input_message" not in st.session_state:
    st.session_state.input_message = ""

if "copied_chat_history" not in st.session_state:
    st.session_state.copied_chat_history = ""

class CompletionExecutor:
    def __init__(self, host, api_key, api_key_primary_val, request_id):
        self._host = host
        self._api_key = api_key
        self._api_key_primary_val = api_key_primary_val
        self._request_id = request_id

    def execute(self, completion_request):
        headers = {
            'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'text/event-stream'
        }

        with requests.post(self._host + '/testapp/v1/chat-completions/HCX-003',
                           headers=headers, json=completion_request, stream=True) as r:
            response_data = r.content.decode('utf-8')

            # 데이터를 줄 단위로 나누기
            lines = response_data.split("\n")

            # 필요한 JSON 데이터만 추출
            json_data = None
            for i, line in enumerate(lines):
                if line.startswith("event:result"):
                    next_line = lines[i + 1]  # "data:" 이후의 문자열 추출
                    json_data = next_line[5:]
                    break

            # JSON 데이터로 변환
            if json_data:
                try:
                    chat_data = json.loads(json_data)
                    # JSON 데이터 확인
                    print(json.dumps(chat_data, indent=2, ensure_ascii=False))

                    # 챗봇의 응답을 대화 기록에 추가
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": chat_data["message"]["content"]})

                except json.JSONDecodeError as e:
                    print("JSONDecodeError:", e)
            else:
                print("JSON 데이터가 없습니다.")


# Initialize the chat bot
completion_executor = CompletionExecutor(
    host='https://clovastudio.stream.ntruss.com',
    api_key='NTA0MjU2MWZlZTcxNDJiY6Yo7+BLuaAQ2B5+PgEazGquXEqiIf8NRhOG34cVQNdq',
    api_key_primary_val='DilhGClorcZK5OTo1QgdfoDQnBNOkNaNksvlAVFE',
    request_id='d1950869-54c9-4bb8-988d-6967d113e03f'
)

# Set the title of the Streamlit app
st.markdown('<h1 class="title">다양한 생물을 이용한 문제해결 아이디어 만들어내기</h1>', unsafe_allow_html=True)

# Add CSS to style the button and align items
st.markdown("""
    <style>
    .title {
        font-size: 28px !important; /* 제목 글씨 크기를 조정 */
        font-weight: bold;
    }
    .input-container {
        display: flex;
        align-items: center;
        width: 100% !important;
        height: 38px;
    }
    .stTextInput > div > div > input {
        height: 38px;
        width: 100% !important; /* 텍스트 입력 필드의 너비를 100%로 설정 */
    }
    .stButton button {
        height: 65px !important;
        width: 100px;
        padding: 0px 10px !important;
    }
    .stForm button {
        height: 38px !important;
        width: 100px;
        padding: 0px 10px !important;
    }

    .copy-button {
        height: 100px;
        width: 240px;
        padding: 0px 10px;
        font-size: 32px;
    }
    </style>
""", unsafe_allow_html=True)

# 콜백 함수 정의
def send_message():
    if st.session_state.input_message:
        st.session_state.chat_history.append({"role": "user", "content": st.session_state.input_message})

        completion_request = {
            'messages': st.session_state.chat_history,
            'topP': 0.8,
            'topK': 0,
            'maxTokens': 256,
            'temperature': 0.7,
            'repeatPenalty': 1.2,
            'stopBefore': [],
            'includeAiFilters': True,
            'seed': 0
        }

        completion_executor.execute(completion_request)
        st.session_state.input_message = ""  # 입력 필드를 초기화합니다.

def copy_chat_history():
    # 두 번째 메시지를 제외하고 대화 내용을 복사합니다.
    chat_history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.chat_history[2:]])
    st.session_state.copied_chat_history = chat_history_text

# Display the chat history (excluding the first initial instruction)
for message in st.session_state.chat_history[2:]:
    role = "User" if message["role"] == "user" else "Chatbot"
    if role == "User":
        st.markdown(f'''
            <div style="
                background-color: #ADD8E6; 
                text-align: right; 
                padding: 10px; 
                border-radius: 5px; 
                margin: 10px 0;
                max-width: 80%;
                float: right;
                clear: both;">
                {message["content"]}
            </div>''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
            <div style="
                background-color: #90EE90; 
                text-align: left; 
                padding: 10px; 
                border-radius: 5px; 
                margin: 10px 0;
                max-width: 80%;
                float: left;
                clear: both;">
                {message["content"]}
            </div>''', unsafe_allow_html=True)

# Create a form for user input and buttons
with st.form(key="input_form", clear_on_submit=True):
    cols = st.columns([4, 1, 1])  # 비율을 설정하여 열을 나눔
    with cols[0]:
        user_message = st.text_input("다양한 생물과 우리 생활에 관련된 이야기를 나눠보세요:", key="input_message", placeholder="")
    with cols[1]:
        submit_button = st.form_submit_button(label="입력", on_click=send_message)
    with cols[2]:
        copy_button = st.form_submit_button(label="대화내용 정리", on_click=copy_chat_history)

# Display the copied chat history in a textbox at the bottom
if st.session_state.copied_chat_history:
    st.markdown("<h3>대화 내용 정리</h3>", unsafe_allow_html=True)
    st.text_area("", value=st.session_state.copied_chat_history, height=200, key="copied_chat_history_text_area")

    chat_history = st.session_state.copied_chat_history.replace("\n", "\\n").replace('"', '\\"')
    st.components.v1.html(f"""
        <textarea id="copied_chat_history_text_area" style="display:none;">{chat_history}</textarea>
        <button onclick="copyToClipboard()" class="copy-button">클립보드로 복사</button>
        <script>
        function copyToClipboard() {{
            var text = document.getElementById('copied_chat_history_text_area').value.replace(/\\\\n/g, '\\n');
            navigator.clipboard.writeText(text).then(function() {{
                alert('클립보드로 복사되었습니다!');
            }}, function(err) {{
                console.error('복사 실패: ', err);
            }});
        }}
        </script>

        <style>
        .copy-button {{
            height: 100%; /* 20% 높이 증가 */
            width: 100%; /* 20% 너비 증가 */
            font-size: 30px; /* 20% 텍스트 크기 증가 */
        }}
        </style>
    """, height=100)
