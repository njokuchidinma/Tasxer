from celery import shared_task

@shared_task
def send_task_notification(task_title):
    print(f"Sending notification for task: {task_title}")
    # Simulate sending an email