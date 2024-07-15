from openai import OpenAI
from .models import ChatbotThreads
from user.models import UserInformations
import os

class Chatbot:
    
    client=OpenAI()
    assistant_id=os.environ.get('ASSISTANT_ID')
    
    def generateNormalGPTMessage(user_message):
        generate_message=Chatbot.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Be good"},
                {"role": "user", "content": f"{user_message}"}
            ]
        )
        return generate_message.choices[0].message.content
    
    def createOrGetThreadID(user_id):
        # first check if there is any threads already created for the user_id
        try:
            user_thread=ChatbotThreads.objects.get(user_id=UserInformations.objects.get(user_id=user_id))
            return user_thread.thread_id
        except ChatbotThreads.DoesNotExist:
            # if there is no thread for the user_id then create a new thread for the user_id
            # generate thread
            try:
                thread =  Chatbot.client.beta.threads.create()
            except Exception as e:
                print(e)
                return False
            try:
                # create a new thread for the user_id
                new_thread_for_user=ChatbotThreads.objects.create(
                    user_id=UserInformations.objects.get(user_id=user_id),
                    thread_id=thread.id
                )
                new_thread_for_user.save()
                return thread.id
            except Exception as e:
                return False
    
    def createMessageToThread(thread_id,user_message):
        try:
            message=Chatbot.client.beta.threads.messages.create(
                thread_id=thread_id,
                role='user',
                content=user_message
            )
            return True
        except Exception as e:
            print(e)
            return False
    
    def createRunAndGenerateMessage(thread_id):
        try:
            run = Chatbot.client.beta.threads.runs.create_and_poll(
                thread_id=thread_id,
                assistant_id=Chatbot.assistant_id,
            )
            if(run.status=='completed'):
                response=Chatbot.client.beta.threads.messages.list(
                    thread_id=thread_id
                )
                assistant_message= response.data[0].content[0].text.value
                return assistant_message
            else:
                print(run.status)
                return False
        except:
            return False
            
    
    def generateAssistantMessages(user_message,user_id):
        thread_id=Chatbot.createOrGetThreadID(user_id)
        if(thread_id==False):
            return False,"Can not generate Thread ID for the user"
        else:
            if(Chatbot.createMessageToThread(thread_id,user_message)):
                assistant_message=Chatbot.createRunAndGenerateMessage(thread_id)
                if(assistant_message==False):
                    return False,"Can not generate Assistant Message"
                else:
                    return True,assistant_message
            else:
                return False,"Can not create User Message"
    
    def getAllMessagesOfUser(user_id):
        user_message_list=[]
        assistant_message_list=[]
        try:
            # get thread id of user

            thread=ChatbotThreads.objects.get(user_id=user_id)
            thread_messages = Chatbot.client.beta.threads.messages.list(thread_id=thread.thread_id)
            for message in (thread_messages.data):
                if(message.role=='user'):
                    user_message_list.append(message.content[0].text.value)
                elif(message.role=='assistant'):
                    assistant_message_list.append(message.content[0].text.value)
            return True,user_message_list,assistant_message_list,"Previous history retrieved!"
        except ChatbotThreads.DoesNotExist:
            return True,user_message_list,assistant_message_list,"No previous chat history was found!"
        except Exception as e:
            print(e)
            return False,user_message_list,assistant_message_list,"Something went wrong while fetching messages"
