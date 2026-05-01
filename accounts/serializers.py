from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers

from accounts.validators import normalize_cpf, normalize_name, validate_birth_date, validate_cpf, validate_full_name

User = get_user_model()


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ("id", "email", "name", "birth_date", "cpf", "is_authorized")
        read_only_fields = ("id", "is_authorized")


class UserCreateSerializer(BaseUserCreateSerializer):
    re_password = serializers.CharField(write_only=True)

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ("id", "email", "name", "birth_date", "cpf", "password", "re_password")
        read_only_fields = ("id",)

    def validate_email(self, value: str) -> str:
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("Email already in use.")
        return email

    def validate_name(self, value: str) -> str:
        return validate_full_name(value)

    def validate_birth_date(self, value):
        return validate_birth_date(value)

    def validate_cpf(self, value: str) -> str:
        cpf = validate_cpf(value)
        if User.objects.filter(cpf=cpf).exists():
            raise serializers.ValidationError("CPF already in use.")
        return cpf

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["name"] = normalize_name(attrs["name"])
        attrs["cpf"] = normalize_cpf(attrs["cpf"])

        password = attrs.get("password")
        email = attrs.get("email", "")
        name = attrs.get("name", "")
        cpf = attrs.get("cpf", "")

        temp_user = User(
            email=email,
            name=name,
            birth_date=attrs.get("birth_date"),
            cpf=cpf,
        )
        validate_password(password, user=temp_user)

        password_lower = password.lower()
        comparisons = {
            email.lower(),
            email.split("@", 1)[0].lower(),
            name.lower(),
            name.replace(" ", "").lower(),
            cpf,
        }
        for item in comparisons:
            if item and item in password_lower:
                raise serializers.ValidationError(
                    {"password": "Password cannot contain personal identification data."}
                )

        return attrs

    def create(self, validated_data):
        validated_data["email"] = validated_data["email"].strip().lower()
        validated_data["name"] = normalize_name(validated_data["name"])
        validated_data["cpf"] = normalize_cpf(validated_data["cpf"])
        return super().create(validated_data)
