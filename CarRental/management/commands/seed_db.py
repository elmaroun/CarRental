from django.core.management.base import BaseCommand
from CarRental.models import User, Client, Car, Reservation
from faker import Faker
import random
from datetime import timedelta, date

fake = Faker()

class Command(BaseCommand):
    help = 'Seed the database with fake data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')
        self.create_users(5)
        self.create_clients(10)
        self.create_cars(10)
        self.create_reservations(20)
        self.stdout.write(self.style.SUCCESS('Database seeded successfully.'))

    def create_users(self, total):
        roles = ['admin', 'manager']
        for _ in range(total):
            User.objects.create(
                full_name=fake.name(),
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                password=fake.password(length=12),
                role=random.choice(roles)
            )

    def create_clients(self, total):
        for _ in range(total):
            Client.objects.create(
                full_name=fake.name(),
                email=fake.unique.email(),
                phone=fake.phone_number(),
                cin=fake.random.randint(2, 7)
            )

    def create_cars(self, total):
        brands = ['Toyota', 'Honda', 'Ford', 'BMW', 'Audi', 'Mercedes', 'Tesla']
        fuel_types = ['Petrol', 'Diesel', 'Electric', 'Hybrid']
        transmissions = ['Manual', 'Automatic']
        car_images = [
            '/media/cars/toyota.jpg',
        ]

        for _ in range(total):
            Car.objects.create(
                brand=random.choice(brands),
                fuel_type=random.choice(fuel_types),
                transmission=random.choice(transmissions),
                number_of_seats=random.randint(2, 7),
                price_per_day=round(random.uniform(30.0, 200.0), 2),
                url_img=random.choice(car_images)
            )

    def create_reservations(self, total):
        clients = list(Client.objects.all())
        cars = list(Car.objects.all())
        statuses = ['pending', 'confirmed', 'cancelled']

        if not clients or not cars:
            self.stdout.write(self.style.WARNING('No clients or cars to create reservations.'))
            return

        for _ in range(total):
            client = random.choice(clients)
            car = random.choice(cars)

            start_date = fake.date_between(start_date='-30d', end_date='today')
            end_date = start_date + timedelta(days=random.randint(1, 14))

            # Save the client and car if they are not already saved
            if not client.pk:  # Check if the client is already saved (has a primary key)
                client.save()

            if not car.pk:  # Check if the car is already saved (has a primary key)
                car.save()

            # Create the reservation
            Reservation.objects.create(
                client=client,
                car=car,
                status=random.choice(statuses),
                start_date=start_date,
                end_date=end_date
            )