from django.shortcuts import render, redirect ,get_object_or_404
from .models import Product
from django.contrib import messages
from django.contrib.auth import logout
from leads.models import RealEstateLead, OnlineMBA, StudyAbroad, LeadAssignmentLog,ForexTrade
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
User = get_user_model()
from landing.models import ContactLead
from django.utils import timezone
from django.db.models import Count, Q
from subscribers.models import Ticket


import openpyxl
from django.contrib.auth.decorators import login_required, user_passes_test


def is_central_admin(user):
    return user.is_authenticated and user.role == 'central_admin'


def add_product(request):
    if request.method == "POST":
        category = request.POST.get('category')
        unit = request.POST.get('unit')
        plan_type = request.POST.get('plan_type')
        short_description = request.POST.get('short_description')
        long_description = request.POST.get('long_description')
        product_image = request.FILES.get('product_image')
        price = request.POST.get('price')
        features = request.POST.get('features')
        heading = request.POST.get('heading')
        
        # Save product
        product = Product(
            category=category,
            unit=unit,
            plan_type=plan_type,
            price = price,
            features = features,
            short_description=short_description,
            heading= heading,
            long_description=long_description,
            product_image=product_image
        )
        product.save()

        messages.success(request, "Product added successfully!")
        return redirect('central_admin:add_product')  
    
    user_name = request.session.get('user_name')
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    short_name = user_name[:2].upper() if user_name else ""
    
    context = {
        'name': user_name,
        'email': user_email,
        'role': user_role,
        'short_name':short_name,
    }
    
    return render(request, 'central_admin/product.html',context)




def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    
    user_name = request.session.get('user_name')
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    short_name = user_name[:2].upper() if user_name else ""

    context = {
        'name': user_name,
        'email': user_email,
        'role': user_role,
        'short_name': short_name,
        'products': products,
    }
    
    return render(request, 'central_admin/products_list.html', context)

def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == "POST":
        product.category = request.POST.get('category')
        product.unit = request.POST.get('unit')
        product.plan_type = request.POST.get('plan_type')
        product.short_description = request.POST.get('short_description')
        product.long_description = request.POST.get('long_description')
        product.price = request.POST.get('price')
        product.features = request.POST.get('features')
        product.heading = request.POST.get('heading')
        
        if 'product_image' in request.FILES:
            product.product_image = request.FILES['product_image']
        
        product.save()
        messages.success(request, "Product updated successfully!")
        return redirect('central_admin:products_list')
    
    user_name = request.session.get('user_name')
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    short_name = user_name[:2].upper() if user_name else ""
    
    context = {
        'name': user_name,
        'email': user_email,
        'role': user_role,
        'short_name': short_name,
        'product': product,
    }
    
    return render(request, 'central_admin/edit_product.html', context)


def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect("/central-admin/products/")
    
    # Agar GET request aaye toh bhi directly delete kar dein
    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect("/central-admin/products/")


def dashboard(request):
    user_name = request.session.get('user_name')
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    short_name = user_name[:2].upper() if user_name else ""

    context = {
        'name': user_name,
        'email': user_email,
        'role': user_role,
        'short_name':short_name,
    }

    return render(request, 'central_admin/dashboard.html', context)


def analytics(request):
    user_name = request.session.get('user_name')
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    short_name = user_name[:2].upper() if user_name else ""

    context = {
        'name': user_name,
        'email': user_email,
        'role': user_role,
        'short_name':short_name,
    }

    return render(request, 'central_admin/analytics.html',context)


def categories(request):
    user_name = request.session.get('user_name')
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    short_name = user_name[:2].upper() if user_name else ""

    context = {
        'name': user_name,
        'email': user_email,
        'role': user_role,
        'short_name':short_name,
    }

    return render(request, 'central_admin/categories.html',context)







