from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from leads.models import RealEstateLead, OnlineMBA, StudyAbroad, BaseLead

@login_required
def dashboard(request):
    user = request.user

    # Assigned leads
    real_estate_leads = RealEstateLead.objects.filter(assigned_to=user).order_by('-created_at')
    online_mba_leads = OnlineMBA.objects.filter(assigned_to=user).order_by('-created_at')
    study_abroad_leads = StudyAbroad.objects.filter(assigned_to=user).order_by('-created_at')

    all_leads = list(real_estate_leads) + list(online_mba_leads) + list(study_abroad_leads)
    total_assigned_leads = len(all_leads)

    # Converted leads
    converted_leads = sum(1 for lead in all_leads if lead.status == 'converted')

    # Pending leads = available credits
    available_credits = user.available_credits
    pending_leads = max(total_assigned_leads - converted_leads, 0)

    context = {
        'user': user,
        'total_leads': total_assigned_leads,
        'converted_leads': converted_leads,
        'pending_leads': pending_leads,
        'available_credits': available_credits,
        'user_industry': getattr(user, 'industry', None),
        'user_sub_industry': getattr(user, 'sub_industry', None),
    }

    return render(request, 'subscribers/dashboard.html', context)


@login_required
def support_tickets(request):
    return render(request,"subscribers/tickets.html")



# @login_required
# def my_leads(request):
#     user = request.user

#     # Collect all leads assigned to this user
#     real_estate_leads = RealEstateLead.objects.filter(assigned_to=user)
#     mba_leads = OnlineMBA.objects.filter(assigned_to=user)
#     study_abroad_leads = StudyAbroad.objects.filter(assigned_to=user)

#     # Combine all in one list (category tagged)
#     all_leads = []

#     for lead in real_estate_leads:
#         all_leads.append({
#             'id': f'realestate_{lead.id}',  # UNIQUE ID ADD KIYA
#             'original_id': lead.id,         # ACTUAL DATABASE ID
#             'model_type': 'realestate',     # MODEL TYPE ADD KIYA
#             'category': lead.sub_industry or 'Real Estate',
#             'name': lead.full_name,
#             'phone': lead.phone_number,
#             'email': lead.email,
#             'extra': f"{lead.location or '-'}/{lead.budget or '-'}",
#             'status': lead.status,
#             'created_at': lead.created_at,
#         })

#     for lead in mba_leads:
#         all_leads.append({
#             'id': f'mba_{lead.id}',        # UNIQUE ID ADD KIYA
#             'original_id': lead.id,        # ACTUAL DATABASE ID
#             'model_type': 'mba',           # MODEL TYPE ADD KIYA
#             'category': 'Online MBA',
#             'name': lead.full_name,
#             'phone': lead.phone_number,
#             'email': lead.email,
#             'extra': f"{lead.course or '-'}/{lead.university or '-'}",
#             'status': lead.status,
#             'created_at': lead.created_at,
#         })

#     for lead in study_abroad_leads:
#         all_leads.append({
#             'id': f'abroad_{lead.id}',     # UNIQUE ID ADD KIYA
#             'original_id': lead.id,        # ACTUAL DATABASE ID
#             'model_type': 'abroad',        # MODEL TYPE ADD KIYA
#             'category': 'Study Abroad',
#             'name': lead.full_name,
#             'phone': lead.phone_number,
#             'email': lead.email,
#             'extra': f"{lead.country or '-'}/{lead.university or '-'}",
#             'status': lead.status,
#             'created_at': lead.created_at,
#         })

#     # Sort by latest first
#     all_leads.sort(key=lambda x: x['created_at'], reverse=True)

#     return render(request, 'subscribers/my_leads.html', {'leads': all_leads})



# @login_required
# def update_lead_status(request):
#     if request.method != "POST":
#         return JsonResponse({"success": False, "error": "Invalid request method."})
    
#     try:
#         data = json.loads(request.body)
#         lead_id = data.get("lead_id")  # Yeh wahi ID hai jo template mein hai (realestate_1, mba_2, etc.)
#         new_status = data.get("status")

#         if not lead_id or not new_status:
#             return JsonResponse({"success": False, "error": "Missing required fields."})

#         # Validate status
#         valid_statuses = [choice[0] for choice in BaseLead.STATUS_CHOICES]
#         if new_status not in valid_statuses:
#             return JsonResponse({"success": False, "error": "Invalid status value."})

#         # Model aur original ID identify karo
#         if lead_id.startswith('realestate_'):
#             model = RealEstateLead
#             original_id = lead_id.replace('realestate_', '')
#         elif lead_id.startswith('mba_'):
#             model = OnlineMBA
#             original_id = lead_id.replace('mba_', '')
#         elif lead_id.startswith('abroad_'):
#             model = StudyAbroad
#             original_id = lead_id.replace('abroad_', '')
#         else:
#             return JsonResponse({"success": False, "error": "Invalid lead ID format."})

