from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import datetime
from pytz import timezone
import sqlite3
import pandas as pd
import json
from .models import ChatHistory
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# Initialize Chroma database
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
database = Chroma(persist_directory="./database", embedding_function=embeddings)

@login_required
def chatting(request):
    if request.method == 'POST':
        # Parse JSON request body
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        query = body_data.get('question')
        
        seoul_time = datetime.now(timezone('Asia/Seoul')).strftime('%H:%M')
        chat = ChatOpenAI(model="gpt-3.5-turbo")

        retriever = database.as_retriever(search_kwargs={"k": 3})
        memory = ConversationBufferMemory(memory_key="chat_history", input_key="question", output_key="answer", return_messages=True)
        qa = ConversationalRetrievalChain.from_llm(llm=chat, retriever=retriever, memory=memory, return_source_documents=True, output_key="answer")
        result = qa({"question": query})

        # Save chat history in the session
        if 'conversation' not in request.session:
            request.session['conversation'] = []
        request.session['conversation'].append({'sender': 'user', 'message': query, 'timestamp': seoul_time})
        request.session['conversation'].append({'sender': 'bot', 'message': result['answer'], 'timestamp': seoul_time})
        request.session.modified = True

        return JsonResponse({'answer': result['answer']})
    elif request.method == 'GET':
        conversation = request.session.get('conversation', [])
        return JsonResponse({'conversation': conversation})

@login_required
def reset(request):
    if request.method == 'POST':
        # Clear chat history from the session
        request.session['conversation'] = []
        request.session.modified = True

        # Clear the database
        ChatHistory.objects.all().delete()
        path = './db_chatlog/chatlog.db'
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute('''DROP TABLE IF EXISTS history''')
        conn.commit()
        conn.close()
        
        # Delete Chroma documents
        db = database.get()
        delete_db = pd.DataFrame(db)
        delete_list = delete_db[delete_db['metadatas'].apply(lambda x: '질문' in x)]['ids'].to_list()
        for id in delete_list:
            database.delete(ids=id)
        
        return JsonResponse({'status': 'success'})
