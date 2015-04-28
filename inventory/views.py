from django.shortcuts import render

def index(request):
    return render(request, 'index.html', {'base_template': 'gso_fr.html'})