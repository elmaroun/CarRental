from django.shortcuts import render, redirect
from django.db.models import Count
from django.utils import timezone
from .models import Car
from .models import Client 
from .models import Reservation 
from django.utils import timezone
from django.db import connection
from bson.objectid import ObjectId
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from datetime import datetime, timedelta
from django.db.models.functions import TruncMonth
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth import get_user_model
from .backends import MongoDBAuthBackend
import json
from django.db.models.functions import ExtractMonth, ExtractYear



User = get_user_model()

def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        print(f"Attempting login with username: {username}")  
        print(f"Attempting login with username: {password}")  # Debug
# Debug
        
        user = MongoDBAuthBackend().authenticate(request, username=username, password=password)
        
        if user is not None:
            auth.login(request, user)
            print(f"Successfully logged in user: {user.email}")  # Debug
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
            print("Login failed")
            print(user)  # Debug
    
    return render(request, 'CarRental/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

def dashboard(request):
    TotalReservation = Reservation.objects.count()
    TotalReservationPending= Reservation.objects.filter(
        status='pending'
        ).count()
    TotalCars= Car.objects.count()
    TotalClient= Client.objects.count()


    
        
    context = {
    'TotalReservation': TotalReservation,
    'TotalReservationPending': TotalReservationPending,
    'TotalCars': TotalCars,
    'TotalClient': TotalClient,

}

    return render(request, 'CarRental/index.html',context)



def ManageReservation(request):
    reservations = Reservation.objects.filter(
        status='pending'
    ).select_related('client', 'car')
    
    return render(request, 'CarRental/MnagaeReservation.html', {'reservations': reservations})

def ManageClient(request):
    clients = Client.objects.annotate(
        reservation_count=Count('reservation')
    ).all()
    return render(request, 'CarRental/ManageClient.html', {'clients': clients})
def CarsDisponible(request):
    cars = Car.objects.all()
    return render(request, 'CarRental/cars.html',{'cars': cars})

def CarManagement(request):
    now = timezone.now()
    
    try:
        with connection['default'].cursor() as cursor:
            reserved_car_ids = cursor.db['carrental_reservation'].find({
                'status': 'confirmed',
                'start_date': {'$lte': now},
                'end_date': {'$gte': now}
            }).distinct('car_id')
            
            # Convert ObjectIds to strings for comparison
            reserved_car_ids = [str(car_id) for car_id in reserved_car_ids]
            
            # Get available cars (not in reserved list)
            available_cars = list(cursor.db['carrental_car'].find({
                '_id': {'$nin': reserved_car_ids}
            }))
            
            # Convert MongoDB documents to Django-like objects
            for car in available_cars:
                car['id'] = str(car['_id'])
                car['is_available'] = True
    
        return render(request, 'CarRental/carManagement.html', {
            'cars': available_cars
        })
        
    except Exception as e:
        # Handle any database errors gracefully
        available_cars = []
        return render(request, 'CarRental/carManagement.html', {
            'cars': available_cars,
            'error': str(e)
        })

def History(request):
    reservations = Reservation.objects.exclude(
        status='pending'
    ).select_related('client', 'car').all()
    
    return render(request, 'CarRental/history.html', {'reservations': reservations})