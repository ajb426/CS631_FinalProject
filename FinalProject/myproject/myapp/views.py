from django.shortcuts import render
from .models import Product, Cart, CartItem, Session, PaymentInfo, Order, OrderItem, ShippingAddress
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import CustomUserCreationForm, PaymentDetailsForm, ShippingAddressForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.conf import settings
from cryptography.fernet import Fernet
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist


def get_cipher():
    """
    Creates and returns a Fernet cipher instance configured with an encryption key from Django settings.

    The function uses the 'ENCRYPTION_KEY' defined in the Django settings, which should be a URL-safe base64-encoded 32-byte key. This key is used to initialize the Fernet encryption system.

    Returns:
    cryptography.fernet.Fernet: An encryption cipher object that can be used for encrypting or decrypting data.

    Raises:
    cryptography.fernet.InvalidToken: If the key is invalid or improperly padded.
    """

    return Fernet(settings.ENCRYPTION_KEY.encode())


def encrypt_data(data):
    """
       Encrypts the provided data using a Fernet cipher derived from the Django settings encryption key.

       This function converts the plaintext data into a securely encrypted string that is safe for storage or transmission.

       Args:
           data (str): The plaintext string data to be encrypted.

       Returns:
           str: The encrypted data encoded in a URL-safe base64 format as a string.

       Raises:
           TypeError: If the input data is not a string.
           cryptography.fernet.InvalidToken: If the encryption fails due to key issues.
       """

    cipher_suite = get_cipher()
    encrypted_data = cipher_suite.encrypt(data.encode())
    return encrypted_data.decode()  # Return as a string for storage


def decrypt_data(encrypted_data):
    """
      Decrypts the provided data using a Fernet cipher derived from the Django settings encryption key.

      This function converts encrypted data back to its original plaintext form assuming it was encrypted by the `encrypt_data` function.

      Args:
          encrypted_data (str): The encrypted string data to be decrypted, encoded in URL-safe base64 format.

      Returns:
          str: The decrypted plaintext data as a string.

      Raises:
          TypeError: If the input encrypted_data is not a string.
          cryptography.fernet.InvalidToken: If the decryption fails due to key issues or data tampering.
      """

    cipher_suite = get_cipher()
    decrypted_data = cipher_suite.decrypt(encrypted_data.encode()).decode()  # Decode back to string
    return decrypted_data


def add_to_cart(cart, product_id, quantity=1):
    """
    Adds a product to the shopping cart or updates its quantity if it already exists.

    This function checks if the product is already in the cart. If it is, it increments the quantity;
    otherwise, it adds a new entry for this product in the cart.

    Args:
        cart (Cart): The cart object to which the product should be added.
        product_id (int): The ID of the product to add to the cart.
        quantity (int, optional): The number of units of the product to add. Defaults to 1.

    Returns:
        None
    """

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product_id=product_id,
        defaults={'quantity': quantity}
    )
    if not created:
        # If the item already exists, increase the quantity
        cart_item.quantity += quantity
        cart_item.save()


def remove_item_from_cart(cart, product_id, quantity=1):
    """
    Removes a specified quantity of a product from the cart or deletes the cart item if the quantity to remove
    equals or exceeds the current quantity in the cart.

    Args:
        cart (Cart): The cart object from which the product should be removed.
        product_id (int): The ID of the product to remove from the cart.
        quantity (int, optional): The number of units of the product to remove. Defaults to 1.

    Returns:
        None

    Raises:
        CartItem.DoesNotExist: If the cart item is not found, it skips any operations.
    """

    try:
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        if cart_item.quantity > quantity:
            # If there's more than one, reduce the quantity
            cart_item.quantity -= quantity
            cart_item.save()
        else:
            # If there's only one, or quantity to remove equals current quantity, delete the item
            cart_item.delete()
    except CartItem.DoesNotExist:
        # If the cart item doesn't exist, there's nothing to remove
        pass


def ajax_load_address(request):
    """
       Handles AJAX request to fetch details for a specific shipping address.

       Retrieves the shipping address details based on the address ID provided via GET request.
       Intended to be used for dynamically updating address information on web pages without reloading.

       Args:
           request (HttpRequest): The request object used to fetch the address ID.

       Returns:
           JsonResponse: Contains detailed fields of the shipping address including
                         street, city, state, country, postal code, and nickname.
       """

    address_id = request.GET.get('address_id')
    address = ShippingAddress.objects.get(shipping_address_id=address_id)
    data = {
        'shipping_address_id': address.shipping_address_id,
        'street': address.street,
        'city': address.city,
        'state': address.state,
        'country': address.country,
        'postal_code': address.postal_code,
        'nickname': address.nickname,
    }
    return JsonResponse(data)


