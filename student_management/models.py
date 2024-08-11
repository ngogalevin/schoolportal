from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password, check_password
class StudentManager(BaseUserManager):
    def create_user(self, registration_number, email, password=None, **extra_fields):
        if not registration_number:
            raise ValueError('The Registration Number must be set')
        email = self.normalize_email(email)
        user = self.model(registration_number=registration_number, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, registration_number, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(registration_number, email, password, **extra_fields)

class Student(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    student_class = models.CharField(max_length=50)
    year_of_admission = models.PositiveIntegerField()
    provisional_exam_results = models.DecimalField(max_digits=5, decimal_places=2)
    cat_results = models.DecimalField(max_digits=5, decimal_places=2)
    year_of_registration = models.PositiveIntegerField()
    pin = models.CharField(max_length=128)  # Store the hashed pin
    parent_names = models.CharField(max_length=200)
    parent_phone_number = models.CharField(max_length=20)
    county_of_residence = models.CharField(max_length=100)
    country_of_residence = models.CharField(max_length=100)
    student_photo = models.ImageField(upload_to='student_photos/')
    date_of_birth = models.DateField()
    expected_year_of_completion = models.PositiveIntegerField()
    discipline_score = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    discipline_cases = models.TextField()
    fee_arrears = models.DecimalField(max_digits=10, decimal_places=2)
    hostel_number = models.CharField(max_length=50)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = StudentManager()

    USERNAME_FIELD = 'registration_number'
    REQUIRED_FIELDS = ['email']

    def set_pin(self, raw_pin):
        self.pin = make_password(raw_pin)

    def check_pin(self, raw_pin):
        return check_password(raw_pin, self.pin)

    def __str__(self):
        return self.name
