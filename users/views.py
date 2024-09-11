from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import *
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
import secrets
import json
from django.core.mail import send_mail

class UserAPIView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Checking if the user is a superuser
        is_superuser = request.user.is_superuser
        print('is superuser:', is_superuser)

        
        role_name = request.data.get('role')
        print('role_name:', role_name)

       
        role = Role.objects.filter(name=role_name).first()
        if role is None:
            return Response({'error': 'Invalid role name.'}, status=status.HTTP_400_BAD_REQUEST)
        
        #
        requesting_user_role = None
        if not is_superuser:
            requesting_user_role = getattr(request.user.role, 'name', None)
        print('requesting_user_role:', requesting_user_role)

        # checking whether the email is unique or not 
        email = request.data.get('email')
        if email and User.objects.filter(email=email).exists():
            return Response({'message': 'User with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        if is_superuser:
            # Superusers can create both the admin and teacher 
            if role_name in ['admin', 'teacher']:
                # Prepare user data
                data = request.data.copy()  
                data['role'] = role.pk  
                
                # Generating a random password
                password_length = 12
                password = secrets.token_urlsafe(password_length)
                data['password'] = password

                user = User(
                    username=email,
                    email=email,
                    first_name=data.get('first_name'),
                    last_name=data.get('last_name'),
                    role=role
                )
                user.set_password(password)
                
                #### finally saving the user  #####
                user.save()
                subject = 'Your Account Credentials'
                message = f'Hello {user.first_name},\n\nYour account has been created successfully.\nYour password is: {password}\n\nPlease change your password after logging in.'
                send_mail(subject,message,'saitreddy06@gmail.com',[email],  fail_silently=False)
                return Response({"message": "User created successfully!"}, status=status.HTTP_201_CREATED)
            else:
                print(f'Role "{role_name}" is not valid for superusers.')
                return Response({'message': 'Superusers can only create admins or teachers.'}, status=status.HTTP_403_FORBIDDEN)
        
        elif requesting_user_role == 'admin':
            ##### if the role is admin then they are able to create only the teachers ######
            if role_name == 'teacher':
                # Prepare user data
                data = request.data.copy()  
                data['role'] = role.pk  
                
               
                password_length = 12
                password = secrets.token_urlsafe(password_length)
                data['password'] = password

              
                user = User(
                    username=email,
                    email=email,
                    first_name=data.get('first_name'),
                    last_name=data.get('last_name'),
                    role=role
                )
                user.set_password(password)  
                user.save()
                subject = 'Your Account Credentials'
                message = f'Hello {user.first_name},\n\nYour account has been created successfully.\nYour password is: {password}\n\nPlease change your password after logging in.\n\nBest regards,\nYour Team'
                send_mail(subject,message,'saitreddy06@gmail.com', [email],fail_silently=False)

                return Response({"message": "User created successfully and password sent successfully to their email"}, status=status.HTTP_201_CREATED)
            else:
                print(f'Role "{role_name}" is not valid for admins.')
                return Response({'message': 'Admins can only create teachers.'}, status=status.HTTP_403_FORBIDDEN)
        
        else:
            print('Requesting user does not have the permission to create users.')
            return Response({'message': 'You do not have permission to create users.'}, status=status.HTTP_403_FORBIDDEN)

class LoginAPIView(viewsets.ViewSet):
    def create(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        print(f"Attempting to login with email 937429374298743####: {email}")

        try:
            user = User.objects.get(email=email)
            print(f"User found8888888(@&#$): {user}")
        except User.DoesNotExist:
            print("User not found")
            return Response({'message': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the provided password matches the hashed password
        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': "Login Successful",
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'role': user.role.name if user.role else None,
                'is_superuser': user.is_superuser,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'user_id': user.id,
                'username':user.username,
                'email':user.email
            }, status=status.HTTP_200_OK)
        else:
            print("Password check failed")
            return Response({'message': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutAPIView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            ###### Taking the refresh token from payload ########
            refresh_token = request.data.get('refresh')
            if refresh_token is None:
                return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
            
            ##### Blacklisting the token so of not to use it futher the same refresh token #######
            token = RefreshToken(refresh_token)
            token.blacklist()  

            return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TeacherListAPIView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    ###### An api to get all the teachers #######
    def list(self, request, *args, **kwargs):
        teachers = User.objects.filter(role__name='teacher')
        print('teachers##############',teachers)
        serializer = UserSerializer(teachers, many=True)
        return Response({"results":serializer.data}, status=status.HTTP_200_OK)
    
    ###### An api to get the teachers by particular id ########
    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            teacher = User.objects.get(pk=pk, role__name='teacher')
        except User.DoesNotExist:
            return Response({"message": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserSerializer(teacher)
        return Response({"results":serializer.data}, status=status.HTTP_200_OK)


class AdminListAPIView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    ###### An api to get all the admins #######
    def list(self, request, *args, **kwargs):
        teachers = User.objects.filter(role__name='admin')
        print('teachers',teachers)
        serializer = UserSerializer(teachers, many=True)
        return Response({"results":serializer.data}, status=status.HTTP_200_OK)

class RoleAPIView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        ####### getting all active roles  ########
        roles = Role.objects.filter(is_active=True)  
        serializer = RoleSerializer(roles, many=True)
        return Response({"results":serializer.data}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        ###### Creating new role ########
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Role created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

