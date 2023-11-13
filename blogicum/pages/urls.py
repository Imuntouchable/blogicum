from . import views

from django.urls import path


app_name = 'pages'

urlpatterns = [
    path('about/', views.AboutView.as_view(),
         name='about'),
    path('rules/', views.RulesView.as_view(),
         name='rules'),
]
