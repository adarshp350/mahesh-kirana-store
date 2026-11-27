import re
from .models import Customer
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.views.decorators.http import require_POST

from .models import (
    Category, Product, Customer, Order, OrderItem,
    StorePaymentSettings
)
from .forms import CustomerRegistrationForm

User = get_user_model()

def calculate_product_subtotal(product, quantity):

    price = Decimal(str(product.price))
    quantity = Decimal(str(quantity))

    if product.product_type == 'packed':
        subtotal = price * quantity
    else:
        pack_size = Decimal(str(product.pack_size))

        if pack_size <= 0:
            raise ValueError("Invalid product pack size.")

        subtotal = price * quantity / pack_size

    return subtotal.quantize(Decimal('0.01'))
# -------------------------
# HOME PAGE
# -------------------------


@login_required(login_url='/login/')
def home(request):

    search = request.GET.get('search', '').strip()
    category_id = request.GET.get('category', '').strip()
    sort_by = request.GET.get('sort', '')


    categories = Category.objects.all().order_by('id')


    product_queryset = Product.objects.filter(
        is_available=True
    ).select_related('category')

    if category_id.isdigit():
        product_queryset = product_queryset.filter(
            category_id=int(category_id)
        )

    if search:
        product_queryset = product_queryset.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(category__name__icontains=search)
        )

    grouped_products = {}
    processed_spice_groups = set()

    for product in product_queryset.order_by('id'):

        is_grouped = (
    'Spices' in product.category.name or
    'ಮಸಾಲೆ ಪದಾರ್ಥಗಳು' in product.category.name
)

        if is_grouped:

            group_name = product.description.strip()
            group_key = (product.category_id, group_name)

            if group_key in processed_spice_groups:
                continue

            processed_spice_groups.add(group_key)

            variants = list(
                Product.objects.filter(
                    category=product.category,
                    description=group_name,
                    is_available=True
                ).order_by('pack_size')
            )

            if variants:
                grouped_products[group_key] = {
                    'name': group_name,
                    'product': variants[0],
                    'variants': variants,
                    'is_spice': True,
                }

        else:

            group_key = ('product', product.id)

            grouped_products[group_key] = {
                'name': product.name,
                'product': product,
                'variants': [product],
                'is_spice': False,
            }

    products = list(grouped_products.values())

    if sort_by == 'price_low':
        products.sort(
            key=lambda item: min(
                variant.price for variant in item['variants']
            )
        )

    elif sort_by == 'price_high':
        products.sort(
            key=lambda item: max(
                variant.price for variant in item['variants']
            ),
            reverse=True
        )

    elif sort_by == 'name_asc':
        products.sort(key=lambda item: item['name'].lower())

    elif sort_by == 'name_desc':
        products.sort(
            key=lambda item: item['name'].lower(),
            reverse=True
        )

    context = {
        'categories': categories,
        'products': products,
        'search': search,
        'selected_category': category_id,
        'sort_by': sort_by,
    }

    return render(request, 'home.html', context)



# -------------------------
# ADD PRODUCT TO CART
# -------------------------



@require_POST
def add_to_cart(request, product_id):

    selected_product_id = request.POST.get(
        'selected_product_id',
        product_id
    )

    product = get_object_or_404(
        Product,
        id=selected_product_id,
        is_available=True
    )

    cart_data = request.session.get('cart', {})
    cart_key = str(product.id)

    try:
        if product.product_type == 'loose':
            quantity = Decimal(request.POST.get('weight', '0'))

            if quantity <= 0:
                raise ValueError

        else:
            quantity = Decimal(request.POST.get('quantity', '1'))

            if quantity <= 0 or quantity != quantity.to_integral_value():
                raise ValueError

    except (ValueError, TypeError, ArithmeticError):
        messages.error(request, 'Please select a valid quantity.')
        return redirect('home')

    try:
        current_quantity = Decimal(
            str(cart_data.get(cart_key, '0'))
        )
    except (ValueError, TypeError, ArithmeticError):
        current_quantity = Decimal('0')

    total_quantity = current_quantity + quantity

    cart_data[cart_key] = str(total_quantity)

    request.session['cart'] = cart_data
    request.session.modified = True

    messages.success(
        request,
        f'{product.name} added to cart.'
    )

    return redirect('cart')

# -------------------------
# SHOPPING CART
# -------------------------



