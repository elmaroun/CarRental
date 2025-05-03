from django.db import models
from decimal import Decimal
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import auth
from djongo.models import ObjectIdField
from djongo import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    _id = models.ObjectIdField()
    email = models.EmailField(_('email address'), unique=True)
    full_name = models.CharField(max_length=255)
    username = models.CharField(_('username'), max_length=150, unique=True)
    role = models.CharField(max_length=50, choices=[('admin', 'Admin'), ('manager', 'Manager')])
    created_at = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # This fixes the AttributeError

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_manager(self):
        return self.role == 'manager'

class Client(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    cin = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.full_name

class Car(models.Model):
    url_img = models.CharField(max_length=255,default=None)
    brand = models.CharField(max_length=255) 
    fuel_type = models.CharField(max_length=100)
    transmission = models.CharField(max_length=100) 
    number_of_seats = models.IntegerField()
    price_per_day = models.DecimalField( max_digits=10, decimal_places=2, default=0.00)   
    date_added = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.brand

class Reservation(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')])
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
      
    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days + 1
    
    @property
    def total_price(self):
        if hasattr(self, 'car') and self.car.price_per_day:
            # Convert Decimal128 to Python Decimal if needed
            daily_rate = Decimal(str(self.car.price_per_day))
            return daily_rate * Decimal(self.duration_days)
        return Decimal('0.00')

    def _str_(self):
        return f"Reservation {self.id} by {self.client.full_name}"
