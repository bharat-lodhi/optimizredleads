from django.shortcuts import render, redirect ,get_object_or_404
from .models import Product
from django.contrib import messages
from django.contrib.auth import logout
from leads.models import RealEstateLead, OnlineMBA, StudyAbroad, LeadAssignmentLog,ForexTrade,LeadStatusHistory,LeadRemarkHistory,LeadReplacementHistory
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
User = get_user_model()
from landing.models import ContactLead
from django.utils import timezone
from django.db.models import Count, Q
from subscribers.models import Ticket
from optimizedleads.send_mail import leadassign_mail
from django.http import JsonResponse

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

from django.contrib.auth.decorators import login_required, user_passes_test

User = get_user_model()

# Only central admin can access
def is_central_admin(user):
    return user.is_authenticated and user.role == 'central_admin'


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




from django.http import JsonResponse
from django.db.models import Count
from django.utils import timezone


def all_tickets(request):
    """Sabh tickets ko list kare with filters"""
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
    
    # Session data
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
        'short_name': short_name,
    }
    
    return render(request, 'central_admin/tickets.html', context)

def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    lead_details = []
    if ticket.category == 'lead' and ticket.replacement_leads:
        raw_data = str(ticket.replacement_leads).strip()
        print(f"DEBUG - Raw data: '{raw_data}'")
        
        # Multiple format handle karo
        if raw_data.startswith('[') and raw_data.endswith(']'):
            # Remove brackets and process
            content = raw_data[1:-1]  # Remove [ and ]
            lead_ids = [id.strip().strip("'\"") for id in content.split(',') if id.strip()]
        else:
            # Direct comma separated
            lead_ids = [id.strip() for id in raw_data.split(',') if id.strip()]
        
        print(f"DEBUG - Lead IDs: {lead_ids}")
        
        # Load leads from database
        for lead_id in lead_ids:
            try:
                if lead_id.startswith('realestate_'):
                    lead = RealEstateLead.objects.get(id=lead_id.replace('realestate_', ''))
                    lead_details.append({
                        'id': lead_id, 'name': lead.full_name, 'phone': lead.phone_number,
                        'email': lead.email, 'category': lead.sub_industry or 'Real Estate', 'status': lead.status
                    })
                elif lead_id.startswith('mba_'):
                    lead = OnlineMBA.objects.get(id=lead_id.replace('mba_', ''))
                    lead_details.append({
                        'id': lead_id, 'name': lead.full_name, 'phone': lead.phone_number,
                        'email': lead.email, 'category': 'Online MBA', 'status': lead.status
                    })
                elif lead_id.startswith('abroad_'):
                    lead = StudyAbroad.objects.get(id=lead_id.replace('abroad_', ''))
                    lead_details.append({
                        'id': lead_id, 'name': lead.full_name, 'phone': lead.phone_number,
                        'email': lead.email, 'category': 'Study Abroad', 'status': lead.status
                    })
                elif lead_id.startswith('forex_'):
                    lead = ForexTrade.objects.get(id=lead_id.replace('forex_', ''))
                    lead_details.append({
                        'id': lead_id, 'name': lead.full_name, 'phone': lead.phone_number,
                        'email': lead.email, 'category': 'Forex Trade', 'status': lead.status
                    })
            except Exception as e:
                print(f"Error loading lead {lead_id}: {e}")
                continue
    
    print(f"DEBUG - Final lead details: {lead_details}")
    
    context = {
        'ticket': ticket,
        'lead_details': lead_details,
        'name': request.session.get('user_name'),
        'email': request.session.get('user_email'),
        'role': request.session.get('user_role'),
        'short_name': request.session.get('user_name', '')[:2].upper(),
    }
    
    return render(request, 'central_admin/ticket_detail.html', context)
def update_ticket_status(request, ticket_id):
    """Ticket status update kare"""
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
    
    return redirect('central_admin:ticket_detail', ticket_id=ticket_id)



# ----------------------------- Lead-Replacement -------------------------------------------------



# from django.contrib.auth import get_user_model

# User = get_user_model()

# @login_required
# def lead_replacement_page(request):
#     """Lead replacement ka main page"""
#     # Sirf admin hi access kar sakta hai
#     if request.user.role not in ['central_admin', 'sub_admin']:
#         return redirect('access_denied')
    
#     subscribers = User.objects.filter(role='subscriber')
    
#     context = {
#         'subscribers': subscribers,
#     }
#     return render(request, 'central_admin/lead_replacement.html', context)

# @login_required  
# def get_user_leads(request):
#     """AJAX endpoint: User ki assigned leads get kare"""
#     user_id = request.GET.get('user_id')
#     if not user_id:
#         return JsonResponse({'error': 'User ID required'}, status=400)
    
#     try:
#         user = User.objects.get(id=user_id)
#         lead_models = [RealEstateLead, OnlineMBA, StudyAbroad, ForexTrade]
        
#         user_leads = []
#         for model in lead_models:
#             content_type = ContentType.objects.get_for_model(model)
#             # Sirf active leads show karein (trashed nahi)
#             leads = model.objects.filter(
#                 assigned_to=user, 
#                 status__in=['new', 'in_process', 'lead_replacement']
#             )
            
#             for lead in leads:
#                 user_leads.append({
#                     'id': f"{content_type.id}_{lead.id}",
#                     'name': f"{lead.full_name} - {model.__name__}",
#                     'content_type_id': content_type.id,
#                     'object_id': lead.id,
#                     'model_name': model.__name__,
#                     'phone': lead.phone_number or 'No Phone',
#                     'email': lead.email or 'No Email',
#                     'status': lead.status
#                 })
        
#         return JsonResponse({'leads': user_leads})
    
#     except User.DoesNotExist:
#         return JsonResponse({'error': 'User not found'}, status=404)

# @login_required
# def get_available_leads(request):
#     """AJAX endpoint: Available leads get kare (jo assigned nahi hain AUR user ki industry se match karein)"""
#     lead_type = request.GET.get('lead_type')  # e.g., 'RealEstateLead'
#     subscriber_id = request.GET.get('subscriber_id')  # ✅ Naya parameter
    
#     if not lead_type or not subscriber_id:
#         return JsonResponse({'error': 'Lead type and subscriber ID required'}, status=400)
    
#     try:
#         # Subscriber get karein
#         subscriber = User.objects.get(id=subscriber_id)
        
#         # Model class find karein
#         model_map = {
#             'RealEstateLead': RealEstateLead,
#             'OnlineMBA': OnlineMBA, 
#             'StudyAbroad': StudyAbroad,
#             'ForexTrade': ForexTrade
#         }
        
#         model_class = model_map.get(lead_type)
#         if not model_class:
#             return JsonResponse({'error': 'Invalid lead type'}, status=400)
        
