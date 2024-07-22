from django.shortcuts import render, redirect, get_object_or_404
from .models import OrderItem, Order
from .forms import OrderCreateForm, OrderEditForm
from cart_app.cart import Cart
from django.contrib.auth.decorators import login_required
import csv
from django.http import HttpResponse
from management_app.models import Care
from django.contrib import messages


@login_required
def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST, user=request.user)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user  # 현재 로그인된 사용자를 주문에 연결
            order.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])

            return redirect('payment_app:payment_form', order_id=order.id)
        
    else:
        form = OrderCreateForm(user=request.user)

    return render(request,
                  'orders/order/create.html',
                  {'cart': cart, 'form': form})

@login_required
def export_orders_to_csv(request):
    orders = Order.objects.filter(email=request.user.email, paid=True)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'

    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Product', 'Price', 'Quantity', 'Total Cost', 'Created'])

    for order in orders:
        for item in order.items.all():
            writer.writerow([order.id, item.product.name, item.price, item.quantity, item.get_cost(), order.created])

    return response

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user, paid=True)
    return render(request, 'orders/order/my_orders.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order/order_detail.html', {'order': order})

@login_required
def order_edit(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if request.method == 'POST':
        form = OrderEditForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('orders_app:order_detail', order_id=order.id)
    else:
        form = OrderEditForm(instance=order)
    return render(request, 'orders/order/order_edit.html', {'form': form, 'order': order})

@login_required
def order_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.user == order.user:
        # 주문과 관련된 Care 객체 삭제
        Care.objects.filter(title=f'배송 서비스 요청 - {order.id}').delete()
        # 주문 삭제
        order.delete()
        messages.success(request, '주문이 성공적으로 취소되었습니다.')
    else:
        messages.error(request, '권한이 없습니다.')
    return redirect('orders_app:my_orders')