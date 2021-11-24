from django.urls import path
from .views import PostsListView, PostDetailView, PostsSearchList, PostsSearchByCategoryList, \
    PostCreateView, PostUpdateView, PostDeleteView


urlpatterns = [
    path('', PostsListView.as_view(), name='home'),
    path('<int:pk>', PostDetailView.as_view(), name='post_detail'),
    path('search/', PostsSearchList.as_view(), name='post_search'),
    path('searchbycategory/', PostsSearchByCategoryList.as_view(), name='post_searchbycategory'),
    path('create/', PostCreateView.as_view(), name='post_create'),
    path('create/<int:pk>', PostUpdateView.as_view(), name='post_update'),
    path('delete/<int:pk>', PostDeleteView.as_view(), name='post_delete'),
]

