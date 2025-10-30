from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from leads.models import RealEstateLead, OnlineMBA, StudyAbroad, BaseLead, ForexTrade

@login_required
def dashboard(request):
    user = request.user

    # Assigned leads
    real_estate_leads = RealEstateLead.objects.filter(assigned_to=user).order_by('-created_at')
    online_mba_leads = OnlineMBA.objects.filter(assigned_to=user).order_by('-created_at')
    study_abroad_leads = StudyAbroad.objects.filter(assigned_to=user).order_by('-created_at')
    forex_trade = ForexTrade.objects.filter(assigned_to=user).order_by('-created_at')
    
    

    all_leads = list(real_estate_leads) + list(online_mba_leads) + list(study_abroad_leads) + list(forex_trade)
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
#     study_abroad_leads = StudyAbroad.objects.filter(assigned_to=user)
#     Forex_trade = ForexTrade.objects.filter(assigned_to=user)
#     # Combine all in one list (category tagged)
#     all_leads = []

#     for lead in real_estate_leads:
#         all_leads.append({
#             'id': f'realestate_{lead.id}',
#             'original_id': lead.id,
#             'model_type': 'realestate',
#             'category': lead.sub_industry or 'Real Estate',
#             'name': lead.full_name,
#             'phone': lead.phone_number,
#             'email': lead.email,
#             'extra': f"{lead.location or '-'}/{lead.budget or '-'}/{lead.visit_day or '-'}",
#             'status': lead.status,
#             'created_at': lead.created_at,
#             'remark': lead.remark or '',  # REMARK FIELD ADD KIYA
#         })

#     for lead in mba_leads:
#         all_leads.append({
#             'id': f'mba_{lead.id}',
#             'original_id': lead.id,
#             'model_type': 'mba',
#             'category': 'Online MBA',
#             'name': lead.full_name,
#             'phone': lead.phone_number,
#             'email': lead.email,
#             'extra': f"{lead.course or '-'}/{lead.university or '-'}",
#             'status': lead.status,
#             'created_at': lead.created_at,
#             'remark': lead.remark or '',  # REMARK FIELD ADD KIYA
#         })

#     for lead in study_abroad_leads:
#         all_leads.append({
#             'id': f'abroad_{lead.id}',
#             'original_id': lead.id,
#             'model_type': 'abroad',
#             'category': 'Study Abroad',
#             'name': lead.full_name,
#             'phone': lead.phone_number,
#             'email': lead.email,
#             'extra': f"{lead.country or '-'}/{lead.university or '-'}",
#             'status': lead.status,
#             'created_at': lead.created_at,
#             'remark': lead.remark or '',  # REMARK FIELD ADD KIYA
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
#         lead_id = data.get("lead_id")
#         new_status = data.get("status")
#         remark = data.get("remark", "").strip()  # REMARK FIELD ADD KIYA

#         if not lead_id:
#             return JsonResponse({"success": False, "error": "Missing lead ID."})

#         # Validate status (agar status update ho raha hai)
#         if new_status:
#             valid_statuses = [choice[0] for choice in BaseLead.STATUS_CHOICES]
#             if new_status not in valid_statuses:
#                 return JsonResponse({"success": False, "error": "Invalid status value."})

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

#         # Update status aur remark
#         if new_status:
#             lead_obj.status = new_status
#         if remark is not None:  # Remark update karo, chahe empty ho
#             lead_obj.remark = remark
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
    forex_trade_leads = ForexTrade.objects.filter(assigned_to=user)  # NEW LINE

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

    # NEW: Forex Trade Leads
    for lead in forex_trade_leads:
        all_leads.append({
            'id': f'forex_{lead.id}',
            'original_id': lead.id,
            'model_type': 'forex',
            'category': 'Forex Trade',
            'name': lead.full_name,
            'phone': lead.phone_number,
            'email': lead.email,
            'extra': f"{lead.experience or '-'}/{lead.broker or '-'}/{lead.initial_investment or '-'}",
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
        elif lead_id.startswith('forex_'):  # NEW: Forex Trade
            model = ForexTrade
            original_id = lead_id.replace('forex_', '')
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
        if remark is not None:  
            lead_obj.remark = remark
        lead_obj.save()

        return JsonResponse({"success": True})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON."})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})