from django.shortcuts import render
from auth_app.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def find_user_id(request):
    if request.method == "GET":
        return render(request, "auth_app/find_user_id.html")

    if request.method == "POST":
        email = request.POST["email"]

        try:
            user = User.objects.get(email=email)
            return JsonResponse({'success': True, 'username': user.username})
        except User.DoesNotExist:
            return JsonResponse({'success': False})
    return render(request, 'auth_app/find_user_id.html')