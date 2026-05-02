from djoser.views import UserViewSet
from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view, inline_serializer
from rest_framework import serializers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from accounts.serializers import UserCreateSerializer, UserSerializer


LoginRequestSerializer = inline_serializer(
    name="LoginRequest",
    fields={
        "email": serializers.EmailField(),
        "password": serializers.CharField(),
    },
)

TokenPairResponseSerializer = inline_serializer(
    name="TokenPairResponse",
    fields={
        "refresh": serializers.CharField(),
        "access": serializers.CharField(),
    },
)

RefreshRequestSerializer = inline_serializer(
    name="RefreshRequest",
    fields={
        "refresh": serializers.CharField(),
    },
)

AccessResponseSerializer = inline_serializer(
    name="AccessResponse",
    fields={
        "access": serializers.CharField(),
    },
)

VerifyRequestSerializer = inline_serializer(
    name="VerifyRequest",
    fields={
        "token": serializers.CharField(),
    },
)

EmptyResponseSerializer = inline_serializer(
    name="EmptyResponse",
    fields={},
)


@extend_schema_view(
    create=extend_schema(
        tags=["Authentication"],
        summary="Register user",
        description="Creates a new user account with email, name, birth date, CPF and password.",
        request=UserCreateSerializer,
        responses={201: UserSerializer},
        examples=[
            OpenApiExample(
                "Register request",
                value={
                    "email": "ana@example.com",
                    "name": "Ana Silva",
                    "birth_date": "1995-08-12",
                    "cpf": "12345678909",
                    "password": "StrongPassword123!",
                    "re_password": "StrongPassword123!",
                },
                request_only=True,
            )
        ],
    ),
    me=extend_schema(
        tags=["Authentication"],
        summary="Get current user",
        description="Returns the authenticated user profile associated with the access token.",
        responses={200: UserSerializer},
        examples=[
            OpenApiExample(
                "User response",
                value={
                    "id": 1,
                    "email": "ana@example.com",
                    "name": "Ana Silva",
                    "birth_date": "1995-08-12",
                    "cpf": "12345678909",
                },
                response_only=True,
            )
        ],
    ),
    partial_update=extend_schema(
        tags=["Authentication"],
        summary="Update current user (partial)",
        description="Updates one or more fields of the authenticated user profile. Use PATCH to update only specific fields.",
        request=UserSerializer,
        responses={200: UserSerializer},
        examples=[
            OpenApiExample(
                "Update name",
                value={"name": "Ana Carolina Silva"},
                request_only=True,
            ),
            OpenApiExample(
                "Update email and name",
                value={
                    "email": "anacarolina@example.com",
                    "name": "Ana Carolina Silva",
                },
                request_only=True,
            )
        ],
    ),
    update=extend_schema(
        tags=["Authentication"],
        summary="Update current user (full)",
        description="Updates all fields of the authenticated user profile. Use PUT to replace the entire resource.",
        request=UserSerializer,
        responses={200: UserSerializer},
    ),
)
class AuthUserViewSet(UserViewSet):
    serializer_class = UserSerializer


class DocumentedTokenObtainPairView(TokenObtainPairView):
    @extend_schema(
        tags=["Authentication"],
        summary="Login",
        description="Authenticates the user with email and password and returns an access token valid for 15 minutes and a refresh token valid for 7 days.",
        request=LoginRequestSerializer,
        responses={200: TokenPairResponseSerializer},
        examples=[
            OpenApiExample(
                "Login request",
                value={"email": "ana@example.com", "password": "StrongPassword123!"},
                request_only=True,
            )
        ],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class DocumentedTokenRefreshView(TokenRefreshView):
    @extend_schema(
        tags=["Authentication"],
        summary="Refresh access token",
        description="Generates a new access token from a valid refresh token without requiring a new login.",
        request=RefreshRequestSerializer,
        responses={200: AccessResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class DocumentedTokenVerifyView(TokenVerifyView):
    @extend_schema(
        tags=["Authentication"],
        summary="Verify token",
        description="Validates whether a JWT is structurally valid and not expired.",
        request=VerifyRequestSerializer,
        responses={200: EmptyResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
