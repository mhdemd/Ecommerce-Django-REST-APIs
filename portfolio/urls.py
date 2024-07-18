from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "portfolio"

urlpatterns = [
    path(
        "",
        TemplateView.as_view(template_name="portfolio/html/portfolio_index.html"),
        name="portfolio_home",
    ),
    path(
        "taha",
        TemplateView.as_view(template_name="portfolio/html/portfolio_index_taha.html"),
        name="portfolio_home",
    ),
    path("download_cv/", views.download_cv, name="download_cv"),
]
