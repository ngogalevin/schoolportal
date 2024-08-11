from rest_framework import serializers
from .models import Student
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
import re
from datetime import date
from django.contrib.auth.hashers import make_password, check_password


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        exclude = ('groups','user_permissions')
        extra_kwargs = {
            'password': {'write_only': True},
            'pin': {'write_only': True},
        }

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("Name cannot be empty.")
        if len(value) > 100:
            raise serializers.ValidationError("Name cannot exceed 100 characters.")
        return value

    def validate_pin(self, value):
        if not re.match(r'^\d{4}$', value):
            raise serializers.ValidationError("PIN must be a 4-digit number.")
        return value

    def validate_email(self, value):
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
            raise serializers.ValidationError("Invalid email address.")
        if Student.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email address is already in use.")
        return value

    def validate_parent_phone_number(self, value):
        if not re.match(r'^\+?\d{7,15}$', value):
            raise serializers.ValidationError("Invalid phone number format.")
        return value

    def validate_discipline_score(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Discipline score must be between 1 and 5.")
        return value

    def validate_date_of_birth(self, value):
        if value >= date.today():
            raise serializers.ValidationError("Date of birth must be in the past.")
        return value

    def validate(self, data):
        year_of_admission = data.get('year_of_admission')
        expected_year_of_completion = data.get('expected_year_of_completion')
        if year_of_admission and expected_year_of_completion:
            if expected_year_of_completion <= year_of_admission:
                raise serializers.ValidationError(
                    "Expected year of course completion must be after the year of admission."
                )
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        pin = validated_data.pop('pin')
        student = Student(**validated_data)
        student.set_password(password)
        student.set_pin(pin)
        student.save()
        return student

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        pin = validated_data.pop('pin', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        if pin:
            instance.set_pin(pin)
        instance.save()
        return instance

    def login(self, registration_number, password):
        try:
            student = Student.objects.get(registration_number=registration_number)
            if student.check_password(password):
                token, created = Token.objects.get_or_create(user=student)
                return token.key
            else:
                raise serializers.ValidationError("Invalid password.")
        except Student.DoesNotExist:
            raise serializers.ValidationError("Invalid registration number.")

    def logout(self, token_key):
        try:
            token = Token.objects.get(key=token_key)
            token.delete()
            return "Logged out successfully."
        except Token.DoesNotExist:
            raise serializers.ValidationError("Invalid token.")
