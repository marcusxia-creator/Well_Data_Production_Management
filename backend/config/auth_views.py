from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


User = get_user_model()


def user_payload(user):
    return {
        "id": user.id,
        "username": user.get_username(),
        "email": user.email,
        "is_staff": user.is_staff,
    }


@api_view(["GET"])
@permission_classes([AllowAny])
def auth_status(request):
    return Response({
        "authenticated": request.user.is_authenticated,
        "setup_required": not User.objects.exists(),
        "user": user_payload(request.user) if request.user.is_authenticated else None,
    })


@api_view(["POST"])
@permission_classes([AllowAny])
def setup_account(request):
    if User.objects.exists():
        return Response({"detail": "Initial account setup has already been completed."}, status=403)

    username = (request.data.get("username") or "").strip()
    email = (request.data.get("email") or "").strip()
    password = request.data.get("password") or ""
    if not username:
        return Response({"detail": "Enter a username."}, status=400)
    try:
        validate_password(password)
    except Exception as exc:
        return Response({"detail": " ".join(exc.messages)}, status=400)

    user = User.objects.create_superuser(username=username, email=email, password=password)
    token = Token.objects.create(user=user)
    return Response({"token": token.key, "user": user_payload(user)}, status=201)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_account(request):
    username = (request.data.get("username") or "").strip()
    password = request.data.get("password") or ""
    user = authenticate(request, username=username, password=password)
    if not user or not user.is_active:
        return Response({"detail": "Invalid username or password."}, status=400)
    token, _created = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "user": user_payload(user)})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_account(request):
    Token.objects.filter(user=request.user).delete()
    return Response({"logged_out": True})