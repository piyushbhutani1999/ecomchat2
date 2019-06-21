from django.urls import path
from . import views
from django.conf.urls import url

app_name="accounts"


urlpatterns = [
    path('', views.HomePageView.as_view(), name= 'home'),
    path('delete/',views.delete_user, name = 'delete_user'),
    path('signup/',views.register_user, name = 'signup'),
    path('login/', views.login_user, name = 'login'),
    path('logout/', views.logout_view, name = 'logout'),
    path('profile/', views.profile_view, name = 'profile'),
    path('aboutus/', views.AboutUsPageView.as_view(), name= 'aboutus'),
    path('contactus/', views.ContactUsPageView.as_view(), name= 'contactus'),
    path('profile/update/', views.update_user_profile, name= 'update_user_profile'),
    path('profile/myad/', views.my_ads_view, name = 'myads'),
    path('profile/myad/editad/<str:slug>', views.edit_product, name = 'editad'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
  

]
