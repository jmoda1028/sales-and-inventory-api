from django.urls import path, include
from . import views
from rest_framework import routers


router = routers.DefaultRouter()
router.register('roles', views.RoleView)
router.register('users', views.UserView)
router.register('customers', views.CustomerView)
router.register('categories', views.CategoryView)
router.register('suppliers', views.SupplierView)
router.register('products', views.ProductView)
router.register('transactions', views.TransactionView)
router.register('transaction-items', views.Transaction_ItemView)

urlpatterns = [
    # path('token/', views.CreateTokenView.as_view(), name='token'),
    path('register-user/', views.AuthenticationView.register_user),
    path('login/', views.AuthenticationView.login),
    path('current-user/', views.AuthenticationView.current_user),
    path('update-profile/', views.AuthenticationView.update_profile),
    path('refresh-token/', views.AuthenticationView.refresh_token),
    path('logout/', views.AuthenticationView.logout),
    path('forgot-password/', views.AuthenticationView.forgot_password),
    path('reset-password/', views.AuthenticationView.reset_password),
    # path('profile/', views.ManageOwnUserView.as_view(), name='profile'),
    # path('logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('get_product_category/', views.CustomView.get_product_category),
    path('', include(router.urls)),
]