#         # Base query - available leads
#         available_leads = model_class.objects.filter(
#             assigned_to__isnull=True,
#             status='new'
#         )
        
#         # ✅ INDUSTRY MATCHING LOGIC ADD KAREIN
#         filtered_leads = []
#         for lead in available_leads:
#             match_score = calculate_industry_match(lead, subscriber, model_class.__name__)
            
#             # Only show leads that have some level of matching
#             if match_score > 0:
#                 filtered_leads.append({
#                     'id': lead.id,
#                     'name': f"{lead.full_name}",
#                     'phone': lead.phone_number or 'No Phone',
#                     'email': lead.email or 'No Email',
#                     'model_type': lead_type,
#                     'match_score': match_score,  # Matching percentage
#                     'match_reason': get_match_reason(lead, subscriber, model_class.__name__)
#                 })
        
#         # Sort by match score (highest first)
#         filtered_leads.sort(key=lambda x: x['match_score'], reverse=True)
        
#         return JsonResponse({'leads': filtered_leads})
    
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)

# def calculate_industry_match(lead, subscriber, lead_type):
#     """Calculate how well lead matches subscriber's preferences"""
#     match_score = 0
    
#     if lead_type == 'RealEstateLead':
#         # Real Estate matching logic
#         if subscriber.industry and 'real estate' in subscriber.industry.lower():
#             match_score += 30
        
#         if subscriber.property_type and lead.property_type:
#             if subscriber.property_type.lower() == lead.property_type.lower():
#                 match_score += 40
        
#         if subscriber.preferred_country and lead.location:
#             if subscriber.preferred_country.lower() in lead.location.lower():
#                 match_score += 30
    
#     elif lead_type == 'StudyAbroad':
#         # Study Abroad matching logic
#         if subscriber.industry and 'education' in subscriber.industry.lower():
#             match_score += 30
        
#         if subscriber.preferred_country and lead.country:
#             if subscriber.preferred_country.lower() == lead.country.lower():
#                 match_score += 40
        
#         if subscriber.sub_industry and lead.exam:
#             if any(sub in lead.exam.lower() for sub in subscriber.sub_industry.lower().split()):
#                 match_score += 30
    
#     elif lead_type == 'ForexTrade':
#         # Forex Trade matching logic
#         if subscriber.industry and 'finance' in subscriber.industry.lower():
#             match_score += 60
        
#         if subscriber.preferred_country and lead.country:
#             if subscriber.preferred_country.lower() == lead.country.lower():
#                 match_score += 40
    
#     elif lead_type == 'OnlineMBA':
#         # Online MBA matching logic
#         if subscriber.industry and 'education' in subscriber.industry.lower():
#             match_score += 60
        
#         if subscriber.sub_industry and lead.course:
#             if any(sub in lead.course.lower() for sub in subscriber.sub_industry.lower().split()):
#                 match_score += 40
    
#     return match_score

# def get_match_reason(lead, subscriber, lead_type):
#     """Get readable reason for matching"""
#     reasons = []
    
#     if lead_type == 'RealEstateLead':
#         if subscriber.property_type and lead.property_type and subscriber.property_type.lower() == lead.property_type.lower():
#             reasons.append(f"Property type: {lead.property_type}")
#         if subscriber.preferred_country and lead.location and subscriber.preferred_country.lower() in lead.location.lower():
#             reasons.append(f"Location: {lead.location}")
    
#     elif lead_type == 'StudyAbroad':
#         if subscriber.preferred_country and lead.country and subscriber.preferred_country.lower() == lead.country.lower():
#             reasons.append(f"Country: {lead.country}")
    
#     return ", ".join(reasons) if reasons else "Basic match"

# @login_required
# def replace_lead(request):
#     """Lead replace karne ka main function"""
#     if request.method == 'POST':
#         try:
#             # Data get karein
#             subscriber_id = request.POST.get('subscriber_id')
#             old_lead_id = request.POST.get('old_lead_id')  # format: "content_type_id_object_id"
#             new_lead_id = request.POST.get('new_lead_id')
#             reason = request.POST.get('reason', '')
            
#             # Old lead details parse karein
#             content_type_id, object_id = old_lead_id.split('_')
#             old_content_type = ContentType.objects.get(id=content_type_id)
#             old_lead_model = old_content_type.model_class()
#             old_lead = old_lead_model.objects.get(id=object_id)
            
#             # New lead details (same type ki lead hi hogi)
#             new_lead = old_lead_model.objects.get(id=new_lead_id)
            
#             # Subscriber get karein
#             subscriber = User.objects.get(id=subscriber_id)
            
#             # Pehle check karein ki old lead actually isi subscriber ko assigned hai
#             if old_lead.assigned_to != subscriber:
#                 return JsonResponse({
#                     'success': False, 
#                     'error': 'Selected lead is not assigned to this subscriber'
#                 }, status=400)
            
#             # Lead replacement history create karein
#             replacement = LeadReplacementHistory.objects.create(
#                 old_lead_content_type=old_content_type,
#                 old_lead_object_id=old_lead.id,
#                 new_lead_content_type=old_content_type, 
#                 new_lead_object_id=new_lead.id,
#                 subscriber=subscriber,
#                 replaced_by_admin=request.user,
#                 reason=reason
#             )
            
#             # Actual lead update karein
#             # Purani lead ko trashed status mein daalein
#             old_lead.status = 'trashed'
#             old_lead.remark = f"Replaced with new lead #{new_lead.id} - {reason}"
#             old_lead.assigned_to = None
#             old_lead.save()
            
#             # Nayi lead assign karein
#             new_lead.assigned_to = subscriber
#             new_lead.status = 'new'
#             new_lead.save()
            
#             # Assignment log create karein
#             LeadAssignmentLog.objects.create(
#                 lead_content_type=old_content_type,
#                 lead_object_id=new_lead.id,
#                 assigned_to=subscriber,
#                 assigned_by=request.user,
#                 status_at_assignment='new',
#                 notes=f"Lead replacement - Replaced lead #{old_lead.id} with this lead"
#             )
            
#             return JsonResponse({
#                 'success': True,
#                 'message': f'Lead successfully replaced! Old: {old_lead.full_name}, New: {new_lead.full_name}'
#             })
            
#         except Exception as e:
#             return JsonResponse({
#                 'success': False, 
#                 'error': str(e)
#             }, status=500)
    
#     return JsonResponse({'error': 'Invalid request'}, status=400)

# @login_required
# def replacement_history(request):
#     """Complete replacement history show kare"""
#     # Sirf admin hi dekh sakta hai
#     if request.user.role not in ['central_admin', 'sub_admin']:
#         return redirect('access_denied')
    