def real_estate(request):
    if request.method == 'POST':
        selected_leads = request.POST.getlist('leads')
        assigned_user_id = request.POST.get('assigned_to')

        if not selected_leads or not assigned_user_id:
            messages.error(request, "Please select leads and a user to assign.")
            return redirect('central_admin:real_estate')

        try:
            assigned_user = User.objects.get(id=assigned_user_id)
        except User.DoesNotExist:
            messages.error(request, "Selected user does not exist.")
            return redirect('central_admin:real_estate')

        for lead_id in selected_leads:
            lead = RealEstateLead.objects.filter(id=lead_id).first()
            if lead:
                
                # Check if lead is being assigned to a different user
                if lead.assigned_to != assigned_user:
                    # Clear the remark when reassigning to a different user
                    lead.remark = ""
                
                lead.assigned_to = assigned_user  # Update existing assignment
                lead.save()

                # Log assignment
                LeadAssignmentLog.objects.create(
                    lead_content_type=ContentType.objects.get_for_model(RealEstateLead),
                    lead_object_id=lead.id,
                    assigned_to=assigned_user,
                    assigned_by=request.user,
                    status_at_assignment=lead.status
                )

        messages.success(request, f"{len(selected_leads)} leads assigned to {assigned_user.username} successfully!")
        return redirect('central_admin:real_estate')

    # GET request -> show all leads (assigned or unassigned)
    leads = RealEstateLead.objects.all().order_by('-created_at')
    users = User.objects.filter(industry='real-estate')  # ya phir jo bhi relevant filter hai

    user_name = request.session.get('user_name')
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    short_name = user_name[:2].upper() if user_name else ""

    context = {
        'name': user_name,
        'email': user_email,
        'role': user_role,
        'short_name': short_name,
        'leads': leads,
        'users': users,  # yeh add karna important hai
    }
    return render(request, "central_admin/real_estate.html", context)

def add_real_estate(request):
    if request.method == 'POST':
        try:
            lead = RealEstateLead.objects.create(
                full_name=request.POST.get('full_name'),
                phone_number=request.POST.get('phone_number'),
                email=request.POST.get('email'),
                budget=request.POST.get('budget'),
                location=request.POST.get('location'),
                visit_day=request.POST.get('visit_day'),
                requirement_sqft=request.POST.get('requirement_sqft'),
                property_type=request.POST.get('property_type'),
                sub_industry=request.POST.get('sub_industry')
            )
            messages.success(request, 'Real estate lead created successfully!')
            return redirect('/central-admin/real_estate/')
        except Exception as e:
            messages.error(request, f'Error creating lead: {str(e)}')

    user_name = request.session.get('user_name')
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    short_name = user_name[:2].upper() if user_name else ""

    context = {
        'name': user_name,
        'email': user_email,
        'role': user_role,
        'short_name': short_name,
        'property_types': RealEstateLead.PROPERTY_TYPE_CHOICES,
        'sub_industries': RealEstateLead.SUB_INDUSTRY_CHOICES,
    }
    
    return render(request, 'central_admin/add_real_estate.html', context)



@login_required
@user_passes_test(is_central_admin)
def edit_real_estate(request, lead_id):
    lead = get_object_or_404(RealEstateLead, id=lead_id)
    
    # Get all choices for dropdowns
    status_choices = RealEstateLead.STATUS_CHOICES
    property_type_choices = RealEstateLead.PROPERTY_TYPE_CHOICES
    sub_industry_choices = RealEstateLead.SUB_INDUSTRY_CHOICES
    
    # Get all users for assignment
    users = User.objects.all()

    if request.method == 'POST':
        # Update lead fields
        lead.full_name = request.POST.get('full_name')
        lead.phone_number = request.POST.get('phone_number')
        lead.email = request.POST.get('email')
        lead.property_type = request.POST.get('property_type')
        lead.sub_industry = request.POST.get('sub_industry')
        lead.budget = request.POST.get('budget')
        lead.location = request.POST.get('location')
        lead.visit_day = request.POST.get('visit_day')
        lead.requirement_sqft = request.POST.get('requirement_sqft')
        lead.status = request.POST.get('status')
        lead.remark = request.POST.get('remark')
        
        # Handle assignment
        assigned_to_id = request.POST.get('assigned_to')
        if assigned_to_id:
            try:
                lead.assigned_to = User.objects.get(id=assigned_to_id)
            except User.DoesNotExist:
                lead.assigned_to = None
        else:
            lead.assigned_to = None
        
        lead.save()
        messages.success(request, "Real estate lead updated successfully!")
        return redirect('central_admin:real_estate')
    
    # Get session data for context
    user_name = request.session.get('user_name')
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    short_name = user_name[:2].upper() if user_name else ""

    context = {
        'name': user_name,
        'email': user_email,
        'role': user_role,
        'short_name': short_name,
        'lead': lead,
        'status_choices': status_choices,
        'property_type_choices': property_type_choices,
        'sub_industry_choices': sub_industry_choices,
        'users': users,
    }
    return render(request, 'central_admin/edit_real_estate.html', context)

