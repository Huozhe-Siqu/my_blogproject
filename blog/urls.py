from django.urls import path
from . import views

app_name = 'blog'
urlpatterns = [
    # path("",views.index,name="index"),
    path("",views.IndexView.as_view(),name="index"),
    # path("posts/<int:pk>/",views.detail,name="detail"),
    path("posts/<int:pk>/",views.PostDetailView.as_view(),name="detail"),
    path("archives/<int:year>/<int:month>/",views.archive,name="archive"),
    # path("categories/<int:pk>/",views.category,name="category"),
    path("categories/<int:pk>/",views.CategoryView.as_view(),name="category"),
    path("tags/<int:pk>/",views.tag,name="tag"),
    path("search/",views.search,name="search"),
]