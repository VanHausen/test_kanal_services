from django.db import models


class Order(models.Model):
    order_num = models.CharField(max_length=50, null=False, verbose_name='заказ №')
    price_usd = models.CharField(max_length=50, null=False, verbose_name='стоимость $')
    price_rub = models.CharField(max_length=50, null=False, verbose_name='стоимость руб')
    delivery_time = models.CharField(max_length=50, null=False, verbose_name='срок поставки')

    def __str__(self):
        return self.order_num
