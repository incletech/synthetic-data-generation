from celery import Celery

celery_app = Celery(
    'my_celery_app',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0' )


celery_app.conf.update(
    task_routes={
        'tasks.generate_synthetic_data': {'queue': 'data_queue'},
    }
)


