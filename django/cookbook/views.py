from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views import generic
from .forms import UploadRecipeForm

from .models import Recipe, Tag
from .files import handle_uploaded_file

import logging
log = logging.getLogger(__name__)


# Create your views here.
class IndexView(generic.ListView):
    template_name = 'cookbook/index.html'
    model = Recipe
    # context_object_name = 'recipes_list'

    def get_queryset(self):
        return Recipe.objects.all()


class DetailView(generic.DetailView):
    model = Recipe
    template_name = 'cookbook/detail.html'


def upload_file(request):
    if request.method == 'POST':
        form = UploadRecipeForm(request.POST, request.FILES)
        if form.is_valid():
            log.info('valid form')
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect(reverse('cookbook:index'))
        log.error('invalid form')
    else:
        form = UploadRecipeForm()
        log.error('empty form')
    log.error('returning error')
    return render(request, 'cookbook/index.html', {
        'upload_error': 'File upload failed!',
    })
