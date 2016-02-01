from django.shortcuts import render
from forms import ProjectForm


def index(request):
    context = {
        'form': ProjectForm()
    }
    return render(request, 'ids_projects/index.html', context)
