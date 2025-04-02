from django.contrib import admin
from django.urls import path
from Courserecommend.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name="home" ),
    path('recommend/', home, name="recommend" ),
    path('login/', login, name="login" ),
    path('register/', register, name="register" ),
    path('logout/', logout, name="logout" ),
]
