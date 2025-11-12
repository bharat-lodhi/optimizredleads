from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404

from django.http import HttpResponse
from central_admin.models import Product
from .models import ContactLead
from optimizedleads.send_mail import register_mail

User = get_user_model()

def register(request):
    print("View hit!") 
    
    if request.method == 'POST':
        
        print("POST detected")
        
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        industry = request.POST.get('industry')
        sub_industry = request.POST.get('sub_industry', '')
        preferred_country = request.POST.get('preferred_country', '')
        
        # New fields from the form
        working_location = request.POST.get('working_location', '')
        property_type = request.POST.get('property_type', '')
        real_estate_type = request.POST.get('real_estate_type', '')
        leads_quantity = request.POST.get('leads_quantity', '100')
        
        # Handle custom quantity
        if leads_quantity == 'custom':
            leads_quantity = request.POST.get('custom_quantity', '100')
        
        # Convert leads_quantity to integer, default to 100 if invalid
        try:
            leads_quantity = int(leads_quantity)
        except (ValueError, TypeError):
            leads_quantity = 100

        print("name----------------------", name)
        print("email----------------------", email)
        print("industry-------------------", industry)
        print("leads_quantity-------------", leads_quantity)
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('/register/')

        # Create user with all fields
        user = User.objects.create(
            username=email,
            first_name=name,
            email=email,
            password=make_password(password),  # hash password
            phone=phone,
            industry=industry,
            sub_industry=sub_industry,
            preferred_country=preferred_country,
            working_location=working_location,
            property_type=property_type,
            real_estate_type=real_estate_type,
            leads_quantity=leads_quantity,
            role='subscriber'  # default role
        )
        
        user.save()
        register_mail(email,password,industry)

        messages.success(request, "Account created successfully! Please login.")
        return redirect('/login/')

    return render(request, 'landing/register.html')


# def register(request):
#     print("View hit!") 
    
#     if request.method == 'POST':
        
#         print("POST detected")
        
#         name = request.POST.get('name')
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         phone = request.POST.get('phone')
#         industry = request.POST.get('industry')
#         sub_industry = request.POST.get('sub_industry', '')
#         preferred_country = request.POST.get('preferred_country', '')

#         print("name----------------------",name)
#         print("email----------------------",email)
        
        
#         # Check if email already exists
#         if User.objects.filter(email=email).exists():
#             messages.error(request, "Email already registered!")
#             return redirect('/register/')

#         # Create user
#         user = User.objects.create(
#             username=email,
#             first_name=name,
#             email=email,
#             password=make_password(password),  # hash password
#             phone=phone,
#             industry=industry,
#             sub_industry=sub_industry,
#             preferred_country=preferred_country,
#             role='subscriber'  # default role
#         )
        
#         user.save()

#         messages.success(request, "Account created successfully! Please login.")
#         return redirect('/login/')

#     return render(request, 'landing/register.html')


User = get_user_model()
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=email, password=password)

        if user is not None:
            auth_login(request, user)  # Django session automatically starts here

            # ✅ Store important details in session
            request.session['user_id'] = user.id
            request.session['user_email'] = user.email
            request.session['user_name'] = user.first_name
            request.session['user_role'] = user.role
            request.session['is_authenticated'] = True

            # Optional: Set session expiry (in seconds) — here, 1 hour
            request.session.set_expiry(86400)

            # Role-based redirection
            if user.role == 'central_admin':
                return redirect('central_admin:dashboard')
            elif user.role == 'sub_admin':
                return redirect('sub_admin:dashboard')
            elif user.role == 'subscriber':
                return redirect('/subscribers/')
            else:
                messages.error(request, "User role not recognized.")
                return redirect('/login/')

        else:
            messages.error(request, "Invalid email or password.")
            return redirect('/login/')

    return render(request, 'landing/login.html')


def landing(request):
    buyers_leads = Product.objects.filter(category='Buyers Leads').order_by('plan_type')
    print(buyers_leads,"-------------------------------------------")
    context = {
        'buyers_leads': buyers_leads,
    }
    return render(request,'landing/landing.html',context)

