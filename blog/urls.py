from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views, feed

app_name = 'blog'
urlpatterns = [
    path("sim/", views.SimIndexView.as_view(), name="sim"),
    path("sim/<int:pk>", views.SimDetailView.as_view(), name='sim_detail'),
    path("sim/archive/<int:year>/<int:month>", views.SimArchivesView.as_view(), name='sim_archive'),
    path("sim/category/<str:name>", views.SimCategoryView.as_view(), name='sim_category'),
    path("sim/tag/<str:name>", views.SimTagView.as_view(), name='sim_tag'),
    path("sim/search/", views.NSearchView.as_view(), name='sim_search'),

    path("argon/", views.ArgonIndexView.as_view(), name='argon'),
    path("argon/<int:pk>", views.ArgonDetailView.as_view(), name='argon_detail'),
    path("argon/archive/", views.ArgonArchiveView.as_view(), name='argon_archive'),
    path("argon/category/<str:name>", views.ArgonCategoryView.as_view(), name='argon_category'),
    path("argon/tag/", views.ArgonAllTagView.as_view(), name='argon_all_tag'),
    path("argon/tag/<str:name>", views.ArgonTagView.as_view(), name='argon_tag'),
    path("argon/search/", views.NSearchView.as_view(), name='argon_search'),

    path("posts/feed/", feed.RssFeed(), name='rss')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
