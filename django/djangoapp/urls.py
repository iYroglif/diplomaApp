from django.urls import path

from . import views

urlpatterns = [
    path('upload', views.upload, name='upload'),
    path('file-props/<int:file_id>', views.file_props, name='file-props'),
    path('file-preview/<int:file_id>', views.file_preview, name='file-preview'),
    path('file-preview-denoised/<int:file_id>', views.file_preview_denoised, name='file-preview-denoised'),
    path('progress/<int:file_id>', views.progress, name='progress'),
    path('download/<int:file_id>', views.download, name='download'),
    path('login', views.login_view, name='login'),
    path('register', views.register, name='register'),
    path('history', views.history, name='history'),
    path('logout', views.logout_view, name='logout'),
]
