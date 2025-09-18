from rooms_service.core.utils import generate_correlation_id


for _ in range(5):
    print(generate_correlation_id())
