from django.contrib import admin
from django.urls import path ,include
from . import views

urlpatterns = [
    path("", views.redirecting,name="redirecting"),
    path("signup", views.signup,name="signup"),

    path("profile/<int:id>", views.profile,name="profile"),
    path("profile/<int:id>/about", views.about,name="about"),
    path("profile/<int:id>/edit",views.edit,name="editProfile"),
    # path("profile/me",views.profile,{"id":},name="userProfile"),

]