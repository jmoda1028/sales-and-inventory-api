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

urlpatterns = [
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('profile/', views.ManageOwnUserView.as_view(), name='profile'),
    path('logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('', include(router.urls)),
]