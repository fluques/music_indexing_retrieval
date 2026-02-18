# scripts/consumer.py (run this file separately, e.g., using a management command or a service manager)
import asyncio
from aiokafka import AIOKafkaConsumer
import json
from asgiref.sync import sync_to_async
from music_indexing_retrieval import settings
from api.views import AudioFileListView
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Starts the Kafka consumer to listen for PDF file events'

    KAFKA_BOOTSTRAP_SERVERS = [settings.KAFKA_BOOTSTRAP_SERVERS]
    KAFKA_TOPIC = settings.KAFKA_TOPIC
    KAFKA_GROUP_ID = settings.KAFKA_GROUP_ID

    async def consume_messages(self):
        consumer = AIOKafkaConsumer(
            self.KAFKA_TOPIC,
            bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,  
            group_id=self.KAFKA_GROUP_ID,
            auto_offset_reset='earliest' # Start reading from the beginning if no offset is committed
        )
        await consumer.start()
        try:
            # Consume messages
            async for msg in consumer:
                print(f"Consumed: Topic={msg.topic}, Partition={msg.partition}, Offset={msg.offset}")
                # Decode the message value (assuming JSON as an example)
                message_value = json.loads(msg.value.decode('utf-8'))
                #mp3_path = message_value.get('mp3_path')
                
                print(f"Value: {message_value}")
                # Process the message (e.g., update Django models asynchronously)
                await self.process_uploads()
        finally:
            # Will leave consumer group; perform autocommit if enabled
            await consumer.stop()

    @sync_to_async
    def process_uploads(self):
        audio_file_list_view = AudioFileListView()
        audio_file_list_view.index_uploads_sync()
        self.stdout.write(self.style.SUCCESS("End Kafka consumer... Indexed files ok"))
        audio_file_list_view.index_save(None)
        self.stdout.write(self.style.SUCCESS("End Kafka consumer... Indexed saved ok"))


    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting Kafka consumer..."))
        asyncio.run(self.consume_messages())

