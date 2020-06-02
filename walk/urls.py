from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('show', views.show, name='show'),
    path('update', views.update, name='update'),
    path('prepupdate', views.prepupdate, name='prepupdate'),
]