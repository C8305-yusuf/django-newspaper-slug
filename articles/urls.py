# We'll have a ListView to list all articles and a DetailView for individual articles.
# Tüm makaleleri listelemek için bir ListView'e ve bireysel makaleler için bir DetailView'a sahip olacağız.

from django.urls import path

from .views import ArticleListView, ArticleDetailView

urlpatterns = [
    path('<slug:slug>', ArticleDetailView.as_view(), name='article_detail'),
    path('', ArticleListView.as_view(), name='article_list'),
]