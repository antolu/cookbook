from django.urls import path

from . import views

app_name = 'cookbook'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<slug:slug>/', views.DetailView.as_view(), name='detail'),
    path('add-recipe', views.upload_file, name='upload_recipe'),
]
