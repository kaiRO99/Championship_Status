from django.urls import path
from . import views

#paths
urlpatterns = [
    path("", views.home, name = 'home'),#to base url, called home, calls views.home 
    path("f1/", views.f1, name = 'f1'),
    path("laliga/", views.laliga, name = 'laliga'),
    path("premierleague/", views.premier_league, name = 'premierleague'),
]