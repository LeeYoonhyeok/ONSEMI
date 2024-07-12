from django.shortcuts import render,get_object_or_404
from management_app.models import Care, Senior, Report, ReportImage

def report_list(request):
    sort_by = request.GET.get('sort_by', '-created_at')
    user_id = request.user.id # 현재 로그인한 사용자의 ID
    selected_senior_id = request.GET.get('selected_senior_id', '')
    type_filter = request.GET.get('type_filter', 'all')
   
    reports = Report.objects.all().order_by(sort_by)
    # 현재 로그인한 사용자의 Care 객체만 필터링
    cares = Care.objects.filter(user_id=user_id)
    if selected_senior_id:
        cares = cares.filter(seniors__id=selected_senior_id)

    
    seniors = Senior.objects.filter(user_id=user_id)
    reports = Report.objects.filter(care__in=cares)
    
    selected_senior = None
    if selected_senior_id:
        selected_senior = Senior.objects.get(id=selected_senior_id)

    if sort_by == '-created_at':
        reports = reports.order_by('-created_at')
    else:
        reports = reports.order_by('created_at')
        
    if type_filter == 'shop':
        reports = reports.filter(care__care_type='쇼핑')
    elif type_filter == 'visit':
        reports = reports.filter(care__care_type='방문')
    elif type_filter == 'hospital':
        reports = reports.filter(care__care_type='병원')   
        
    
    reports_imgs = ReportImage.objects.filter(report__in=reports)
    
    context = {
        "cares": cares, 
        "selected_user": user_id,
        'selected_senior_id': selected_senior_id,
        "seniors": seniors,
        "selected_senior": selected_senior,
        "type_filter": type_filter,
        "reports" : reports,
        "report_imgs" : reports_imgs,
    }
    return render(request, "monitoring_app/monitor_report_list.html", context)


def show_one_report(request,report_id):
    report = get_object_or_404(Report, id=report_id)
    reports_imgs = ReportImage.objects.filter(report=report)
    
    context = {"report":report, "report_imgs" : reports_imgs,}
    
    return render(request, "monitoring_app/show_one_report.html", context)