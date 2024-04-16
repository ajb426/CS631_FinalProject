from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from .forms import ProductForm
from django.contrib.auth.decorators import login_required
from myapp.models import Product, User
from django.shortcuts import render, redirect, get_object_or_404


def is_admin_user(user):
    # Check if the given user instance has an admin role.
    return user.role == 'admin'

@login_required
def admin(request):
    """
    Admin view that handles multiple administrative actions on products and users.

    Depending on the POST action, it can add, remove, enable, or change the role of products and users.
    Only admin users can perform these actions. Non-admin attempts redirect to a different page.

    Args:
        request (HttpRequest): The HTTP request object containing metadata and user data.

    Returns:
        HttpResponse: The response with the rendered template for admin actions or redirects based on actions.
    """

    user = request.user
    User = get_user_model()
    users = User.objects.exclude(user_id=request.user.user_id)
    products = Product.objects.all()
    action = request.POST.get('action', '')
    form = ProductForm()
    if is_admin_user(user):
        if request.method == 'POST' and action == 'add_product':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                new_product = form.save(commit=False)
                new_product.is_active = 1
                new_product.save()
                return redirect('custom_admin')
            else:
                return redirect('custom_admin')

        elif request.method == 'POST' and action == 'remove_product':
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, pk=product_id)
            product.is_active = False
            product.save()
            # Redirect to the admin product list page
            return redirect('custom_admin')

        elif request.method == 'POST' and action == 'enable_product':
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, pk=product_id)
            product.is_active = True
            product.save()
            # Redirect to the admin product list page
            return redirect('custom_admin')
        elif request.method == 'POST' and action == 'demote_admin':
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, pk=user_id)
            user.role = 'client'
            user.save()
            return redirect('custom_admin')
        elif request.method == 'POST' and action == 'promote_admin':
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, pk=user_id)
            user.role = 'admin'
            user.save()
            return redirect('custom_admin')

        else:
            return render(request, 'customadmin/admin.html', {'form': form, 'products': products, 'users':users})
