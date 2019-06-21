# chat/consumers.py
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from chat.models import Message, Dialog
from accounts.models import User
import datetime

datetime_str = '2016-05-18T15:37:36.993048Z'
old_format = '%Y-%m-%dT%H:%M:%S.%fZ'
new_format = '%d-%m-%Y %H:%M:%S'

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
    def fetch_messages(self,room_id):

        dialogbox = Dialog.objects.filter(id = room_id)[0]
        message_Qset = (Message.objects.filter(dialogbox = dialogbox).order_by('-date')[:40])
        message_Qset = reversed(list(message_Qset))

        content = {
            'command': 'oldmessages',
            'messages': self.messages_to_json(message_Qset)
        }
        self.send_message(content)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
            d = message.date
            date_new = d.strftime('%d %b')
            time_new = d.strftime('%I:%M %p')
            date_str  = time_new + " | "  + date_new
            return {
                'author_name': message.author.first_name,
                'content': message.content,
                'author_email':message.author.email,
                'date' : date_str 
            }

    def receive(self, text_data):
        received_obj = json.loads(text_data)
        command = received_obj['command']
        if command=='fetch_messages':
            room_id = received_obj['room_id']
            self.fetch_messages(room_id)

        else :
            print("receiving again again")
            author_email = received_obj['author_email']
            content = received_obj['content']
            room_id = received_obj['room_id']
            opponent_email = received_obj['opponent_email']
            dialogbox = Dialog.objects.filter(id= room_id)[0]
            
            author = User.objects.filter(email = author_email)[0]
            message_obj = Message.objects.create(
                content = content,
                dialogbox = dialogbox,
                author = author
            )
            dialogbox.date_of_dialog = message_obj.date
            dialogbox.save()
            d = message_obj.date
            # d= d.strftime("%A %d. %B %Y")
            # print(d)
            # datetime_str =  str(message_obj.date)
            date_new = d.strftime('%d %b')
            time_new = d.strftime('%I:%M %p')
            date_str  = time_new + " | "  + date_new
            msg ={
                'author_name' :author.first_name,
                'content' : content,
                'author_email': author.email,
                'date' : date_str,
                'command': 'newmessage'
            }
            # Send message to room group
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': msg
                }
            )

    def send_message(self, message):
        self.send(text_data=json.dumps({'message':message}))
        # Receive message from room group

    def chat_message(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))