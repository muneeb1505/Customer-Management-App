from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="dashboard"),
    path('user/', views.userPage, name="user"),
    path('account/', views.accountSettings, name="account"),
    path('register/', views.registerUser, name="register"),
    path('login/', views.loginUser, name="login"),
    path('logout/', views.logoutUser, name="logout"),

    path('products/', views.products, name='products'),
    path('customers/<str:pk>/', views.customers, name='customers'),
    path('create_order/<str:pk>/', views.createOrder, name='create_order'),
    path('update_order/<str:pk>/', views.updateOrder, name='update_order'),
    path('delete_order/<str:pk>/', views.deleteOrder, name='delete_order'),
]