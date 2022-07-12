from django.shortcuts import render


# Create your views here.
def v_home(request):
    return render(request, "home.html", {})