def ajax_load_paymentDetail(request):
    """
        Handles AJAX request to retrieve decrypted payment information details.

        This function fetches and decrypts the payment method details based on the payment method ID provided via GET request.
        Used for securely displaying payment information to users on demand without reloading the webpage.

        Args:
            request (HttpRequest): The request object used to fetch the payment method ID.

        Returns:
            JsonResponse: Contains decrypted payment information fields including
                          payment method type, card type, card number, CVV, and nickname.
        """

    payment_method_id = request.GET.get('paymentMethod_id')
    payment_method = PaymentInfo.objects.get(payment_info_id=payment_method_id)
    decrypt_card_number = decrypt_data(payment_method.card_number)
    decrypt_cvv = decrypt_data(payment_method.cvv)
    data = {
        'payment_method_id': payment_method.payment_info_id,
        'payment_method': payment_method.payment_method,
        'card_type': payment_method.card_type,
        'card_number': decrypt_card_number,
        'cvv': decrypt_cvv,
        'nickname': payment_method.card_nickname
    }
    return JsonResponse(data)


def homepage(request):
    """
    Renders the homepage which displays products and handles product additions to the cart.

    If the user is authenticated, the function ensures there is a session and an active cart associated with the user.
    If the user is not authenticated, it manages only the session.
    When a POST request is received (typically when adding a product to the cart), it processes the product addition.
    If the user is not authenticated and tries to add a product, they are redirected to the registration page.

    Args:
        request (HttpRequest): The request object containing metadata about the request.

    Returns:
        HttpResponse: The homepage rendered with the list of active products.

    Notes:
        Redirects to the registration page if an unauthenticated user attempts to add a product to the cart.
    """

    products = Product.objects.filter(is_active=1)
    session_id = request.session.session_key
    user = request.user
    if user.is_authenticated:
        home_page_session, hps_created = Session.objects.get_or_create(session_id=session_id, user=user)
        active_cart, active_cart_created = Cart.objects.get_or_create(user=user, is_active=1,
                                                                      session_id=home_page_session)
    else:
        home_page_session, hps_created = Session.objects.get_or_create(session_id=session_id)
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity', 1)
        product_id = int(product_id)
        quantity = int(quantity)
        if user.is_authenticated:
            active_cart, created = Cart.objects.get_or_create(user=user, is_active=1)
            add_to_cart(active_cart, product_id, quantity)
        else:
            redirect('register/')
    return render(request, 'myapp/homepage.html', {'products': products})


def register(request):
    """
    Handles the user registration process including user data, payment details, and shipping address.

    This view handles both GET and POST requests. On a GET request, it displays empty registration, payment, and
    shipping forms. On a POST request, it processes the filled forms, validates them, and if valid, creates a new
    user along with associated payment and shipping details. The user's payment card number and CVV are encrypted
    before storage.

    Args:
        request (HttpRequest): Contains metadata and data about the request.

    Returns:
        HttpResponse: On a GET request, returns the registration page with empty forms.
                      On a POST request, after successful registration, redirects to the homepage.

    Notes:
        The user is logged in and immediately redirected to the homepage after successful registration.
    """

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        payment_form = PaymentDetailsForm(request.POST)
        shipping_form = ShippingAddressForm(request.POST)
        if form.is_valid() and payment_form.is_valid() and shipping_form.is_valid():
            user = form.save(commit=False)
            user.role = 'client'
            user.save()
            login(request, user)
            # Redirect or log in the user
            cleaned_data = payment_form.cleaned_data
            encrypted_card_number = encrypt_data(cleaned_data['card_number'])
            encrypted_cvv = encrypt_data((cleaned_data['cvv']))
            payment_detail = payment_form.save(commit=False)
            payment_detail.user = user
            payment_detail.card_number = encrypted_card_number
            payment_detail.cvv = encrypted_cvv
            # Set the user to the payment detail
            payment_detail.save()
            shipping_address = shipping_form.save(commit=False)
            shipping_address.user = user
            shipping_address.save()
            return redirect('homepage')
    else:
        form = CustomUserCreationForm()
        payment_form = PaymentDetailsForm()
        shipping_form = ShippingAddressForm()
    return render(request, 'registration/register.html',
                  {'form': form, 'payment_form': payment_form, 'shipping_form': shipping_form})


