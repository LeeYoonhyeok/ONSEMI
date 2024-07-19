from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.timezone import make_aware
from django.http import HttpResponse

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
import base64
import csv 

from ..forms import FilterForm
from orders_app.models import Order
from datetime import datetime, time
from management_app.models import Care , Senior
from matplotlib import font_manager, rc
import matplotlib.font_manager as fm

# 한글 폰트 설정

# font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
# font_name = fm.FontProperties(fname=font_path, size=10).get_name()
# plt.rcParams['font.family'] = font_name

font_path = 'C:\\Windows\\Fonts\\Arial.ttf'
font_name = fm.FontProperties(fname=font_path, size=10).get_name()
plt.rcParams['font.family'] = font_name


# 주문 데이터 DataFrame으로 변환
def order_to_dataframe(orders):
    data = []
    for order in orders:
        for item in order.items.all():
            data.append({
                'Order ID': order.id,
                'Product': item.product.name,
                'Category': item.product.category.name,
                'Price': float(item.price),
                'Quantity': item.quantity,
                'Total Cost': float(item.price * item.quantity),
                'created': order.created.isoformat(),
            })
    df = pd.DataFrame(data)
    if 'created' in df.columns: #임의로 만든 데이터들은 created고 서비스 상에서 데이터를 쌓으면 Created임
        df['created'] = pd.to_datetime(df['created'], format='ISO8601', errors='coerce')

    if 'Created' in df.columns: #임의로 만든 데이터들은 created고 서비스 상에서 데이터를 쌓으면 Created임
        df['Created'] = pd.to_datetime(df['Created'], format='ISO8601', errors='coerce')

    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], format='ISO8601', errors='coerce')

    if 'quantity' in df.columns: #임의로 만든 데이터들은 created고 서비스 상에서 데이터를 쌓으면 Created임
        df['quantity'] = df['quantity'].astype(float)

    if 'Quantity' in df.columns: #임의로 만든 데이터들은 created고 서비스 상에서 데이터를 쌓으면 Created임
        df['Quantity'] = df['Quantity'].astype(float)
        
    return df, data

##########################################################################################################

# 케어 데이터 DataFrame으로 변환
def care_to_dataframe(cares, start_date, end_date, category_service, selected_senior):
    data_care = []
        
    if start_date:
        cares = cares.filter(datetime__gte=start_date)
    if end_date:
        cares = cares.filter(datetime__lte=end_date)
    if category_service and category_service != 'all':
        cares = cares.filter(care_type=category_service)
    if selected_senior and selected_senior != 'all':
        cares = cares.filter(seniors__id=selected_senior)

    total_cares = cares.count()
    completed_cares = cares.filter(care_state='COMPLETED').count()

    completed_rate = 0
    if total_cares > 0:
        completed_rate = (completed_cares / total_cares) * 100

    for care in cares:
        data_care.append({
            'care_type': care.care_type,
            'datetime': care.datetime.isoformat(),
            'care_state': care.care_state,
        })
    df_care = pd.DataFrame(data_care)
    if not df_care.empty and 'datetime' in df_care.columns:
        df_care['datetime'] = pd.to_datetime(df_care['datetime'], format='ISO8601', errors='coerce')
        
    return df_care, data_care, completed_rate

##########################################################################################################

@login_required
def generate(request):
    
    # 현재 로그인한 유저에 해당되는 데이터 DB에서 불러오기
    form = FilterForm(request.POST or None, user=request.user)
    seniors = Senior.objects.filter(user_id=request.user)
    orders = Order.objects.filter(user=request.user)
    cares = Care.objects.filter(user_id=request.user)
    
    graph_url = None
    pie_chart_url = None

    # 폼 시니어 필드 지정
    # 한글화 하면서 해당 코드 삭제
    
    if request.method == 'POST' and form.is_valid():
        
        # 사용자가 선택한 필터 값 불러오기
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        category_order = form.cleaned_data.get('category_order')
        category_service = form.cleaned_data.get('category_service')
        selected_senior = form.cleaned_data.get('selected_senior')
        
        # 세션에 필터 값을 저장
        request.session['start_date'] = start_date.isoformat() if start_date else None
        request.session['end_date'] = end_date.isoformat() if end_date else None
        request.session['category_order'] = category_order
        request.session['category_service'] = category_service
        request.session['selected_senior'] = selected_senior

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

