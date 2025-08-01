"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from CarRental import views
from django.conf import settings
from django.conf.urls.static import static
from CarRental.views import user_login


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('manage-client/', views.ManageClient, name='manage_client'),
    path('cars/', views.CarManagement, name='cars_management'),
    path('history/', views.History, name='history'),
    path('available-cars/', views.CarsDisponible, name='available_cars'),  
    path('login/', user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('add_car/', views.add_car, name='add_car'),

    path('cars/delete/<str:car_id>/', views.delete_car, name='delete_car'),
    path('add_reservation/<int:car_id>/', views.add_reservation, name='add_reservation'),

    path('reservation/<int:id>/accept/', views.accept_reservation, name='accept_reservation'),
    path('reservation/<int:id>/decline/', views.decline_reservation, name='decline_reservation'),
    path('reservations/manage/', views.ManageReservation, name='manage_reservation'),
    path('modify-car/', views.modify_car, name='modify_car'),


    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('delete-manager/<str:_id>/', views.delete_manager, name='delete_manager'),
    path('add-manager/', views.add_manager, name='add_manager'),
    path('edit-manager/<str:_id>/', views.edit_manager, name='edit_manager'),

    path('clients/create/', views.add_client, name='create_client'),

    path('clients/delete/<int:client_id>/', views.delete_client, name='delete_client'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