@login_required
def view_cart(request):
    """
        Displays the user's shopping cart and handles cart item modifications.

        This view retrieves the active cart for the logged-in user, calculates the total price for the items,
        and handles POST requests for adding or removing items. If an item's stock is depleted, it is removed from the cart.

        Args:
            request (HttpRequest): The HTTP request object containing metadata and user interaction data.

        Returns:
            HttpResponse: Renders the cart view with the cart items and total price or redirects based on user actions.
        """

    user = request.user
    active_cart = Cart.objects.get(user=user, is_active=1)
    cart_items = CartItem.objects.filter(cart=active_cart)
    cart_id = int(active_cart.cart_id)
    total_price_for_all_items = 0

    # Calculate total price for each item and add to running total
    for item in cart_items:
        if item.product.in_stock_quantity <= 0:
            item.delete()
        item.total_price = item.quantity * item.product.price
        total_price_for_all_items += item.total_price

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        try:
            product_id = int(product_id)  # Convert product_id to integer
            quantity = int(request.POST.get('quantity', 1))
              # Default to 1 if no quantity is provided
        except (ValueError, TypeError):
            return redirect('view_cart')  # Redirect to the cart page to show an error or a message

        if 'add_to_cart' in request.POST:
            # Call a function to handle adding items
            print(f"cart before = {cart_id}")
            add_to_cart(cart_id, product_id, quantity)
        elif 'remove_item_from_cart' in request.POST:
            # Call a function to handle removing items
            remove_item_from_cart(active_cart, product_id, quantity)

        return redirect('view_cart')

    return render(request, 'myapp/view_cart.html', {
        'cart_items': cart_items,
        'total_price_for_all_items': total_price_for_all_items
    })


@login_required
def checkout_view(request):
    """
       Handles the checkout process, including order creation and payment handling.

       Retrieves the active cart and associated items, calculates total prices, and processes
       the order upon POST request. Checks stock levels and updates them accordingly. If any
       information is missing or incorrect, it redirects to update pages.

       Args:
           request (HttpRequest): The request object containing metadata and user interaction data.

       Returns:
           HttpResponse: Renders the checkout page with detailed cart and order information or
                         redirects to other pages based on the outcome of the checkout process.
       """

    user = request.user
    session_id = request.session.session_key
    session = Session.objects.get(session_id=session_id)
    if not user.is_authenticated:
        return redirect('/accounts/login')  # Redirect to login if the user is not authenticated
    active_cart, active_cart_created = Cart.objects.get_or_create(
        user=user, is_active=1,
        defaults={'session_id': session})
    cart_items = CartItem.objects.filter(cart=active_cart)  # Get all cart items for the user
    paymentInfo_all = PaymentInfo.objects.filter(user=user)
    shippingAddress_all = ShippingAddress.objects.filter(user=user)

    total_price_for_all_items = 0

    items_with_totals = []
    for item in cart_items:
        if item.product.in_stock_quantity <= 0:
            item.delete()
        total_price = item.quantity * item.product.price
        items_with_totals.append({
            'item': item,
            'total_price': total_price
        })
        # Add to the overall total
        total_price_for_all_items += total_price

    context = {
        'items_with_totals': items_with_totals,
        'total_price_for_all_items': total_price_for_all_items,
        'paymentInfo': paymentInfo_all,
        'shippingAddress': shippingAddress_all
    }

    if request.method == 'POST':
        # Here, process the order creation
        user = request.user
        session_id = request.session.session_key
        order_session = Session.objects.get(session_id=session_id, user=user)
        try:
            payment_info_id = request.POST.get('paymentInfo')
            payment_info = PaymentInfo.objects.get(payment_info_id=payment_info_id,
                                                   user=user)  # Ensure the payment detail belongs to the user
            shipping_address_id = request.POST.get('shippingAddress')
            shipping_address = ShippingAddress.objects.get(shipping_address_id=shipping_address_id, user=user)
        except ObjectDoesNotExist:
            messages.error(request, "Please update your payment and shipping information before checkout.")
            return redirect('profile')

        order = Order.objects.create(
            user=user,
            total_price=total_price_for_all_items,
            order_status='Pending',  # Example status, adjust based on your logic
            payment_info=payment_info,
            payment_status='Successful',  # Adjust based on your payment processing outcome
            order_datetime=timezone.now(),
            shipping_address=shipping_address,
            session_id=order_session,
        )
        cart = Cart.objects.get(user=user, is_active=1)
        cart_items = CartItem.objects.filter(cart=cart)

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price  # Assuming the price does not change
            )
            product = item.product
            if product.in_stock_quantity >= item.quantity:
                product.in_stock_quantity -= item.quantity
                product.save()
            else:
                messages.error(request, f"Not enough stock for {product.name}. Only {product.in_stock_quantity} left.")
                return redirect('checkout_view')
            #deactivate cart
            active_cart.is_active = 0
            active_cart.save()

        # Redirect to homepage
        return redirect('homepage')

    return render(request, 'myapp/checkout.html', context)


