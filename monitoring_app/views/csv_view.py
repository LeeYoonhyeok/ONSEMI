from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.timezone import make_aware

from ..forms import FilterForm
from orders_app.models import Order
from datetime import datetime, time
from management_app.models import Care

# 맥 전용 한글 폰트
from matplotlib import rc
rc('font', family='AppleGothic')


@login_required
def csv_view(request):
    data_type = request.GET.get('type')
    
    initial_data = {
        'start_date': request.session.get('start_date'),
        'end_date': request.session.get('end_date'),
        'category_order': request.session.get('category_order'),
        'category_service': request.session.get('category_service'),
        'selected_senior': request.session.get('selected_senior'),
    }

    form = FilterForm(request.POST or None, 
                      initial=initial_data, 
                      user=request.user)

    # POST 방식
    if request.method == 'POST' and form.is_valid():
        
        # 폼 값 가져오기
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        category_order = form.cleaned_data.get('category_order')
        category_service = form.cleaned_data.get('category_service')
        selected_senior = form.cleaned_data.get('selected_senior')

        # 폼에서 가져온 값 세션에 저장하기
        request.session['start_date'] = start_date.isoformat() if start_date else None
        request.session['end_date'] = end_date.isoformat() if end_date else None
        request.session['category_order'] = category_order
        request.session['category_service'] = category_service
        request.session['selected_senior'] = selected_senior
        
    # GET 방식
    else:
        start_date = initial_data.get('start_date')
        end_date = initial_data.get('end_date')
        category_order = initial_data.get('category_order')
        category_service = initial_data.get('category_service')
        selected_senior = initial_data.get('selected_senior')

    if start_date and isinstance(start_date, str):
        start_date = make_aware(datetime.combine(datetime.strptime(start_date, '%Y-%m-%d'), time.min))
    if end_date and isinstance(end_date, str):
        end_date = make_aware(datetime.combine(datetime.strptime(end_date, '%Y-%m-%d'), time.max))

    # Care에 대한 표 생성
    if data_type == 'care':
        data_care = []
        
        # 본인이 요청한 케어만 모두 불러오기
        cares = Care.objects.filter(user_id=request.user)
        
        # 케어 필터링 적용 후 조회하기
        if start_date:
            start_date = make_aware(datetime.combine(start_date, time.min))
            cares = cares.filter(datetime__gte=start_date)
        if end_date:
            end_date = make_aware(datetime.combine(end_date, time.max))
            cares = cares.filter(datetime__lte=end_date)
        if category_service and category_service != 'all':
            cares = cares.filter(care_type=category_service)
        if selected_senior and selected_senior != 'all':
            cares = cares.filter(seniors__id=selected_senior)
        
        # 케어 완료 비율 계산
        total_cares = cares.count()
        completed_cares = cares.filter(care_state='COMPLETED').count()
        completed_rate = 0
        if total_cares > 0:
            completed_rate = (completed_cares / total_cares) * 100

        for care in cares:
            if care.visit_date and care.visit_time:
                hour = care.visit_time.hour
                minute = care.visit_time.minute
                period = "오전" if hour < 12 else "오후"
                hour = hour if hour <= 12 else hour - 12
                visit_time_str = f"{period} {hour}시 {minute}분"
                visit_date_str = f"{care.visit_date.strftime('%Y년 %m월 %d일')} {visit_time_str}"
            else:
                visit_date_str = '방문 날짜가 정해지지 않았습니다.'

            data_care.append({
                'care_title': care.title,
                'care_type': care.care_type,
                'datetime': care.datetime.strftime('%Y년 %m월 %d일 %H시 %M분'),
                'visit_date': visit_date_str,
                'care_state': care.care_state,
                'care_content': care.content,
                'care_seniors': ', '.join([senior.name for senior in care.seniors.all()]),  # assuming Senior model has a 'name' field
            })

        request.session['filtered_cares'] = data_care

        return render(request, 'monitoring_app/csv_view.html', {
            'filtered_cares': data_care, 
            'data_type': 'care',
            'completed_rate': completed_rate,
            'form': form,
        })

    # Order에 대한 표 생성
    else:
        
        # 본인이 주문한 주문 내역만 불러오기
        orders = Order.objects.filter(user=request.user)
        
        # 주문 조회 필터링 작업
        if start_date:
            start_date = make_aware(datetime.combine(start_date, time.min))
            orders = orders.filter(created__gte=start_date)
        if end_date:
            end_date = make_aware(datetime.combine(end_date, time.max))
            orders = orders.filter(created__lte=end_date)
        if category_order and category_order != 'all':
            orders = orders.filter(items__product__category__name=category_order).distinct()
        if selected_senior and selected_senior != 'all':
            orders = orders.filter(senior_id=selected_senior)

        data = []
        for order in orders:
            for item in order.items.all():
                data.append({
                    'order_id': order.id,
                    'product': item.product.name,
                    'category': item.product.category.name,
                    'price': float(item.price),
                    'quantity': item.quantity,
                    'total_cost': float(item.price * item.quantity),
                    'created': order.created.strftime('%Y년 %m월 %d일 %H시 %M분')
                })


        if category_order and category_order != 'all':
            data = [order for order in data if order['category'] == category_order]

        return render(request, 'monitoring_app/csv_view.html', {
            'filtered_orders': data, 
            'data_type': 'order',
            'form': form,
        })