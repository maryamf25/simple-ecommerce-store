from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Product, CartItem, Order, OrderProduct
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}. You can now login.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'store/register.html', {'form': form})


# Home page - shows all products
def product_list(request):
    query = request.GET.get('search', '').strip()  # get and clean input

    if query:
        products = Product.objects.filter(name__istartswith=query)
    else:
        products = Product.objects.all()  # show all if empty

    return render(request, 'store/product_list.html', {
        'products': products
    })

    

# Product details page
def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'store/product_detail.html', {'product': product})



@login_required
def profile(request):
    return render(request, 'store/profile.html')


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        # Check if CartItem already exists for this user-product
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += 1
        else:
            cart_item.quantity = 1
        cart_item.save()

    else:
        # Handle guest (session-based) cart
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            cart[str(product_id)] += 1
        else:
            cart[str(product_id)] = 1
        request.session['cart'] = cart

    return redirect('product_list')


def view_cart(request):
    if not request.user.is_authenticated:
        return render(request, 'store/cart.html', {
            'cart_items': [],
            'total_price': 0,
        })

    cart_items = CartItem.objects.filter(user=request.user)
    total_price = 0

    for item in cart_items:
        total_price += item.product.price * item.quantity

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }

    return render(request, 'store/cart.html', context)

def buy_now(request, product_id):
    # Temporarily store only this product for direct checkout
    request.session['buy_now'] = {
        'product_id': product_id,
        'quantity': 1
    }
    return redirect('checkout_buy_now')

def checkout_buy_now(request):
    buy_now = request.session.get('buy_now')
    if not buy_now:
        return redirect('product_list')

    product = get_object_or_404(Product, id=buy_now['product_id'])
    quantity = buy_now.get('quantity', 1)
    total_price = product.price * quantity

    context = {
        'product': product,
        'quantity': quantity,
        'total_price': total_price,
        'is_buy_now': True
    }
    return render(request, 'store/checkout.html', context)

@csrf_exempt

def place_order(request):
    if request.method == "POST":
        print("Received POST request to place order")
        print("Request data:", request.POST)

        is_buy_now = request.POST.get("is_buy_now") == "1"
        print(f"Is Buy Now: {is_buy_now}")

        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to place an order.")
            return redirect("login")

        if is_buy_now:
            # ----- Handle Buy Now -----
            product_id = request.POST.get("product_id")
            quantity = int(request.POST.get("final_quantity", 1))
            product = get_object_or_404(Product, id=product_id)

            # Create one order for one product
            order = Order.objects.create(user=request.user)

            # Create intermediate OrderProduct (order item)
            OrderProduct.objects.create(
                order=order,
                product=product,
                quantity=quantity
            )

            total = product.price * quantity
            print(f"Buy Now order placed for {product.name} x {quantity}")

            return render(request, "store/order_success.html", {
                'order_type': 'Buy Now',
                'order': order,
                'items': [{
                    'product': product,
                    'quantity': quantity,
                    'subtotal': total,
                }],
                'total_price': total,
            })

        else:
            # ----- Handle Cart Checkout -----
            cart_items = CartItem.objects.filter(user=request.user)
            if not cart_items.exists():
                messages.warning(request, "Your cart is empty.")
                return redirect("view_cart")

            # Create ONE order for all cart items
            order = Order.objects.create(user=request.user)
            total_price = 0
            items = []

            for item in cart_items:
                OrderProduct.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity
                )
                subtotal = item.product.price * item.quantity
                total_price += subtotal
                items.append({
                    'product': item.product,
                    'quantity': item.quantity,
                    'subtotal': subtotal
                })

            # Clear cart
            cart_items.delete()
            request.session['cart'] = {}

            return render(request, "store/order_success.html", {
                'order_type': 'Cart',
                'order': order,
                'items': items,
                'total_price': total_price,
            })

    return redirect("product_list")



from django.views.decorators.http import require_POST

@require_POST
def update_cart_quantity(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1

        if request.user.is_authenticated:
            product = get_object_or_404(Product, id=product_id)
            cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
            cart_item.quantity = quantity
            cart_item.save()
        else:
            # Fallback to session-based cart
            cart = request.session.get('cart', {})
            cart[str(product_id)] = quantity
            request.session['cart'] = cart

    return redirect('view_cart')

@login_required
def checkout_view(request):
    is_buy_now = request.GET.get('buy_now') == '1'
    context = {'is_buy_now': is_buy_now}

    if is_buy_now:
        product_id = request.GET.get('product_id')
        quantity = int(request.GET.get('quantity', 1))
        product = get_object_or_404(Product, id=product_id)
        total_price = product.price * quantity
        context.update({
            'product': product,
            'quantity': quantity,
            'total_price': total_price
        })
    else:
        cart_items = CartItem.objects.filter(user=request.user)
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        context.update({
            'cart_items': cart_items,
            'total_price': total_price
        })

    return render(request, 'store/checkout.html', context)

def remove_from_cart(request, product_id):
    if request.user.is_authenticated and request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        CartItem.objects.filter(user=request.user, product=product).delete()
    return redirect('view_cart')

def view_orders(request):
    if not request.user.is_authenticated:
        return redirect("login")

    orders = Order.objects.filter(user=request.user).order_by("-ordered_at")

    orders_with_items = []

    for order in orders:
        total = 0
        items_with_subtotal = []

        for item in order.orderproduct_set.all():
            subtotal = item.product.price * item.quantity
            total += subtotal
            items_with_subtotal.append({
                "product": item.product,
                "quantity": item.quantity,
                "price": item.product.price,
                "subtotal": subtotal
            })

        orders_with_items.append({
            "order": order,
            "items": items_with_subtotal,
            "total_price": total
        })

    return render(request, "store/view_orders.html", {
        "orders_with_items": orders_with_items
    })

def logout_success(request):
    logout(request)
    return redirect('login')  # Redirects to product list page directly


def dashboard(request):
    orders = Order.objects.filter(user=request.user)
    cart = CartItem.objects.filter(user=request.user).first()
    cart_items = cart.cartitem_set.all() if cart else []

    return render(request, 'store/dashboard.html', {
        'orders': orders,
        'cart_items': cart_items,
    })