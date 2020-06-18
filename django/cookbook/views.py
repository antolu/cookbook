import json
import logging
from os import path
import traceback
from collections import OrderedDict

import yaml
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.urls import reverse
from django.views import generic
from django.contrib import messages

from .files import handle_uploaded_file
from .forms import UploadRecipeForm
from .models import Recipe
from qml.parsers import recipe_to_dict, format_for_output
from .file_io import compile, write_recipe
from qml.mappings import TypeParser

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

        context['recipe'].cooking_time = TypeParser.duration_str(context['recipe'].cooking_time)

        return context


def upload_file(request):
    if request.method == 'POST':
        form = UploadRecipeForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                files = request.FILES.getlist('file')
                for f in files:
                    handle_uploaded_file(f)
                return HttpResponseRedirect(reverse('cookbook:index'), {
                    'upload_success': 'Files successfully uploaded!'
                })
            except (KeyError, NameError, MemoryError) as err:
                # traceback.print_exc()
                log.error(str(err))
                messages.add_message(request, messages.ERROR, f'File upload failed: {str(err)}')
                return HttpResponseRedirect(reverse('cookbook:index'))
    else:
        form = UploadRecipeForm()
    return HttpResponseRedirect(reverse('cookbook:index'), {
        'upload_error': 'File upload failed!',
    })


def download_yaml(request, pk):
    recipe = Recipe.objects.get(pk=pk)

    data = recipe_to_dict(recipe)
    formatted_data = format_for_output(data)

    response = HttpResponse(content_type='text/yaml')
    response['Content-Disposition'] = 'attachment; filename="{}.yml"'.format(recipe.title.lower().replace(' ', '_'))

    yaml.dump(formatted_data, response)

    return response


def download_tex(request, pk):
    recipe = Recipe.objects.get(pk=pk)

    response = HttpResponse(content_type='text/tex')
    response['Content-Disposition'] = 'attachment; filename="{}.tex"'.format(recipe.title.lower().replace(' ', '_'))

    data = format_for_output(recipe_to_dict(recipe))

    response.write(write_recipe(data, raw_buffer=True))

    return response


def download_pdf(request, pk):
    recipe = Recipe.objects.get(pk=pk)

    data = format_for_output(recipe_to_dict(recipe))

    out_base = path.join('output', recipe.title).lower()
    out_tex = out_base + '.tex'
    out_pdf = out_base + '.pdf'

    write_recipe(out_tex, data)

    compile(out_tex)

    response = FileResponse(open(out_pdf, 'rb'), as_attachment=True, filename='{}.pdf'.format(recipe.title.lower().replace(' ', '_')))

    return response
