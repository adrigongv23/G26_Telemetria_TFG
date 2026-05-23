from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required # Esto obliga a que el usuario tenga que loguearse antes de ver la web
def index(request):
    # 'request.user' contiene los datos del usuario que está navegando
    return render(request, 'index.html')