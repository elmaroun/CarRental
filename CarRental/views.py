import os
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
from django.core.exceptions import ValidationError
from django.conf import settings
import traceback
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
import traceback
from django.http import JsonResponse
from decimal import Decimal, InvalidOperation
from djongo.models import ObjectIdField





User = get_user_model()

def user_login(request):
    if request.user.is_authenticated:
        # Redirect based on role if already logged in
        if request.user.role == 'admin':
            return redirect('admin_dashboard')  # We'll create this view
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        user = MongoDBAuthBackend().authenticate(request, username=username, password=password)
        
        if user is not None:
            auth.login(request, user)
            
            # Redirect based on role
            if user.role == 'admin':
                return redirect('admin_dashboard')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'CarRental/login.html')


def user_logout(request):
    logout(request)
    return redirect('login')

def dashboard(request):
    try:
        TotalReservation = Reservation.objects.count()
        TotalReservationPending = Reservation.objects.filter(status='pending').count()
        TotalCars = Car.objects.count()
        TotalClient = Client.objects.count()

        one_year_ago = timezone.now() - timedelta(days=365)
        
        reservations = Reservation.objects.filter(
            created_at__gte=one_year_ago
        ).values_list('created_at', flat=True)
        
        from collections import defaultdict
        monthly_counts = defaultdict(int)
        
        for date in reservations:
            key = date.strftime('%Y-%m')  
            monthly_counts[key] += 1
        
        sorted_months = sorted(monthly_counts.items())
        months = [datetime.strptime(m[0], '%Y-%m').strftime('%B %Y') for m in sorted_months]
        counts = [m[1] for m in sorted_months]
        

        status_counts = Reservation.objects.values('status').annotate(
            count=Count('id')
            ).order_by('status')
        
        # Prepare data for the pie chart
        status_labels = []
        status_data = []
        status_colors = {
            'cancelled': '#f44336',   # Red
            'confirmed': '#4caf50',  # Green
            'pending': '#ffc107'    # Yellow
        }
        
        for item in status_counts:
            status_labels.append(item['status'].capitalize())
            status_data.append(item['count'])
        
        context = {
            'TotalReservation': TotalReservation,
            'TotalReservationPending': TotalReservationPending,
            'TotalCars': TotalCars,
            'TotalClient': TotalClient,
            'months': months,
            'counts': counts,
            'status_labels': status_labels,
            'status_data': status_data,
            'status_colors': list(status_colors.values())
        }
        return render(request, 'CarRental/index.html', context)
    
    except Exception as e:
        # For debugging - remove in production
        import traceback
        traceback.print_exc()
        return render(request, 'error.html', {'error': str(e)})



def ManageClient(request):
    clients = Client.objects.annotate(
        reservation_count=Count('reservation')
    ).all()
    return render(request, 'CarRental/ManageClient.html', {'clients': clients})

def delete_car(request,car_id):
    car = Car.objects.get(id=car_id)
    car.delete()
    return redirect('available_cars') 

def CarManagementt(request):
    target_date =  timezone.now().date()

    try:
        # Obtenir les voitures réservées à cette date
        reserved_car_ids = Reservation.objects.filter(
            end_date__gte=target_date,
            start_date__lte=target_date
        ).values_list('car_id', flat=True)

        # Obtenir les voitures non réservées
        available_cars = Car.objects.exclude(id__in=list(reserved_car_ids))
        
        return render(request, 'CarRental/carManagement.html', {
            'cars': available_cars
        })
        
    except Exception as e:
        error_details = traceback.format_exc()  # full traceback
        messages.error(request, "Error fetching cars. Check logs for details.")
        print(error_details)  # or use logging.error(error_details)
        return render(request, 'CarRental/carManagement.html', {
            'cars': [],
            'error': error_details
        })

from django.db.models import Q

