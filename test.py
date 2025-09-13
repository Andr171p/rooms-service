from rooms_service.core.utils import total_pages

print(total_pages(103, 4))


from faststream.kafka import KafkaBroker

broker = KafkaBroker()

broker.publish()