@login_required
@user_passes_test(is_central_admin)
def delete_real_estate(request, lead_id):
    lead = get_object_or_404(RealEstateLead, id=lead_id)
    
    if request.method == 'POST':
        lead.delete()
        messages.success(request, "Real estate lead deleted successfully!")
        return redirect('central_admin:real_estate')
    
    # If not POST, show confirmation page or handle differently
    return redirect('central_admin:real_estate')



from django.contrib.contenttypes.models import ContentType

def online_mba(request):
    if request.method == 'POST':
        selected_leads = request.POST.getlist('leads')
        assigned_user_id = request.POST.get('assigned_to')

        if not selected_leads or not assigned_user_id:
            messages.error(request, "Please select leads and a user to assign.")
            return redirect('central_admin:online_mba')

        try:
            assigned_user = User.objects.get(id=assigned_user_id)
        except User.DoesNotExist:
            messages.error(request, "Selected user does not exist.")
            return redirect('central_admin:online_mba')

        for lead_id in selected_leads:
            lead = OnlineMBA.objects.filter(id=lead_id).first()
            if lead:
                
                # Check if lead is being assigned to a different user
                if lead.assigned_to != assigned_user:
                    # Clear the remark when reassigning to a different user
                    lead.remark = ""
                
                lead.assigned_to = assigned_user  # Update existing assignment
                lead.save()

                # Log assignment
                LeadAssignmentLog.objects.create(
                    lead_content_type=ContentType.objects.get_for_model(OnlineMBA),
                    lead_object_id=lead.id,
                    assigned_to=assigned_user,
                    assigned_by=request.user,
                    status_at_assignment=lead.status
                )

        messages.success(request, f"{len(selected_leads)} leads assigned to {assigned_user.username} successfully!")
        return redirect('central_admin:online_mba')

    # GET request -> show all leads (assigned or unassigned)
    leads = OnlineMBA.objects.all().order_by('-created_at')  # changed here
    users = User.objects.filter(industry='education')

    context = {
        'leads': leads,
        'users': users,
    }
    return render(request, "central_admin/online_mba.html", context)



def add_online_mba(request):
    if request.method == 'POST':
        try:
            lead = OnlineMBA.objects.create(
                full_name=request.POST.get('full_name'),
                phone_number=request.POST.get('phone_number'),
                email=request.POST.get('email'),
                course=request.POST.get('course'),
                university=request.POST.get('university'),
                higher_qualification=request.POST.get('higher_qualification')
            )
            messages.success(request, 'Online MBA lead created successfully!')
            return redirect('/central-admin/add_online_mba/')              
        except Exception as e:
            messages.error(request, f'Error creating lead: {str(e)}')
    user_name = request.session.get('user_name')
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    short_name = user_name[:2].upper() if user_name else ""

    context = {
        'name': user_name,
        'email': user_email,
        'role': user_role,
        'short_name':short_name,
    }
    return render(request, 'central_admin/add_online_mba.html',context)



@login_required
@user_passes_test(is_central_admin)
def edit_online_mba(request, lead_id):
    lead = get_object_or_404(OnlineMBA, id=lead_id)
    
    # Get all choices for dropdowns
    status_choices = OnlineMBA.STATUS_CHOICES
    
    # Get all users for assignment
    users = User.objects.all()

    if request.method == 'POST':
        # Update lead fields
        lead.full_name = request.POST.get('full_name')
        lead.phone_number = request.POST.get('phone_number')
        lead.email = request.POST.get('email')
        lead.course = request.POST.get('course')
        lead.university = request.POST.get('university')
        lead.higher_qualification = request.POST.get('higher_qualification')
        lead.status = request.POST.get('status')
        lead.remark = request.POST.get('remark')
        
        # Handle assignment
        assigned_to_id = request.POST.get('assigned_to')
        if assigned_to_id:
            try:
                lead.assigned_to = User.objects.get(id=assigned_to_id)
            except User.DoesNotExist:
                lead.assigned_to = None
        else:
            lead.assigned_to = None
        
        lead.save()
        messages.success(request, "Online MBA lead updated successfully!")
        return redirect('central_admin:online_mba')
    
    # Get session data for context
    user_name = request.session.get('user_name')
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    short_name = user_name[:2].upper() if user_name else ""

    context = {
        'name': user_name,
        'email': user_email,
        'role': user_role,
        'short_name': short_name,
        'lead': lead,
        'status_choices': status_choices,
        'users': users,
    }
    return render(request, 'central_admin/edit_online_mba.html', context)

