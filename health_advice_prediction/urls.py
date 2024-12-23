from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from health_prediction_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html', next_page='login'), name='logout'),
    path('', views.select_attributes_view, name='select_attributes'),
]