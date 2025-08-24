from django.shortcuts import render
from .models import PromoBanner, FeaturedSection,Service,Testimonial

# Pages that extend base.html
def home(request):
    banner = PromoBanner.objects.first()
    categories = ProductCategory.objects.all()
    featured = FeaturedSection.objects.all()
    services = Service.objects.all()
    testimonials = Testimonial.objects.all()   # 👈 Add this

    return render(request, 'core/home.html', {
        'categories': categories,
        'banner': banner,
        'featured': featured,
        'services': services,
        'testimonials': testimonials   # 👈 Pass to template
    })      
   


# login/signup/logout
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

User = get_user_model()

def _letters_spaces_only(s: str) -> bool:
    import re
    return bool(re.fullmatch(r"[A-Za-z ]+", s or ""))

def _valid_email(s: str) -> bool:
    import re
    return bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]{2,}", s or ""))

def _valid_password(s: str) -> bool:
    # min 6, at least 1 letter and 1 number
    import re
    return bool(re.fullmatch(r"(?=.*[A-Za-z])(?=.*\d).{6,}", s or ""))

def login_view(request):
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = (request.POST.get("password") or "").strip()
        remember = request.POST.get("remember") == "on"

        # Does user exist?
        try:
            User.objects.get(username__iexact=username)
            user_exists = True
        except User.DoesNotExist:
            user_exists = False

        if not user_exists:
            messages.error(request, "No user found with that username. Please sign up.")
            return redirect("login")

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Incorrect password. Please try again.")
            return redirect("login")

        login(request, user)
        if not remember:
            request.session.set_expiry(0)  # session ends on browser close
        messages.success(request, "Welcome back!")
        return redirect("home")

    return render(request, "auth/login.html")

@require_http_methods(["GET", "POST"])
def signup_view(request):
    if request.method == "POST":
        first_name = (request.POST.get("first_name") or "").strip()
        last_name  = (request.POST.get("last_name") or "").strip()
        email      = (request.POST.get("email") or "").strip()
        username   = (request.POST.get("username") or "").strip()
        password   = (request.POST.get("password") or "").strip()
        terms      = request.POST.get("terms") == "on"

        # client-like strict checks server-side too
        if not _letters_spaces_only(first_name) or not _letters_spaces_only(last_name):
            messages.error(request, "Name should contain only letters and spaces.")
            return redirect("signup")

        if not _valid_email(email):
            messages.error(request, "Please enter a valid email address.")
            return redirect("signup")

        if not _valid_password(password):
            messages.error(request, "Password must be 6+ chars with at least one letter and one number.")
            return redirect("signup")

        if not terms:
            messages.error(request, "You must agree to the terms & conditions.")
            return redirect("signup")

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username already exists. Try a different one or log in.")
            return redirect("signup")
        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email already registered. Try logging in.")
            return redirect("signup")

        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        messages.success(request, "Account created! You can log in now.")
        return redirect("login")

    return render(request, "auth/signup.html")

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")

# about page 
from django.shortcuts import render
from .models import AboutPage

def about_view(request):
    about = AboutPage.objects.first()   # Only one record needed
    return render(request, "core/about.html", {"about": about})

# contact page
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from .models import ContactPage
from .forms import ContactForm

def contact_view(request):
    contact = ContactPage.objects.first()
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            phone = form.cleaned_data["phone"]
            how_find = form.cleaned_data["how_find"]
            message = form.cleaned_data["message"]

            # Send email
            subject = f"New Contact from {name}"
            body = f"""
            Name: {name}
            Email: {email}
            Phone: {phone}
            Found Us By: {how_find}
            Message: {message}
            """
            send_mail(subject, body, "yourgmail@gmail.com", ["info@mailjewellery.com"])

            messages.success(request, "Our team will contact you shortly. We received your message!")
            return redirect("contact")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ContactForm()

    return render(request, "core/contact.html", {"contact": contact, "form": form})

# products
from django.shortcuts import render, get_object_or_404
from .models import ProductCategory, Product

# Show all categories


# Show products under a category
from django.core.paginator import Paginator

def category_products(request, slug):
    category = get_object_or_404(ProductCategory, slug=slug)
    products_list = category.products.all()  
    banner = getattr(category, "banner", None)

    paginator = Paginator(products_list, 12)  # show 12 products per page
    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)

    return render(request, "core/product_detail.html", {
        "category": category,
        "products": products,
        "banner": banner,
    })


from django.shortcuts import render, get_object_or_404

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = request.session.get('cart', {})

    total = sum(item['price'] * item['qty'] for item in cart.values())
    quantity_in_cart = cart.get(str(pk), {}).get('qty', 1)  # default 1 if not in cart

    context = {
        "product": product,
        "cart": cart,
        "total": total,
        "quantity_in_cart": quantity_in_cart
    }
    return render(request, "core/product_description.html", context)
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .models import Product

