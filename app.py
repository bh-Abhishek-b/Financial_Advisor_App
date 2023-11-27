import streamlit as st
import openai
import os
import json

openai_api_key =st.secrets['OPENAI_API_KEY']


def new_session():
    st.session_state['text']=''
    file = 'database.json'
    with open (file,'w') as f:
        f.seek(0)
        f.truncate()
def clear_history():
    file = 'database.json'
    with open (file,'w') as f:
        f.seek(0)
        f.truncate()


if 'chat_history' not in st.session_state:                                                                                  # Creating a list -chat history  in session state if not existed
    st.session_state.chat_history=[]

if "messages" not in st.session_state:                                                                                      # Creating messages list in session state if not existed
    st.session_state.messages = []

for message in st.session_state["messages"]:
    if message["role"] == "user":
                                                                                                                            # Display a user message in the chat interface
        with st.chat_message("user"):
            st.markdown(message["content"])
    elif message["role"] == "assistant":
                                                                                                                            # Display an assistant message in the chat interface
        with st.chat_message("assistant"):
            st.markdown(message["content"])





with st.sidebar:
    st.header("Financial Advisor ")
    st.button("New Session",on_click=new_session)
    st.write("For Reference")
    st.write('''-[Streamlit](https://streamlit.io/) 
            -  [LangChain](https://python.langchain.com/)
            -  [OpenAI](https://platform.openai.com/docs/models)''')


def main():
    st.header("Welcome to Your Personal Financial Advisor")
    options=st.chat_input("Enter your response ")
    # if options == '':
    if options == None:
            st.markdown("Hi, How can I Help You")
      
    #     # st.write("Enter your role")
    else:   
        # with st.chat_message("assistant"): 
            # st.write(f" Here's some ideas ")
        # response=st.chat_input("Enter your response")
        with st.chat_message("assistant"):
            
            chat_response=get_chat_response(options)
            st.markdown(chat_response)
    

def get_chat_response(user_message):
    messages = load_messages()
    messages.append({"role": "user", "content": user_message})

    # Send to ChatGpt/OpenAi
    gpt_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
        )

    parsed_gpt_response = gpt_response['choices'][0]['message']['content']

    # Save messages
    save_messages(user_message, parsed_gpt_response)

    return parsed_gpt_response

def load_messages():
    messages = []
    options=''
    name=''
    file = 'database.json'

    empty = os.stat(file).st_size == 0

    if not empty:
        with open(file) as db_file:
            data = json.load(db_file)
            for item in data:
                messages.append(item)
    else:
        messages.append(
            {"role": "system", "content": f"You are a financial advisor for a Bank.When a user asks for any financial advise, guide them in best way possible.Remember to greet the user with 'hi welcome to the your Financial Advisor App, how can I help you?' if the user asks 'hi' or 'hello."}
        )
    return messages


def save_messages(user_message, gpt_response):
    file = 'database.json'
    messages = load_messages()
    messages.append({"role": "user", "content": user_message})
    st.session_state.messages.append({"role": "user", "content": user_message})
    messages.append({"role": "assistant", "content": gpt_response})
    st.session_state.messages.append({"role": "assistant", "content": gpt_response})
    with open(file, 'w') as f:
        json.dump(messages, f)



if __name__ == '__main__':
    main()
    