@login_required
@user_passes_test(is_central_admin)
def delete_online_mba(request, lead_id):
    lead = get_object_or_404(OnlineMBA, id=lead_id)
    lead.delete()
    messages.success(request, "Online MBA lead deleted successfully!")
    return redirect('central_admin:online_mba')



def study_abroad(request):
    if request.method == 'POST':
        selected_leads = request.POST.getlist('leads')
        assigned_user_id = request.POST.get('assigned_to')

        if not selected_leads or not assigned_user_id:
            messages.error(request, "Please select leads and a user to assign.")
            return redirect('central_admin:study_abroad')

        try:
            assigned_user = User.objects.get(id=assigned_user_id)
        except User.DoesNotExist:
            messages.error(request, "Selected user does not exist.")
            return redirect('central_admin:study_abroad')

        for lead_id in selected_leads:
            lead = StudyAbroad.objects.filter(id=lead_id).first()
            if lead:
                # Check if lead is being assigned to a different user
                if lead.assigned_to != assigned_user:
                    # Clear the remark when reassigning to a different user
                    lead.remark = ""
                    
                lead.assigned_to = assigned_user  # Update existing assignment
                lead.save()

                # Log assignment
                LeadAssignmentLog.objects.create(
                    lead_content_type=ContentType.objects.get_for_model(StudyAbroad),
                    lead_object_id=lead.id,
                    assigned_to=assigned_user,
                    assigned_by=request.user,
                    status_at_assignment=lead.status
                )

        messages.success(request, f"{len(selected_leads)} leads assigned to {assigned_user.username} successfully!")
        return redirect('central_admin:study_abroad')

    # GET request -> show all leads (assigned or unassigned)
    leads = StudyAbroad.objects.all().order_by('-created_at')
    users = User.objects.filter(industry='study-abroad')  # ya phir jo bhi relevant filter hai

    user_name = request.session.get('user_name')
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    short_name = user_name[:2].upper() if user_name else ""

    context = {
        'name': user_name,
        'email': user_email,
        'role': user_role,
        'short_name': short_name,
        'leads': leads,
        'users': users,  # yeh add karna important hai
    }
    return render(request, "central_admin/study_abroad.html", context)


def add_study_abroad(request):
    if request.method == 'POST':
        try:
            lead = StudyAbroad.objects.create(
                full_name=request.POST.get('full_name'),
                phone_number=request.POST.get('phone_number'),
                email=request.POST.get('email'),
                country=request.POST.get('country'),
                exam=request.POST.get('exam'),
                budget=request.POST.get('budget'),
                university=request.POST.get('university')
            )
            messages.success(request, 'Study Abroad lead created successfully!')
            return redirect('/central-admin/add_study_abroad/')
        except Exception as e:
            messages.error(request, f'Error creating lead: {str(e)}')
            
    user_name = request.session.get('user_name')
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    short_name = user_name[:2].upper() if user_name else ""

    context = {
        'name': user_name,
        'email': user_email,
        'role': user_role,
        'short_name':short_name,
    }
    
    return render(request, 'central_admin/add_study_abroad.html',context)

