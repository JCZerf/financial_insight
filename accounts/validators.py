from __future__ import annotations

from datetime import date
import re

from django.core.exceptions import ValidationError


def normalize_name(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def validate_full_name(value: str) -> str:
    normalized = normalize_name(value)

    if len(normalized) < 2:
        raise ValidationError("Name must contain at least 2 characters.")

    alpha_count = sum(1 for char in normalized if char.isalpha())
    if alpha_count < 2:
        raise ValidationError("Name must contain at least 2 letters.")

    if not any(char.isalpha() for char in normalized):
        raise ValidationError("Name must contain letters.")

    if all(not char.isalpha() for char in normalized.replace(" ", "")):
        raise ValidationError("Name contains no valid alphabetic characters.")

    return normalized


def normalize_cpf(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def validate_cpf(value: str) -> str:
    digits = normalize_cpf(value)

    if len(digits) != 11:
        raise ValidationError("CPF must contain exactly 11 digits.")

    if digits == digits[0] * 11:
        raise ValidationError("CPF is invalid.")

    for index in (9, 10):
        total = sum(int(digits[num]) * ((index + 1) - num) for num in range(index))
        verifier = ((total * 10) % 11) % 10
        if verifier != int(digits[index]):
            raise ValidationError("CPF is invalid.")

    return digits


def validate_birth_date(value: date) -> date:
    today = date.today()
    if value >= today:
        raise ValidationError("Birth date must be in the past.")

    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 18:
        raise ValidationError("User must be at least 18 years old.")
    if age > 120:
        raise ValidationError("Birth date is outside the allowed range.")

    return value
