"""
URL configuration for Task_Module project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Task import views
## for images upload as well
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.homepage, name='home'),
    path('register', views.register, name='register'),
    path('allpage', views.allpage, name='allpage'),
    path('login', views.loginpage, name='login'),
    path('loginpage', views.loginpage, name='loginpage'),
    path('settings', views.settings, name='settings'),
    path('projects', views.projects, name='projects'),
    path('Dash', views.Dash, name='Dash'),
    path('update-task-status/', views.update_task_status, name='update_task_status'),
    path('create-task/', views.create_task, name='create_task'),
    path('delete-task/', views.delete_task, name='delete_task'),
    path('edit-task/<str:task_id>/', views.edit_task, name='edit_task'),
    path('create-project/', views.create_project, name='create_project'),
    path('edit-project/<int:project_id>/', views.edit_project, name='edit_project'),
    path('delete-project/<int:project_id>/', views.delete_project, name='delete_project'),
    path('verify-email/<uuid:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    path('members/', views.members, name='members'),
    path('members/add/', views.add_member, name='add_member'),
    path('members/edit/<int:member_id>/', views.edit_member, name='edit_member'),
    path('members/delete/<int:member_id>/', views.delete_member, name='delete_member'),
    path('members/details/<int:member_id>/', views.get_member_details, name='get_member_details'),
    
    # Password reset URLs
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset-confirm/<uuid:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # Notification URLs
    path('notifications/', views.notifications, name='notifications'),
    path('notification/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notification/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notification/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('notification/delete-all/', views.delete_all_notifications, name='delete_all_notifications'),
    path('notification/count/', views.get_notification_count, name='get_notification_count'),
    path('notification/list/', views.get_notifications_list, name='get_notifications_list'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