@login_required
@user_passes_test(is_central_admin)
def edit_study_abroad(request, lead_id):
    lead = get_object_or_404(StudyAbroad, id=lead_id)
    
    # Get all choices for dropdowns
    status_choices = StudyAbroad.STATUS_CHOICES
    
    # Get all users for assignment
    users = User.objects.all()

    if request.method == 'POST':
        # Update lead fields
        lead.full_name = request.POST.get('full_name')
        lead.phone_number = request.POST.get('phone_number')
        lead.email = request.POST.get('email')
        lead.country = request.POST.get('country')
        lead.exam = request.POST.get('exam')
        lead.budget = request.POST.get('budget')
        lead.university = request.POST.get('university')
        lead.status = request.POST.get('status')
        lead.remark = request.POST.get('remark')
        
        # Handle assignment
        assigned_to_id = request.POST.get('assigned_to')
        if assigned_to_id:
            try:
                lead.assigned_to = User.objects.get(id=assigned_to_id)
            except User.DoesNotExist:
                lead.assigned_to = None
        else:
            lead.assigned_to = None
        
        lead.save()
        messages.success(request, "Study Abroad lead updated successfully!")
        return redirect('central_admin:study_abroad')
    
    # Get session data for context
    user_name = request.session.get('user_name')
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    short_name = user_name[:2].upper() if user_name else ""

    context = {
        'name': user_name,
        'email': user_email,
        'role': user_role,
        'short_name': short_name,
        'lead': lead,
        'status_choices': status_choices,
        'users': users,
    }
    return render(request, 'central_admin/edit_study_abroad.html', context)

@login_required
@user_passes_test(is_central_admin)
def delete_study_abroad(request, lead_id):
    lead = get_object_or_404(StudyAbroad, id=lead_id)
    lead.delete()
    messages.success(request, "Study Abroad lead deleted successfully!")
    return redirect('central_admin:study_abroad')



def add_forex_trade(request):
    if request.method == 'POST':
        try:
            # Create new forex trade lead
            forex_lead = ForexTrade.objects.create(
                full_name=request.POST.get('full_name'),
                phone_number=request.POST.get('phone_number'),
                email=request.POST.get('email'),
                experience=request.POST.get('experience'),
                broker=request.POST.get('broker'),
                initial_investment=request.POST.get('initial_investment'),
                country=request.POST.get('country'),
                note=request.POST.get('note'),
            )
            
            messages.success(request, 'Forex trade lead created successfully!')
            return redirect('/central-admin/add_forex_trade/')
            
        except Exception as e:
            messages.error(request, f'Error creating lead: {str(e)}')
            
    user_name = request.session.get('user_name')
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    short_name = user_name[:2].upper() if user_name else ""

    context = {
        'name': user_name,
        'email': user_email,
        'role': user_role,
        'short_name': short_name,
    }
    
    return render(request, 'central_admin/add_forex_trade.html',context)



@login_required
@user_passes_test(is_central_admin)
def edit_forex_trade(request, lead_id):
    lead = get_object_or_404(ForexTrade, id=lead_id)
    
    # Get all choices for dropdowns
    status_choices = ForexTrade.STATUS_CHOICES
    
    # Get all users for assignment
    users = User.objects.all()

    if request.method == 'POST':
        # Update lead fields
        lead.full_name = request.POST.get('full_name')
        lead.phone_number = request.POST.get('phone_number')
        lead.email = request.POST.get('email')
        lead.experience = request.POST.get('experience')
        lead.broker = request.POST.get('broker')
        lead.initial_investment = request.POST.get('initial_investment')
        lead.country = request.POST.get('country')
        lead.note = request.POST.get('note')
        lead.status = request.POST.get('status')
        lead.remark = request.POST.get('remark')
        
        # Handle assignment
        assigned_to_id = request.POST.get('assigned_to')
        if assigned_to_id:
            try:
                lead.assigned_to = User.objects.get(id=assigned_to_id)
            except User.DoesNotExist:
                lead.assigned_to = None
        else:
            lead.assigned_to = None
        
        lead.save()
        messages.success(request, "Forex Trade lead updated successfully!")
        return redirect('central_admin:forex_trade')
    
    # Get session data for context
    user_name = request.session.get('user_name')
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    short_name = user_name[:2].upper() if user_name else ""

    context = {
        'name': user_name,
        'email': user_email,
        'role': user_role,
        'short_name': short_name,
        'lead': lead,
        'status_choices': status_choices,
        'users': users,
    }
    return render(request, 'central_admin/edit_forex_trade.html', context)

