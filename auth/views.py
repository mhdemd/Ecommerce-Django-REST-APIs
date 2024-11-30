from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

class RegisterView(APIView):
    def post(self, request):
        # Extract user data from the request
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        # Create a new user and set is_active to False
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False  # User remains inactive until email is verified
        user.save()

        # Generate a verification link and print it to the terminal
        verification_link = f"http://127.0.0.1:8000/api/verify-email/?user_id={user.id}"
        print(f"Verification Link: {verification_link}")

        # Respond with a success message
        return Response(
            {"message": "User registered successfully. Please verify your email."}, 
            status=status.HTTP_201_CREATED
        )

class VerifyEmailView(APIView):
    def get(self, request):
        # Retrieve user_id from query parameters
        user_id = request.query_params.get("user_id")
        if not user_id:
            return Response({"error": "User ID not provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Try to fetch the user by ID
            user = User.objects.get(id=user_id)
            if user.is_active:
                # If the user is already active, return a success message
                return Response({"message": "User is already verified."}, status=status.HTTP_200_OK)
            
            # Activate the user and save the changes
            user.is_active = True
            user.save()
            return Response({"message": "User verified successfully."}, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            # Return an error if the user does not exist
            return Response({"error": "Invalid user ID."}, status=status.HTTP_404_NOT_FOUND)

class LoginView(APIView):
    def post(self, request):
        from django.contrib.auth import authenticate
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        user = get_object_or_404(User, email=email)
        send_mail(
            "Reset your password",
            f"Click the link to reset your password: http://example.com/reset-password/?user_id={user.id}",
            "no-reply@example.com",
            [email],
        )
        return Response({"message": "Password reset link sent."}, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
    def post(self, request):
        user_id = request.query_params.get("user_id")
        new_password = request.data.get("new_password")
        user = get_object_or_404(User, id=user_id)
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "username": user.username,
            "email": user.email,
        }, status=status.HTTP_200_OK)

class UpdateProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        user = request.user
        user.username = request.data.get("username", user.username)
        user.email = request.data.get("email", user.email)
        user.save()
        return Response({"message": "Profile updated successfully."}, status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if not user.check_password(old_password):
            return Response({"error": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
