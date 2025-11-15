from django.shortcuts import render, redirect ,get_object_or_404
from .models import Product
from django.contrib import messages
from django.contrib.auth import logout
from leads.models import RealEstateLead, OnlineMBA, StudyAbroad, LeadAssignmentLog,ForexTrade,LeadStatusHistory,LeadRemarkHistory
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
User = get_user_model()
from landing.models import ContactLead
from django.utils import timezone
from django.db.models import Count, Q
from subscribers.models import Ticket
from optimizedleads.send_mail import leadassign_mail


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
        country = request.POST.get('country') 
        
        # Save product
        product = Product(
            category=category,
            unit=unit,
            plan_type=plan_type,
            country=country,
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



# def real_estate(request):
#     if request.method == 'POST':
#         selected_leads = request.POST.getlist('leads')
#         assigned_user_id = request.POST.get('assigned_to')
#         remarks = request.POST.get('remarks', '')

#         if not selected_leads or not assigned_user_id:
#             messages.error(request, "Please select leads and a user to assign.")
#             return redirect('central_admin:real_estate')

#         try:
#             assigned_user = User.objects.get(id=assigned_user_id)
#         except User.DoesNotExist:
#             messages.error(request, "Selected user does not exist.")
#             return redirect('central_admin:real_estate')

#         assigned_count = 0
#         already_assigned_count = 0
#         skipped_leads = []

#         for lead_id in selected_leads:
#             lead = RealEstateLead.objects.filter(id=lead_id).first()
#             if lead:
#                 # ✅ CHECK: Agar lead already isi user ko assigned hai
#                 if lead.assigned_to == assigned_user:
#                     already_assigned_count += 1
#                     skipped_leads.append(lead.full_name or f"Lead #{lead.id}")
#                     continue
                
#                 # ✅ CHECK: Agar lead pehle kabhi isi user ko assign hui hai
#                 previously_assigned = LeadAssignmentLog.objects.filter(
#                     lead_content_type=ContentType.objects.get_for_model(RealEstateLead),
#                     lead_object_id=lead.id,
#                     assigned_to=assigned_user
#                 ).exists()
                
#                 if previously_assigned:
#                     already_assigned_count += 1
#                     skipped_leads.append(lead.full_name or f"Lead #{lead.id}")
#                     continue

#                 # ✅ Nahi toh assign karo
#                 lead.assigned_to = assigned_user
#                 lead.save()

#                 # Log assignment
#                 LeadAssignmentLog.objects.create(
#                     lead_content_type=ContentType.objects.get_for_model(RealEstateLead),
#                     lead_object_id=lead.id,
#                     assigned_to=assigned_user,
#                     assigned_by=request.user,
#                     status_at_assignment=lead.status,
#                     notes=remarks
#                 )
#                 assigned_count += 1
                
#         # Success message with details
#         if assigned_count > 0:
#             messages.success(request, f"{assigned_count} leads assigned to {assigned_user.username} successfully!")
        
#         if already_assigned_count > 0:
#             skipped_names = ", ".join(skipped_leads[:5])  # Show first 5 skipped leads
#             if len(skipped_leads) > 5:
#                 skipped_names += f" and {len(skipped_leads) - 5} more"
#             messages.warning(request, f"{already_assigned_count} leads were already assigned to {assigned_user.username} and skipped: {skipped_names}")

#         leadassign_mail(assigned_user.email)
#         return redirect('central_admin:real_estate')
    
#     # GET request -> show all leads (assigned or unassigned)
#     leads = RealEstateLead.objects.all().order_by('-created_at')
#     users = User.objects.filter(industry='real-estate')

#     user_name = request.session.get('user_name')
#     user_email = request.session.get('user_email')
#     user_role = request.session.get('user_role')
#     short_name = user_name[:2].upper() if user_name else ""

#     context = {
#         'name': user_name,
#         'email': user_email,
#         'role': user_role,
#         'short_name': short_name,
#         'leads': leads,
#         'users': users,
#     }
#     return render(request, "central_admin/real_estate.html", context)

def real_estate(request):
    if request.method == 'POST':
        selected_leads = request.POST.getlist('leads')
        assigned_user_id = request.POST.get('assigned_to')
        remarks = request.POST.get('remarks', '')

        if not selected_leads or not assigned_user_id:
            messages.error(request, "Please select leads and a user to assign.")
            return redirect('central_admin:real_estate')

        try:
            assigned_user = User.objects.get(id=assigned_user_id)
        except User.DoesNotExist:
            messages.error(request, "Selected user does not exist.")
            return redirect('central_admin:real_estate')

        assigned_count = 0
        already_assigned_count = 0
        skipped_leads = []

        for lead_id in selected_leads:
            lead = RealEstateLead.objects.filter(id=lead_id).first()
            if lead:
                # ✅ CHECK: Agar lead already isi user ko assigned hai
                if lead.assigned_to == assigned_user:
                    already_assigned_count += 1
                    skipped_leads.append(lead.full_name or f"Lead #{lead.id}")
                    continue
                
                # ✅ CHECK: Agar lead pehle kabhi isi user ko assign hui hai
                previously_assigned = LeadAssignmentLog.objects.filter(
                    lead_content_type=ContentType.objects.get_for_model(RealEstateLead),
                    lead_object_id=lead.id,
                    assigned_to=assigned_user
                ).exists()
                
                if previously_assigned:
                    already_assigned_count += 1
                    skipped_leads.append(lead.full_name or f"Lead #{lead.id}")
                    continue

                # ✅ Nahi toh assign karo
                lead.assigned_to = assigned_user
                lead.save()

                # Log assignment
                LeadAssignmentLog.objects.create(
                    lead_content_type=ContentType.objects.get_for_model(RealEstateLead),
                    lead_object_id=lead.id,
                    assigned_to=assigned_user,
                    assigned_by=request.user,
                    status_at_assignment=lead.status,
                    notes=remarks
                )
                assigned_count += 1
        
        # ✅ CREDIT MANAGEMENT: Add credits_used for new assignments only
        if assigned_count > 0:
            assigned_user.credits_used += assigned_count
            assigned_user.save()
                
        # Success message with details
        if assigned_count > 0:
            messages.success(
                request, 
                f"{assigned_count} leads assigned to {assigned_user.username} successfully! "
                f"({assigned_count} credits deducted)"
            )
        
        if already_assigned_count > 0:
            skipped_names = ", ".join(skipped_leads[:5])  # Show first 5 skipped leads
            if len(skipped_leads) > 5:
                skipped_names += f" and {len(skipped_leads) - 5} more"
            messages.warning(request, f"{already_assigned_count} leads were already assigned to {assigned_user.username} and skipped: {skipped_names}")

        leadassign_mail(assigned_user.email)
        return redirect('central_admin:real_estate')
    
    # GET request -> show all leads (assigned or unassigned)
    leads = RealEstateLead.objects.all().order_by('-created_at')
    users = User.objects.filter(industry='real-estate')

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
        'users': users,
    }
    return render(request, "central_admin/real_estate.html", context)


