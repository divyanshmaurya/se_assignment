"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("polls/", include("polls.urls")),
    path("admin/", admin.site.urls),
    # Send visitors of the bare domain to the polls app.
    path("", RedirectView.as_view(pattern_name="polls:index")),
]
