from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views import generic

from .models import Recipe

# Create your views here.


class IndexView(generic.ListView):
    template_name = 'cookbook/index.html'
    context_object_name = 'recipes_list'

    def get_queryset(self):
        return Recipe.objects


class DetailView(generic.DetailView):
    model = Recipe
    template_name = 'cookbook/detail.html'

# class ResultsView(generic.DetailView):
#     model = Question
#     template_name = 'cookbook/results.html'

# def vote(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     try:
#         selected_choice = question.choice_set.get(pk=request.POST['choice'])
#     except (KeyError, Choice.DoesNotExist):
#         return render(request, 'cookbook/detail.html', {
#             'question': question,
#             'error_message': 'You did not select a choice.',
#         })
#     else:
#         selected_choice.votes += 1
#         selected_choice.save() 

#         return HttpResponseRedirect(reverse('cookbook:results', args=(question.id)))