from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType


        
# def lead_history(request, lead_id):
#     try:
#         lead = RealEstateLead.objects.get(id=lead_id)
        
#         # Get all histories directly
#         assignment_history = LeadAssignmentLog.objects.filter(
#             lead_content_type=ContentType.objects.get_for_model(RealEstateLead),
#             lead_object_id=lead_id
#         ).order_by('-assigned_at')
        
#         status_history = LeadStatusHistory.objects.filter(
#             lead_content_type=ContentType.objects.get_for_model(RealEstateLead),
#             lead_object_id=lead_id
#         ).order_by('-created_at')
        
#         remark_history = LeadRemarkHistory.objects.filter(
#             lead_content_type=ContentType.objects.get_for_model(RealEstateLead),
#             lead_object_id=lead_id
#         ).order_by('-created_at')
        
#         # Combine all histories for timeline
#         all_histories = []
        
#         for assignment in assignment_history:
#             all_histories.append({
#                 'type': 'assignment',
#                 'timestamp': assignment.assigned_at,
#                 'assignment': assignment
#             })
        
#         for status in status_history:
#             all_histories.append({
#                 'type': 'status_change', 
#                 'timestamp': status.created_at,
#                 'status': status
#             })
        
#         for remark in remark_history:
#             all_histories.append({
#                 'type': 'remark',
#                 'timestamp': remark.created_at,
#                 'remark': remark
#             })
        
#         # Sort by timestamp
#         all_histories.sort(key=lambda x: x['timestamp'], reverse=True)

#         user_name = request.session.get('user_name')
#         user_email = request.session.get('user_email')
#         user_role = request.session.get('user_role')
#         short_name = user_name[:2].upper() if user_name else ""

#         context = {
#             'name': user_name,
#             'email': user_email,
#             'role': user_role,
#             'short_name': short_name,
#             'lead': lead,
#             'assignment_history': assignment_history,
#             'status_history': status_history,
#             'remark_history': remark_history,
#             'timeline_history': all_histories,
#         }
#         return render(request, "central_admin/lead_history.html", context)
        
