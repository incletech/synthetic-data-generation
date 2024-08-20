from .celery_config import celery_app

@celery_app.task
def generate_synthetic_data(param1, param2):
    import time
    time.sleep(10)  
    result = f'Data generated with {param1} and {param2}'
    return result
