from django.urls import path
from .views import HomeView, ReportHistoryView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('history/open/<path:fname>/', ReportHistoryView.as_view(), name='open_history_file'),
]
