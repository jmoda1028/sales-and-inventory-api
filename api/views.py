from django.shortcuts import render
from django.core.mail import send_mail
import random
import string
import datetime


from .serializers import *
from .models import *
from .authentication import (
    create_access_token, 
    JWTAuthentication, 
    create_refresh_token, 
    decode_refresh_token
)    

from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework import exceptions, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.settings import api_settings
from rest_framework import (
    viewsets,
    generics,
    authentication,
    permissions
)

# Create your views here.
class RoleView(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class UserView(viewsets.ModelViewSet):  
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserSerializer


class AuthenticationView(APIView):

    @api_view(['POST'])
    def register_user(self, request):
        data = request.data

        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords do not match!')

        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


    @api_view(['POST'])
    def login(request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise exceptions.AuthenticationFailed('Invalid credentials')

        if not user.check_password(password):
            raise exceptions.AuthenticationFailed('Invalid credentials')

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        UserToken.objects.create(
            user_id=user.id,
            token=refresh_token,
            expired_at=datetime.datetime.utcnow() + datetime.timedelta(days=7)
        )

        response = Response()
        response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
        response.data = {
            'token': access_token
        }
        return response


    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    def current_user(request):
        return Response(UserSerializer(request.user).data)


    @api_view(['PATCH'])
    @authentication_classes([JWTAuthentication])
    def update_profile(request, *args, **kwargs):
    
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

        # user_id = request.GET.get('user_id')
        # first_name = request.GET.get('first_name')
        # last_name = request.GET.get('last_name')
        # email = request.GET.get('email')

        #  user = User.objects.get(pk=user_id)
        # user = User.objects.get(pk=user_id).update(
        #     email=email,
        #     first_name=first_name,
        #     last_name=last_name,
        # )
        # return Response({'message':"Successfully updated"})
        # serializer = UserSerializer(user, data=request.data,context={'request': request})
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @api_view(['POST'])
    def refresh_token(request):
        refresh_token = request.COOKIES.get('refresh_token')
        id = decode_refresh_token(refresh_token)

        if not UserToken.objects.filter(
                user_id=id,
                token=refresh_token,
                expired_at__gt=datetime.datetime.now(tz=datetime.timezone.utc)
        ).exists():
            raise exceptions.AuthenticationFailed('unauthenticated')

        access_token = create_access_token(id)

        return Response({
            'token': access_token
        })


    @api_view(['POST'])
    def logout(request):
        refresh_token = request.COOKIES.get('refresh_token')
        UserToken.objects.filter(token=refresh_token).delete()

        response = Response()
        response.delete_cookie(key='refresh_token')
        response.data = {
            'message': 'success'
        }

        return response


    @api_view(['POST'])
    def forgot_password(request):
        email = request.data['email']
        token = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))

        Reset.objects.create(
            email=email,
            token=token
        )

        url = 'http://localhost:3000/reset/' + token

        send_mail(
            subject='Reset your password!',
            message='Click <a href="%s">here</a> to reset your password!' % url,
            from_email='from@example.com',
            recipient_list=[email]
        )

        return Response({
            'message': 'success'
        })
   

    @api_view(['POST'])
    def reset_password(request):
        data = request.data

        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords do not match!')

        reset_password = Reset.objects.filter(token=data['token']).first()

        if not reset_password:
            raise exceptions.APIException('Invalid link!')

        user = User.objects.filter(email=reset_password.email).first()

        if not user:
            raise exceptions.APIException('User not found!')

        user.set_password(data['password'])
        user.save()

        return Response({
            'message': 'success'
        })

# class CreateTokenView(ObtainAuthToken):
#     """Create a new auth token for user."""
#     serializer_class = AuthTokenSerializer
#     renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

# customize token
# class CreateTokenView(ObtainAuthToken):

#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data,
#                                            context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#         token, created = Token.objects.get_or_create(user=user)
#         return Response({
#             'token_type': 'token',
#             'token': token.key,
#             'user_id': user.pk,
#             'email': user.email
#         })

# class LogoutAPIView(GenericAPIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]

#     def get(self, request, format=None):
#         # delete token
     
#         request.user.auth_token.delete()
#         data = {
#             'message' : 'logout was successfully'
#         }  
#         return Response(data=data, status=status.HTTP_200_OK)

# class ManageOwnUserView(generics.RetrieveUpdateAPIView):
#     """Manage the authenticated user."""
#     serializer_class = UserSerializer
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [permissions.IsAuthenticated]

#     def get_object(self):
#         return self.request.user

class CustomerView(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class CategoryView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class SupplierView(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

class ProductView(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def perform_create(self,serializer):
		    serializer.save(created_by=self.request.user)

class TransactionView(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().order_by('-created_at')
    serializer_class = TransactionSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    # def perform_create(self,serializer):
	# 	    serializer.save(created_by=self.request.user)

class Transaction_ItemView(viewsets.ModelViewSet):
    queryset = Transaction_Item.objects.all()
    serializer_class = Transaction_ItemSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    # def perform_create(self,serializer):
	# 	    serializer.save(created_by=self.request.user)


class CustomView(APIView):

    @api_view(['GET'])
    def get_product_category(request):
        # category = request.GET.get('category', 'default')

        # res = Product.objects.filter(category=category).order_by('-created_at').values('id','category','category__name','product_code','name','qty_on_hand','price','image')
        res = Product.objects.order_by('-created_at').values('id','category__name','product_code','name','qty_on_hand','price','description')
        data = list(res)
        return Response(data)