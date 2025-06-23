from django.urls import path
from . import views

urlpatterns = [
    path('', views.iso_list_html, name='iso_list_html'),

    # ✅ download-excel আগে লিখতে হবে
    path('download-excel/', views.iso_download_excel, name='iso_download_excel'),

    # ❗️এইটা সবশেষে রাখুন যাতে যেকোনো slug match না হয়
    path('iso/<slug:slug>/', views.iso_detail_json, name='iso_detail_json'),
]