def buyers_leads(request):
    buyers_leads = Product.objects.filter(category='Buyers Leads').order_by('plan_type')
    print(buyers_leads,"-------------------------------------------")
    context = {
        'buyers_leads': buyers_leads,
    }
    return render(request,'landing/buyers_leads.html',context)

def tenant_leads(request):
    tenant_leads = Product.objects.filter(category='Tenant Leads').order_by('plan_type')
    print(tenant_leads,"-------------------------------------------")
    context = {
        'tenant_leads': tenant_leads,
    }
    return render(request,'landing/tenant_leads.html',context)


def product_details(request):
    # Yeh string return karta hai, product object nahi
    product_id = request.GET.get('id')
    
    # Product object fetch karo database se
    product = get_object_or_404(Product, id=product_id)
    
    # Ab features access kar sakte hain
    if product.features:
        product.features_list = [feature.strip() for feature in product.features.split('\n') if feature.strip()]
    
    # Related products fetch karna
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:3]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'landing/product_details.html', context)


#---------------------------------------------------------------------------------------------------------------
  
    
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from central_admin.models import Product
from landing.models import Payment
from django.contrib.auth import get_user_model
import razorpay
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
import hmac, hashlib

User = get_user_model()
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# Utility function
def calculate_order_amount(product_price):
    base_price = Decimal(str(product_price))
    platform_fee = base_price * Decimal('0.02')  # 2% platform fee
    gst_amount = 0 #(base_price + platform_fee) * Decimal('0.18') 
    total_amount = base_price + gst_amount + platform_fee
    return {
        'base_price': round(base_price, 2),
        'gst_amount': round(gst_amount, 2),
        'platform_fee': round(platform_fee, 2),
        'total_amount': round(total_amount, 2),
    }

# Extract credits from unit (e.g., "10 Leads" -> 10 credits)
def extract_credits_from_unit(unit):
    try:
        # Extract numbers from unit string
        import re
        numbers = re.findall(r'\d+', unit)
        return int(numbers[0]) if numbers else 0
    except:
        return 0