#         # Database se lead fetch karo
#         try:
#             lead_obj = model.objects.get(id=original_id, assigned_to=request.user)
#         except model.DoesNotExist:
#             return JsonResponse({"success": False, "error": "Lead not found or not assigned to you."})

#         # Update status
#         lead_obj.status = new_status
#         lead_obj.save()

#         return JsonResponse({"success": True})

#     except json.JSONDecodeError:
#         return JsonResponse({"success": False, "error": "Invalid JSON."})
#     except Exception as e:
#         return JsonResponse({"success": False, "error": str(e)})

@login_required
def my_leads(request):
    user = request.user

    # Collect all leads assigned to this user
    real_estate_leads = RealEstateLead.objects.filter(assigned_to=user)
    mba_leads = OnlineMBA.objects.filter(assigned_to=user)
    study_abroad_leads = StudyAbroad.objects.filter(assigned_to=user)

    # Combine all in one list (category tagged)
    all_leads = []

    for lead in real_estate_leads:
        all_leads.append({
            'id': f'realestate_{lead.id}',
            'original_id': lead.id,
            'model_type': 'realestate',
            'category': lead.sub_industry or 'Real Estate',
            'name': lead.full_name,
            'phone': lead.phone_number,
            'email': lead.email,
            'extra': f"{lead.location or '-'}/{lead.budget or '-'}/{lead.visit_day or '-'}",
            'status': lead.status,
            'created_at': lead.created_at,
            'remark': lead.remark or '',  # REMARK FIELD ADD KIYA
        })

    for lead in mba_leads:
        all_leads.append({
            'id': f'mba_{lead.id}',
            'original_id': lead.id,
            'model_type': 'mba',
            'category': 'Online MBA',
            'name': lead.full_name,
            'phone': lead.phone_number,
            'email': lead.email,
            'extra': f"{lead.course or '-'}/{lead.university or '-'}",
            'status': lead.status,
            'created_at': lead.created_at,
            'remark': lead.remark or '',  # REMARK FIELD ADD KIYA
        })

    for lead in study_abroad_leads:
        all_leads.append({
            'id': f'abroad_{lead.id}',
            'original_id': lead.id,
            'model_type': 'abroad',
            'category': 'Study Abroad',
            'name': lead.full_name,
            'phone': lead.phone_number,
            'email': lead.email,
            'extra': f"{lead.country or '-'}/{lead.university or '-'}",
            'status': lead.status,
            'created_at': lead.created_at,
            'remark': lead.remark or '',  # REMARK FIELD ADD KIYA
        })

    # Sort by latest first
    all_leads.sort(key=lambda x: x['created_at'], reverse=True)

    return render(request, 'subscribers/my_leads.html', {'leads': all_leads})