#     replacements = LeadReplacementHistory.objects.all().select_related(
#         'subscriber', 'replaced_by_admin'
#     ).order_by('-replaced_at')
    
#     # Statistics ke liye data
#     unique_subscribers = replacements.values('subscriber').distinct().count()
#     unique_admins = replacements.values('replaced_by_admin').distinct().count()
#     last_replacement = replacements.first()
    
#     # All subscribers and admins for filters
#     subscribers = User.objects.filter(role='subscriber')
#     admins = User.objects.filter(role__in=['central_admin', 'sub_admin'])
    
#     # Pagination
#     paginator = Paginator(replacements, 20)  # 20 items per page
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
    
#     context = {
#         'replacements': page_obj,
#         'unique_subscribers': unique_subscribers,
#         'unique_admins': unique_admins,
#         'last_replacement': last_replacement,
#         'subscribers': subscribers,
#         'admins': admins,
#     }
#     return render(request, 'leads/replacement_history.html', context)

# @login_required
# def get_subscriber_info(request):
#     """AJAX endpoint: Subscriber information get kare"""
#     subscriber_id = request.GET.get('subscriber_id')
#     try:
#         subscriber = User.objects.get(id=subscriber_id)
#         return JsonResponse({
#             'subscriber': {
#                 'username': subscriber.username,
#                 'email': subscriber.email,
#                 'phone': subscriber.phone,
#                 'industry': subscriber.industry,
#                 'sub_industry': subscriber.sub_industry,
#                 'preferred_country': subscriber.preferred_country,
#                 'property_type': subscriber.property_type,
#                 'plan_type': subscriber.plan_type,
#             }
#         })
#     except User.DoesNotExist:
#         return JsonResponse({'error': 'Subscriber not found'}, status=404)



@login_required
@user_passes_test(is_central_admin)
def lead_replacement_start(request):
    """
    Step 1: User selection for lead replacement
    """
    users = User.objects.filter(
        Q(role='subscriber') | Q(role='sub_admin'),
        is_active=True
    ).order_by('username')
    
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
    }
    return render(request, 'central_admin/lead_replacement_start.html', context)


# @login_required
# @user_passes_test(is_central_admin)
# def lead_replacement_select_lead(request, user_id):
#     """
#     Step 2: Show user's assigned leads for replacement
#     """
#     try:
#         user = User.objects.get(id=user_id, is_active=True)
        
#         # Get all assigned leads for this user
#         assigned_leads = []
        
#         # Real Estate Leads
#         real_estate_leads = RealEstateLead.objects.filter(assigned_to=user)
#         for lead in real_estate_leads:
#             assigned_leads.append({
#                 'id': lead.id,
#                 'type': 'real_estate',
#                 'type_display': 'Real Estate',
#                 'full_name': lead.full_name or 'N/A',
#                 'phone_number': lead.phone_number or 'N/A',
#                 'email': lead.email or 'N/A',
#                 'status': lead.status,
#                 'created_at': lead.created_at
#             })
        
#         # Online MBA Leads
#         mba_leads = OnlineMBA.objects.filter(assigned_to=user)
#         for lead in mba_leads:
#             assigned_leads.append({
#                 'id': lead.id,
#                 'type': 'online_mba',
#                 'type_display': 'Online MBA',
#                 'full_name': lead.full_name or 'N/A',
#                 'phone_number': lead.phone_number or 'N/A',
#                 'email': lead.email or 'N/A',
#                 'status': lead.status,
#                 'created_at': lead.created_at
#             })
        
#         # Study Abroad Leads
#         abroad_leads = StudyAbroad.objects.filter(assigned_to=user)
#         for lead in abroad_leads:
#             assigned_leads.append({
#                 'id': lead.id,
#                 'type': 'study_abroad',
#                 'type_display': 'Study Abroad',
#                 'full_name': lead.full_name or 'N/A',
#                 'phone_number': lead.phone_number or 'N/A',
#                 'email': lead.email or 'N/A',
#                 'status': lead.status,
#                 'created_at': lead.created_at
#             })
        
#         # Forex Trade Leads
#         forex_leads = ForexTrade.objects.filter(assigned_to=user)
#         for lead in forex_leads:
#             assigned_leads.append({
#                 'id': lead.id,
#                 'type': 'forex_trade',
#                 'type_display': 'Forex Trade',
#                 'full_name': lead.full_name or 'N/A',
#                 'phone_number': lead.phone_number or 'N/A',
#                 'email': lead.email or 'N/A',
#                 'status': lead.status,
#                 'created_at': lead.created_at
#             })
        
#         user_name = request.session.get('user_name')
#         user_email = request.session.get('user_email')
#         user_role = request.session.get('user_role')
#         short_name = user_name[:2].upper() if user_name else ""

#         context = {
#             'name': user_name,
#             'email': user_email,
#             'role': user_role,
#             'short_name': short_name,
#             'user': user,
#             'assigned_leads': assigned_leads,
#         }
        
#         if not assigned_leads:
#             messages.info(request, f"{user.username} has no assigned leads to replace.")
        
#         return render(request, 'central_admin/lead_replacement_select_lead.html', context)
        
#     except User.DoesNotExist:
#         messages.error(request, "User not found.")
#         return redirect('central_admin:lead_replacement_start')


# @login_required
# @user_passes_test(is_central_admin)
# def lead_replacement_select_lead(request, user_id):
#     """
#     Step 2: Show user's assigned leads for replacement
#     """
#     try:
#         user = User.objects.get(id=user_id, is_active=True)
        
#         # Get all assigned leads for this user
#         assigned_leads = []
        
#         # Real Estate Leads - EXCLUDE REPLACED LEADS
#         real_estate_leads = RealEstateLead.objects.filter(
#             assigned_to=user
#         ).exclude(
#             is_replaced=True, replaced_for_user=user
#         )
#         for lead in real_estate_leads:
#             assigned_leads.append({
#                 'id': lead.id,
#                 'type': 'real_estate',
#                 'type_display': 'Real Estate',
#                 'full_name': lead.full_name or 'N/A',
#                 'phone_number': lead.phone_number or 'N/A',
#                 'email': lead.email or 'N/A',
#                 'status': lead.status,
#                 'created_at': lead.created_at,
#                 'is_replaced': lead.is_replaced  # For debugging
#             })
        
