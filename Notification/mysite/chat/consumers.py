from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth.models import User
import jwt

class ChatConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.room_name = self.scope['url_route']['kwargs']['room_name']
		self.room_group_name = 'chat_%s' % self.room_name
		self.token = self.scope['url_route']['kwargs']['token']
		data = jwt.decode(self.token, 'SECRET_KEY', algorithm='HS256')
		self.user = data["username"]
		print(self.room_name)
		try:
			self.u = User.objects.get(username=self.user)
			if self.u.is_superuser:
				# Join room group
				await self.channel_layer.group_add(
            				self.room_group_name,
            				self.channel_name
        		)
				await self.accept()
			else:
				flag = False
				for key, value in data.items():
					print(key)
					if self.room_name == key:
						# Join room group
						flag = True        			
						await self.channel_layer.group_add(
            						self.room_group_name,
            						self.channel_name
        				)
						await self.accept()
				if flag == False:
					await self.close()
		except User.DoesNotExist:
			flag = False
			for key, value in data.items():
				if self.room_name == key:
					# Join room group
					flag = True        			
					await self.channel_layer.group_add(
           						self.room_group_name,
           						self.channel_name
					)
					await self.accept()
			if flag == False:
				await self.close()
			print(flag)
		else:
			await self.close()

	
	async def disconnect(self, close_code):
		# Leave room group
		await self.channel_layer.group_discard(
	            self.room_group_name,
	            self.channel_name
	        )
	
	# Receive message from WebSocket
	async def receive(self, text_data):
		text_data_json = json.loads(text_data)
		message = text_data_json['message']

		try:
			self.u = User.objects.get(username=self.user)
			if self.u.is_superuser:
				# Send message to room group
        			await self.channel_layer.group_send(self.room_group_name,
				{
				'type': 'chat_message',
				'message': message
				}
				)
		except:
			pass

			

	# Receive message from room group
	async def chat_message(self, event):
	        message = event['message']
	
	        # Send message to WebSocket
	        await self.send(text_data=json.dumps({
	            'message': message
	        }))
