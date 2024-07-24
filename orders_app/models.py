from django.db import models
from shop_app.models import Product
from auth_app.models import User
from management_app.models import Care, Senior

# 실제 서비스에서 작동할 코드
# class Order(models.Model):
#     first_name = models.CharField(max_length=50)
#     last_name = models.CharField(max_length=50)
#     email = models.EmailField()
#     address = models.CharField(max_length=250)
#     postal_code = models.CharField(max_length=20)
#     city = models.CharField(max_length=100)
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
#     paid = models.BooleanField(default=False)

# 데이터 조작용 코드
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    senior = models.ForeignKey(Senior, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    phone = models.CharField(max_length=15, default='000-0000-0000')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    care = models.ForeignKey(Care, on_delete=models.CASCADE, null=True, blank=True, default=None)  # 여기를 수정

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    # def save(self, *args, **kwargs):
    #     if self.pk is not None:  # 업데이트되는 경우에만 처리
    #         orig = Order.objects.get(pk=self.pk)
    #         if not orig.paid and self.paid:  # 결제 상태가 False에서 True로 변경될 때만 실행
    #             content = "\n".join([f"{item.quantity}x {item.product.name}" for item in self.items.all()])
    #             care, created = Care.objects.update_or_create(
    #                 care_type="SHOP",
    #                 user_id=self.user,
    #                 title=f'SHOP 서비스 요청 - {self.id}',
    #                 defaults={
    #                     'content': f'주문 번호 {self.id}에 대한 SHOP 서비스 요청입니다.\n\n{content}',
    #                     'care_state': 'NOT_APPROVED',
    #                 }
    #             )
    #     super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order,
                              related_name='items',
                              on_delete=models.CASCADE)
    product = models.ForeignKey(Product,
                                related_name='order_items',
                                on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10,
                                decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity