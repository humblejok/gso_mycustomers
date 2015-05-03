from container.utilities.utils import get_or_create_user_profile
from django.shortcuts import render

def index(request):
    if request.user.is_authenticated():
        profile = get_or_create_user_profile(request.user.id)
        return render(request, 'index.html', {'base_template': profile['base_template'], 'profile': profile})
    else:
        return render(request, 'index.html', {'base_template': 'gso_en.html', 'profile': None})