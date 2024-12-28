from confluent_kafka import Consumer, Producer
from transformers import pipeline
import json
import uuid

# Kafka consumer configuration
consumer = Consumer({
    'bootstrap.servers': 'kafka:9093',
    'group.id': 'en2ar_translation_service_group',
    'auto.offset.reset': 'earliest'
})

# Kafka producer configuration
producer = Producer({
    'bootstrap.servers': 'kafka:9093',
    'client.id': 'en2ar_translation_service_consumer'
})

# Load translation model (English to Arabic)
translator_en_to_ar = pipeline("translation_en_to_ar", model="Helsinki-NLP/opus-mt-en-ar")

def kafka_produce_message(topic, message):
    """ Function to send messages to Kafka topic. """
    producer.produce(topic, value=json.dumps(message))
    producer.flush()

def kafka_consume_messages():
    """ Function to consume messages from Kafka. """
    consumer.subscribe(['translation-requests'])
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        # Process message
        message = json.loads(msg.value().decode('utf-8'))
        process_translation(message)

def process_translation(message):
    """ Process the translation request and send the result back to Kafka. """
    text = message.get('text')
    request_id = message.get('request_id')

    # Perform translation
    result = translator_en_to_ar(text, max_length=400)[0]['translation_text']

    # Update the status dictionary
    translation_status[request_id] = {"status": "completed", "result": result}

    # Send result back to Kafka
    response_message = {
        "request_id": request_id,
        "status": "completed",
        "translated_text": result
    }

    kafka_produce_message('translation-responses', response_message)

# Start the Kafka consumer
if __name__ == "__main__":
    print("Starting Kafka consumer...")
    kafka_consume_messages()