def CarManagementtt(request):
    brand = request.GET.get('brand', '').strip()
    start_date = parse_date(request.GET.get('start_date', ''))
    end_date = parse_date(request.GET.get('end_date', ''))

    try:
        # Start with all cars
        cars = Car.objects.all()

        # Filter by brand if given
        if brand:
            cars = cars.filter(brand__icontains=brand)

        # If both dates are provided, filter out cars that are reserved during that period
        if start_date and end_date:
            reserved_car_ids = Reservation.objects.filter(
                start_date__lte=end_date,
                end_date__gte=start_date
            ).values_list('car_id', flat=True)

            cars = cars.exclude(id__in=reserved_car_ids)

        return render(request, 'CarRental/carManagement.html', {
            'cars': cars
        })

    except Exception as e:
        error_details = traceback.format_exc()
        messages.error(request, "Error fetching cars. Check logs for details.")
        print(error_details)
        return render(request, 'CarRental/carManagement.html', {
            'cars': [],
            'error': error_details
        })

def CarManagement(request):
    brand = request.GET.get('brand', '').strip()
    start_date = parse_date(request.GET.get('start_date', ''))
    end_date = parse_date(request.GET.get('end_date', ''))

    try:
        cars = Car.objects.all()

        if brand:
            cars = cars.filter(brand__icontains=brand)

        # Filter only if both start and end date are provided
        if start_date and end_date:
            # Get reservations that are confirmed and intersect with selected period
            reserved_car_ids = Reservation.objects.filter(
                status='confirmed',
                start_date__lte=end_date,
                end_date__gte=start_date
            ).values_list('car_id', flat=True)

            # Exclude those cars from the list
            cars = cars.exclude(id__in=reserved_car_ids)

        return render(request, 'CarRental/carManagement.html', {
            'cars': cars
        })

    except Exception as e:
        error_details = traceback.format_exc()
        messages.error(request, "Error fetching cars. Check logs for details.")
        print(error_details)
        return render(request, 'CarRental/carManagement.html', {
            'cars': [],
            'error': error_details
        })

def History(request):
    reservations = Reservation.objects.exclude(status='pending').select_related('client', 'car')

    client_name = request.GET.get('client_name', '').strip()
    car_name = request.GET.get('car_name', '').strip()
    status = request.GET.get('status', '').strip()

    if client_name:
        reservations = reservations.filter(client__full_name__icontains=client_name)

    if car_name:
        reservations = reservations.filter(car__brand__icontains=car_name)

    if status:
        reservations = reservations.filter(status=status)

    context = {
        'reservations': reservations,
        'client_name': client_name,
        'car_name': car_name,
        'status': status,
    }
    return render(request, 'CarRental/history.html', context)