#         # Online MBA Leads - EXCLUDE REPLACED LEADS
#         mba_leads = OnlineMBA.objects.filter(
#             assigned_to=user
#         ).exclude(
#             is_replaced=True, replaced_for_user=user
#         )
#         for lead in mba_leads:
#             assigned_leads.append({
#                 'id': lead.id,
#                 'type': 'online_mba',
#                 'type_display': 'Online MBA',
#                 'full_name': lead.full_name or 'N/A',
#                 'phone_number': lead.phone_number or 'N/A',
#                 'email': lead.email or 'N/A',
#                 'status': lead.status,
#                 'created_at': lead.created_at,
#                 'is_replaced': lead.is_replaced  # For debugging
#             })
        
#         # Study Abroad Leads - EXCLUDE REPLACED LEADS
#         abroad_leads = StudyAbroad.objects.filter(
#             assigned_to=user
#         ).exclude(
#             is_replaced=True, replaced_for_user=user
#         )
#         for lead in abroad_leads:
#             assigned_leads.append({
#                 'id': lead.id,
#                 'type': 'study_abroad',
#                 'type_display': 'Study Abroad',
#                 'full_name': lead.full_name or 'N/A',
#                 'phone_number': lead.phone_number or 'N/A',
#                 'email': lead.email or 'N/A',
#                 'status': lead.status,
#                 'created_at': lead.created_at,
#                 'is_replaced': lead.is_replaced  # For debugging
#             })
        
#         # Forex Trade Leads - EXCLUDE REPLACED LEADS
#         forex_leads = ForexTrade.objects.filter(
#             assigned_to=user
#         ).exclude(
#             is_replaced=True, replaced_for_user=user
#         )
#         for lead in forex_leads:
#             assigned_leads.append({
#                 'id': lead.id,
#                 'type': 'forex_trade',
#                 'type_display': 'Forex Trade',
#                 'full_name': lead.full_name or 'N/A',
#                 'phone_number': lead.phone_number or 'N/A',
#                 'email': lead.email or 'N/A',
#                 'status': lead.status,
#                 'created_at': lead.created_at,
#                 'is_replaced': lead.is_replaced  # For debugging
#             })
        
#         print(f"🔍 DEBUG: Found {len(assigned_leads)} assigned leads for {user.username}")
        
#         user_name = request.session.get('user_name')
#         user_email = request.session.get('user_email')
#         user_role = request.session.get('user_role')
#         short_name = user_name[:2].upper() if user_name else ""

#         context = {
#             'name': user_name,
#             'email': user_email,
#             'role': user_role,
#             'short_name': short_name,
#             'user': user,
#             'assigned_leads': assigned_leads,
#         }
        
#         if not assigned_leads:
#             messages.info(request, f"{user.username} has no assigned leads to replace.")
        
#         return render(request, 'central_admin/lead_replacement_select_lead.html', context)
        
#     except User.DoesNotExist:
#         messages.error(request, "User not found.")
#         return redirect('central_admin:lead_replacement_start')



@login_required
@user_passes_test(is_central_admin)
def lead_replacement_select_lead(request, user_id):
    """
    Step 2: Show user's assigned leads for replacement
    """
    try:
        user = User.objects.get(id=user_id, is_active=True)
        
        # Get all assigned leads for this user (BOTH direct + assignment history)
        assigned_leads = []
        
        # Method 1: Direct assigned_to se (single assignment)
        # Real Estate Leads - EXCLUDE REPLACED LEADS
        real_estate_leads = RealEstateLead.objects.filter(
            assigned_to=user
        ).exclude(
            is_replaced=True, replaced_for_user=user
        )
        for lead in real_estate_leads:
            assigned_leads.append({
                'id': lead.id,
                'type': 'real_estate',
                'type_display': 'Real Estate',
                'full_name': lead.full_name or 'N/A',
                'phone_number': lead.phone_number or 'N/A',
                'email': lead.email or 'N/A',
                'status': lead.status,
                'created_at': lead.created_at,
                'assignment_type': 'direct'
            })
        
        # Online MBA Leads - EXCLUDE REPLACED LEADS
        mba_leads = OnlineMBA.objects.filter(
            assigned_to=user
        ).exclude(
            is_replaced=True, replaced_for_user=user
        )
        for lead in mba_leads:
            assigned_leads.append({
                'id': lead.id,
                'type': 'online_mba',
                'type_display': 'Online MBA',
                'full_name': lead.full_name or 'N/A',
                'phone_number': lead.phone_number or 'N/A',
                'email': lead.email or 'N/A',
                'status': lead.status,
                'created_at': lead.created_at,
                'assignment_type': 'direct'
            })
        
        # Study Abroad Leads - EXCLUDE REPLACED LEADS
        abroad_leads = StudyAbroad.objects.filter(
            assigned_to=user
        ).exclude(
            is_replaced=True, replaced_for_user=user
        )
        for lead in abroad_leads:
            assigned_leads.append({
                'id': lead.id,
                'type': 'study_abroad',
                'type_display': 'Study Abroad',
                'full_name': lead.full_name or 'N/A',
                'phone_number': lead.phone_number or 'N/A',
                'email': lead.email or 'N/A',
                'status': lead.status,
                'created_at': lead.created_at,
                'assignment_type': 'direct'
            })
        
        # Forex Trade Leads - EXCLUDE REPLACED LEADS
        forex_leads = ForexTrade.objects.filter(
            assigned_to=user
        ).exclude(
            is_replaced=True, replaced_for_user=user
        )
        for lead in forex_leads:
            assigned_leads.append({
                'id': lead.id,
                'type': 'forex_trade',
                'type_display': 'Forex Trade',
                'full_name': lead.full_name or 'N/A',
                'phone_number': lead.phone_number or 'N/A',
                'email': lead.email or 'N/A',
                'status': lead.status,
                'created_at': lead.created_at,
                'assignment_type': 'direct'
            })

        # Method 2: Assignment history se (multiple assignment) - SAME AS my_leads
        from django.contrib.contenttypes.models import ContentType
        
        # Get content types for all lead models
        real_estate_ct = ContentType.objects.get_for_model(RealEstateLead)
        mba_ct = ContentType.objects.get_for_model(OnlineMBA)
        study_abroad_ct = ContentType.objects.get_for_model(StudyAbroad)
        forex_ct = ContentType.objects.get_for_model(ForexTrade)

        # Get lead IDs from assignment logs for this user
        assignment_lead_ids = LeadAssignmentLog.objects.filter(
            assigned_to=user
        ).values_list('lead_object_id', 'lead_content_type')

        # Set to track already added leads
        added_lead_ids = set()

        # Helper function to add lead if not already added
        def add_lead(lead_data, lead_id, model_type):
            lead_key = f"{model_type}_{lead_id}"
            if lead_key not in added_lead_ids:
                added_lead_ids.add(lead_key)
                assigned_leads.append(lead_data)
                return True
            return False

        # Mark already added direct leads
        for lead in assigned_leads:
            lead_key = f"{lead['type']}_{lead['original_id']}" if 'original_id' in lead else f"{lead['type']}_{lead['id']}"
            added_lead_ids.add(lead_key)

        # Process assignment history leads (only add if not already present)
        for lead_id, content_type_id in assignment_lead_ids:
            try:
                content_type = ContentType.objects.get_for_id(content_type_id)
                lead_model = content_type.model_class()
                lead = lead_model.objects.get(id=lead_id)
                
                # Skip if lead is replaced for this user
                if lead.is_replaced and lead.replaced_for_user == user:
                    continue
                    
                model_type = content_type.model
                
                # Check if lead already exists using our tracking set
                lead_key = f"{model_type}_{lead.id}"
                if lead_key in added_lead_ids:
                    continue
                    
                if isinstance(lead, RealEstateLead):
                    lead_data = {
                        'id': lead.id,
                        'type': 'real_estate',
                        'type_display': 'Real Estate',
                        'full_name': lead.full_name or 'N/A',
                        'phone_number': lead.phone_number or 'N/A',
                        'email': lead.email or 'N/A',
                        'status': lead.status,
                        'created_at': lead.created_at,
                        'assignment_type': 'history'
                    }
                    add_lead(lead_data, lead.id, 'real_estate')
                    
                elif isinstance(lead, OnlineMBA):
                    lead_data = {
                        'id': lead.id,
                        'type': 'online_mba',
                        'type_display': 'Online MBA',
                        'full_name': lead.full_name or 'N/A',
                        'phone_number': lead.phone_number or 'N/A',
                        'email': lead.email or 'N/A',
                        'status': lead.status,
                        'created_at': lead.created_at,
                        'assignment_type': 'history'
                    }
                    add_lead(lead_data, lead.id, 'online_mba')
                    
                elif isinstance(lead, StudyAbroad):
                    lead_data = {
                        'id': lead.id,
                        'type': 'study_abroad',
                        'type_display': 'Study Abroad',
                        'full_name': lead.full_name or 'N/A',
                        'phone_number': lead.phone_number or 'N/A',
                        'email': lead.email or 'N/A',
                        'status': lead.status,
                        'created_at': lead.created_at,
                        'assignment_type': 'history'
                    }
                    add_lead(lead_data, lead.id, 'study_abroad')
                    
                elif isinstance(lead, ForexTrade):
                    lead_data = {
                        'id': lead.id,
                        'type': 'forex_trade',
                        'type_display': 'Forex Trade',
                        'full_name': lead.full_name or 'N/A',
                        'phone_number': lead.phone_number or 'N/A',
                        'email': lead.email or 'N/A',
                        'status': lead.status,
                        'created_at': lead.created_at,
                        'assignment_type': 'history'
                    }
                    add_lead(lead_data, lead.id, 'forex_trade')
                        
            except Exception as e:
                print(f"Error processing lead from history: {e}")
                continue

        print(f"🔍 DEBUG: Total assigned leads for {user.username}: {len(assigned_leads)}")
        
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
            'assigned_leads': assigned_leads,
        }
        
        if not assigned_leads:
            messages.info(request, f"{user.username} has no assigned leads to replace.")
        
        return render(request, 'central_admin/lead_replacement_select_lead.html', context)
        
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('central_admin:lead_replacement_start')


