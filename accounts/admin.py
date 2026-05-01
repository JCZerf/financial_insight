from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from accounts.models import User


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email", "name", "birth_date", "cpf", "is_active", "is_staff", "is_authorized")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = "__all__"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User

    list_display = ("email", "name", "cpf", "is_active", "is_authorized", "is_staff", "is_superuser")
    list_filter = ("is_active", "is_authorized", "is_staff", "is_superuser")
    ordering = ("email",)
    search_fields = ("email", "name", "cpf")

    fieldsets = (
        ("Credentials", {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("name", "birth_date", "cpf")}),
        ("Permissions", {"fields": ("is_active", "is_authorized", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "name", "birth_date", "cpf", "password1", "password2", "is_active", "is_authorized", "is_staff"),
            },
        ),
    )
