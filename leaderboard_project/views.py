from django.http import HttpResponse

def homepage(request):
    return HttpResponse("<h1>Welcome to My Site</h1><p>This is the homepage.</p>")
