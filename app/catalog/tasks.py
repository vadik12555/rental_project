from celery import shared_task
import time

@shared_task
def send_order_confirmation(order_id):
    print(f" Начинаем отправку подтверждения для заказа №{order_id} ")
    time.sleep(10) # Имитируем долгую работу (10 секунд)
    print(f"Письмо для заказа №{order_id} успешно отправлено! ")