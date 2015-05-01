from django.shortcuts import render
from container.utilities.utils import get_or_create_user_profile

def index(request):
    profile = get_or_create_user_profile(request.user.id)
    return render(request, 'index.html', {'base_template': profile['base_template'], 'profile': profile})