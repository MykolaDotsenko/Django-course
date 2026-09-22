from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def saved_state(request):
    return render(request, "travel/saved_state.html")