@login_required
def update_lead_status(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method."})
    
    try:
        data = json.loads(request.body)
        lead_id = data.get("lead_id")
        new_status = data.get("status")
        remark = data.get("remark", "").strip()  # REMARK FIELD ADD KIYA

        if not lead_id:
            return JsonResponse({"success": False, "error": "Missing lead ID."})

        # Validate status (agar status update ho raha hai)
        if new_status:
            valid_statuses = [choice[0] for choice in BaseLead.STATUS_CHOICES]
            if new_status not in valid_statuses:
                return JsonResponse({"success": False, "error": "Invalid status value."})

        # Model aur original ID identify karo
        if lead_id.startswith('realestate_'):
            model = RealEstateLead
            original_id = lead_id.replace('realestate_', '')
        elif lead_id.startswith('mba_'):
            model = OnlineMBA
            original_id = lead_id.replace('mba_', '')
        elif lead_id.startswith('abroad_'):
            model = StudyAbroad
            original_id = lead_id.replace('abroad_', '')
        else:
            return JsonResponse({"success": False, "error": "Invalid lead ID format."})

        # Database se lead fetch karo
        try:
            lead_obj = model.objects.get(id=original_id, assigned_to=request.user)
        except model.DoesNotExist:
            return JsonResponse({"success": False, "error": "Lead not found or not assigned to you."})

        # Update status aur remark
        if new_status:
            lead_obj.status = new_status
        if remark is not None:  # Remark update karo, chahe empty ho
            lead_obj.remark = remark
        lead_obj.save()

        return JsonResponse({"success": True})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON."})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})








# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from leads.models import RealEstateLead, OnlineMBA, StudyAbroad

# @login_required
# def dashboard(request):
#     # Session se user details get karo
#     user_id = request.session.get('user_id')
#     user_email = request.session.get('user_email')
#     user_name = request.session.get('user_name')
#     user_role = request.session.get('user_role')
    
#     # Agar session mein details nahi hain, toh current user se lelo
#     if not user_id:
#         user_id = request.user.id
#         user_email = request.user.email
#         user_name = request.user.first_name or request.user.username
#         user_role = request.user.role
    
#     # Sirf current logged-in user ko assigned leads
#     real_estate_leads = RealEstateLead.objects.filter(assigned_to=request.user).order_by('-created_at')
#     online_mba_leads = OnlineMBA.objects.filter(assigned_to=request.user).order_by('-created_at')
#     study_abroad_leads = StudyAbroad.objects.filter(assigned_to=request.user).order_by('-created_at')
    
#     # Statistics calculate karo
#     all_leads = list(real_estate_leads) + list(online_mba_leads) + list(study_abroad_leads)
#     total_leads = len(all_leads)
#     converted_leads = sum(1 for lead in all_leads if lead.status == 'converted')
#     pending_leads = sum(1 for lead in all_leads if lead.status == 'new')
    
#     context = {
#         'user': request.user,
#         'real_estate_leads': real_estate_leads,
#         'online_mba_leads': online_mba_leads,
#         'study_abroad_leads': study_abroad_leads,
#         'total_leads': total_leads,
#         'converted_leads': converted_leads,
#         'pending_leads': pending_leads,
#         'user_industry': request.user.industry,
#         'user_sub_industry': request.user.sub_industry,
#         # Session data for template
#         'session_user_name': user_name,
#         'session_user_email': user_email,
#         'session_user_role': user_role,
#     }
    
#     return render(request, 'subscribers/dashboard.html', context)

# def my_leads(request):
#     user = request.user

#     # Collect all leads assigned to this user
#     real_estate_leads = RealEstateLead.objects.filter(assigned_to=user)
#     mba_leads = OnlineMBA.objects.filter(assigned_to=user)
#     study_abroad_leads = StudyAbroad.objects.filter(assigned_to=user)

#     # Combine all in one list (category tagged)
#     all_leads = []

#     for lead in real_estate_leads:
#         all_leads.append({
#             'category': lead.sub_industry or 'Real Estate',
#             'name': lead.full_name,
#             'phone': lead.phone_number,
#             'email': lead.email,
#             'extra': f"{lead.location or '-'} / {lead.budget or '-'}",
#             'status': lead.status,
#             'created_at': lead.created_at,
#         })

#     for lead in mba_leads:
#         all_leads.append({
#             'category': 'Online MBA',
#             'name': lead.full_name,
#             'phone': lead.phone_number,
#             'email': lead.email,
#             'extra': f"{lead.course or '-'} / {lead.university or '-'}",
#             'status': lead.status,
#             'created_at': lead.created_at,
#         })

#     for lead in study_abroad_leads:
#         all_leads.append({
#             'category': 'Study Abroad',
#             'name': lead.full_name,
#             'phone': lead.phone_number,
#             'email': lead.email,
#             'extra': f"{lead.country or '-'} / {lead.university or '-'}",
#             'status': lead.status,
#             'created_at': lead.created_at,
#         })

#     # Sort by latest first
#     all_leads.sort(key=lambda x: x['created_at'], reverse=True)

#     return render(request, 'subscribers/my_leads.html', {'leads': all_leads})



# def support_tickets(request):
#     return render(request,"subscribers/tickets.html")

# import json
# from django.http import JsonResponse


# def update_lead_status(request):
#     if request.method != "POST":
#         return JsonResponse({"success": False, "error": "Invalid request method."})
    
#     try:
#         data = json.loads(request.body)
#         lead_id = data.get("lead_id")
#         category = data.get("category")
#         new_status = data.get("status")

#         if not lead_id or not category or not new_status:
#             return JsonResponse({"success": False, "error": "Missing required fields."})

#         # Validate status
#         valid_statuses = [choice[0] for choice in BaseLead.STATUS_CHOICES]
#         if new_status not in valid_statuses:
#             return JsonResponse({"success": False, "error": "Invalid status value."})

#         # Normalize category
#         category_norm = category.strip().lower()
#         lead_obj = None

#         # Determine model based on category
#         if category_norm in ["buyers leads", "tenant leads"]:
#             lead_obj = RealEstateLead.objects.filter(id=lead_id, assigned_to=request.user).first()
#         elif category_norm == "online mba":
#             lead_obj = OnlineMBA.objects.filter(id=lead_id, assigned_to=request.user).first()
#         elif category_norm == "study abroad":
#             lead_obj = StudyAbroad.objects.filter(id=lead_id, assigned_to=request.user).first()
#         else:
#             return JsonResponse({"success": False, "error": "Invalid category."})

#         if not lead_obj:
#             return JsonResponse({"success": False, "error": "Lead not found or not assigned to you."})

#         # Update status safely
#         lead_obj.status = new_status
#         lead_obj.save()

#         return JsonResponse({"success": True})

#     except json.JSONDecodeError:
#         return JsonResponse({"success": False, "error": "Invalid JSON."})
#     except Exception as e:
#         return JsonResponse({"success": False, "error": str(e)})