@login_required
@user_passes_test(is_central_admin)
def delete_forex_trade(request, lead_id):
    lead = get_object_or_404(ForexTrade, id=lead_id)
    lead.delete()
    messages.success(request, "Forex Trade lead deleted successfully!")
    return redirect('central_admin:forex_trade')


from django.contrib.contenttypes.models import ContentType

def forex_trade(request):
    if request.method == 'POST':
        selected_leads = request.POST.getlist('leads')
        assigned_user_id = request.POST.get('assigned_to')

        if not selected_leads or not assigned_user_id:
            messages.error(request, "Please select leads and a user to assign.")
            return redirect('central_admin:forex_trade')

        try:
            assigned_user = User.objects.get(id=assigned_user_id)
        except User.DoesNotExist:
            messages.error(request, "Selected user does not exist.")
            return redirect('central_admin:forex_trade')

        for lead_id in selected_leads:
            lead = ForexTrade.objects.filter(id=lead_id).first()
            if lead:
                # Check if lead is being assigned to a different user
                if lead.assigned_to != assigned_user:
                    # Clear the remark when reassigning to a different user
                    lead.remark = ""
                lead.assigned_to = assigned_user  # Update existing assignment
                lead.save()

                # Log assignment
                LeadAssignmentLog.objects.create(
                    lead_content_type=ContentType.objects.get_for_model(ForexTrade),
                    lead_object_id=lead.id,
                    assigned_to=assigned_user,
                    assigned_by=request.user,
                    status_at_assignment=lead.status
                )

        messages.success(request, f"{len(selected_leads)} Forex Trade leads assigned to {assigned_user.username} successfully!")
        return redirect('central_admin:forex_trade')

    # GET request -> show all leads (assigned or unassigned)
    leads = ForexTrade.objects.all().order_by('-created_at')
    users = User.objects.filter(industry='trading') 

    user_name = request.session.get('user_name')
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    short_name = user_name[:2].upper() if user_name else ""

    context = {
        'leads': leads,
        'users': users,
        'name': user_name,
        'email': user_email,
        'role': user_role,
        'short_name': short_name,
    }
    return render(request, "central_admin/forex_trade.html", context)



# ---------------------------------------------------------------------------------------


from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test

User = get_user_model()

# Only central admin can access
def is_central_admin(user):
    return user.is_authenticated and user.role == 'central_admin'

@login_required
@user_passes_test(is_central_admin)
def users_list(request):
    users = User.objects.all().order_by('-date_joined')
    
    user_name = request.session.get('user_name')
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    short_name = user_name[:2].upper() if user_name else ""

    context = {
        'name': user_name,
        'email': user_email,
        'role': user_role,
        'short_name':short_name,
        'users': users,
    }
    
    return render(request, 'central_admin/users_list.html', context,)


@login_required
@user_passes_test(is_central_admin)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, f"{user.username} deleted successfully.")
    return redirect('/central-admin/users/')




@login_required
@user_passes_test(is_central_admin)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Pass choices to template
    role_choices = User.ROLE_CHOICES
    plan_choices = User.PLAN_CHOICES
    status_choices = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('expired', 'Expired'),
    ]

    if request.method == 'POST':
        # Update basic user information
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.username = request.POST.get('email')
        user.role = request.POST.get('role')
        user.plan_type = request.POST.get('plan_type')
        user.plan_status = request.POST.get('plan_status')
        user.credit_limit = request.POST.get('credit_limit') or 0
        user.is_verified = bool(request.POST.get('is_verified'))
        
        # Handle password change
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password:
            if new_password == confirm_password:
                if len(new_password) >= 8:  # Basic password strength check
                    user.set_password(new_password)
                    messages.success(request, "User details and password updated successfully!")
                else:
                    messages.error(request, "Password must be at least 8 characters long.")
                    return render(request, 'central_admin/edit_user.html', {
                        'user': user,
                        'role_choices': role_choices,
                        'plan_choices': plan_choices,
                        'status_choices': status_choices,
                        'name': request.session.get('user_name'),
                        'email': request.session.get('user_email'),
                        'role': request.session.get('user_role'),
                        'short_name': request.session.get('user_name')[:2].upper() if request.session.get('user_name') else "",
                    })
            else:
                messages.error(request, "Passwords do not match.")
                return render(request, 'central_admin/edit_user.html', {
                    'user': user,
                    'role_choices': role_choices,
                    'plan_choices': plan_choices,
                    'status_choices': status_choices,
                    'name': request.session.get('user_name'),
                    'email': request.session.get('user_email'),
                    'role': request.session.get('user_role'),
                    'short_name': request.session.get('user_name')[:2].upper() if request.session.get('user_name') else "",
                })
        else:
            messages.success(request, "User details updated successfully!")
        
        user.save()
        return redirect('central_admin:users_list')
    
    user_name = request.session.get('user_name')
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    short_name = user_name[:2].upper() if user_name else ""

    context = {
        'name': user_name,
        'email': user_email,
        'role': user_role,
        'short_name': short_name,
        'user': user,
        'role_choices': role_choices,
        'plan_choices': plan_choices,
        'status_choices': status_choices,
    }
    return render(request, 'central_admin/edit_user.html', context)





