from django.shortcuts import render,get_object_or_404
from management_app.models import Care, Senior, Report, ReportImage
from ..forms import FilterForm
from django.core.paginator import Paginator


def report_list(request):
    sort_by = request.GET.get('sort_by', '-created_at')
    form = FilterForm(request.GET)
    user_id = request.user.id  # 현재 로그인한 사용자의 ID
    selected_senior_id = request.GET.get('selected_senior_id', '')
    type_filter = request.GET.get('type_filter', 'all')

    # 현재 로그인한 사용자의 Care 객체만 필터링
    cares = Care.objects.filter(user_id=user_id)
    if selected_senior_id:
        cares = cares.filter(seniors__id=selected_senior_id)

    seniors = Senior.objects.filter(user_id=user_id)
    reports = Report.objects.filter(care__in=cares)

    selected_senior = None
    if selected_senior_id:
        selected_senior = Senior.objects.get(id=selected_senior_id)

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        if start_date and end_date:
            reports = reports.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)

    if type_filter == 'shop':
        reports = reports.filter(care__care_type='배송')
    elif type_filter == 'visit':
        reports = reports.filter(care__care_type='방문')
    elif type_filter == 'hospital':
        reports = reports.filter(care__care_type='병원')

    if sort_by == '-created_at':
        reports = reports.order_by('-created_at')
    else:
        reports = reports.order_by('created_at')

    paginator = Paginator(reports, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    senior_list = seniors.all()

    # 각 report에 대한 이미지와 senior 정보 추가
    report_details = []
    for report in page_obj:
        imgs = ReportImage.objects.filter(report=report)
        seniors = report.care.seniors.all()        
        report_details.append({
            'report': report,
            'images': imgs,
            'seniors': seniors,
        })

    context = {
        "cares": cares,
        "selected_user": user_id,
        'selected_senior_id': selected_senior_id,
        "seniors": seniors,
        "selected_senior": selected_senior,
        "sort_by": sort_by,
        "start_date": start_date,
        "end_date": end_date,
        "type_filter": type_filter,
        'form': form,
        "reports_details": report_details,
        'page_obj': page_obj,
        'senior_list' : senior_list,
    }
    return render(request, "monitoring_app/monitor_report_list.html", context)


def show_one_report(request,report_id):
    report = get_object_or_404(Report, id=report_id)
    reports_imgs = ReportImage.objects.filter(report=report)
    
    filter_params = request.GET.urlencode()  # 기존 GET 파라미터를 가져옵니다.
    
    context = {"report":report, "report_imgs" : reports_imgs,"filter_params": filter_params,}
    
    return render(request, "monitoring_app/show_one_report.html", context)