# @login_required
# @user_passes_test(is_central_admin)
# def lead_replacement_select_new_lead(request, user_id):
#     """
#     Step 3: Show available leads for replacement
#     """
#     try:
#         user = User.objects.get(id=user_id, is_active=True)
        
#         # Get old lead details from POST
#         old_lead_id = request.POST.get('old_lead_id')
#         old_lead_type = request.POST.get('old_lead_type')
        
#         print(f"🔍 DEBUG: User ID = {user_id}")
#         print(f"🔍 DEBUG: User Industry = '{user.industry}'")
#         print(f"🔍 DEBUG: Old Lead Type = '{old_lead_type}'")
        
#         if not old_lead_id or not old_lead_type:
#             messages.error(request, "Please select a lead to replace.")
#             return redirect('central_admin:lead_replacement_select_lead', user_id=user_id)
        
#         # Get old lead object
#         old_lead = None
#         if old_lead_type == 'real_estate':
#             old_lead = get_object_or_404(RealEstateLead, id=old_lead_id)
#         elif old_lead_type == 'online_mba':
#             old_lead = get_object_or_404(OnlineMBA, id=old_lead_id)
#         elif old_lead_type == 'study_abroad':
#             old_lead = get_object_or_404(StudyAbroad, id=old_lead_id)
#         elif old_lead_type == 'forex_trade':
#             old_lead = get_object_or_404(ForexTrade, id=old_lead_id)
        
#         # **FINAL FIX: Sirf same industry ke leads dikhao**
#         available_leads = []
        
#         # Industry mapping
#         industry_mapping = {
#             'real-estate': 'real_estate',
#             'education': 'online_mba', 
#             'study-abroad': 'study_abroad',
#             'trading': 'forex_trade'
#         }
        
#         # Get target industry type
#         target_industry_type = industry_mapping.get(user.industry)
#         print(f"🔍 DEBUG: Target Industry Type = '{target_industry_type}'")
        
#         # Agar industry match kare toh sirf usi type ke leads dikhao
#         if target_industry_type:
#             if target_industry_type == 'real_estate':
#                 leads = RealEstateLead.objects.exclude(assigned_to=user)
#                 lead_type_display = 'Real Estate'
#             elif target_industry_type == 'online_mba':
#                 leads = OnlineMBA.objects.exclude(assigned_to=user)
#                 lead_type_display = 'Online MBA'
#             elif target_industry_type == 'study_abroad':
#                 leads = StudyAbroad.objects.exclude(assigned_to=user)
#                 lead_type_display = 'Study Abroad'
#             elif target_industry_type == 'forex_trade':
#                 leads = ForexTrade.objects.exclude(assigned_to=user)
#                 lead_type_display = 'Forex Trade'
            
#             print(f"🔍 DEBUG: Found {leads.count()} {lead_type_display} leads for industry '{user.industry}'")
            
