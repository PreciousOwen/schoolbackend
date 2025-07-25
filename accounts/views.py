from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .models import UserProfile
from .serializers import UserProfileSerializer, CustomerRegistrationSerializer
from django.utils import timezone

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    print("=== LOGIN VIEW CALLED ===")
    print(f"DEBUG: request.data = {request.data}")
    
    email = request.data.get('email')  # Frontend sends email
    password = request.data.get('password')
    
    if not email or not password:
        return Response({
            'error': 'Email and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Authenticate using email (not username)
    try:
        user = User.objects.get(email=email)
        if user.check_password(password):
            # Create or get token
            from rest_framework.authtoken.models import Token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'username': user.username
                }
            })
        else:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    GET/PATCH /api/accounts/profile/
    """
    user = request.user
    
    # Ensure user has a profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        # Update user fields
        if 'first_name' in request.data:
            user.first_name = request.data['first_name']
        if 'last_name' in request.data:
            user.last_name = request.data['last_name']
        if 'email' in request.data:
            user.email = request.data['email']
        
        user.save()
        
        # Update profile fields
        if 'phone' in request.data:
            profile.phone = request.data['phone']
        if 'address' in request.data:
            profile.address = request.data['address']
        if 'avatar' in request.FILES:
            # Delete old avatar if exists
            if profile.avatar:
                profile.avatar.delete(save=False)
            profile.avatar = request.FILES['avatar']
            
        profile.save()
        
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def test_view(request):
    """Test endpoint to verify routing works"""
    return Response({'message': 'Accounts app is working!'})

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Customer registration endpoint"""
    print("=== REGISTER VIEW CALLED ===")
    print(f"DEBUG: request.data = {request.data}")
    
    serializer = CustomerRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Create user profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        return Response({
            'message': 'Registration successful',
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)
    else:
        print(f"Registration validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout endpoint - delete user's token"""
    try:
        # Delete the user's token
        request.user.auth_token.delete()
        return Response({'message': 'Successfully logged out'})
    except:
        return Response({'message': 'Logged out'})
