from django.urls import path, include

from . import views

app_name = 'cookbook'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<slug:slug>/', views.DetailView.as_view(), name='detail'),
    path('add-recipe', views.upload_file, name='upload_recipe'),
    path('download_yaml/<uuid:pk>', views.download_source, name='download_yaml'),
    path('download_tex/<uuid:pk>', views.download_tex, name='download_tex'),
    path('download_pdf/<uuid:pk>', views.download_pdf, name='download_pdf'),
    path('accounts/', include('django.contrib.auth.urls')),
]