#     except RealEstateLead.DoesNotExist:
#         messages.error(request, "Lead not found.")
#         return redirect('central_admin:real_estate')
    
   
def lead_history(request, lead_id):
    try:
        lead = RealEstateLead.objects.get(id=lead_id)
        print(f"🔍 Lead found: {lead.id} - {lead.full_name}")
        
        # Get all histories
        assignment_history = LeadAssignmentLog.objects.filter(
            lead_content_type=ContentType.objects.get_for_model(RealEstateLead),
            lead_object_id=lead_id
        ).order_by('-assigned_at')
        
        status_history = LeadStatusHistory.objects.filter(
            lead_content_type=ContentType.objects.get_for_model(RealEstateLead),
            lead_object_id=lead_id
        ).order_by('-created_at')
        
        remark_history = LeadRemarkHistory.objects.filter(
            lead_content_type=ContentType.objects.get_for_model(RealEstateLead),
            lead_object_id=lead_id
        ).order_by('-created_at')
        
        print(f"📊 Assignment count: {assignment_history.count()}")
        print(f"📊 Status count: {status_history.count()}")
        print(f"📊 Remark count: {remark_history.count()}")
        
        # Check if we have any data
        for i, assignment in enumerate(assignment_history):
            print(f"Assignment {i}: {assignment.assigned_to} -> {assignment.assigned_by}")
        
        for i, status in enumerate(status_history):
            print(f"Status {i}: {status.old_status} -> {status.new_status}")
        
        for i, remark in enumerate(remark_history):
            print(f"Remark {i}: {remark.remark_text}")

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
            'assignment_history': assignment_history,
            'status_history': status_history,
            'remark_history': remark_history,
        }
        return render(request, "central_admin/lead_history.html", context)
        
    except RealEstateLead.DoesNotExist:
        print(f"❌ Lead not found: {lead_id}")
        messages.error(request, "Lead not found.")
        return redirect('central_admin:real_estate')
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        messages.error(request, "Error loading lead history.")
        return redirect('central_admin:real_estate')   
 
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



# def online_mba(request):
#     if request.method == 'POST':
#         selected_leads = request.POST.getlist('leads')
#         assigned_user_id = request.POST.get('assigned_to')
#         remarks = request.POST.get('remarks', '')

#         if not selected_leads or not assigned_user_id:
#             messages.error(request, "Please select leads and a user to assign.")
#             return redirect('central_admin:online_mba')

#         try:
#             assigned_user = User.objects.get(id=assigned_user_id)
#         except User.DoesNotExist:
#             messages.error(request, "Selected user does not exist.")
#             return redirect('central_admin:online_mba')

#         assigned_count = 0
#         already_assigned_count = 0
#         skipped_leads = []

#         for lead_id in selected_leads:
#             lead = OnlineMBA.objects.filter(id=lead_id).first()
#             if lead:
#                 # ✅ CHECK: Agar lead already isi user ko assigned hai
#                 if lead.assigned_to == assigned_user:
#                     already_assigned_count += 1
#                     skipped_leads.append(lead.full_name or f"Lead #{lead.id}")
#                     continue
                
#                 # ✅ CHECK: Agar lead pehle kabhi isi user ko assign hui hai
#                 previously_assigned = LeadAssignmentLog.objects.filter(
#                     lead_content_type=ContentType.objects.get_for_model(OnlineMBA),
#                     lead_object_id=lead.id,
#                     assigned_to=assigned_user
#                 ).exists()
                
#                 if previously_assigned:
#                     already_assigned_count += 1
#                     skipped_leads.append(lead.full_name or f"Lead #{lead.id}")
#                     continue

#                 # ✅ Nahi toh assign karo
#                 lead.assigned_to = assigned_user
#                 lead.save()

#                 # Log assignment
#                 LeadAssignmentLog.objects.create(
#                     lead_content_type=ContentType.objects.get_for_model(OnlineMBA),
#                     lead_object_id=lead.id,
#                     assigned_to=assigned_user,
#                     assigned_by=request.user,
#                     status_at_assignment=lead.status,
#                     notes=remarks
#                 )
#                 assigned_count += 1
                
#         # Success message with details
#         if assigned_count > 0:
#             messages.success(request, f"{assigned_count} leads assigned to {assigned_user.username} successfully!")
        
#         if already_assigned_count > 0:
#             skipped_names = ", ".join(skipped_leads[:5])  # Show first 5 skipped leads
#             if len(skipped_leads) > 5:
#                 skipped_names += f" and {len(skipped_leads) - 5} more"
#             messages.warning(request, f"{already_assigned_count} leads were already assigned to {assigned_user.username} and skipped: {skipped_names}")

#         leadassign_mail(assigned_user.email)
#         return redirect('central_admin:online_mba')

#     # GET request -> show all leads (assigned or unassigned)
#     leads = OnlineMBA.objects.all().order_by('-created_at')
#     users = User.objects.filter(industry='education')

#     context = {
#         'leads': leads,
#         'users': users,
#     }
#     return render(request, "central_admin/online_mba.html", context)


