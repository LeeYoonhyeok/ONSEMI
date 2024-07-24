from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from shop_app.models import Product
from .cart import Cart
from .forms import CartAddProductForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        if form.is_valid():
            cd = form.cleaned_data
            if not cart.add(product=product,
                            quantity=cd['quantity'],
                            override_quantity=cd['override']):
                messages.error(request, '재고가 부족합니다.')
                return redirect('shop_app:product_detail',  id=product.id, slug=product.slug)
        else:
            cart.add(product=product,
                     quantity=cd['quantity'],
                     override_quantity=cd['override'])
    return redirect('cart_app:cart_detail')

@login_required
@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_app:cart_detail')

@login_required
def cart_detail(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = CartAddProductForm(request.POST)
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        if form.is_valid():
            cd = form.cleaned_data
            if not cart.add(product=product, quantity=cd['quantity'], override_quantity=cd['override']):
                messages.error(request, '재고가 부족합니다.')
                return redirect('cart_app:cart_detail')
            else:
                messages.success(request, '수량이 변경되었습니다.')
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True
        })
    return render(request, 'cart/detail.html', {'cart': cart})

@login_required
def stock_alert(request):
    return render(request, 'cart/stock_alert.html')