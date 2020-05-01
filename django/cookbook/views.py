import json
import logging
from collections import OrderedDict

import yaml
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from .files import handle_uploaded_file
from .forms import UploadRecipeForm
from .models import Recipe
from .parsers import recipe_to_dict, format_for_output

log = logging.getLogger(__name__)

represent_dict_order = lambda self, data: self.represent_mapping('tag:yaml.org,2002:map', data.items())
yaml.add_representer(OrderedDict, represent_dict_order)


# Create your views here.
class IndexView(generic.ListView):
    template_name = 'cookbook/index.html'
    model = Recipe
    context_object_name = 'recipe_list'

    def get_queryset(self):
        return Recipe.objects.all()


class DetailView(generic.DetailView):
    model = Recipe
    template_name = 'cookbook/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)

        # Load the jsonified elements into python dictionaries
        context['recipe'].ingredients = json.loads(context['recipe'].ingredients)
        context['recipe'].instructions = json.loads(context['recipe'].instructions)
        context['recipe'].changelog = json.loads(context['recipe'].changelog)

        return context


def upload_file(request):
    if request.method == 'POST':
        form = UploadRecipeForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect(reverse('cookbook:index'))
    else:
        form = UploadRecipeForm()
    return render(request, 'cookbook/index.html', {
        'upload_error': 'File upload failed!',
    })


def download_yaml(request, pk):
    recipe = Recipe.objects.get(pk=pk)

    data = recipe_to_dict(recipe)
    formatted_data = format_for_output(data)

    response = HttpResponse(content_type='text/yaml')
    response['Content-Disposition'] = 'attachment; filename="{}.yml"'.format(recipe.title).replace('-', '_')

    yaml.dump({'recipe': formatted_data}, response)

    return response
