from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth import get_user_model

class UserManager(BaseUserManager):
    def create_user(self, email, name, phone_number, password=None, is_staff=False, is_superuser=False):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            phone_number=phone_number,
            is_staff=is_staff,
            is_superuser=is_superuser,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, phone_number, password):
        return self.create_user(
            email,
            name,
            phone_number,
            password,
            is_staff=True,
            is_superuser=True,
        )

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    username = None 
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    phone_number = models.CharField(max_length=20)
    is_staff = models.BooleanField(default=False)      # Required by admin
    is_active = models.BooleanField(default=True)      # Required by admin
    is_superuser = models.BooleanField(default=True)  # Required by PermissionsMixin

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone_number']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name
    
User = get_user_model()

User = get_user_model()

class Book(models.Model):
    name = models.CharField(max_length=200)
    unique_id = models.CharField(max_length=100, unique=True)
    author = models.CharField(max_length=200)
    cover_photo = models.ImageField(upload_to='book_covers/')
    pdf = models.FileField(upload_to='book_pdfs/')
    is_rented = models.BooleanField(default=False)

class BookRentRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('returned', 'Returned'),
        ('return_pending', 'Return Pending'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)