# @login_required
# @user_passes_test(is_central_admin)
# def edit_user(request, user_id):
#     user = get_object_or_404(User, id=user_id)

#     # Pass choices to template
#     role_choices = User.ROLE_CHOICES
#     plan_choices = User.PLAN_CHOICES
#     status_choices = [
#         ('active', 'Active'),
#         ('inactive', 'Inactive'),
#         ('expired', 'Expired'),
#     ]

#     if request.method == 'POST':
#         user.first_name = request.POST.get('first_name')
#         user.last_name = request.POST.get('last_name')
#         user.email = request.POST.get('email')
#         user.role = request.POST.get('role')
#         user.plan_type = request.POST.get('plan_type')
#         user.plan_status = request.POST.get('plan_status')
#         user.credit_limit = request.POST.get('credit_limit') or 0
#         user.is_verified = bool(request.POST.get('is_verified'))
#         user.save()
#         messages.success(request, "User details updated successfully!")
#         return redirect('central_admin:users_list')
    
#     user_name = request.session.get('user_name')
#     user_email = request.session.get('user_email')
#     user_role = request.session.get('user_role')
#     short_name = user_name[:2].upper() if user_name else ""

#     context = {
#         'name': user_name,
#         'email': user_email,
#         'role': user_role,
#         'short_name':short_name,
#         'user': user,
#         'role_choices': role_choices,
#         'plan_choices': plan_choices,
#         'status_choices': status_choices,
        
#     }
#     return render(request, 'central_admin/edit_user.html', context)

# ---------------------------------------Leads Upload---------------------------------------



@login_required
@user_passes_test(is_central_admin)
def upload_leads(request, category):
    model_map = {
        'real_estate': RealEstateLead,
        'online_mba': OnlineMBA,
        'study_abroad': StudyAbroad,
        'forex_trade': ForexTrade,
    }

    if category not in model_map:
        messages.error(request, "Invalid category.")
        return redirect('/central-admin/')

    Model = model_map[category]

    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']

        if not excel_file.name.endswith('.xlsx'):
            messages.error(request, "Please upload a valid .xlsx file")
            return redirect(request.path)

        try:
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active

            # Safe header processing
            headers = []
            for cell in sheet[1]:
                header_value = cell.value
                if header_value is None:
                    headers.append(f"column_{cell.column}")
                else:
                    headers.append(str(header_value).strip())

            created_count = 0
            skipped_count = 0

            for row in sheet.iter_rows(min_row=2, values_only=True):
                # Create data dictionary safely
                data = {}
                for i, value in enumerate(row):
                    if i < len(headers):
                        header_name = headers[i]
                        clean_header = header_name.lower().replace(" ", "_")
                        data[clean_header] = value

                # Skip if no data
                if not any(value for value in data.values() if value is not None):
                    continue

                try:
                    # Filter valid fields
                    valid_fields = [f.name for f in Model._meta.fields]
                    filtered_data = {k: v for k, v in data.items() 
                                   if k in valid_fields and v is not None}
                    
                    Model.objects.create(**filtered_data)
                    created_count += 1
                    
                except Exception as e:
                    skipped_count += 1
                    print(f"Skipped: {e}")

            messages.success(request, f"{created_count} leads uploaded, {skipped_count} skipped.")
            return redirect(request.path)

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect(request.path)

    return render(request, 'central_admin/upload_leads.html', {'category': category})