def cart(request):
    cart_data = request.session.get('cart', {})
    cart_items = []
    total_amount = Decimal('0.00')

    for product_id, saved_quantity in cart_data.items():
        try:
            product = Product.objects.get(
                id=product_id,
                is_available=True
            )

            quantity = Decimal(str(saved_quantity))

            if quantity <= 0:
                continue

            subtotal = calculate_product_subtotal(
                product,
                quantity
            )

            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })

            total_amount += subtotal

        except (
            Product.DoesNotExist,
            ValueError,
            TypeError,
            ArithmeticError
        ):
            continue

    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
    }

    return render(request, 'cart.html', context)



# -------------------------
# UPDATE CART QUANTITY
# -------------------------


@require_POST
def update_cart(request, product_id):

    cart_data = request.session.get('cart', {})
    cart_key = str(product_id)

    if cart_key not in cart_data:
        return redirect('cart')

    try:
        product = Product.objects.get(
            id=product_id,
            is_available=True
        )

        quantity = Decimal(str(cart_data[cart_key]))

    except (
        Product.DoesNotExist,
        ValueError,
        TypeError,
        ArithmeticError
    ):
        cart_data.pop(cart_key, None)
        request.session['cart'] = cart_data
        request.session.modified = True
        return redirect('cart')

    if product.product_type == 'loose':
        step = Decimal('0.250')
    else:
        step = Decimal('1')

    action = request.POST.get('action')

    if action == 'increase':

        new_quantity = quantity + step
        available_stock = Decimal(str(product.stock))

        if new_quantity <= available_stock:
            cart_data[cart_key] = str(new_quantity)
        else:
            messages.warning(request, 'Maximum available stock reached.')

    elif action == 'decrease':

        new_quantity = quantity - step

        if new_quantity > 0:
            cart_data[cart_key] = str(new_quantity)
        else:
            cart_data.pop(cart_key, None)

    request.session['cart'] = cart_data
    request.session.modified = True

    return redirect('cart')

# -------------------------
# REMOVE PRODUCT FROM CART
# -------------------------

@require_POST
def remove_from_cart(request, product_id):

    cart_data = request.session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart_data:

        cart_data.pop(product_id)

        request.session['cart'] = cart_data
        request.session.modified = True

        messages.success(
            request,
            'Product removed from cart.'
        )

    return redirect('cart')


# -------------------------
# CUSTOMER REGISTRATION
# -------------------------


