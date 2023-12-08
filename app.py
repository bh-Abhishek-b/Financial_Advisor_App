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
from streamlit_chat import message
from streamlit_lottie import st_lottie


openai_api_key =st.secrets['OPENAI_API_KEY']
st.set_page_config(page_title='Finanical Advisor', page_icon='💸', layout="centered")
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
    del st.session_state.past
    del st.session_state.generated
    file = 'database.json'
    with open (file,'w') as f:
        f.seek(0)
        f.truncate()


if 'chat_history' not in st.session_state:                                                                                  # Creating a list -chat history  in session state if not existed
    st.session_state.chat_history=[]

if "messages" not in st.session_state:                                                                                      # Creating messages list in session state if not existed
    st.session_state.messages = []

if 'past' not in st.session_state:
    st.session_state.past=[]
if 'generated' not in st.session_state:
    st.session_state.generated=[]

with st.sidebar:
    st.header("Financial Advisor App ")
    st_lottie("https://lottie.host/8ff1e553-8f49-4b36-9ec6-4b3b4685d888/fsUA57khHn.json",quality="high")
    # st.image("https://cdn.dribbble.com/users/1299339/screenshots/2982257/media/a0a4dcb030548cd22cc59c8214bfa1a4.gif")
    st.header("About")
    st.markdown("This interactive chatbot will engage users in conversations about their financial goals and provide personalized guidance on managing their finances, paying off loans, investing, planning for retirement, and addressing other financial concerns.")
    
    st.write("For Reference")
    st.write('''-[Streamlit](https://streamlit.io/) 
            -  [OpenAI](https://platform.openai.com/docs/models)''')


def main():
    st.header("Welcome to Your Personal Financial Advisor",divider='rainbow')
    options=st.chat_input("Enter your response ")
    
   
    if options == None:
            st.markdown("Hi, How can I Help You")
      
   
    else:   
        
        with st.spinner("Bot is working"):
            
            chat_response=get_chat_response(options)
         
        chat_placeholder = st.empty()
        
        with chat_placeholder.container():    
            for i in range(len(st.session_state['generated'])):                
                message(message='You : '+st.session_state['past'][i], is_user=True, key=f"{i}_user",avatar_style="thumbs",seed="Aneka")
                message(message='Bot : '+
                    st.session_state['generated'][i], 
                    key=f"{i}",avatar_style="bottts-neutral",seed="Aneka")
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
            {"role": "system", "content": f"""You are a financial advisor for a Bank. When a user asks for any financial advice, guide them in the best way possible.
                                            Remember to greet the user with 'Hi welcome to your Financial Advisor App, how can I help you?' if the user asks 'hi' or 'hello.
                                            You need to identify who they are speaking with: Are they speaking with a borrower (who is looking for their own financing), or with a broker (who is looking for financing for a client)? Ask direct questions early on in the conversation to determine if the user is seeking financing personally or on behalf of a client. Follow-up questions should be framed accordingly.
                                            Your goal is to sell some sort of financial product of the bank (loan, insurance, health plan, etc) to the user, one specific goal in the beginning - Get the consumer to agree they want to start the deal(as in take the loan, insurance, retirement plan, etc based on the specific user conversation) from the bank.
                                            Don't ask multiple questions at time, one question at a time.
                                            Adapt the 'Always Be Closing' principle carefully for chatbot use. Another theory is when selling anything, everything should be framed within the idea of YES. Always compliment. Always confirm. Always be optimistic. Always push the borrower to the closing point goals (in this case - to speak with another human, to get the deals started).
                                            """}
        )
    return messages


def save_messages(user_message, gpt_response):
    file = 'database.json'
    messages = load_messages()
    messages.append({"role": "user", "content": user_message})
    st.session_state.messages.append({"role": "user", "content": user_message})
    st.session_state.past.append(user_message)
    messages.append({"role": "assistant", "content": gpt_response})
    st.session_state.messages.append({"role": "assistant", "content": gpt_response})
    st.session_state.generated.append(gpt_response)
    with open(file, 'w') as f:
        json.dump(messages, f)



if __name__ == '__main__':
    main()
    
