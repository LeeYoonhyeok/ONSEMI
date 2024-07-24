from django.shortcuts import render
from management_app.models import Senior
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from auth_app.utils import family_required
from django.core.paginator import Paginator
from datetime import date

def calculate_age(birthdate):
    today = date.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day)) + 1

@login_required
@family_required
def list_senior(request):
    user_id = request.user.id
    seniors = Senior.objects.filter(user_id=user_id)
    senior_data = []

    for senior in seniors:
        senior_data.append({
            'senior': senior,
            'age': calculate_age(senior.birthdate),
            'gender_display': '여성' if senior.gender == 'Female' else '남성',
            'has_alzheimers_display': '유' if senior.has_alzheimers else '무',
            'has_parkinsons_display': '유' if senior.has_parkinsons else '무'
        })

    paginator = Paginator(senior_data, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'total_seniors': seniors.count(),
    }
    return render(request, 'management_app/user_senior_list.html', context)