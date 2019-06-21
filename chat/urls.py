from django.urls   import path

from . import views
app_name = 'chat'
urlpatterns = [
    path("", views.index, name='index'),
    path("<str:slug>/", views.create_dialogbox, name='create_dialog'),
    path("<str:slug>/<int:room_id>/", views.room, name = 'room'),
]