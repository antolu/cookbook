import json
import logging
import traceback
from os import path
from collections import OrderedDict

import yaml
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.urls import reverse
from django.views import generic
from django.contrib import messages

from cookbook.io.files import handle_uploaded_file
from .forms import UploadRecipeForm
from .io.recipefile import RecipeFile
from .models import Recipe
from cookbook.io.latex import compile, write_recipe
from qml import to_string

log = logging.getLogger(__name__)


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

        context['recipe'].cooking_time = to_string(context['recipe'].cooking_time)

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
            except (KeyError, NameError, MemoryError, ValueError) as err:
                traceback.print_exc()
                log.error(str(err))
                messages.add_message(request, messages.ERROR, f'File upload failed: {str(err)}')
                return HttpResponseRedirect(reverse('cookbook:index'))
    else:
        form = UploadRecipeForm()
    return HttpResponseRedirect(reverse('cookbook:index'), {
        'upload_error': 'File upload failed!',
    })


def download_yaml(request, pk):
    recipe = Recipe.objects.get(pk=pk).__dict__

    recipe_file = RecipeFile(recipe, format='django')
    output = recipe_file.to_qml()

    response = HttpResponse(content_type='text/yaml')
    response['Content-Disposition'] = 'attachment; filename="{}.rcp"'.format(recipe.title.lower().replace(' ', '_'))

    yaml.dump(output, response)

    return response


def download_tex(request, pk):
    recipe = Recipe.objects.get(pk=pk)

    response = HttpResponse(content_type='text/tex')
    response['Content-Disposition'] = 'attachment; filename="{}.tex"'.format(recipe.title.lower().replace(' ', '_'))

    recipe_file = RecipeFile(recipe, format='django')
    data = recipe_file.to_qml()

    response.write(write_recipe(data, raw_buffer=True))

    return response


def download_pdf(request, pk):
    recipe = Recipe.objects.get(pk=pk)

    recipe_file = RecipeFile(recipe, format='django')
    data = recipe_file.to_qml()

    out_base = path.join('output', recipe.name).lower()
    out_tex = out_base + '.tex'
    out_pdf = out_base + '.pdf'

    write_recipe(data, out_tex)

    compile(out_tex)

    response = FileResponse(open(out_pdf, 'rb'), as_attachment=True, filename='{}.pdf'.format(recipe.title.lower().replace(' ', '_')))

    return response