@login_required
def book_now(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = request.session.get('cart', {})

    if request.method == "POST":
        qty = int(request.POST.get('qty', 1))

        # Instead of incrementing, overwrite with chosen qty
        cart[str(pk)] = {
            'name': product.name,
            'price': float(product.price_per_day),
            'image': product.image.url if product.image else '',
            'qty': qty
        }

        request.session['cart'] = cart
        request.session.modified = True

        # Redirect back to product detail page
        return redirect('product_detail', pk=pk)

    return redirect('product_detail', pk=pk)


# rental page
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Product, ProductCategory

from django.db.models import Q

def rental_page(request):
    products = Product.objects.all().order_by('-id')
    categories = ProductCategory.objects.all()

    category = request.GET.get('category')
    material = request.GET.get('material')
    price = request.GET.get('price')
    gender = request.GET.get('gender')

    if category and category.lower() != "all":
        products = products.filter(category__name__iexact=category)

    if material:
        products = products.filter(Q(metal__icontains=material) | Q(short_description__icontains=material))

    if price:
        if price == "2000":
            products = products.filter(price_per_day__lt=2000)
        elif price == "4000":
            products = products.filter(price_per_day__gte=2000, price_per_day__lte=6000)
        elif price == "6000":
            products = products.filter(price_per_day__gt=6000)

    if gender:
        products = products.filter(gender__iexact=gender)

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/rental.html', {
        'products': page_obj,
        'categories': categories,
        'selected_category': category,
        'selected_material': material,
        'selected_price': price,
        'selected_gender': gender,
    })

# whislist page 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product

# Add to Wishlist
def add_to_wishlist(request, pk):
    product = get_object_or_404(Product, pk=pk)
    wishlist = request.session.get('wishlist', [])

    if pk not in wishlist:
        wishlist.append(pk)
        request.session['wishlist'] = wishlist
        messages.success(request, f"{product.name} added to Wishlist!")
    else:
        messages.info(request, f"{product.name} is already in Wishlist!")

    # Redirect to wishlist after adding
    return redirect('wishlist')


# Wishlist Page
def wishlist_view(request):
    wishlist_ids = request.session.get('wishlist', [])
    products = Product.objects.filter(id__in=wishlist_ids)
    return render(request, 'core/wishlist.html', {'products': products})


# Remove All
def clear_wishlist(request):
    request.session['wishlist'] = []
    messages.success(request, "Wishlist cleared!")
    return redirect('wishlist')


# cart logics
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product

# Add to cart
# @login_required
# def add_to_cart(request, pk):
#     product = get_object_or_404(Product, pk=pk)
#     cart = request.session.get('cart', {})

#     if str(pk) in cart:
#         cart[str(pk)]['qty'] += 1
#     else:
#         cart[str(pk)] = {
#             'name': product.name,
#             'price': float(product.price_per_day),
#             'image': product.image.url if product.image else '',
#             'qty': 1
#         }

#     request.session['cart'] = cart
#     messages.success(request, f"{product.name} added to cart!")
#     return redirect('cart_view')

@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = request.session.get('cart', {})

    if str(pk) in cart:
        cart[str(pk)]['qty'] += 1
    else:
        cart[str(pk)] = {
            'name': product.name,
            'price': float(product.price_per_day),
            'image': product.image.url if product.image else '',
            'qty': 1
        }

    request.session['cart'] = cart

    # Instead of redirecting to cart page, stay on same page
    referer = request.META.get('HTTP_REFERER', 'home')  
    return redirect(referer)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def orders(request):
    # Example: fetch cart or order details from session/db
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['qty'] for item in cart.values())

    context = {
        "cart": cart,
        "total": total,
    }
    request.session['cart'] = {}
    request.session.modified = True
    return render(request, "core/orders.html", context)

# View Cart
@login_required
def cart_view(request):
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['qty'] for item in cart.values())
    tax = total * 0.1
    grand_total = total + tax

    return render(request, 'core/cart.html', {
        'cart': cart,
        'total': total,
        'tax': tax,
        'grand_total': grand_total
    })


# Update quantity
@login_required
def update_cart(request, pk, action):
    cart = request.session.get('cart', {})

    if str(pk) in cart:
        if action == "increase":
            cart[str(pk)]['qty'] += 1
        elif action == "decrease":
            if cart[str(pk)]['qty'] > 1:
                cart[str(pk)]['qty'] -= 1
        elif action == "remove":
            del cart[str(pk)]

    request.session['cart'] = cart
    return redirect('cart_view')


# checkout
# core/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def checkout(request):
    if request.method == "POST":
        fname = request.POST.get("fname")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        if not fname or not email or not phone or not address:
            messages.error(request, "Please fill all required fields correctly.")
            return redirect("checkout")

        # ✅ Save order later here
        messages.success(request, "✅ Order placed successfully!")
        return redirect("home")

    # cart_total, cart_items, cart_count come from context processor automatically
    return render(request, "core/checkout.html")
