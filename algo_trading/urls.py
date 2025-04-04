from django.urls import path
from .views import upload_and_run, download_report

urlpatterns = [
    path('', upload_and_run, name='upload'),
    path('download/', download_report, name='download_report'),
]