# Checkout page
def checkout(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    amounts = calculate_order_amount(product.price)
    
    context = {
        'product': product,
        **amounts,
        'checkout_steps': ['Cart', 'Details', 'Payment', 'Confirm'],
        'RAZORPAY_KEY_ID': settings.RAZORPAY_KEY_ID,
    }
    return render(request, 'landing/checkout.html', context)

# Create Razorpay order
def create_order(request, product_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    product = get_object_or_404(Product, id=product_id)
    amounts = calculate_order_amount(product.price)
    total_amount_paise = int(amounts['total_amount'] * 100)

    # Razorpay order creation
    try:
        razorpay_order = client.order.create({
            "amount": total_amount_paise,
            "currency": "INR",
            "payment_capture": 1
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    # Save in DB with all customer information
    payment = Payment.objects.create(
        user=request.user if request.user.is_authenticated else None,
        
        # Customer Information
        full_name=request.POST.get('full_name'),
        email=request.POST.get('email'),
        mobile_number=request.POST.get('mobile_number'),
        company_agency_name=request.POST.get('company_agency_name'),
        business_location_city=request.POST.get('business_location_city'),
        target_area_location=request.POST.get('target_area_location'),
        additional_requirements=request.POST.get('additional_requirements'),
        
        # Product Information
        product_category=product.category,
        product_plan_type=product.plan_type,
        product_quantity=extract_credits_from_unit(product.unit),
        
        # Payment Information
        razorpay_order_id=razorpay_order['id'],
        amount=total_amount_paise,
        status='created'
    )

    return JsonResponse({
        "success": True,
        "order_id": razorpay_order['id'],
        "amount": total_amount_paise,
        "currency": "INR"
    })

# Verify payment and add credits to user
@csrf_exempt
def verify_payment(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)
    
    razorpay_order_id = request.POST.get('razorpay_order_id')
    razorpay_payment_id = request.POST.get('razorpay_payment_id')
    razorpay_signature = request.POST.get('razorpay_signature')
    
    try:
        payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
    except Payment.DoesNotExist:
        return JsonResponse({"success": False, "error": "Order not found"}, status=404)
    
    # Signature verification
    generated_signature = hmac.new(
        bytes(settings.RAZORPAY_KEY_SECRET, 'utf-8'),
        msg=bytes(f"{razorpay_order_id}|{razorpay_payment_id}", 'utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    if generated_signature == razorpay_signature:
        # Payment successful
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = "paid"
        payment.save()
        
        # Add credits to user if logged in
        if payment.user:
            try:
                credits_to_add = payment.product_quantity
                user = payment.user
                
                # Increase user's credit limit
                user.credit_limit += credits_to_add
                user.save()
                
                # Log the credit addition (optional)
                print(f"Added {credits_to_add} credits to user {user.username}")
                
            except Exception as e:
                print(f"Error adding credits to user: {e}")
        
        return JsonResponse({
            "success": True,
            "status": "Payment verified and credits added",
            "credits_added": payment.product_quantity if payment.user else 0
        })
    else:
        # Payment failed
        payment.status = "failed"
        payment.save()
        return JsonResponse({
            "success": False, 
            "error": "Payment verification failed"
        }, status=400)

# Success page
def order_success(request):
    order_id = request.GET.get('order_id', 'N/A')
    
    try:
        payment = Payment.objects.get(razorpay_order_id=order_id)
        context = {
            'order_id': order_id,
            'amount': payment.amount_in_rupees,
            'payment': payment,
            'credits_added': payment.product_quantity if payment.user else 0
        }
    except Payment.DoesNotExist:
        context = {
            'order_id': order_id,
            'amount': 0,
            'payment': None,
            'credits_added': 0
        }
    
    return render(request, 'landing/order_success.html', context)    
    
    
    
    
    

    
# ----------------------------------------------------------------------------------------------------------------------------

def study_abroad(request):
    return render(request,'landing/study_abroad.html')

def online_mba(request):
    online_mba = Product.objects.filter(category='Online MBA').order_by('plan_type')
    print(tenant_leads,"-------------------------------------------")
    context = {
        'online_mba': online_mba,
        # 'offline_mba':offline_mba,
    }
    return render(request,'landing/online_mba.html',context)

def certification(request):
    return render(request,'landing/certification.html')

def phd_doctorate(request):
    return render(request,'landing/phd_doctorate.html')

# def forex_trader(request):
#     forex_market = Product.objects.filter(category='Forex Market').order_by('plan_type')
#     print(tenant_leads,"-------------------------------------------")
#     context = {
#         'forex_market': forex_market,
#     }
#     return render(request,'landing/forex_trader.html',context)


def forex_trader(request):
    # Get all countries from products
    countries = Product.objects.filter(category='Forex Market').values_list('country', flat=True).distinct()
    
    # Get selected country from request or default to first country
    selected_country = request.GET.get('country', 'India')
    
    # Filter products by selected country and limit to 3
    forex_market = Product.objects.filter(
        category='Forex Market', 
        country=selected_country
    ).order_by('plan_type')[:3]
    
    context = {
        'forex_market': forex_market,
        'countries': countries,
        'selected_country': selected_country,
    }
    return render(request, 'landing/forex_trader.html', context)


def about_us(request):
    return render(request,'landing/about_us.html')

def contact_us(request):
    if request.method == 'POST':
        try:
            # Get data from form
            full_name = request.POST.get('name')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone')
            industry = request.POST.get('industry')
            message = request.POST.get('message', '')
            
            # Basic validation
            if not all([full_name, email, phone_number, industry]):
                messages.error(request, 'Please fill all required fields.')
                return render(request, 'landing/contact_us.html')
            
            # Create and save ContactLead object
            contact_lead = ContactLead(
                full_name=full_name,
                email=email,
                phone_number=phone_number,
                industry=industry.lower().replace(' ', '_'), 
                message=message
            )
            contact_lead.save()
            
            messages.success(request, 'Thank you! We will be in touch soon.')
            return redirect('/contact_us/')
            
        except Exception as e:
            messages.error(request, 'An error occurred. Please try again.')
            print(f"Error saving contact lead: {e}")
    
    return render(request, 'landing/contact_us.html')


def start_free_trail(request):
    return redirect('/register/')


def terms(request):
    return render(request,"landing/Terms.html")

def policy(request):
    return render(request,"landing/policy.html")
# ------------------------------------------------------------------------------