def add_car(request):
    if request.method == 'POST':
        # Initialize error message
        error_message = None
        
        # Get form data
        brand = request.POST.get('brand', '').strip()
        fuel_type = request.POST.get('fuel_type', '').strip()
        transmission = request.POST.get('transmission', '').strip()
        
        # Validate required text fields
        if not all([brand, fuel_type, transmission]):
            error_message = "Please fill all required fields"
        
        # Validate and convert numbers
        try:
            number_of_seats = int(request.POST.get('number_of_seats', 0))
            price_per_day = float(request.POST.get('price_per_day', 0.0))
        except (TypeError, ValueError):
            error_message = "Please enter valid numbers for seats and price"
        
        # Validate image
        image = request.FILES.get('url_img')
        if not image:
            error_message = "Please upload an image"
        
        # If no errors, proceed with saving
        if not error_message:
            try:
                # Create upload directory
                upload_dir = os.path.join(settings.MEDIA_ROOT, 'cars')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Generate unique filename
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"{timestamp}_{image.name}"
                file_path = os.path.join(upload_dir, filename)
                
                # Save the file
                with open(file_path, 'wb+') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)
                    
                # Create and save car
                car = Car(
                    url_img=f"/media/cars/{filename}",  # Full path as requested
                    brand=brand,
                    fuel_type=fuel_type,
                    transmission=transmission,
                    number_of_seats=number_of_seats,
                    price_per_day=price_per_day
                )
                car.save()
                
                messages.success(request, "Car added successfully!")
                return redirect('available_cars')            
            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
        
            return render(request, 'CarRental/add_car.html', {
                'error_message': error_message,
                'form_data': request.POST  # Preserve form inputs
            })
        return render(request, 'CarRental/add_car.html')
    if request.method == 'POST':
        try:
            # Get form data with proper validation
            brand = request.POST.get('brand', '').strip()
            fuel_type = request.POST.get('fuel_type', '').strip()
            transmission = request.POST.get('transmission', '').strip()
            
            # Convert numbers with validation
            try:
                number_of_seats = int(request.POST.get('number_of_seats', 0))
                price_per_day = float(request.POST.get('price_per_day', 0.0))
            except (TypeError, ValueError):
                raise ValidationError("Invalid number input")

            # Validate required fields
            if not all([brand, fuel_type, transmission]):
                raise ValidationError("Please fill all required fields")

            # Handle image upload
            image = request.FILES.get('url_img')
            if not image:
                raise ValidationError("Please upload an image")

            # Create upload directory
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'car_images')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{timestamp}_{image.name}"
            file_path = os.path.join(upload_dir, filename)
            
            # Save the file
            with open(file_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
            
            # Create and save car
            car = Car(
                url_img=os.path.join('car_images', filename),
                brand=brand,
                fuel_type=fuel_type,
                transmission=transmission,
                number_of_seats=number_of_seats,
                price_per_day=price_per_day
            )
            car.save()
            
            return redirect('success_page')
            
        except ValidationError as e:
            error_message = str(e)
            # You can pass this error back to the template
            return render(request, 'CarRental/add_car.html', {'error_message': error_message})

    return render(request, 'CarRental/add_car.html')

def add_reservation(request, car_id):
    try:
        car = Car.objects.get(id=car_id)
        
        if request.method == 'POST':
            # Parse datetime strings
            start_date = parse_date(request.POST.get('start_date'))
            end_date = parse_date(request.POST.get('end_date'))

            if not start_date or not end_date:
                raise ValueError("Invalid date format")
            # Get form data
            cin = request.POST.get('cin')
            client_name = request.POST.get('full_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            
            # Check if client exists by CIN
            try:
                client = Client.objects.get(cin=cin)
                # Update existing client info if needed
                client.full_name = client_name
                client.email = email
                client.phone = phone
                client.save()
            except Client.DoesNotExist:
                # Create new client
                client = Client.objects.create(
                    full_name=client_name,
                    email=email,
                    phone=phone,
                    cin=cin
                )
            
            # Create reservation
            Reservation.objects.create(
                client=client,
                car=car,
                start_date=start_date,
                end_date=end_date,
                status='pending'  # or 'confirmed' depending on your workflow
            )
            
            messages.success(request, "Reservation created successfully!")
            return redirect('manage_reservation')            
            
        return render(request, 'CarRental/add_reservation.html', {
            'car': car,
            'today': timezone.now().strftime('%Y-%m-%dT%H:%M')
        })
        
    except Car.DoesNotExist:
        messages.error(request, "Car not found")
        return redirect('cars_overview')
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return render(request, 'CarRental/add_reservation.html', {
            'car': car,
            'error_message': str(e),
            'today': timezone.now().strftime('%Y-%m-%dT%H:%M')
        })

def accept_reservation(request, id):
    reservation = get_object_or_404(Reservation, id=id)
    reservation.status = 'confirmed'
    reservation.save()
    return redirect('history')

def decline_reservation(request, id):
    reservation = get_object_or_404(Reservation, id=id)
    reservation.status = 'cancelled'
    reservation.save()
    return redirect('history')


def ManageReservation(request):
    reservations = Reservation.objects.filter(status='pending').select_related('client', 'car')

    client_name = request.GET.get('client_name', '').strip()
    car_name = request.GET.get('car_name', '').strip()

    if client_name:
        reservations = reservations.filter(client__full_name__icontains=client_name)

    if car_name:
        reservations = reservations.filter(car__brand__icontains=car_name)  # Adjust if your car name is in another field

    context = {
        'reservations': reservations,
        'client_name': client_name,
        'car_name': car_name
    }
    return render(request, 'CarRental/MnagaeReservation.html',context)


def ManageClient(request):
    clients = Client.objects.annotate(
        reservation_count=Count('reservation')
    ).all()
    
    # Get search parameters from GET request
    client_name = request.GET.get('client_name', '').strip()
    cin = request.GET.get('cin', '').strip()
    
    # Apply filters if they exist
    if client_name:
        clients = clients.filter(full_name__icontains=client_name)
    
    if cin:
        clients = clients.filter(cin__icontains=cin)
    
    context = {
        'clients': clients,
        'client_name': client_name,
        'cin': cin
    }
    return render(request, 'CarRental/ManageClient.html', context)

def CarsDisponible(request):
    cars = Car.objects.all()
    car_name = request.GET.get('car_name', '').strip()
    price_range = request.GET.get('price_range', '').strip()

    # Filter by car name
    if car_name:
        cars = cars.filter(brand__icontains=car_name)

    # Filter and sort by price only if price_range is provided
    if price_range:
        if price_range == 'under_100':
            cars = cars.filter(price_per_day__lt=100)
        elif price_range == '100_250':
            cars = cars.filter(price_per_day__gte=100, price_per_day__lte=250)
        elif price_range == '250_500':
            cars = cars.filter(price_per_day__gte=250, price_per_day__lte=500)
        elif price_range == '500_1000':
            cars = cars.filter(price_per_day__gte=500, price_per_day__lte=1000)
        elif price_range == 'over_1000':
            cars = cars.filter(price_per_day__gt=1000)

        # Sort by price when filtering by price
        cars = cars.order_by('price_per_day')
    else:
        # Default sort by brand (car name)
        cars = cars.order_by('brand')

    context = {
        'cars': cars,
        'car_name': car_name,
        'price_range': price_range,
    }
    return render(request, 'CarRental/cars.html', context)


def modify_car(request):
    if request.method == 'POST':
        try:
            car_id = request.POST.get('car_id')
            car = Car.objects.get(id=car_id)
            
            # Update fields
            car.brand = request.POST.get('carBrand')
            car.fuel_type = request.POST.get('carFuel')
            car.transmission = request.POST.get('carTransmission')
            car.number_of_seats = int(request.POST.get('carSeats'))
            car.price_per_day = request.POST.get('carPrice')
            
            # Handle file upload
            if 'carImage' in request.FILES:
                uploaded_file = request.FILES['carImage']
                # Generate a new filename or use the original
                car.url_img = f"/media/cars/{uploaded_file.name}"
                # Save the file to your media directory
                with open(f"media/cars/{uploaded_file.name}", 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
            
            car.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def admin_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
    
    managers = User.objects.filter(role='manager')

    context = {
        'managers': managers
    }
    return render(request, 'CarRental/admin_dashboard.html', context)

def add_manager(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
    
    if request.method == 'POST':
        # Process form data
        email = request.POST.get('email')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        
        try:
            # Create new manager user
            user = User.objects.create_user(
                email=email,
                password=password,
                full_name=full_name,
                username=username,
                role='manager'
            )
            messages.success(request, 'Manager added successfully!')
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f'Error adding manager: {str(e)}')
    
    return render(request, 'CarRental/add_manager.html')
from bson.objectid import ObjectId
from django.shortcuts import get_object_or_404

def delete_manager(request, _id):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
    
    try:
        # Convert string ID to ObjectId and use _id field for querying
        manager = User.objects.get(_id=ObjectId(_id))
        manager.delete()
        messages.success(request, 'Manager deleted successfully!')
    except User.DoesNotExist:
        messages.error(request, 'Manager not found!')
    except Exception as e:
        messages.error(request, f'Error deleting manager: {str(e)}')
    
    return redirect('admin_dashboard')