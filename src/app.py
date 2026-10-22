import json
import streamlit as st
import utils

st.title('OFFLINE CHATBOT')
chatfile = 'chat_history.json'
summary_file = 'chat_summary.txt'

welcome_msg = {'role': 'ai', 'content': 'How Can I Help You ?'}
model = 'qwen2.5-coder:7b'


def load_history():
    with open(chatfile, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def save_history(msgs):
    with open(chatfile, 'w', encoding='utf-8') as f:
        json.dump(msgs, f, ensure_ascii=False, indent=2)


def clear_history():
    with open(chatfile, 'w', encoding='utf-8') as f:
        f.close()
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.close()


if 'messages' not in st.session_state:
    st.session_state['messages'] = [welcome_msg.copy()]

if 'stop' not in st.session_state:
    st.session_state['stop'] = False


col1, col2, col3 = st.columns(3)

with col1:
    if st.button('[-] stop'):
        st.session_state['stop'] = True
        st.warning('model stopped')

with col2:
    if st.button('[+] come'):
        st.session_state['stop'] = False
        st.warning('model is active')
        st.rerun()

with col3:
    if st.button('Cleaner'):
        st.session_state['messages'] = [welcome_msg.copy()]
        st.session_state['stop'] = False
        clear_history()
        st.rerun()


for msg in st.session_state['messages']:
    st.chat_message(msg['role']).write(msg['content'])
prompt = st.chat_input('Ask Your Question:')

if prompt:
    if st.session_state['stop']:
        st.error('stopping...............')

    else:
        st.chat_message('user').write(prompt)
        st.session_state['messages'].append({'role': 'user', 'content': prompt})

        with st.spinner('Answer...'):
            response = utils.call_ollama_model(prompt, model)
        st.chat_message('ai').write(response)
        st.session_state['messages'].append({'role': 'ai', 'content': response})
        save_history(st.session_state['messages'])


if st.button('summary_msgs'):
    if len(st.session_state['messages']) > 1:
        summary = "Transcript of the conversation:\n"
        for msg in st.session_state['messages']:
            summary += f"{msg['role']}: {msg['content']}\n"

        with st.spinner('Summarizing...'):
            summary = utils.call_ollama_model(summary, model)

        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)

        st.success('Summary saved')
        st.write(summary)
    else:
        st.warning('Nothing for summary...')
