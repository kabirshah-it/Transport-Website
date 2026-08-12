from django.urls import path
from . import views
urlpatterns = [
    # path('', views.main, name='main'),
    path('home/', views.home, name="home"),
    path("quote/details/", views.quote_details, name="quote_details"),
    path(
        "quoteSuccess/<int:quote_id>/",
        views.quote_success,
        name="quoteSuccess"
    ),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services')
]