#             for lead in leads:
#                 available_leads.append({
#                     'id': lead.id,
#                     'type': target_industry_type,
#                     'type_display': lead_type_display,
#                     'full_name': lead.full_name or 'N/A',
#                     'phone_number': lead.phone_number or 'N/A',
#                     'email': lead.email or 'N/A',
#                     'status': lead.status,
#                     'created_at': lead.created_at,
#                     'currently_assigned_to': lead.assigned_to.username if lead.assigned_to else 'Unassigned'
#                 })
#         else:
#             # Agar industry map na ho toh old lead type ke hisaab se dikhao
#             print(f"⚠️ DEBUG: No industry mapping found, using old lead type: {old_lead_type}")
#             if old_lead_type == 'real_estate':
#                 leads = RealEstateLead.objects.exclude(assigned_to=user)
#                 lead_type_display = 'Real Estate'
#             elif old_lead_type == 'online_mba':
#                 leads = OnlineMBA.objects.exclude(assigned_to=user)
#                 lead_type_display = 'Online MBA'
#             elif old_lead_type == 'study_abroad':
#                 leads = StudyAbroad.objects.exclude(assigned_to=user)
#                 lead_type_display = 'Study Abroad'
#             elif old_lead_type == 'forex_trade':
#                 leads = ForexTrade.objects.exclude(assigned_to=user)
#                 lead_type_display = 'Forex Trade'
            
#             for lead in leads:
#                 available_leads.append({
#                     'id': lead.id,
#                     'type': old_lead_type,
#                     'type_display': lead_type_display,
#                     'full_name': lead.full_name or 'N/A',
#                     'phone_number': lead.phone_number or 'N/A',
#                     'email': lead.email or 'N/A',
#                     'status': lead.status,
#                     'created_at': lead.created_at,
#                     'currently_assigned_to': lead.assigned_to.username if lead.assigned_to else 'Unassigned'
#                 })
        
#         print(f"🔍 DEBUG: Total filtered available leads = {len(available_leads)}")
        
#         user_name = request.session.get('user_name')
#         user_email = request.session.get('user_email')
#         user_role = request.session.get('user_role')
#         short_name = user_name[:2].upper() if user_name else ""

#         context = {
#             'name': user_name,
#             'email': user_email,
#             'role': user_role,
#             'short_name': short_name,
#             'user': user,
#             'old_lead': old_lead,
#             'old_lead_type': old_lead_type,
#             'available_leads': available_leads,
#             'show_assignment_info': True
#         }
        
#         if not available_leads:
#             messages.info(request, f"No available {lead_type_display} leads for replacement.")
        
#         return render(request, 'central_admin/lead_replacement_select_new_lead.html', context)
        
#     except User.DoesNotExist:
#         messages.error(request, "User not found.")
#         return redirect('central_admin:lead_replacement_start')
    

@login_required
@user_passes_test(is_central_admin)
def lead_replacement_select_new_lead(request, user_id):
    """
    Step 3: Show available leads for replacement
    """
    try:
        user = User.objects.get(id=user_id, is_active=True)
        
        # Get old lead details from POST
        old_lead_id = request.POST.get('old_lead_id')
        old_lead_type = request.POST.get('old_lead_type')
        
        print(f"🔍 DEBUG: User ID = {user_id}")
        print(f"🔍 DEBUG: User Industry = '{user.industry}'")
        print(f"🔍 DEBUG: Old Lead Type = '{old_lead_type}'")
        
        if not old_lead_id or not old_lead_type:
            messages.error(request, "Please select a lead to replace.")
            return redirect('central_admin:lead_replacement_select_lead', user_id=user_id)
        
        # Get old lead object
        old_lead = None
        if old_lead_type == 'real_estate':
            old_lead = get_object_or_404(RealEstateLead, id=old_lead_id)
        elif old_lead_type == 'online_mba':
            old_lead = get_object_or_404(OnlineMBA, id=old_lead_id)
        elif old_lead_type == 'study_abroad':
            old_lead = get_object_or_404(StudyAbroad, id=old_lead_id)
        elif old_lead_type == 'forex_trade':
            old_lead = get_object_or_404(ForexTrade, id=old_lead_id)
        
        # **UPDATED: Sirf same industry ke leads dikhao + replaced leads exclude karo**
        available_leads = []
        
        # Industry mapping
        industry_mapping = {
            'real-estate': 'real_estate',
            'education': 'online_mba', 
            'study-abroad': 'study_abroad',
            'trading': 'forex_trade'
        }
        
        # Get target industry type
        target_industry_type = industry_mapping.get(user.industry)
        print(f"🔍 DEBUG: Target Industry Type = '{target_industry_type}'")
        
        # Agar industry match kare toh sirf usi type ke leads dikhao
        if target_industry_type:
            if target_industry_type == 'real_estate':
                leads = RealEstateLead.objects.exclude(assigned_to=user).exclude(
                    is_replaced=True, replaced_for_user=user
                )
                lead_type_display = 'Real Estate'
            elif target_industry_type == 'online_mba':
                leads = OnlineMBA.objects.exclude(assigned_to=user).exclude(
                    is_replaced=True, replaced_for_user=user
                )
                lead_type_display = 'Online MBA'
            elif target_industry_type == 'study_abroad':
                leads = StudyAbroad.objects.exclude(assigned_to=user).exclude(
                    is_replaced=True, replaced_for_user=user
                )
                lead_type_display = 'Study Abroad'
            elif target_industry_type == 'forex_trade':
                leads = ForexTrade.objects.exclude(assigned_to=user).exclude(
                    is_replaced=True, replaced_for_user=user
                )
                lead_type_display = 'Forex Trade'
            
            print(f"🔍 DEBUG: Found {leads.count()} {lead_type_display} leads for industry '{user.industry}'")
            
            for lead in leads:
                available_leads.append({
                    'id': lead.id,
                    'type': target_industry_type,
                    'type_display': lead_type_display,
                    'full_name': lead.full_name or 'N/A',
                    'phone_number': lead.phone_number or 'N/A',
                    'email': lead.email or 'N/A',
                    'status': lead.status,
                    'created_at': lead.created_at,
                    'currently_assigned_to': lead.assigned_to.username if lead.assigned_to else 'Unassigned',
                    'is_replaced': lead.is_replaced  # For debugging
                })
        else:
            # Agar industry map na ho toh old lead type ke hisaab se dikhao
            print(f"⚠️ DEBUG: No industry mapping found, using old lead type: {old_lead_type}")
            if old_lead_type == 'real_estate':
                leads = RealEstateLead.objects.exclude(assigned_to=user).exclude(
                    is_replaced=True, replaced_for_user=user
                )
                lead_type_display = 'Real Estate'
            elif old_lead_type == 'online_mba':
                leads = OnlineMBA.objects.exclude(assigned_to=user).exclude(
                    is_replaced=True, replaced_for_user=user
                )
                lead_type_display = 'Online MBA'
            elif old_lead_type == 'study_abroad':
                leads = StudyAbroad.objects.exclude(assigned_to=user).exclude(
                    is_replaced=True, replaced_for_user=user
                )
                lead_type_display = 'Study Abroad'
            elif old_lead_type == 'forex_trade':
                leads = ForexTrade.objects.exclude(assigned_to=user).exclude(
                    is_replaced=True, replaced_for_user=user
                )
                lead_type_display = 'Forex Trade'
            
            for lead in leads:
                available_leads.append({
                    'id': lead.id,
                    'type': old_lead_type,
                    'type_display': lead_type_display,
                    'full_name': lead.full_name or 'N/A',
                    'phone_number': lead.phone_number or 'N/A',
                    'email': lead.email or 'N/A',
                    'status': lead.status,
                    'created_at': lead.created_at,
                    'currently_assigned_to': lead.assigned_to.username if lead.assigned_to else 'Unassigned',
                    'is_replaced': lead.is_replaced  # For debugging
                })
        
        print(f"🔍 DEBUG: Total filtered available leads = {len(available_leads)}")
        
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
            'old_lead': old_lead,
            'old_lead_type': old_lead_type,
            'available_leads': available_leads,
            'show_assignment_info': True
        }
        
        if not available_leads:
            messages.info(request, f"No available {lead_type_display} leads for replacement.")
        
        return render(request, 'central_admin/lead_replacement_select_new_lead.html', context)
        
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('central_admin:lead_replacement_start')


        
# @login_required
# @user_passes_test(is_central_admin)
# def lead_replacement_confirm(request):
#     """
#     Step 4: Confirm and process lead replacement
#     """
#     if request.method == 'POST':
#         try:
#             user_id = request.POST.get('user_id')
#             old_lead_id = request.POST.get('old_lead_id')
#             old_lead_type = request.POST.get('old_lead_type')
#             new_lead_id = request.POST.get('new_lead_id')
#             new_lead_type = request.POST.get('new_lead_type')
#             reason = request.POST.get('reason', '')
            