def online_mba(request):
    if request.method == 'POST':
        selected_leads = request.POST.getlist('leads')
        assigned_user_id = request.POST.get('assigned_to')
        remarks = request.POST.get('remarks', '')

        if not selected_leads or not assigned_user_id:
            messages.error(request, "Please select leads and a user to assign.")
            return redirect('central_admin:online_mba')

        try:
            assigned_user = User.objects.get(id=assigned_user_id)
        except User.DoesNotExist:
            messages.error(request, "Selected user does not exist.")
            return redirect('central_admin:online_mba')

        assigned_count = 0
        already_assigned_count = 0
        skipped_leads = []

        for lead_id in selected_leads:
            lead = OnlineMBA.objects.filter(id=lead_id).first()
            if lead:
                # ✅ CHECK: Agar lead already isi user ko assigned hai
                if lead.assigned_to == assigned_user:
                    already_assigned_count += 1
                    skipped_leads.append(lead.full_name or f"Lead #{lead.id}")
                    continue
                
                # ✅ CHECK: Agar lead pehle kabhi isi user ko assign hui hai
                previously_assigned = LeadAssignmentLog.objects.filter(
                    lead_content_type=ContentType.objects.get_for_model(OnlineMBA),
                    lead_object_id=lead.id,
                    assigned_to=assigned_user
                ).exists()
                
                if previously_assigned:
                    already_assigned_count += 1
                    skipped_leads.append(lead.full_name or f"Lead #{lead.id}")
                    continue

                # ✅ Nahi toh assign karo
                lead.assigned_to = assigned_user
                lead.save()

                # Log assignment
                LeadAssignmentLog.objects.create(
                    lead_content_type=ContentType.objects.get_for_model(OnlineMBA),
                    lead_object_id=lead.id,
                    assigned_to=assigned_user,
                    assigned_by=request.user,
                    status_at_assignment=lead.status,
                    notes=remarks
                )
                assigned_count += 1
        
        # ✅ CREDIT MANAGEMENT: Add credits_used for new assignments only
        if assigned_count > 0:
            assigned_user.credits_used += assigned_count
            assigned_user.save()
                
        # Success message with details
        if assigned_count > 0:
            messages.success(
                request, 
                f"{assigned_count} leads assigned to {assigned_user.username} successfully! "
                f"({assigned_count} credits deducted)"
            )
        
        if already_assigned_count > 0:
            skipped_names = ", ".join(skipped_leads[:5])  # Show first 5 skipped leads
            if len(skipped_leads) > 5:
                skipped_names += f" and {len(skipped_leads) - 5} more"
            messages.warning(request, f"{already_assigned_count} leads were already assigned to {assigned_user.username} and skipped: {skipped_names}")

        leadassign_mail(assigned_user.email)
        return redirect('central_admin:online_mba')

    # GET request -> show all leads (assigned or unassigned)
    leads = OnlineMBA.objects.all().order_by('-created_at')
    users = User.objects.filter(industry='education')

    context = {
        'leads': leads,
        'users': users,
    }
    return render(request, "central_admin/online_mba.html", context)