# @login_required
# @user_passes_test(is_central_admin)
# def upload_leads(request, category):
#     model_map = {
#         'real_estate': RealEstateLead,
#         'online_mba': OnlineMBA,
#         'study_abroad': StudyAbroad,
#     }

#     if category not in model_map:
#         messages.error(request, "Invalid category.")
#         return redirect('/central-admin/')

#     Model = model_map[category]

#     if request.method == 'POST' and request.FILES.get('excel_file'):
#         excel_file = request.FILES['excel_file']

#         # Check file type
#         if not excel_file.name.endswith('.xlsx'):
#             messages.error(request, "Please upload a valid .xlsx file")
#             return redirect(request.path)

#         # Load workbook
#         wb = openpyxl.load_workbook(excel_file)
#         sheet = wb.active

#         # Get headers
#         headers = [cell.value for cell in sheet[1]]

#         created_count = 0
#         skipped_count = 0

#         # Iterate rows
#         for row in sheet.iter_rows(min_row=2, values_only=True):
#             data = dict(zip(headers, row))
#             # Clean field keys to match model
#             data = {k.strip().lower().replace(" ", "_"): v for k, v in data.items() if v is not None}

#             try:
#                 obj = Model.objects.create(**{k: v for k, v in data.items() if k in [f.name for f in Model._meta.fields]})
#                 created_count += 1
#             except Exception as e:
#                 skipped_count += 1
#                 print("Skipped:", e)

#         messages.success(request, f"{created_count} leads uploaded, {skipped_count} skipped.")
#         return redirect(request.path)

#     return render(request, 'central_admin/upload_leads.html', {'category': category})

# ------------------------------------------------------------------------------------------


def logout_view(request):
    logout(request)
    request.session.flush()  
    return redirect('/login/')



def contact_leads_list(request):
    contact_leads = ContactLead.objects.all()
    
    user_name = request.session.get('user_name')
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    short_name = user_name[:2].upper() if user_name else ""
    
    context = {
        'name': user_name,
        'email': user_email,
        'role': user_role,
        'short_name':short_name,
        'contact_leads': contact_leads
    }
    
    return render(request, 'central_admin/contact_leads_list.html',context)




def all_tickets(request):
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    category_filter = request.GET.get('category', '')

    
    # Start with all tickets
    tickets = Ticket.objects.select_related('user', 'assigned_to').all()
    
    # Apply filters
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
    if category_filter:
        tickets = tickets.filter(category=category_filter)
    
    # Get counts for filters
    status_counts = Ticket.objects.values('status').annotate(count=Count('status'))
    priority_counts = Ticket.objects.values('priority').annotate(count=Count('priority'))
    category_counts = Ticket.objects.values('category').annotate(count=Count('category'))
    
    
    user_name = request.session.get('user_name')
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    short_name = user_name[:2].upper() if user_name else ""

    
    context = {
        'tickets': tickets,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'status_counts': status_counts,
        'priority_counts': priority_counts,
        'category_counts': category_counts,
        'STATUS_CHOICES': Ticket.STATUS_CHOICES,
        'PRIORITY_CHOICES': Ticket.PRIORITY_CHOICES,
        'CATEGORY_CHOICES': Ticket.CATEGORY_CHOICES,
        'name': user_name,
        'email': user_email,
        'role': user_role,
        'short_name':short_name,
    }
    
    return render(request, 'central_admin/tickets.html', context)

def update_ticket_status(request, ticket_id):
    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, id=ticket_id)
        new_status = request.POST.get('status')
        admin_notes = request.POST.get('admin_notes', '')
        
        if new_status in dict(Ticket.STATUS_CHOICES):
            ticket.status = new_status
            if admin_notes:
                ticket.admin_notes = admin_notes
            
            # Set resolved_at if status is resolved or closed
            if new_status in ['resolved', 'closed'] and not ticket.resolved_at:
                ticket.resolved_at = timezone.now()
            
            ticket.save()
            messages.success(request, f'Ticket {ticket.ticket_id} status updated to {new_status}.')
        else:
            messages.error(request, 'Invalid status selected.')
    
    return redirect('central_admin:all_tickets')