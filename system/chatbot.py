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
            thread =  Chatbot.client.beta.threads.create()
            # create a new thread for the user_id
            new_thread_for_user=ChatbotThreads.objects.create(
                user_id=UserInformations.objects.get(user_id=user_id),
                thread_id=thread.id
            )
            new_thread_for_user.save()
            return thread.id