def get_assignment_history_online_mba(request, lead_id):
    try:
        # Get all assignment logs for this Online MBA lead
        assignments = LeadAssignmentLog.objects.filter(
            lead_content_type=ContentType.objects.get_for_model(OnlineMBA),
            lead_object_id=lead_id
        ).order_by('-assigned_at')
        
        assignment_data = []
        for assignment in assignments:
            assignment_data.append({
                'assigned_to': assignment.assigned_to.username if assignment.assigned_to else 'Unknown',
                'assigned_by': assignment.assigned_by.username if assignment.assigned_by else 'Unknown',
                'assigned_at': assignment.assigned_at.strftime("%d %b %Y %H:%M"),
                'status': assignment.status_at_assignment,
                'notes': assignment.notes or ''
            })
        
        return JsonResponse({'assignments': assignment_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


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


# def study_abroad(request):
#     if request.method == 'POST':
#         selected_leads = request.POST.getlist('leads')
#         assigned_user_id = request.POST.get('assigned_to')
#         remarks = request.POST.get('remarks', '')

#         if not selected_leads or not assigned_user_id:
#             messages.error(request, "Please select leads and a user to assign.")
#             return redirect('central_admin:study_abroad')

#         try:
#             assigned_user = User.objects.get(id=assigned_user_id)
#         except User.DoesNotExist:
#             messages.error(request, "Selected user does not exist.")
#             return redirect('central_admin:study_abroad')

#         assigned_count = 0
#         already_assigned_count = 0
        
#         # ✅ SPEED OPTIMIZATION: Ek baar mein sab leads fetch karo
#         lead_ids = [int(lead_id) for lead_id in selected_leads]
#         leads = StudyAbroad.objects.filter(id__in=lead_ids)
        
#         # ✅ SPEED OPTIMIZATION: Pehle se assigned leads ki list bana lo
#         already_assigned_leads = leads.filter(assigned_to=assigned_user)
#         already_assigned_count = already_assigned_leads.count()
        
#         # ✅ SPEED OPTIMIZATION: Naye leads assign karo
#         new_leads = leads.exclude(assigned_to=assigned_user)
        
#         # ✅ BULK UPDATE for assignment
#         if new_leads.exists():
#             new_leads.update(assigned_to=assigned_user)
#             assigned_count = new_leads.count()
            
#             # ✅ BULK CREATE assignment logs
#             content_type = ContentType.objects.get_for_model(StudyAbroad)
#             assignment_logs = []
#             for lead in new_leads:
#                 assignment_logs.append(
#                     LeadAssignmentLog(
#                         lead_content_type=content_type,
#                         lead_object_id=lead.id,
#                         assigned_to=assigned_user,
#                         assigned_by=request.user,
#                         status_at_assignment=lead.status,
#                         notes=remarks
#                     )
#                 )
#             LeadAssignmentLog.objects.bulk_create(assignment_logs)

#         # Success message with details
#         if assigned_count > 0:
#             messages.success(request, f"{assigned_count} leads assigned to {assigned_user.username} successfully!")
        
#         if already_assigned_count > 0:
#             messages.warning(request, f"{already_assigned_count} leads were already assigned to {assigned_user.username} and skipped.")

#         leadassign_mail(assigned_user.email)
#         return redirect('central_admin:study_abroad')

#     # GET request -> show all leads (assigned or unassigned)
#     leads = StudyAbroad.objects.all().order_by('-created_at')
#     users = User.objects.filter(industry='study-abroad')

#     user_name = request.session.get('user_name')
#     user_email = request.session.get('user_email')
#     user_role = request.session.get('user_role')
#     short_name = user_name[:2].upper() if user_name else ""

#     context = {
#         'name': user_name,
#         'email': user_email,
#         'role': user_role,
#         'short_name': short_name,
#         'leads': leads,
#         'users': users,
#     }
#     return render(request, "central_admin/study_abroad.html", context)


def study_abroad(request):
    if request.method == 'POST':
        selected_leads = request.POST.getlist('leads')
        assigned_user_id = request.POST.get('assigned_to')
        remarks = request.POST.get('remarks', '')

        if not selected_leads or not assigned_user_id:
            messages.error(request, "Please select leads and a user to assign.")
            return redirect('central_admin:study_abroad')

        try:
            assigned_user = User.objects.get(id=assigned_user_id)
        except User.DoesNotExist:
            messages.error(request, "Selected user does not exist.")
            return redirect('central_admin:study_abroad')

        assigned_count = 0
        already_assigned_count = 0
        
        # ✅ SPEED OPTIMIZATION: Ek baar mein sab leads fetch karo
        lead_ids = [int(lead_id) for lead_id in selected_leads]
        leads = StudyAbroad.objects.filter(id__in=lead_ids)
        
        # ✅ SPEED OPTIMIZATION: Pehle se assigned leads ki list bana lo
        already_assigned_leads = leads.filter(assigned_to=assigned_user)
        already_assigned_count = already_assigned_leads.count()
        
        # ✅ SPEED OPTIMIZATION: Naye leads assign karo
        new_leads = leads.exclude(assigned_to=assigned_user)
        
        # ✅ BULK UPDATE for assignment
        if new_leads.exists():
            assigned_count = new_leads.count()
            
            # ✅ CREDIT MANAGEMENT: Add credits_used for new assignments only
            assigned_user.credits_used += assigned_count
            assigned_user.save()
            
            new_leads.update(assigned_to=assigned_user)
            
            # ✅ BULK CREATE assignment logs
            content_type = ContentType.objects.get_for_model(StudyAbroad)
            assignment_logs = []
            for lead in new_leads:
                assignment_logs.append(
                    LeadAssignmentLog(
                        lead_content_type=content_type,
                        lead_object_id=lead.id,
                        assigned_to=assigned_user,
                        assigned_by=request.user,
                        status_at_assignment=lead.status,
                        notes=remarks
                    )
                )
            LeadAssignmentLog.objects.bulk_create(assignment_logs)

        # Success message with details
        if assigned_count > 0:
            messages.success(
                request, 
                f"{assigned_count} leads assigned to {assigned_user.username} successfully! "
                f"({assigned_count} credits deducted)"
            )
        
        if already_assigned_count > 0:
            messages.warning(request, f"{already_assigned_count} leads were already assigned to {assigned_user.username} and skipped.")

        leadassign_mail(assigned_user.email)
        return redirect('central_admin:study_abroad')

    # GET request -> show all leads (assigned or unassigned)
    leads = StudyAbroad.objects.all().order_by('-created_at')
    users = User.objects.filter(industry='study-abroad')

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
        'users': users,
    }
    return render(request, "central_admin/study_abroad.html", context)




def get_assignment_history_study_abroad(request, lead_id):
    try:
        # Get all assignment logs for this Study Abroad lead
        assignments = LeadAssignmentLog.objects.filter(
            lead_content_type=ContentType.objects.get_for_model(StudyAbroad),
            lead_object_id=lead_id
        ).order_by('-assigned_at')
        
        assignment_data = []
        for assignment in assignments:
            assignment_data.append({
                'assigned_to': assignment.assigned_to.username if assignment.assigned_to else 'Unknown',
                'assigned_by': assignment.assigned_by.username if assignment.assigned_by else 'Unknown',
                'assigned_at': assignment.assigned_at.strftime("%d %b %Y %H:%M"),
                'status': assignment.status_at_assignment,
                'notes': assignment.notes or ''
            })
        
        return JsonResponse({'assignments': assignment_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


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


# def forex_trade(request):
#     if request.method == 'POST':
#         selected_leads = request.POST.getlist('leads')
#         assigned_user_id = request.POST.get('assigned_to')
#         remarks = request.POST.get('remarks', '')

#         if not selected_leads or not assigned_user_id:
#             messages.error(request, "Please select leads and a user to assign.")
#             return redirect('central_admin:forex_trade')

#         try:
#             assigned_user = User.objects.get(id=assigned_user_id)
#         except User.DoesNotExist:
#             messages.error(request, "Selected user does not exist.")
#             return redirect('central_admin:forex_trade')

#         # ✅ SPEED OPTIMIZATION: Direct bulk operations
#         lead_ids = [int(lead_id) for lead_id in selected_leads]
        
#         # Get leads that are NOT already assigned to this user
#         leads_to_assign = ForexTrade.objects.filter(
#             id__in=lead_ids
#         ).exclude(
#             assigned_to=assigned_user
#         )
        
#         assigned_count = leads_to_assign.count()
#         already_assigned_count = len(selected_leads) - assigned_count
        
#         if assigned_count > 0:
#             # ✅ BULK UPDATE assignment
#             leads_to_assign.update(assigned_to=assigned_user)
            
#             # ✅ BULK CREATE logs
#             content_type = ContentType.objects.get_for_model(ForexTrade)
#             logs = [
#                 LeadAssignmentLog(
#                     lead_content_type=content_type,
#                     lead_object_id=lead.id,
#                     assigned_to=assigned_user,
#                     assigned_by=request.user,
#                     status_at_assignment=lead.status,
#                     notes=remarks
#                 ) for lead in leads_to_assign
#             ]
#             LeadAssignmentLog.objects.bulk_create(logs)
            
#             messages.success(request, f"{assigned_count} Forex Trade leads assigned to {assigned_user.username} successfully!")
        
#         if already_assigned_count > 0:
#             messages.warning(request, f"{already_assigned_count} leads were already assigned to {assigned_user.username} and skipped.")

#         leadassign_mail(assigned_user.email)
#         return redirect('central_admin:forex_trade')
    
#     # GET request -> show all leads (assigned or unassigned)
#     leads = ForexTrade.objects.all().order_by('-created_at')
#     users = User.objects.filter(industry='trading') 

#     user_name = request.session.get('user_name')
#     user_email = request.session.get('user_email')
#     user_role = request.session.get('user_role')
#     short_name = user_name[:2].upper() if user_name else ""

#     context = {
#         'leads': leads,
#         'users': users,
#         'name': user_name,
#         'email': user_email,
#         'role': user_role,
#         'short_name': short_name,
#     }
#     return render(request, "central_admin/forex_trade.html", context)

def forex_trade(request):
    if request.method == 'POST':
        selected_leads = request.POST.getlist('leads')
        assigned_user_id = request.POST.get('assigned_to')
        remarks = request.POST.get('remarks', '')

        if not selected_leads or not assigned_user_id:
            messages.error(request, "Please select leads and a user to assign.")
            return redirect('central_admin:forex_trade')

        try:
            assigned_user = User.objects.get(id=assigned_user_id)
        except User.DoesNotExist:
            messages.error(request, "Selected user does not exist.")
            return redirect('central_admin:forex_trade')

        # ✅ SPEED OPTIMIZATION: Direct bulk operations
        lead_ids = [int(lead_id) for lead_id in selected_leads]
        
        # Get leads that are NOT already assigned to this user
        leads_to_assign = ForexTrade.objects.filter(
            id__in=lead_ids
        ).exclude(
            assigned_to=assigned_user
        )
        
        assigned_count = leads_to_assign.count()
        already_assigned_count = len(selected_leads) - assigned_count
        
        if assigned_count > 0:
            # ✅ CREDIT MANAGEMENT: Add credits_used for new assignments only
            assigned_user.credits_used += assigned_count
            assigned_user.save()
            
            # ✅ BULK UPDATE assignment
            leads_to_assign.update(assigned_to=assigned_user)
            
            # ✅ BULK CREATE logs
            content_type = ContentType.objects.get_for_model(ForexTrade)
            logs = [
                LeadAssignmentLog(
                    lead_content_type=content_type,
                    lead_object_id=lead.id,
                    assigned_to=assigned_user,
                    assigned_by=request.user,
                    status_at_assignment=lead.status,
                    notes=remarks
                ) for lead in leads_to_assign
            ]
            LeadAssignmentLog.objects.bulk_create(logs)
            
            messages.success(
                request, 
                f"{assigned_count} Forex Trade leads assigned to {assigned_user.username} successfully! "
                f"({assigned_count} credits deducted)"
            )
        
        if already_assigned_count > 0:
            messages.warning(
                request, 
                f"{already_assigned_count} leads were already assigned to {assigned_user.username} and skipped."
            )

        leadassign_mail(assigned_user.email)
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

def get_assignment_history_forex_trade(request, lead_id):
    try:
        # Get all assignment logs for this Forex Trade lead
        assignments = LeadAssignmentLog.objects.filter(
            lead_content_type=ContentType.objects.get_for_model(ForexTrade),
            lead_object_id=lead_id
        ).order_by('-assigned_at')
        
        assignment_data = []
        for assignment in assignments:
            assignment_data.append({
                'assigned_to': assignment.assigned_to.username if assignment.assigned_to else 'Unknown',
                'assigned_by': assignment.assigned_by.username if assignment.assigned_by else 'Unknown',
                'assigned_at': assignment.assigned_at.strftime("%d %b %Y %H:%M"),
                'status': assignment.status_at_assignment,
                'notes': assignment.notes or ''
            })
        
        return JsonResponse({'assignments': assignment_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# ---------------------------------------------------------------------------------------


from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test

User = get_user_model()

# Only central admin can access
def is_central_admin(user):
    return user.is_authenticated and user.role == 'central_admin'



# @login_required
# @user_passes_test(is_central_admin)
# def users_list(request):
#     users = User.objects.all().order_by('-date_joined')
    
#     # ✅ Get assigned leads count for each user from ALL TIME (assignment history)
#     from django.contrib.contenttypes.models import ContentType
    
#     user_leads_data = {}
    
#     for user in users:
#         # LeadAssignmentLog se TOTAL assigned leads count (all time)
#         assigned_logs = LeadAssignmentLog.objects.filter(assigned_to=user)
        
#         # Unique leads count using phone+email combination (all time assignments)
#         unique_leads = set()
#         for log in assigned_logs:
#             lead = log.lead
#             if lead:
#                 identifier = f"{getattr(lead, 'phone_number', '')}-{getattr(lead, 'email', '')}"
#                 if identifier:
#                     unique_leads.add(identifier)
        
#         user_leads_data[user.id] = len(unique_leads)

#     # ✅ Add leads count to each user object
#     for user in users:
#         user.assigned_leads_count = user_leads_data.get(user.id, 0)

#     user_name = request.session.get('user_name')
#     user_email = request.session.get('user_email')
#     user_role = request.session.get('user_role')
#     short_name = user_name[:2].upper() if user_name else ""

#     context = {
#         'name': user_name,
#         'email': user_email,
#         'role': user_role,
#         'short_name': short_name,
#         'users': users,
#         'user_leads_count': user_leads_data,
#     }
    
#     return render(request, 'central_admin/users_list.html', context)

@login_required
@user_passes_test(is_central_admin)
def users_list(request):
    users = User.objects.all().order_by('-date_joined')

    user_leads_data = {}   # user_id : total_leads_count

    for user in users:

        # ----------------------------------------------------
        # SAME LOGIC AS SUBSCRIBER DASHBOARD (NO CHANGE)
        # ----------------------------------------------------

        # Direct assigned leads
        direct_real = RealEstateLead.objects.filter(assigned_to=user)
        direct_mba = OnlineMBA.objects.filter(assigned_to=user)
        direct_abroad = StudyAbroad.objects.filter(assigned_to=user)
        direct_forex = ForexTrade.objects.filter(assigned_to=user)

        added = set()
        total_leads_count = 0

        # Helper: avoids duplicates like dashboard
        def add_lead(lead, prefix):
            key = f"{prefix}_{lead.id}"
            if key not in added:
                added.add(key)
                return 1
            return 0

        # Direct lead counting
        for l in direct_real:
            total_leads_count += add_lead(l, "realestate")

        for l in direct_mba:
            total_leads_count += add_lead(l, "mba")

        for l in direct_abroad:
            total_leads_count += add_lead(l, "abroad")

        for l in direct_forex:
            total_leads_count += add_lead(l, "forex")

        # Assignment history leads
        history = LeadAssignmentLog.objects.filter(assigned_to=user).select_related("assigned_to")

        for h in history:
            lead = h.lead
            if not lead:
                continue

            if isinstance(lead, RealEstateLead):
                total_leads_count += add_lead(lead, "realestate")

            elif isinstance(lead, OnlineMBA):
                total_leads_count += add_lead(lead, "mba")

            elif isinstance(lead, StudyAbroad):
                total_leads_count += add_lead(lead, "abroad")

            elif isinstance(lead, ForexTrade):
                total_leads_count += add_lead(lead, "forex")

        # FINAL unique count for this user
        user_leads_data[user.id] = total_leads_count

        # Attach to user object for template
        user.assigned_leads_count = total_leads_count

    # Session data
    user_name = request.session.get('user_name')
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    short_name = user_name[:2].upper() if user_name else ""

    context = {
        'name': user_name,
        'email': user_email,
        'role': user_role,
        'short_name': short_name,
        'users': users,
        'user_leads_count': user_leads_data,
    }

    return render(request, 'central_admin/users_list.html', context)


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
        user.is_verified = bool(request.POST.get('is_verified'))
        
        # Handle credit limit adjustment
        adjustment_type = request.POST.get('credit_adjustment_type')
        adjustment_amount = int(request.POST.get('credit_adjustment_amount') or 0)
        
        if adjustment_amount > 0:
            if adjustment_type == 'increase':
                user.credit_limit += adjustment_amount
                messages.success(request, f"Credit limit increased by {adjustment_amount}. New limit: {user.credit_limit}")
            elif adjustment_type == 'decrease':
                user.credit_limit = max(0, user.credit_limit - adjustment_amount)
                messages.success(request, f"Credit limit decreased by {adjustment_amount}. New limit: {user.credit_limit}")
            elif adjustment_type == 'set':
                user.credit_limit = max(0, adjustment_amount)
                messages.success(request, f"Credit limit set to {user.credit_limit}")
        
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
            if adjustment_amount > 0:
                messages.success(request, f"User details updated! Credit limit adjusted to {user.credit_limit}")
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
#         # Update basic user information
#         user.first_name = request.POST.get('first_name')
#         user.last_name = request.POST.get('last_name')
#         user.email = request.POST.get('email')
#         user.username = request.POST.get('email')
#         user.role = request.POST.get('role')
#         user.plan_type = request.POST.get('plan_type')
#         user.plan_status = request.POST.get('plan_status')
#         user.credit_limit = request.POST.get('credit_limit') or 0
#         user.is_verified = bool(request.POST.get('is_verified'))
        
#         # Handle password change
#         new_password = request.POST.get('new_password')
#         confirm_password = request.POST.get('confirm_password')
        
#         if new_password:
#             if new_password == confirm_password:
#                 if len(new_password) >= 8:  # Basic password strength check
#                     user.set_password(new_password)
#                     messages.success(request, "User details and password updated successfully!")
#                 else:
#                     messages.error(request, "Password must be at least 8 characters long.")
#                     return render(request, 'central_admin/edit_user.html', {
#                         'user': user,
#                         'role_choices': role_choices,
#                         'plan_choices': plan_choices,
#                         'status_choices': status_choices,
#                         'name': request.session.get('user_name'),
#                         'email': request.session.get('user_email'),
#                         'role': request.session.get('user_role'),
#                         'short_name': request.session.get('user_name')[:2].upper() if request.session.get('user_name') else "",
#                     })
#             else:
#                 messages.error(request, "Passwords do not match.")
#                 return render(request, 'central_admin/edit_user.html', {
#                     'user': user,
#                     'role_choices': role_choices,
#                     'plan_choices': plan_choices,
#                     'status_choices': status_choices,
#                     'name': request.session.get('user_name'),
#                     'email': request.session.get('user_email'),
#                     'role': request.session.get('user_role'),
#                     'short_name': request.session.get('user_name')[:2].upper() if request.session.get('user_name') else "",
#                 })
#         else:
#             messages.success(request, "User details updated successfully!")
        
#         user.save()
#         return redirect('central_admin:users_list')
    
#     user_name = request.session.get('user_name')
#     user_email = request.session.get('user_email')
#     user_role = request.session.get('user_role')
#     short_name = user_name[:2].upper() if user_name else ""

#     context = {
#         'name': user_name,
#         'email': user_email,
#         'role': user_role,
#         'short_name': short_name,
#         'user': user,
#         'role_choices': role_choices,
#         'plan_choices': plan_choices,
#         'status_choices': status_choices,
#     }
#     return render(request, 'central_admin/edit_user.html', context)





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

