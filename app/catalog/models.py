from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Item(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='items/' , blank=True , null=True)

    def __str__(self):
        return self.title

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачено'),
        ('shipped', 'Доставлено'),
        ('canceled', 'Отменено'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE , related_name='orders', verbose_name="Покупатель")
    items = models.ManyToManyField(Item, related_name='orders', verbose_name="Товары")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Общая стоимость")

    status = models.CharField(max_length=20, default='pending')

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    def __str__(self):
        return f"Заказ #{self.id} | {self.user.username} | {self.get_status_display()}"

    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if  is_new:
            for item in self.items.all():
                if item.stock > 0:
                    item.stock -= 1 
                    item.save()

            self.update_total_price()

    def update_total_price(self):
        # Считаем сумму цен всех товаров
        total = sum(item.price for item in self.items.all())
        # Обновляем только поле total_price, чтобы не вызывать save() по кругу
        Order.objects.filter(pk=self.pk).update(total_price=total)
        
        

class Meta:
    verbos_name = 'Заказ'
    verbos_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ №{self.id} от {self.user.username}"
    

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=10, verbose_name="Остаток на складе")
        
    def __str__(self):
        return f"{self.name} (Осталось: {self.stock})"