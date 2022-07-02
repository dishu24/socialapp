from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup', views.signup, name='signup'),
    path('login', views.loginuser,  name='login'),
    path('logout', views.logout_view, name="logout"),
    path('mainview', views.mainview, name="mainview"),
    path('profile/<str:username>', views.profile, name="profile"),
    path("<str:username>/follow", views.follow, name="followuser"),
    path("<str:username>/unfollow", views.unfollow, name="unfollowuser"),
    path('following', views.following, name='following'),
    path("saved", views.saved, name="saved"),
    path("post/<int:id>/save", views.save_post, name="savepost"),
    path("post/<int:id>/unsave", views.unsave_post, name="unsavepost"),
    path("post/<int:id>/like", views.like_post, name="likepost"),
    path("post/<int:id>/unlike", views.unlike_post, name="unlikepost"),
    path('createpost', views.createpost, name='createpost'),
    path('post/<int:post_id>/delete', views.delete_post , name="deletepost"),
    path('post/<int:post_id>/edit', views.edit_post, name="editpost"),
    path('post/<int:post_id>/comments', views.comment, name="comments"),
    path("post/<int:post_id>/write_comment",views.comment, name="writecomment"),
]
urlpatterns += static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)
