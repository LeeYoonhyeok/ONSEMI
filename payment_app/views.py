from django.shortcuts import render, get_object_or_404, redirect
from orders_app.models import Order, OrderItem
from shop_app.models import Product
from django.contrib import messages
from management_app.models import Care
from django.db import transaction
from cart_app.cart import Cart

def payment_form(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {
        'order': order,
    }
    return render(request, 'payment_app/payment_form.html', context)

def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # 주문된 상품들의 재고를 줄입니다.
    for item in order.items.all():
        product = item.product
        if product.stock >= item.quantity:
            product.stock -= item.quantity
            product.save()
        else:
            messages.error(request, f'{product.name}의 재고가 부족합니다.')
            return render(request, 'payment_app/payment_fail.html', {'order_id': order_id})
    
    with transaction.atomic():
        # 결제 완료로 주문 상태를 업데이트합니다.
        order.paid = True
        order.save()

        # 주문이 완료되면 care 객체를 생성
        content = "\n".join([f"{item.quantity}x {item.product.name}" for item in order.items.all()])
        
        care, created = Care.objects.update_or_create(
            care_type="배송",
            user_id=order.user,
            title=f'배송 서비스 요청 - {order.id}',  # order_number 대신 order.id 사용
            defaults={
                'content': f'주문 번호 {order.id}에 대한 배송 서비스 요청입니다.\n\n{content}',
                'care_state': 'NOT_APPROVED',
            }
        )

        # 주문의 senior 정보를 care 객체에 추가
        if order.senior:
            care.seniors.add(order.senior)
        care.save()

        # Order 모델의 care 필드 업데이트
        order.care = care
        order.save()


    # 결제가 성공하면 장바구니를 비웁니다.
    cart = Cart(request)
    cart.clear()

    # return render(request, 'orders/order/created.html', {'order': order})
    return render(request, 'payment_app/payment_success.html', {'order_id': order_id})

def payment_fail(request, order_id):
    # 주문 실패 시 주문 삭제
    order = get_object_or_404(Order, id=order_id)
    # messages.error(request, '결제가 실패했습니다. 다시 시도해주세요.')
    return render(request, 'payment_app/payment_fail.html', {'order_id': order_id})