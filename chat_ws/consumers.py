import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from convos.models import Convo, Message
from channels.layers import get_channel_layer



class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        print("Connection attempt")
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        convo_id = self.scope['url_route']['kwargs']['convo_id']
        member1_id = self.scope['url_route']['kwargs']['member1_id']
        # print(user_id)
        convo = Convo.objects.filter(uuid=convo_id).first()
        print(convo)

        group_name = convo.uuid
        await self.channel_layer.group_add(group_name, self.channel_name)
        await self.accept()
        print("Connection established")
        messages = Message.objects.filter(convo=convo).order_by('created_at')

        message_data = []

        for message in messages:
            m_data = {
                "sender": message.sender.username,
                "receiver": message.receiver.username,
                "content": message.content,
                "convo": message.convo.uuid,
                "created_at": message.created_at.isoformat(),
            }

            message_data.append(m_data)
        print(message_data)
        await self.send_json(message_data)


    async def notify(self, event):
        print(event)
        await self.send_json(event['content'])

    async def decode_json(self, content):
        try:
            import ast
            data = ast.literal_eval(content)
            return data
        except:
            return None

    async def receive_json(self, content):
        print("Received json")
        print(content)
        convo_id = self.scope['url_route']['kwargs']['convo_id']
        member1_id = self.scope['url_route']['kwargs']['member1_id']
        convo = Convo.objects.filter(uuid=convo_id).first()
        user_1 = User.objects.filter(id=member1_id).first()

        for m in convo.members.all():
            if m != user_1:
                member2_id = m.id
                break
        user_2 = User.objects.filter(id=member2_id).first()

        sender = user_1
        receiver = user_2

        message = Message(
            content=content['message'],
            sender=sender,
            receiver=receiver,
            convo=convo
        )

        message.save()

        

        message_data = {
            "sender": message.sender.username,
            "receiver": message.receiver.username,
            "content": message.content,
            "convo": message.convo.uuid,
            "created_at": message.created_at.isoformat(),
        }

        # await self.send_json(message_data)

        channel_layer = get_channel_layer()

        await channel_layer.group_send(
            f"{convo_id}",
            {
                "type": "notify",
                "content": {
                    "data": message_data
                }
            }
        )