#             user = User.objects.get(id=user_id, is_active=True)
            
#             # Get lead objects
#             old_lead = None
#             new_lead = None
            
#             # Get old lead
#             if old_lead_type == 'real_estate':
#                 old_lead = RealEstateLead.objects.get(id=old_lead_id)
#             elif old_lead_type == 'online_mba':
#                 old_lead = OnlineMBA.objects.get(id=old_lead_id)
#             elif old_lead_type == 'study_abroad':
#                 old_lead = StudyAbroad.objects.get(id=old_lead_id)
#             elif old_lead_type == 'forex_trade':
#                 old_lead = ForexTrade.objects.get(id=old_lead_id)
            
#             # Get new lead
#             if new_lead_type == 'real_estate':
#                 new_lead = RealEstateLead.objects.get(id=new_lead_id)
#             elif new_lead_type == 'online_mba':
#                 new_lead = OnlineMBA.objects.get(id=new_lead_id)
#             elif new_lead_type == 'study_abroad':
#                 new_lead = StudyAbroad.objects.get(id=new_lead_id)
#             elif new_lead_type == 'forex_trade':
#                 new_lead = ForexTrade.objects.get(id=new_lead_id)
            
#             # PERFORM REPLACEMENT
#             # 1. Old lead ko unassign karo
#             old_lead.assigned_to = None
#             old_lead.status = 'lead_replacement'
#             old_lead.save()
            
#             # 2. New lead ko assign karo
#             new_lead.assigned_to = user
#             new_lead.status = 'new'
#             new_lead.save()
            
#             # 3. LeadReplacementHistory create karo
#             old_content_type = ContentType.objects.get_for_model(type(old_lead))
#             new_content_type = ContentType.objects.get_for_model(type(new_lead))
            
#             LeadReplacementHistory.objects.create(
#                 old_lead_content_type=old_content_type,
#                 old_lead_object_id=old_lead.id,
#                 new_lead_content_type=new_content_type,
#                 new_lead_object_id=new_lead.id,
#                 subscriber=user,
#                 replaced_by_admin=request.user,
#                 reason=reason
#             )
            
#             # 4. Assignment logs create karo
#             # Old lead unassignment log
#             LeadAssignmentLog.objects.create(
#                 lead_content_type=old_content_type,
#                 lead_object_id=old_lead.id,
#                 assigned_to=None,  # Unassigned
#                 assigned_by=request.user,
#                 status_at_assignment='lead_replacement',
#                 notes=f"Unassigned during replacement. Reason: {reason}"
#             )
            
#             # New lead assignment log
#             LeadAssignmentLog.objects.create(
#                 lead_content_type=new_content_type,
#                 lead_object_id=new_lead.id,
#                 assigned_to=user,
#                 assigned_by=request.user,
#                 status_at_assignment='new',
#                 notes=f"Assigned as replacement. Reason: {reason}"
#             )
            
#             messages.success(
#                 request, 
#                 f"Lead replaced successfully! {old_lead.full_name or 'Old lead'} replaced with {new_lead.full_name or 'New lead'} for {user.username}"
#             )
            
#             return redirect('central_admin:lead_replacement_start')
            
#         except Exception as e:
#             messages.error(request, f"Error during lead replacement: {str(e)}")
#             return redirect('central_admin:lead_replacement_start')
    
#     return redirect('central_admin:lead_replacement_start')




