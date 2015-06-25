from django.shortcuts import redirect

def index(request):
    return redirect('/container/lists.html?item=CONT_UNIVERSE')
