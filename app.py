import streamlit as st
import openai
import os
import json
from gptcache import cache
from gptcache.adapter import openai
from gptcache.embedding import Onnx
from gptcache.manager import CacheBase, VectorBase, get_data_manager
from gptcache.similarity_evaluation.distance import SearchDistanceEvaluation
import time


openai_api_key =st.secrets['OPENAI_API_KEY']
onnx = Onnx()
data_manager = get_data_manager(CacheBase("sqlite"), VectorBase("faiss", dimension=onnx.dimension))
cache.init(
    embedding_func=onnx.to_embeddings,
    data_manager=data_manager,
    similarity_evaluation=SearchDistanceEvaluation(),
    )
cache.set_openai_key()

def new_session():
    st.session_state['text']=''
    del st.session_state.messages
    file = 'database.json'
    with open (file,'w') as f:
        f.seek(0)
        f.truncate()


if 'chat_history' not in st.session_state:                                                                                  # Creating a list -chat history  in session state if not existed
    st.session_state.chat_history=[]

if "messages" not in st.session_state:                                                                                      # Creating messages list in session state if not existed
    st.session_state.messages = []



with st.sidebar:
    st.header("Financial Advisor App ")
    st.image("https://cdn.dribbble.com/users/1299339/screenshots/2982257/media/a0a4dcb030548cd22cc59c8214bfa1a4.gif")
    st.header("About")
    st.markdown("This interactive chatbot will engage users in conversations about their financial goals and provide personalized guidance on managing their finances, paying off loans, investing, planning for retirement, and addressing other financial concerns.")
    
    st.write("For Reference")
    st.write('''-[Streamlit](https://streamlit.io/) 
            -  [OpenAI](https://platform.openai.com/docs/models)''')


def main():
    st.header("Welcome to Your Personal Financial Advisor💸")
    options=st.chat_input("Enter your response ")
    start_time = time.time()
    
   
    if options == None:
            st.markdown("Hi, How can I Help You")
      
   
    else:   
        
        with st.chat_message("assistant"):
            
            chat_response=get_chat_response(options)
         
    
        for message in st.session_state["messages"]:
            if message["role"] == "user":
                                                                                                                                    # Display a user message in the chat interface
              
                    st.write('👤:',message["content"])
            elif message["role"] == "assistant":
                                                                                                                                    # Display an assistant message in the chat interface
                    st.write("Time consuming: {:.2f}s".format(time.time() - start_time))
                    st.write('🤖:',message["content"])
    st.button("End Chat",on_click=new_session,help="To start over")
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
    