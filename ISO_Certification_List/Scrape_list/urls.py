from django.urls import path
from .views import iso_list_html, iso_detail_json

urlpatterns = [
    path("", iso_list_html, name="iso_list_html"),
    path("<slug:slug>/", iso_detail_json, name="iso_detail_json"),
]