def register(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':

        form = CustomerRegistrationForm(request.POST)
        phone = request.POST.get('phone', '').strip()

        if not re.fullmatch(r'[6-9][0-9]{9}', phone):
            messages.error(request, 'Please enter a valid 10-digit phone number.')

        elif form.is_valid():

            user = form.save()

            Customer.objects.get_or_create(
                user=user,
                defaults={
                    'phone': phone,
                    'address': '',
                    'city': '',
                    'pincode': '',
                }
            )

            # Update phone if Customer already exists
            Customer.objects.filter(user=user).update(phone=phone)

            login(request, user)

            messages.success(
                request,
                'Registration successful! Welcome to Mahesh Kirana Store.'
            )

            return redirect('home')

    else:
        form = CustomerRegistrationForm()

    return render(
        request,
        'register.html',
        {'form': form}
    )


# -------------------------
# CUSTOMER LOGIN
# -------------------------

def customer_login(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':

        name = request.POST.get('name', '').strip()
        password = request.POST.get('password', '')

        if not name or not password:

            messages.error(
                request,
                'Please enter your name and password.'
            )

            return render(request, 'login.html')

        users = User.objects.filter(
            first_name__iexact=name
        )

        for account in users:

            user = authenticate(
                request,
                username=account.username,
                password=password
            )

            if user is not None:

                login(request, user)

                messages.success(
                    request,
                    'Login successful!'
                )

                return redirect('home')

        messages.error(
            request,
            'Invalid name or password.'
        )

    return render(request, 'login.html')


# -------------------------
# CUSTOMER LOGOUT
# -------------------------

def customer_logout(request):

    if request.method == 'POST':

        logout(request)

        messages.success(
            request,
            'You have logged out successfully.'
        )

    return redirect('login')


# -------------------------
# CHECKOUT PAGE
# -------------------------




@login_required(login_url='login')
def checkout(request):

    cart_data = request.session.get('cart', {})

    if not cart_data:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')

    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')

    store_payment_settings = StorePaymentSettings.objects.first()

    if request.method == 'POST':

        phone = request.POST.get('phone', '').strip()
        payment_method = request.POST.get('payment_method')

       
        payment_receipt = request.FILES.get('payment_receipt')

        if not phone.isdigit() or len(phone) != 10:
            messages.error(request, 'Please enter a valid 10-digit phone number.')
            return redirect('checkout')

        if payment_method not in ['COD', 'UPI']:
            messages.error(request, 'Please select a valid payment method.')
            return redirect('checkout')

        if payment_method == 'UPI':

            if not store_payment_settings or not store_payment_settings.upi_id or not store_payment_settings.qr_code:
                messages.error(request, 'Store UPI payment details are not configured.')
                return redirect('checkout')

            if not payment_receipt:
                messages.error(request, 'Please upload your UPI payment receipt.')
                return redirect('checkout')

            if not payment_receipt.content_type.startswith('image/'):
                messages.error(request, 'Please upload a valid image receipt.')
                return redirect('checkout')

            if payment_receipt.size > 5 * 1024 * 1024:
                messages.error(request, 'Receipt image must be smaller than 5 MB.')
                return redirect('checkout')

        address = 'Not provided'

        try:
            with transaction.atomic():

                total_amount = Decimal('0.00')
                order_products = []

                for product_id, saved_quantity in cart_data.items():

                    product = Product.objects.get(
                        id=product_id,
                        is_available=True
                    )

                    quantity = Decimal(str(saved_quantity))

                    if quantity <= 0:
                        raise ValueError(
                            f'Invalid quantity for {product.name}.'
                        )

                    if product.product_type == 'packed':
                        if quantity != quantity.to_integral_value():
                            raise ValueError(
                                f'Invalid packet quantity for {product.name}.'
                            )

                    subtotal = calculate_product_subtotal(
                        product, quantity
                    )

                    total_amount += subtotal
                    order_products.append((product, quantity))

                if not order_products:
                    raise ValueError('Your cart is empty.')

                order = Order.objects.create(
                    customer=customer,
                    total_amount=total_amount,
                    address=address,
                    payment_method=payment_method,
                    payment_status=(
                        'Pending Verification'
                        if payment_method == 'UPI'
                        else 'Not Required'
                    ),
                    payment_receipt=(
                        payment_receipt if payment_method == 'UPI' else None
                    ),
                    status='Pending'
                )

                for product, quantity in order_products:

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price
                    )

                customer.phone = phone
                customer.save(update_fields=['phone'])

                request.session['cart'] = {}
                request.session.modified = True

            messages.success(
                request,
                f'Your order #{order.id} has been placed successfully!'
            )

            return redirect('my_orders')

        except Product.DoesNotExist:
            messages.error(request, 'A product is no longer available.')
            return redirect('cart')

        except (ValueError, TypeError, ArithmeticError) as error:
            messages.error(request, str(error))
            return redirect('cart')

    checkout_items = []
    total_amount = Decimal('0.00')

    for product_id, saved_quantity in cart_data.items():

        try:
            product = Product.objects.get(
                id=product_id,
                is_available=True
            )

            quantity = Decimal(str(saved_quantity))

            if quantity <= 0:
                raise ValueError('Invalid product quantity.')

            subtotal = calculate_product_subtotal(
                product, quantity
            )

            checkout_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })

            total_amount += subtotal

        except (
            Product.DoesNotExist,
            ValueError,
            TypeError,
            ArithmeticError
        ):
            messages.error(
                request,
                'A cart product is unavailable or has invalid quantity.'
            )
            return redirect('cart')

    context = {
        'customer': customer,
        'checkout_items': checkout_items,
        'total_amount': total_amount,
        'store_payment_settings': store_payment_settings,
    }

    return render(request, 'checkout.html', context)


# -------------------------
# CUSTOMER ORDER HISTORY
# -------------------------

@login_required(login_url='login')
def my_orders(request):

    try:

        customer = Customer.objects.get(
            user=request.user
        )

    except Customer.DoesNotExist:

        messages.error(
            request,
            'Customer profile not found.'
        )

        return redirect('home')

    orders = Order.objects.filter(
        customer=customer
    ).prefetch_related(
        'items__product'
    ).order_by('-created_at')

    context = {
        'orders': orders,
    }

    return render(
        request,
        'my_orders.html',
        context
    )


# -------------------------
# CUSTOMER PROFILE
# -------------------------

@login_required(login_url='login')
def profile(request):

    try:
        customer = Customer.objects.get(
            user=request.user
        )

    except Customer.DoesNotExist:

        messages.error(
            request,
            'Customer profile not found.'
        )

        return redirect('home')

    return render(
        request,
        'profile.html',
        {
            'customer': customer
        }
    )