####################################################################################

        # 주문 데이터를 데이터프레임으로 변환
        df, data = order_to_dataframe(orders)
        
        # 서비스 요청 데이터를 데이터프레임으로 변환
        df_care, data_care, completed_rate = care_to_dataframe(cares, start_date, end_date, category_service, selected_senior)
        
####################################################################################
        if not df_care.empty:
            # 꺾은선 그래프 생성 (주간 단위)
            df_care['Week'] = df_care['datetime'].dt.to_period('W').apply(lambda r: r.start_time)
            weekly_data = df_care.groupby(['Week', 'care_type']).size().unstack().fillna(0)

            plt.figure(figsize=(10, 6))
            colors = ['#2D4059', '#EA5455', '#F07B3F', '#FFD460', '#CABBE9']  # 필요한 색상을 리스트로 정의
            for idx, column in enumerate(weekly_data.columns):
                plt.plot(weekly_data.index, weekly_data[column], marker='o', label=column, color=colors[idx % len(colors)])
            
            plt.legend(prop=fm.FontProperties(fname=font_path))
            plt.xlabel('기간', fontproperties=fm.FontProperties(fname=font_path))
            plt.ylabel('요청횟수', fontproperties=fm.FontProperties(fname=font_path))
            plt.ylim(0, 10)
            plt.xticks(rotation=45, fontproperties=fm.FontProperties(fname=font_path))
            plt.yticks(fontproperties=fm.FontProperties(fname=font_path))
            plt.tight_layout()

            # 그래프 이미지를 메모리에 저장
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()

            graph_url = base64.b64encode(image_png).decode('utf-8')
            graph_url = 'data:image/png;base64,' + graph_url

        else:
            # 데이터가 없을 경우 빈 꺾은선 그래프 생성
            plt.figure(figsize=(10, 6))
            plt.title('요청된 데이터가 없습니다', fontproperties=fm.FontProperties(fname=font_path))
            plt.xlabel('기간', fontproperties=fm.FontProperties(fname=font_path))
            plt.ylabel('요청횟수', fontproperties=fm.FontProperties(fname=font_path))
            plt.xticks(rotation=45, fontproperties=fm.FontProperties(fname=font_path))
            plt.yticks(fontproperties=fm.FontProperties(fname=font_path))
            plt.tight_layout()

            # 빈 그래프 이미지를 메모리에 저장
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()

            graph_url = base64.b64encode(image_png).decode('utf-8')
            graph_url = 'data:image/png;base64,' + graph_url

####################################################################################
        # 전체 데이터 기반 원형 그래프 생성
        if start_date:
            orders = orders.filter(created__gte=start_date)
        if end_date:
            orders = orders.filter(created__lte=end_date)
        
        all_data = []
        for order in orders:
            for item in order.items.all():
                all_data.append({
                    'Category': item.product.category.name,
                    'Quantity': item.quantity,
                })
        all_df = pd.DataFrame(all_data)
        all_df['Quantity'] = all_df['Quantity'].astype(float)

        if not all_df.empty:
            plt.figure(figsize=(10, 6))
            category_counts = all_df.groupby('Category')['Quantity'].sum()
            plt.pie(category_counts, labels=category_counts.index, colors=colors[:len(category_counts)], autopct='%1.1f%%', startangle=140,
                    textprops={'fontproperties': fm.FontProperties(fname=font_path)})
            plt.axis('equal')

            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()

            pie_chart_url = base64.b64encode(image_png).decode('utf-8')
            pie_chart_url = 'data:image/png;base64,' + pie_chart_url

        else:
            plt.figure(figsize=(10, 6))
            plt.title('요청된 데이터가 없습니다', fontproperties=fm.FontProperties(fname=font_path))
            plt.axis('equal')

            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()

            pie_chart_url = base64.b64encode(image_png).decode('utf-8')
            pie_chart_url = 'data:image/png;base64,' + pie_chart_url

        for record in data:
            record['Price'] = float(record['Price'])
            record['Total_Cost'] = float(record['Total Cost'])
            record['Order_ID'] = record.pop('Order ID')

        request.session['filtered_orders'] = data
        request.session['filtered_cares'] = data_care
        request.session['category_order'] = category_order
        request.session['category_service'] = category_service
        request.session['completed_rate'] = completed_rate
        request.session['selected_senior'] = selected_senior
        
        
    return render(request, 'monitoring_app/generate.html', {
        'form': form, 
        'graph_url': graph_url, 
        'pie_chart_url': pie_chart_url
    })
####################################################################################