from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

from .decorators import unauthenticated_user, allowed_users, admin_only
from .models import *
from .forms import OrderForm, CreateUserForm, CustomerForm
from .filters import OrderFilter

from django.contrib import messages

# admin panel pswd-> Baig@150

# Create your views here.
@unauthenticated_user
def registerUser(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            group = Group.objects.get(name='customer')
            user.groups.add(group)

            Customer.objects.create(user=user)

            messages.success(request, 'Account was created for ' + username)

            return redirect('login')
    
    context = {'form': form}
    return render(request, 'accounts/register.html', context)

@unauthenticated_user
def loginUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.info(request, "username OR password is incorrect")

    context = {}
    return render(request, 'accounts/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
@admin_only
def home(request):
    customers = Customer.objects.all()
    orders = Order.objects.all()

    total_orders = orders.count()
    delivered = orders.filter(status="Delivered").count()
    pending = orders.filter(status="Pending").count()

    context = {'customers': customers, 'orders': orders, 'total_orders': total_orders, 'delivered': delivered, 'pending': pending}
    return render(request, "accounts/dashboard.html", context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):

    orders = request.user.customer.order_set.all()

    total_orders = orders.count()
    delivered = orders.filter(status="Delivered").count()
    pending = orders.filter(status="Pending").count()

    context = {'orders': orders, 'total_orders': total_orders, 'delivered': delivered, 'pending': pending}
    return render(request, 'accounts/user.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
       form = CustomerForm(request.POST, request.FILES, instance=customer)
       if form.is_valid():
          form.save()

    context = {'form': form}
    return render(request, 'accounts/account_settings.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()
    return render(request, "accounts/products.html", {'products': products})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customers(request, pk):
    customer = Customer.objects.get(id=pk)
    orders = customer.order_set.all()
    orders_total = orders.count()

    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs

    context = {'customer': customer, 'orders': orders, 'orders_total': orders_total, 'myFilter': myFilter}
    
    return render(request, "accounts/customer.html", context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request, pk):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=10)
    customer = Customer.objects.get(id=pk)
    formSet = OrderFormSet(queryset=Order.objects.none(), instance=customer)
    # form = OrderForm()

    if request.method == "POST":
       formSet = OrderFormSet(request.POST, instance=customer)
       if formSet.is_valid():
          formSet.save()
          return redirect("/")

    context = {'formSet': formSet}
    return render(request, "accounts/order_form.html", context)

# @login_required(login_url='login')
# @allowed_users(allowed_roles=['admin'])
# def updateOrder(request, pk):
#     order = Order.objects.get(id=pk)
#     form = OrderForm(instance=order)

#     if request.method == "POST":
#        form = OrderForm(request.POST, instance=order)
#        if form.is_valid():
#           form.save()
#           return redirect("/")
           
#     context = {'form': form}
#     return render(request, "accounts/order_form.html", context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)

    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect("/")

    context = {'form': form}
    return render(request, "accounts/update_order.html", context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)

    if request.method == "POST":
        order.delete()
        return redirect("/")

    context = {'item': order}
    return render(request, "accounts/delete_order.html", context)