@login_required
@user_passes_test(is_central_admin)
def lead_replacement_confirm(request):
    """
    Step 4: Confirm and process lead replacement
    """
    if request.method == 'POST':
        try:
            user_id = request.POST.get('user_id')
            old_lead_id = request.POST.get('old_lead_id')
            old_lead_type = request.POST.get('old_lead_type')
            new_lead_id = request.POST.get('new_lead_id')
            new_lead_type = request.POST.get('new_lead_type')
            reason = request.POST.get('reason', '')
            
            user = User.objects.get(id=user_id, is_active=True)
            
            # Get lead objects
            old_lead = None
            new_lead = None
            
            # Get old lead
            if old_lead_type == 'real_estate':
                old_lead = RealEstateLead.objects.get(id=old_lead_id)
            elif old_lead_type == 'online_mba':
                old_lead = OnlineMBA.objects.get(id=old_lead_id)
            elif old_lead_type == 'study_abroad':
                old_lead = StudyAbroad.objects.get(id=old_lead_id)
            elif old_lead_type == 'forex_trade':
                old_lead = ForexTrade.objects.get(id=old_lead_id)
            
            # Get new lead
            if new_lead_type == 'real_estate':
                new_lead = RealEstateLead.objects.get(id=new_lead_id)
            elif new_lead_type == 'online_mba':
                new_lead = OnlineMBA.objects.get(id=new_lead_id)
            elif new_lead_type == 'study_abroad':
                new_lead = StudyAbroad.objects.get(id=new_lead_id)
            elif new_lead_type == 'forex_trade':
                new_lead = ForexTrade.objects.get(id=new_lead_id)
            
            print(f"🔍 DEBUG: BEFORE REPLACEMENT")
            print(f"Old Lead: {old_lead_type} ID {old_lead_id}, Assigned To: {old_lead.assigned_to}")
            print(f"New Lead: {new_lead_type} ID {new_lead_id}, Assigned To: {new_lead.assigned_to}")
            
            # **NEW LOGIC: Use is_replaced field**
            
            # 1. Old lead ko mark as replaced for this specific user
            old_lead.is_replaced = True
            old_lead.replaced_at = timezone.now()
            old_lead.replaced_for_user = user
            old_lead.status = 'lead_replacement'
            
            # Remark/note update
            replacement_note = f"Replaced for {user.username} on {timezone.now().strftime('%Y-%m-%d %H:%M')}. Reason: {reason}"
            
            if old_lead_type in ['real_estate', 'online_mba', 'study_abroad']:
                old_lead.remark = replacement_note
            elif old_lead_type == 'forex_trade':
                old_lead.note = replacement_note
            
            old_lead.save()
            
            # 2. New lead ko assign karo
            new_lead.assigned_to = user
            new_lead.status = 'new'
            
            # New lead ka remark/note update
            assignment_note = f"Assigned as replacement lead on {timezone.now().strftime('%Y-%m-%d %H:%M')}"
            
            if new_lead_type in ['real_estate', 'online_mba', 'study_abroad']:
                new_lead.remark = assignment_note
            elif new_lead_type == 'forex_trade':
                new_lead.note = assignment_note
            
            new_lead.save()
            
            print(f"🔍 DEBUG: AFTER REPLACEMENT")
            print(f"Old Lead - Is Replaced: {old_lead.is_replaced}, For User: {old_lead.replaced_for_user}")
            print(f"New Lead - Assigned To: {new_lead.assigned_to}")
            
            # 3. LeadReplacementHistory create karo
            old_content_type = ContentType.objects.get_for_model(type(old_lead))
            new_content_type = ContentType.objects.get_for_model(type(new_lead))
            
            LeadReplacementHistory.objects.create(
                old_lead_content_type=old_content_type,
                old_lead_object_id=old_lead.id,
                new_lead_content_type=new_content_type,
                new_lead_object_id=new_lead.id,
                subscriber=user,
                replaced_by_admin=request.user,
                reason=reason
            )
            
            # 4. Assignment logs create karo
            # Old lead replacement log
            LeadAssignmentLog.objects.create(
                lead_content_type=old_content_type,
                lead_object_id=old_lead.id,
                assigned_to=old_lead.assigned_to,  # Keep original assignment
                assigned_by=request.user,
                status_at_assignment='lead_replacement',
                notes=f"Marked as replaced for {user.username}. Reason: {reason}"
            )
            
            # New lead assignment log
            LeadAssignmentLog.objects.create(
                lead_content_type=new_content_type,
                lead_object_id=new_lead.id,
                assigned_to=user,
                assigned_by=request.user,
                status_at_assignment='new',
                notes=f"Assigned as replacement to {user.username}. Reason: {reason}"
            )
            
            messages.success(
                request, 
                f"Lead replaced successfully! {old_lead.full_name or 'Old lead'} replaced with {new_lead.full_name or 'New lead'} for {user.username}"
            )
            
            return redirect('central_admin:lead_replacement_start')
            
        except Exception as e:
            messages.error(request, f"Error during lead replacement: {str(e)}")
            import traceback
            print(f"❌ ERROR: {traceback.format_exc()}")
            return redirect('central_admin:lead_replacement_start')
    
    return redirect('central_admin:lead_replacement_start')



# @login_required
# @user_passes_test(is_central_admin)
# def replacement_history(request, user_id):
#     """
#     User-wise replacement history
#     """
#     try:
#         user = User.objects.get(id=user_id, is_active=True)
        
#         # Get replacement history for this user
#         replacement_history = LeadReplacementHistory.objects.filter(
#             subscriber=user
#         ).order_by('-replaced_at')
        
#         # Get user's current assigned leads count
#         current_leads_count = (
#             RealEstateLead.objects.filter(assigned_to=user).count() +
#             OnlineMBA.objects.filter(assigned_to=user).count() +
#             StudyAbroad.objects.filter(assigned_to=user).count() +
#             ForexTrade.objects.filter(assigned_to=user).count()
#         )
        
#         user_name = request.session.get('user_name')
#         user_email = request.session.get('user_email')
#         user_role = request.session.get('user_role')
#         short_name = user_name[:2].upper() if user_name else ""

#         context = {
#             'name': user_name,
#             'email': user_email,
#             'role': user_role,
#             'short_name': short_name,
#             'user': user,
#             'replacement_history': replacement_history,
#             'current_leads_count': current_leads_count,
#         }
        
#         return render(request, 'central_admin/replacement_history.html', context)
        
#     except User.DoesNotExist:
#         messages.error(request, "User not found.")
#         return redirect('central_admin:lead_replacement_start')





@login_required
@user_passes_test(is_central_admin)
def replacement_history(request, user_id):
    """
    User-wise replacement history
    """
    try:
        user = User.objects.get(id=user_id, is_active=True)
        
        # Get replacement history for this user
        replacement_history = LeadReplacementHistory.objects.filter(
            subscriber=user
        ).order_by('-replaced_at')
        
        # **UPDATED: Get user's current assigned leads count (EXCLUDE REPLACED LEADS)**
        current_leads_count = (
            RealEstateLead.objects.filter(assigned_to=user).exclude(
                is_replaced=True, replaced_for_user=user
            ).count() +
            OnlineMBA.objects.filter(assigned_to=user).exclude(
                is_replaced=True, replaced_for_user=user
            ).count() +
            StudyAbroad.objects.filter(assigned_to=user).exclude(
                is_replaced=True, replaced_for_user=user
            ).count() +
            ForexTrade.objects.filter(assigned_to=user).exclude(
                is_replaced=True, replaced_for_user=user
            ).count()
        )
        
        # **NEW: Get replaced leads count for this user**
        replaced_leads_count = (
            RealEstateLead.objects.filter(
                is_replaced=True, replaced_for_user=user
            ).count() +
            OnlineMBA.objects.filter(
                is_replaced=True, replaced_for_user=user
            ).count() +
            StudyAbroad.objects.filter(
                is_replaced=True, replaced_for_user=user
            ).count() +
            ForexTrade.objects.filter(
                is_replaced=True, replaced_for_user=user
            ).count()
        )
        
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
            'replacement_history': replacement_history,
            'current_leads_count': current_leads_count,
            'replaced_leads_count': replaced_leads_count,  # New field for template
        }
        
        return render(request, 'central_admin/replacement_history.html', context)
        
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('central_admin:lead_replacement_start')