def product_detail(request, product_id):
    """
       Displays the detail page for a specific product.

       Retrieves a product using its primary key and renders a detail page for it. If no product
       is found with the given ID, the view will raise a 404 error, effectively handling
       non-existent products gracefully.

       Args:
           request (HttpRequest): The request object containing metadata about the request.
           product_id (int): The primary key of the product to retrieve.

       Returns:
           HttpResponse: Renders the product detail page with the product context if found,
                         otherwise raises Http404.
       """

    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'myapp/product_detail.html', {'product': product})


@login_required
def profile(request):
    """
       View function for user profile that handles shipping addresses, payment details,
       and order history.

       Allows users to add or edit their shipping addresses and payment methods. Also displays
       the user's order history. Each POST request is handled based on an 'action' parameter
       which determines the specific operation to perform.

       Args:
           request (HttpRequest): Contains metadata about the request.

       Returns:
           HttpResponse: Renders the user profile page with forms for shipping and payment details,
                         list of addresses, payment methods, and orders.
       """

    user = request.user
    action = request.POST.get('action', '')
    shipping_form = ShippingAddressForm()
    payment_form = PaymentDetailsForm()
    orders = Order.objects.filter(user=request.user).prefetch_related('order_items')
    for order in orders:
        for item in order.order_items.all():
            item.total_price = item.price * item.quantity
    if request.method == 'POST':
        if action == 'add_shipping_address':
            shipping_form = ShippingAddressForm(request.POST)
            if shipping_form.is_valid():
                new_address = shipping_form.save(commit=False)
                new_address.user = request.user
                new_address.save()
                return redirect('profile')
        elif action == 'edit_shipping_address':
            address_id = request.POST.get('shipping_address_id')
            address_instance = get_object_or_404(ShippingAddress, pk=address_id, user=user)
            shipping_form = ShippingAddressForm(request.POST, instance=address_instance)
            if shipping_form.is_valid():
                shipping_form.save()
                return redirect('profile')
        elif action == 'add_payment_details':
            payment_form = PaymentDetailsForm(request.POST)
            if payment_form.is_valid():
                new_payment_form = payment_form.save(commit=False)
                new_payment_form.user = user
                cleaned_data = payment_form.cleaned_data
                encrypted_card_number = encrypt_data(cleaned_data['card_number'])
                encrypted_cvv = encrypt_data((cleaned_data['cvv']))
                new_payment_form.card_number = encrypted_card_number
                new_payment_form.cvv = encrypted_cvv
                new_payment_form.save()
                return redirect('profile')

        elif action == 'edit_payment_details':
            payment_info_id = request.POST.get('payment_info_id')
            payment_info_instance = get_object_or_404(PaymentInfo, pk=payment_info_id, user=user)
            payment_form = PaymentDetailsForm(request.POST, instance=payment_info_instance)
            if payment_form.is_valid():
                payment_info = payment_form.save(commit=False)
                encrypted_card_number = encrypt_data(payment_form.cleaned_data['card_number'])
                encrypted_cvv = encrypt_data(payment_form.cleaned_data['cvv'])

                payment_info.card_number = encrypted_card_number
                payment_info.cvv = encrypted_cvv
                payment_info.save()
                return redirect('profile')
    else:
        shipping_form = ShippingAddressForm()
        payment_form = PaymentDetailsForm()

    user_addresses = ShippingAddress.objects.filter(user=user)
    user_payments = PaymentInfo.objects.filter(user=user)

    return render(request, 'myapp/profile.html', {
        'shipping_form': shipping_form,
        'payment_form': payment_form,
        'user_addresses': user_addresses,
        'user_payments': user_payments,
        'orders': orders,
    })
