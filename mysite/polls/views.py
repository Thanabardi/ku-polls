from django.http import HttpResponse


def index(request):
    return HttpResponse("Oh..hi, you’re a bit too early. We are just getting started.")