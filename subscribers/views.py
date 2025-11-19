from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from leads.models import RealEstateLead, OnlineMBA, StudyAbroad, BaseLead, ForexTrade, LeadAssignmentLog, LeadStatusHistory, LeadRemarkHistory
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

# @login_required
# def dashboard(request):
#     user = request.user

#     # ------------------------------------
#     # SAME COUNTING LOGIC AS my_leads PAGE
#     # ------------------------------------

#     # Direct assigned leads
#     direct_real = RealEstateLead.objects.filter(assigned_to=user)
#     direct_mba = OnlineMBA.objects.filter(assigned_to=user)
#     direct_abroad = StudyAbroad.objects.filter(assigned_to=user)
#     direct_forex = ForexTrade.objects.filter(assigned_to=user)

#     # Set to avoid duplicate entries (same logic as added_lead_ids)
#     added = set()
#     total_leads_count = 0

#     # Helper to add unique leads
#     def add_lead(lead, prefix):
#         key = f"{prefix}_{lead.id}"
#         if key not in added:
#             added.add(key)
#             return 1
#         return 0

#     # Direct assigned leads counting
#     for l in direct_real:
#         total_leads_count += add_lead(l, "realestate")

#     for l in direct_mba:
#         total_leads_count += add_lead(l, "mba")

#     for l in direct_abroad:
#         total_leads_count += add_lead(l, "abroad")

#     for l in direct_forex:
#         total_leads_count += add_lead(l, "forex")

#     # Assignment history leads
#     history = LeadAssignmentLog.objects.filter(assigned_to=user).select_related("assigned_to")

#     for h in history:
#         lead = h.lead
#         if not lead:
#             continue

#         if isinstance(lead, RealEstateLead):
#             total_leads_count += add_lead(lead, "realestate")

#         elif isinstance(lead, OnlineMBA):
#             total_leads_count += add_lead(lead, "mba")

#         elif isinstance(lead, StudyAbroad):
#             total_leads_count += add_lead(lead, "abroad")

#         elif isinstance(lead, ForexTrade):
#             total_leads_count += add_lead(lead, "forex")

#     # Final result
#     total_assigned_leads = total_leads_count

#     # ------------------------------------
#     # Your OLD logic (NOT CHANGED AT ALL)
#     # ------------------------------------

#     # Lead status history stats (converted & replacement)
#     from django.contrib.contenttypes.models import ContentType
#     real_estate_ct = ContentType.objects.get_for_model(RealEstateLead)
#     online_mba_ct = ContentType.objects.get_for_model(OnlineMBA)
#     study_abroad_ct = ContentType.objects.get_for_model(StudyAbroad)
#     forex_trade_ct = ContentType.objects.get_for_model(ForexTrade)

#     # Get lead IDs for status lookup
#     lead_id_map = {h.lead.id: True for h in history if h.lead}

#     status_history = LeadStatusHistory.objects.filter(
#         lead_content_type__in=[real_estate_ct, online_mba_ct, study_abroad_ct, forex_trade_ct],
#         lead_object_id__in=lead_id_map.keys(),
#         changed_by=user
#     )

#     converted_leads = 0
#     replacement_leads = 0

#     conv_set = set()
#     rep_set = set()

#     for s in status_history:
#         if s.new_status == 'converted':
#             conv_set.add(s.lead_object_id)
#         elif s.new_status == 'lead_replacement':
#             rep_set.add(s.lead_object_id)

#     converted_leads = len(conv_set)
#     lead_replacement = len(rep_set)

#     # Credits
#     available_credits = user.available_credits

#     # Tickets
#     try:
#         from .models import Ticket
#         tickets = Ticket.objects.filter(user=user)
#         ticket_stats = {
#             'total': tickets.count(),
#             'open': tickets.filter(status='open').count(),
#             'in_progress': tickets.filter(status='in_progress').count(),
#             'resolved': tickets.filter(status='resolved').count(),
#             'closed': tickets.filter(status='closed').count(),
#         }
#     except:
#         ticket_stats = {
#             'total': 0,
#             'open': 0,
#             'in_progress': 0,
#             'resolved': 0,
#             'closed': 0,
#         }

#     context = {
#         'user': user,
#         'total_leads': total_assigned_leads,   # FIXED ✔
#         'converted_leads': converted_leads,
#         'lead_replacement': lead_replacement,
#         'available_credits': available_credits,
#         'user_industry': getattr(user, 'industry', None),
#         'user_sub_industry': getattr(user, 'sub_industry', None),
#         'ticket_stats': ticket_stats,
#     }

#     return render(request, 'subscribers/dashboard.html', context)



@login_required
def dashboard(request):
    user = request.user

    # ------------------------------------
    # SAME COUNTING LOGIC AS my_leads PAGE
    # ------------------------------------

    # Direct assigned leads
    direct_real = RealEstateLead.objects.filter(assigned_to=user)
    direct_mba = OnlineMBA.objects.filter(assigned_to=user)
    direct_abroad = StudyAbroad.objects.filter(assigned_to=user)
    direct_forex = ForexTrade.objects.filter(assigned_to=user)

    # Set to avoid duplicate entries (same logic as added_lead_ids)
    added = set()
    total_leads_count = 0

    # Helper to add unique leads
    def add_lead(lead, prefix):
        key = f"{prefix}_{lead.id}"
        if key not in added:
            added.add(key)
            return 1
        return 0

    # Direct assigned leads counting
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

    # Final result
    total_assigned_leads = total_leads_count

    # ------------------------------------
    # Lead status history stats (converted & replacement)
    # ------------------------------------
    from django.contrib.contenttypes.models import ContentType
    real_estate_ct = ContentType.objects.get_for_model(RealEstateLead)
    online_mba_ct = ContentType.objects.get_for_model(OnlineMBA)
    study_abroad_ct = ContentType.objects.get_for_model(StudyAbroad)
    forex_trade_ct = ContentType.objects.get_for_model(ForexTrade)

    # Get lead IDs for status lookup
    lead_id_map = {h.lead.id: True for h in history if h.lead}

    status_history = LeadStatusHistory.objects.filter(
        lead_content_type__in=[real_estate_ct, online_mba_ct, study_abroad_ct, forex_trade_ct],
        lead_object_id__in=lead_id_map.keys(),
        changed_by=user
    )

    converted_leads = 0
    replacement_leads = 0

    conv_set = set()
    rep_set = set()

    for s in status_history:
        if s.new_status == 'converted':
            conv_set.add(s.lead_object_id)
        elif s.new_status == 'lead_replacement':
            rep_set.add(s.lead_object_id)

    converted_leads = len(conv_set)
    lead_replacement = len(rep_set)

    # ------------------------------------
    # NEW: Lead Replacement TICKETS Count
    # ------------------------------------
    try:
        from .models import Ticket
        # Count tickets with category 'lead' (lead replacement tickets)
        lead_replacement_tickets_count = Ticket.objects.filter(
            user=user, 
            category='lead'
        ).count()
    except:
        lead_replacement_tickets_count = 0

    # Credits
    available_credits = user.available_credits

    # Tickets - COMPLETE stats (including lead replacement in total)
    try:
        from .models import Ticket
        tickets = Ticket.objects.filter(user=user)
        ticket_stats = {
            'total': tickets.count(),
            'open': tickets.filter(status='open').count(),
            'in_progress': tickets.filter(status='in_progress').count(),
            'resolved': tickets.filter(status='resolved').count(),
            'closed': tickets.filter(status='closed').count(),
            'lead_replacement': lead_replacement_tickets_count,  # NEW: Lead replacement tickets count
        }
    except:
        ticket_stats = {
            'total': 0,
            'open': 0,
            'in_progress': 0,
            'resolved': 0,
            'closed': 0,
            'lead_replacement': 0,
        }

    context = {
        'user': user,
        'total_leads': total_assigned_leads,   # FIXED ✔
        'converted_leads': converted_leads,
        'lead_replacement': lead_replacement,  # Lead status wala count (existing)
        'available_credits': available_credits,
        'user_industry': getattr(user, 'industry', None),
        'user_sub_industry': getattr(user, 'sub_industry', None),
        'ticket_stats': ticket_stats,
        'lead_replacement_tickets_count': lead_replacement_tickets_count,  # NEW: For display
    }

    return render(request, 'subscribers/dashboard.html', context)


# @login_required
# def dashboard(request):
#     user = request.user

#     # ✅ Get unique leads count from LeadAssignmentLog (across all lead types)
#     from django.contrib.contenttypes.models import ContentType
    
#     # Get content types for all lead models
#     real_estate_ct = ContentType.objects.get_for_model(RealEstateLead)
#     online_mba_ct = ContentType.objects.get_for_model(OnlineMBA)
#     study_abroad_ct = ContentType.objects.get_for_model(StudyAbroad)
#     forex_trade_ct = ContentType.objects.get_for_model(ForexTrade)
    
#     # Get all assignment logs for this user
#     assignment_logs = LeadAssignmentLog.objects.filter(assigned_to=user)
    
#     # Get unique lead identifiers from assignment logs
#     unique_lead_identifiers = set()
#     lead_id_to_identifier = {}  # Map lead IDs to identifiers
    
#     for log in assignment_logs:
#         lead = log.lead
#         if lead:
#             # Create unique identifier using phone and email
#             identifier = f"{getattr(lead, 'phone_number', '')}-{getattr(lead, 'email', '')}"
#             if identifier:
#                 unique_lead_identifiers.add(identifier)
#                 lead_id_to_identifier[lead.id] = identifier
    
#     total_assigned_leads = len(unique_lead_identifiers)
    
#     # ✅ Get converted and lead_replacement counts from LeadStatusHistory - ONLY FOR THIS USER
#     converted_leads = 0
#     lead_replacement = 0
    
#     # Get all status changes made BY THIS USER for leads that were assigned to this user
#     status_history = LeadStatusHistory.objects.filter(
#         lead_content_type__in=[real_estate_ct, online_mba_ct, study_abroad_ct, forex_trade_ct],
#         lead_object_id__in=lead_id_to_identifier.keys(),
#         changed_by=user  # ✅ ONLY COUNT STATUS CHANGES DONE BY THIS USER
#     ).select_related('changed_by')
    
#     # Track which leads have been converted or marked for replacement BY THIS USER
#     converted_identifiers = set()
#     replacement_identifiers = set()
    
#     for history in status_history:
#         lead_identifier = lead_id_to_identifier.get(history.lead_object_id)
#         if lead_identifier:
#             # Check if status was changed to 'converted' BY THIS USER
#             if history.new_status == 'converted':
#                 converted_identifiers.add(lead_identifier)
#             # Check if status was changed to 'lead_replacement' BY THIS USER
#             elif history.new_status == 'lead_replacement':
#                 replacement_identifiers.add(lead_identifier)
    
#     converted_leads = len(converted_identifiers)
#     lead_replacement = len(replacement_identifiers)

#     # ✅ Available credits from user model
#     available_credits = user.available_credits

#     # Ticket statistics
#     try:
#         from .models import Ticket
#         tickets = Ticket.objects.filter(user=user)
#         ticket_stats = {
#             'total': tickets.count(),
#             'open': tickets.filter(status='open').count(),
#             'in_progress': tickets.filter(status='in_progress').count(),
#             'resolved': tickets.filter(status='resolved').count(),
#             'closed': tickets.filter(status='closed').count(),
#         }
#     except:
#         ticket_stats = {
#             'total': 0,
#             'open': 0,
#             'in_progress': 0,
#             'resolved': 0,
#             'closed': 0,
#         }

#     context = {
#         'user': user,
#         'total_leads': total_assigned_leads,
#         'converted_leads': converted_leads,
#         'lead_replacement': lead_replacement,
#         'available_credits': available_credits,
#         'user_industry': getattr(user, 'industry', None),
#         'user_sub_industry': getattr(user, 'sub_industry', None),
#         'ticket_stats': ticket_stats,
#     }

#     return render(request, 'subscribers/dashboard.html', context)




# @login_required
# def my_leads(request):
#     user = request.user

#     # Method 1: Direct assigned_to se (single assignment)
#     real_estate_leads = RealEstateLead.objects.filter(assigned_to=user)
#     mba_leads = OnlineMBA.objects.filter(assigned_to=user)
#     study_abroad_leads = StudyAbroad.objects.filter(assigned_to=user)
#     forex_trade_leads = ForexTrade.objects.filter(assigned_to=user)

#     # Method 2: Assignment history se (multiple assignment)
#     from django.contrib.contenttypes.models import ContentType
    
#     # Get content types for all lead models
#     real_estate_ct = ContentType.objects.get_for_model(RealEstateLead)
#     mba_ct = ContentType.objects.get_for_model(OnlineMBA)
#     study_abroad_ct = ContentType.objects.get_for_model(StudyAbroad)
#     forex_ct = ContentType.objects.get_for_model(ForexTrade)

#     # Get lead IDs from assignment logs for this user
#     assignment_lead_ids = LeadAssignmentLog.objects.filter(
#         assigned_to=user
#     ).values_list('lead_object_id', 'lead_content_type')

#     all_leads = []

#     # Process direct assignments
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
#             'remark': lead.remark or '',
#             'assignment_type': 'direct'
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
#             'remark': lead.remark or '',
#             'assignment_type': 'direct'
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
#             'remark': lead.remark or '',
#             'assignment_type': 'direct'
#         })

#     for lead in forex_trade_leads:
#         all_leads.append({
#             'id': f'forex_{lead.id}',
#             'original_id': lead.id,
#             'model_type': 'forex',
#             'category': 'Forex Trade',
#             'name': lead.full_name,
#             'phone': lead.phone_number,
#             'email': lead.email,
#             'extra': f"{lead.experience or '-'}/{lead.broker or '-'}/{lead.initial_investment or '-'}",
#             'status': lead.status,
#             'created_at': lead.created_at,
#             'remark': lead.remark or '',
#             'assignment_type': 'direct'
#         })

#     # Process assignment history leads (remove duplicates)
#     for lead_id, content_type_id in assignment_lead_ids:
#         try:
#             content_type = ContentType.objects.get_for_id(content_type_id)
#             lead_model = content_type.model_class()
#             lead = lead_model.objects.get(id=lead_id)
            
#             # Check if lead already exists in all_leads
#             existing_lead = None
#             for existing in all_leads:
#                 if existing['original_id'] == lead.id and existing['model_type'] == content_type.model:
#                     existing_lead = existing
#                     break
            
#             if not existing_lead:
#                 if isinstance(lead, RealEstateLead):
#                     all_leads.append({
#                         'id': f'realestate_{lead.id}',
#                         'original_id': lead.id,
#                         'model_type': 'realestate',
#                         'category': lead.sub_industry or 'Real Estate',
#                         'name': lead.full_name,
#                         'phone': lead.phone_number,
#                         'email': lead.email,
#                         'extra': f"{lead.location or '-'}/{lead.budget or '-'}/{lead.visit_day or '-'}",
#                         'status': lead.status,
#                         'created_at': lead.created_at,
#                         'remark': lead.remark or '',
#                         'assignment_type': 'history'
#                     })
#                 elif isinstance(lead, OnlineMBA):
#                     all_leads.append({
#                         'id': f'mba_{lead.id}',
#                         'original_id': lead.id,
#                         'model_type': 'mba',
#                         'category': 'Online MBA',
#                         'name': lead.full_name,
#                         'phone': lead.phone_number,
#                         'email': lead.email,
#                         'extra': f"{lead.course or '-'}/{lead.university or '-'}",
#                         'status': lead.status,
#                         'created_at': lead.created_at,
#                         'remark': lead.remark or '',
#                         'assignment_type': 'history'
#                     })
#                 elif isinstance(lead, StudyAbroad):
#                     all_leads.append({
#                         'id': f'abroad_{lead.id}',
#                         'original_id': lead.id,
#                         'model_type': 'abroad',
#                         'category': 'Study Abroad',
#                         'name': lead.full_name,
#                         'phone': lead.phone_number,
#                         'email': lead.email,
#                         'extra': f"{lead.country or '-'}/{lead.university or '-'}",
#                         'status': lead.status,
#                         'created_at': lead.created_at,
#                         'remark': lead.remark or '',
#                         'assignment_type': 'history'
#                     })
#                 elif isinstance(lead, ForexTrade):
#                     all_leads.append({
#                         'id': f'forex_{lead.id}',
#                         'original_id': lead.id,
#                         'model_type': 'forex',
#                         'category': 'Forex Trade',
#                         'name': lead.full_name,
#                         'phone': lead.phone_number,
#                         'email': lead.email,
#                         'extra': f"{lead.experience or '-'}/{lead.broker or '-'}/{lead.initial_investment or '-'}",
#                         'status': lead.status,
#                         'created_at': lead.created_at,
#                         'remark': lead.remark or '',
#                         'assignment_type': 'history'
#                     })
                    
#         except Exception as e:
#             print(f"Error processing lead from history: {e}")
#             continue

#     # Sort by latest first
#     all_leads.sort(key=lambda x: x['created_at'], reverse=True)

#     # Calendar connection check
#     calendar_connected = False
#     try:
#         auth = GoogleCalendarAuth.objects.filter(user=user).first()
#         if auth and auth.is_connected:
#             calendar_connected = True
#     except Exception as e:
#         print(f"Error checking calendar status: {e}")

#     return render(request, 'subscribers/my_leads.html', {
#         'leads': all_leads,
#         'calendar_connected': calendar_connected
#     })
    
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
#         elif lead_id.startswith('forex_'):  # NEW: Forex Trade
#             model = ForexTrade
#             original_id = lead_id.replace('forex_', '')
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
#         if remark is not None:  
#             lead_obj.remark = remark
#         lead_obj.save()

#         return JsonResponse({"success": True})

#     except json.JSONDecodeError:
#         return JsonResponse({"success": False, "error": "Invalid JSON."})
#     except Exception as e:
#         return JsonResponse({"success": False, "error": str(e)})
    
    
    
    
    
# @login_required
# def my_leads(request):
#     user = request.user

#     # Method 1: Direct assigned_to se (single assignment)
#     real_estate_leads = RealEstateLead.objects.filter(assigned_to=user)
#     mba_leads = OnlineMBA.objects.filter(assigned_to=user)
#     study_abroad_leads = StudyAbroad.objects.filter(assigned_to=user)
#     forex_trade_leads = ForexTrade.objects.filter(assigned_to=user)

#     # Method 2: Assignment history se (multiple assignment)
#     from django.contrib.contenttypes.models import ContentType
    
#     # Get content types for all lead models
#     real_estate_ct = ContentType.objects.get_for_model(RealEstateLead)
#     mba_ct = ContentType.objects.get_for_model(OnlineMBA)
#     study_abroad_ct = ContentType.objects.get_for_model(StudyAbroad)
#     forex_ct = ContentType.objects.get_for_model(ForexTrade)

#     # Get lead IDs from assignment logs for this user
#     assignment_lead_ids = LeadAssignmentLog.objects.filter(
#         assigned_to=user
#     ).values_list('lead_object_id', 'lead_content_type')

#     all_leads = []

#     # Process direct assignments
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
#             'remark': lead.remark or '',
#             'assignment_type': 'direct'
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
#             'remark': lead.remark or '',
#             'assignment_type': 'direct'
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
#             'remark': lead.remark or '',
#             'assignment_type': 'direct'
#         })

#     for lead in forex_trade_leads:
#         all_leads.append({
#             'id': f'forex_{lead.id}',
#             'original_id': lead.id,
#             'model_type': 'forex',
#             'category': 'Forex Trade',
#             'name': lead.full_name,
#             'phone': lead.phone_number,
#             'email': lead.email,
#             'extra': f"{lead.experience or '-'}/{lead.broker or '-'}/{lead.initial_investment or '-'}",
#             'status': lead.status,
#             'created_at': lead.created_at,
#             'remark': lead.remark or '',
#             'assignment_type': 'direct'
#         })

#     # Process assignment history leads (remove duplicates)
#     for lead_id, content_type_id in assignment_lead_ids:
#         try:
#             content_type = ContentType.objects.get_for_id(content_type_id)
#             lead_model = content_type.model_class()
#             lead = lead_model.objects.get(id=lead_id)
            
#             # Check if lead already exists in all_leads
#             existing_lead = None
#             for existing in all_leads:
#                 if existing['original_id'] == lead.id and existing['model_type'] == content_type.model:
#                     existing_lead = existing
#                     break
            
#             if not existing_lead:
#                 if isinstance(lead, RealEstateLead):
#                     all_leads.append({
#                         'id': f'realestate_{lead.id}',
#                         'original_id': lead.id,
#                         'model_type': 'realestate',
#                         'category': lead.sub_industry or 'Real Estate',
#                         'name': lead.full_name,
#                         'phone': lead.phone_number,
#                         'email': lead.email,
#                         'extra': f"{lead.location or '-'}/{lead.budget or '-'}/{lead.visit_day or '-'}",
#                         'status': lead.status,
#                         'created_at': lead.created_at,
#                         'remark': lead.remark or '',
#                         'assignment_type': 'history'
#                     })
#                 elif isinstance(lead, OnlineMBA):
#                     all_leads.append({
#                         'id': f'mba_{lead.id}',
#                         'original_id': lead.id,
#                         'model_type': 'mba',
#                         'category': 'Online MBA',
#                         'name': lead.full_name,
#                         'phone': lead.phone_number,
#                         'email': lead.email,
#                         'extra': f"{lead.course or '-'}/{lead.university or '-'}",
#                         'status': lead.status,
#                         'created_at': lead.created_at,
#                         'remark': lead.remark or '',
#                         'assignment_type': 'history'
#                     })
#                 elif isinstance(lead, StudyAbroad):
#                     all_leads.append({
#                         'id': f'abroad_{lead.id}',
#                         'original_id': lead.id,
#                         'model_type': 'abroad',
#                         'category': 'Study Abroad',
#                         'name': lead.full_name,
#                         'phone': lead.phone_number,
#                         'email': lead.email,
#                         'extra': f"{lead.country or '-'}/{lead.university or '-'}",
#                         'status': lead.status,
#                         'created_at': lead.created_at,
#                         'remark': lead.remark or '',
#                         'assignment_type': 'history'
#                     })
#                 elif isinstance(lead, ForexTrade):
#                     all_leads.append({
#                         'id': f'forex_{lead.id}',
#                         'original_id': lead.id,
#                         'model_type': 'forex',
#                         'category': 'Forex Trade',
#                         'name': lead.full_name,
#                         'phone': lead.phone_number,
#                         'email': lead.email,
#                         'extra': f"{lead.experience or '-'}/{lead.broker or '-'}/{lead.initial_investment or '-'}",
#                         'status': lead.status,
#                         'created_at': lead.created_at,
#                         'remark': lead.remark or '',
#                         'assignment_type': 'history'
#                     })
                    
#         except Exception as e:
#             print(f"Error processing lead from history: {e}")
#             continue

#     # Sort by latest first
#     all_leads.sort(key=lambda x: x['created_at'], reverse=True)

#     # Calendar connection check
#     calendar_connected = False
#     try:
#         auth = GoogleCalendarAuth.objects.filter(user=user).first()
#         if auth and auth.is_connected:
#             calendar_connected = True
#     except Exception as e:
#         print(f"Error checking calendar status: {e}")

#     return render(request, 'subscribers/my_leads.html', {
#         'leads': all_leads,
#         'calendar_connected': calendar_connected
#     })

@login_required
def my_leads(request):
    user = request.user
    
    # Method 1: Direct assigned_to se (single assignment)
    real_estate_leads = RealEstateLead.objects.filter(assigned_to=user)
    mba_leads = OnlineMBA.objects.filter(assigned_to=user)
    study_abroad_leads = StudyAbroad.objects.filter(assigned_to=user)
    forex_trade_leads = ForexTrade.objects.filter(assigned_to=user)
    
    # Method 2: Assignment history se (multiple assignment)
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
    all_leads = []

    # Helper function to add lead if not already added
    def add_lead(lead_data, lead_id, model_type):
        lead_key = f"{model_type}_{lead_id}"
        if lead_key not in added_lead_ids:
            added_lead_ids.add(lead_key)
            all_leads.append(lead_data)
            return True
        return False

    # Process direct assignments
    for lead in real_estate_leads:
        lead_data = {
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
            'remark': lead.remark or '',
            'assignment_type': 'direct'
        }
        add_lead(lead_data, lead.id, 'realestate')

    for lead in mba_leads:
        lead_data = {
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
            'remark': lead.remark or '',
            'assignment_type': 'direct'
        }
        add_lead(lead_data, lead.id, 'mba')

    for lead in study_abroad_leads:
        lead_data = {
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
            'remark': lead.remark or '',
            'assignment_type': 'direct'
        }
        add_lead(lead_data, lead.id, 'abroad')

    for lead in forex_trade_leads:
        lead_data = {
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
            'remark': lead.remark or '',
            'assignment_type': 'direct'
        }
        add_lead(lead_data, lead.id, 'forex')

    # Process assignment history leads (only add if not already present)
    for lead_id, content_type_id in assignment_lead_ids:
        try:
            content_type = ContentType.objects.get_for_id(content_type_id)
            lead_model = content_type.model_class()
            lead = lead_model.objects.get(id=lead_id)
            
            model_type = content_type.model
            
            # Check if lead already exists using our tracking set
            lead_key = f"{model_type}_{lead.id}"
            if lead_key in added_lead_ids:
                continue
                
            if isinstance(lead, RealEstateLead):
                lead_data = {
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
                    'remark': lead.remark or '',
                    'assignment_type': 'history'
                }
                add_lead(lead_data, lead.id, 'realestate')
                
            elif isinstance(lead, OnlineMBA):
                lead_data = {
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
                    'remark': lead.remark or '',
                    'assignment_type': 'history'
                }
                add_lead(lead_data, lead.id, 'mba')
                
            elif isinstance(lead, StudyAbroad):
                lead_data = {
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
                    'remark': lead.remark or '',
                    'assignment_type': 'history'
                }
                add_lead(lead_data, lead.id, 'abroad')
                
            elif isinstance(lead, ForexTrade):
                lead_data = {
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
                    'remark': lead.remark or '',
                    'assignment_type': 'history'
                }
                add_lead(lead_data, lead.id, 'forex')
                    
        except Exception as e:
            print(f"Error processing lead from history: {e}")
            continue

    # Sort by latest first
    all_leads.sort(key=lambda x: x['created_at'], reverse=True)

    # Calendar connection check
    calendar_connected = False
    try:
        auth = GoogleCalendarAuth.objects.filter(user=user).first()
        if auth and auth.is_connected:
            calendar_connected = True
    except Exception as e:
        print(f"Error checking calendar status: {e}")

    return render(request, 'subscribers/my_leads.html', {
        'leads': all_leads,
        'calendar_connected': calendar_connected
    })

@login_required
def update_lead_status(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method."})
    
    try:
        data = json.loads(request.body)
        lead_id = data.get("lead_id")
        new_status = data.get("status")
        remark = data.get("remark", "").strip()

        print(f"DEBUG: Received data - lead_id: {lead_id}, status: {new_status}, remark: {remark}")

        if not lead_id:
            return JsonResponse({"success": False, "error": "Missing lead ID."})

        # Validate status
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
        elif lead_id.startswith('forex_'):
            model = ForexTrade
            original_id = lead_id.replace('forex_', '')
        else:
            return JsonResponse({"success": False, "error": "Invalid lead ID format."})

        # Database se lead fetch karo - BOTH direct assignment AND assignment history check
        try:
            # Pehle direct assignment check karo
            # ✅ IMPORT ContentType here
            from django.contrib.contenttypes.models import ContentType
            lead_obj = model.objects.get(id=original_id, assigned_to=request.user)
            print(f"DEBUG: Found lead via direct assignment")
        except model.DoesNotExist:
            # Agar direct assignment nahi mila, toh assignment history check karo
            try:
                from django.contrib.contenttypes.models import ContentType
                content_type = ContentType.objects.get_for_model(model)
                
                # Check if this lead was ever assigned to this user in assignment history
                assignment_exists = LeadAssignmentLog.objects.filter(
                    lead_content_type=content_type,
                    lead_object_id=original_id,
                    assigned_to=request.user
                ).exists()
                
                if assignment_exists:
                    # Agar assignment history mein hai, toh lead access de do
                    lead_obj = model.objects.get(id=original_id)
                    print(f"DEBUG: Found lead via assignment history")
                else:
                    return JsonResponse({"success": False, "error": "Lead not found or not assigned to you."})
                    
            except model.DoesNotExist:
                return JsonResponse({"success": False, "error": "Lead not found."})
            except Exception as e:
                print(f"DEBUG: Error in assignment history check: {str(e)}")
                return JsonResponse({"success": False, "error": "Lead access verification failed."})

        # NEW: Use the update_status method to track history
        if new_status:
            lead_obj.update_status(new_status, request.user, remark)
        elif remark:
            # If only remark is being added (without status change)
            content_type = ContentType.objects.get_for_model(model)
            LeadRemarkHistory.objects.create(
                lead_content_type=content_type,
                lead_object_id=original_id,
                remark_text=remark,
                created_by=request.user
            )
            # Update legacy remark field
            lead_obj.remark = remark
            lead_obj.save()

        print(f"DEBUG: Successfully updated lead {lead_id} with status {new_status} and remark: {remark}")

        return JsonResponse({"success": True})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON."})
    except Exception as e:
        print(f"DEBUG: Error in update_lead_status: {str(e)}")
        return JsonResponse({"success": False, "error": str(e)})

@login_required
def add_lead_remark(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method."})
    
    try:
        data = json.loads(request.body)
        lead_id = data.get("lead_id")
        remark_text = data.get("remark", "").strip()

        if not lead_id or not remark_text:
            return JsonResponse({"success": False, "error": "Missing lead ID or remark."})

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
        elif lead_id.startswith('forex_'):
            model = ForexTrade
            original_id = lead_id.replace('forex_', '')
        else:
            return JsonResponse({"success": False, "error": "Invalid lead ID format."})

        # Database se lead fetch karo
        try:
            # ✅ IMPORT ContentType here
            from django.contrib.contenttypes.models import ContentType
            lead_obj = model.objects.get(id=original_id, assigned_to=request.user)
        except model.DoesNotExist:
            try:
                # ✅ IMPORT ContentType here
                from django.contrib.contenttypes.models import ContentType
                content_type = ContentType.objects.get_for_model(model)
                
                assignment_exists = LeadAssignmentLog.objects.filter(
                    lead_content_type=content_type,
                    lead_object_id=original_id,
                    assigned_to=request.user
                ).exists()
                
                if assignment_exists:
                    lead_obj = model.objects.get(id=original_id)
                else:
                    return JsonResponse({"success": False, "error": "Lead not found or not assigned to you."})
                    
            except model.DoesNotExist:
                return JsonResponse({"success": False, "error": "Lead not found."})
            except Exception as e:
                return JsonResponse({"success": False, "error": "Lead access verification failed."})

        # Create remark history
        content_type = ContentType.objects.get_for_model(model)
        LeadRemarkHistory.objects.create(
            lead_content_type=content_type,
            lead_object_id=original_id,
            remark_text=remark_text,
            created_by=request.user
        )
        
        # Update legacy remark field
        lead_obj.remark = remark_text
        lead_obj.save()

        print(f"DEBUG: Successfully added remark to lead {lead_id}")

        return JsonResponse({"success": True})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON."})
    except Exception as e:
        print(f"DEBUG: Error in add_lead_remark: {str(e)}")
        return JsonResponse({"success": False, "error": str(e)})

# @login_required
# def get_lead_remarks(request):
#     lead_id = request.GET.get("lead_id")
    
#     if not lead_id:
#         return JsonResponse({"success": False, "error": "Missing lead ID."})

#     try:
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
#         elif lead_id.startswith('forex_'):
#             model = ForexTrade
#             original_id = lead_id.replace('forex_', '')
#         else:
#             return JsonResponse({"success": False, "error": "Invalid lead ID format."})

#         # Database se lead fetch karo
#         try:
#             lead_obj = model.objects.get(id=original_id, assigned_to=request.user)
#         except model.DoesNotExist:
#             try:
#                 from django.contrib.contenttypes.models import ContentType
#                 content_type = ContentType.objects.get_for_model(model)
                
#                 assignment_exists = LeadAssignmentLog.objects.filter(
#                     lead_content_type=content_type,
#                     lead_object_id=original_id,
#                     assigned_to=request.user
#                 ).exists()
                
#                 if assignment_exists:
#                     lead_obj = model.objects.get(id=original_id)
#                 else:
#                     return JsonResponse({"success": False, "error": "Lead not found or not assigned to you."})
                    
#             except model.DoesNotExist:
#                 return JsonResponse({"success": False, "error": "Lead not found."})
#             except Exception as e:
#                 return JsonResponse({"success": False, "error": "Lead access verification failed."})
        
#         # Get remarks from LeadRemarkHistory
#         remarks_history = lead_obj.remark_history
        
#         remarks_list = []
#         for remark in remarks_history:
#             remarks_list.append({
#                 'id': remark.id,
#                 'text': remark.remark_text,
#                 'created_by': remark.created_by.get_full_name() or remark.created_by.username,
#                 'created_at': remark.created_at.strftime("%d %b %Y, %I:%M %p")
#             })

#         return JsonResponse({
#             "success": True,
#             "remarks": remarks_list
#         })

#     except Exception as e:
#         print(f"DEBUG: Error in get_lead_remarks: {str(e)}")
#         return JsonResponse({"success": False, "error": str(e)})

# @login_required
# def get_lead_status_history(request):
#     lead_id = request.GET.get("lead_id")
    
#     if not lead_id:
#         return JsonResponse({"success": False, "error": "Missing lead ID."})

#     try:
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
#         elif lead_id.startswith('forex_'):
#             model = ForexTrade
#             original_id = lead_id.replace('forex_', '')
#         else:
#             return JsonResponse({"success": False, "error": "Invalid lead ID format."})

#         # Database se lead fetch karo
#         try:
#             lead_obj = model.objects.get(id=original_id, assigned_to=request.user)
#         except model.DoesNotExist:
#             try:
#                 from django.contrib.contenttypes.models import ContentType
#                 content_type = ContentType.objects.get_for_model(model)
                
#                 assignment_exists = LeadAssignmentLog.objects.filter(
#                     lead_content_type=content_type,
#                     lead_object_id=original_id,
#                     assigned_to=request.user
#                 ).exists()
                
#                 if assignment_exists:
#                     lead_obj = model.objects.get(id=original_id)
#                 else:
#                     return JsonResponse({"success": False, "error": "Lead not found or not assigned to you."})
                    
#             except model.DoesNotExist:
#                 return JsonResponse({"success": False, "error": "Lead not found."})
#             except Exception as e:
#                 return JsonResponse({"success": False, "error": "Lead access verification failed."})
        
#         # Get status history from LeadStatusHistory
#         status_history = lead_obj.status_history
        
#         history_list = []
#         for history in status_history:
#             history_list.append({
#                 'id': history.id,
#                 'old_status': history.old_status,
#                 'new_status': history.new_status,
#                 'changed_by': history.changed_by.get_full_name() or history.changed_by.username,
#                 'created_at': history.created_at.strftime("%d %b %Y, %I:%M %p")
#             })

#         return JsonResponse({
#             "success": True,
#             "status_history": history_list
#         })

#     except Exception as e:
#         print(f"DEBUG: Error in get_lead_status_history: {str(e)}")
#         return JsonResponse({"success": False, "error": str(e)})
    
@login_required
def get_lead_remarks(request):
    lead_id = request.GET.get("lead_id")
    
    if not lead_id:
        return JsonResponse({"success": False, "error": "Missing lead ID."})

    try:
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
        elif lead_id.startswith('forex_'):
            model = ForexTrade
            original_id = lead_id.replace('forex_', '')
        else:
            return JsonResponse({"success": False, "error": "Invalid lead ID format."})

        # Database se lead fetch karo
        try:
            # ✅ IMPORT ContentType here
            from django.contrib.contenttypes.models import ContentType
            lead_obj = model.objects.get(id=original_id, assigned_to=request.user)
        except model.DoesNotExist:
            try:
                from django.contrib.contenttypes.models import ContentType
                content_type = ContentType.objects.get_for_model(model)
                
                assignment_exists = LeadAssignmentLog.objects.filter(
                    lead_content_type=content_type,
                    lead_object_id=original_id,
                    assigned_to=request.user
                ).exists()
                
                if assignment_exists:
                    lead_obj = model.objects.get(id=original_id)
                else:
                    return JsonResponse({"success": False, "error": "Lead not found or not assigned to you."})
                    
            except model.DoesNotExist:
                return JsonResponse({"success": False, "error": "Lead not found."})
            except Exception as e:
                return JsonResponse({"success": False, "error": "Lead access verification failed."})
        
        # Get remarks from LeadRemarkHistory - ONLY FOR CURRENT USER
        content_type = ContentType.objects.get_for_model(model)
        remarks_history = LeadRemarkHistory.objects.filter(
            lead_content_type=content_type,
            lead_object_id=original_id,
            created_by=request.user  # YAHAN FILTER LAGAO - sirf current user ki remarks
        ).order_by('-created_at')
        
        remarks_list = []
        for remark in remarks_history:
            remarks_list.append({
                'id': remark.id,
                'text': remark.remark_text,
                'created_by': remark.created_by.get_full_name() or remark.created_by.username,
                'created_at': remark.created_at.strftime("%d %b %Y, %I:%M %p")
            })

        return JsonResponse({
            "success": True,
            "remarks": remarks_list
        })

    except Exception as e:
        print(f"DEBUG: Error in get_lead_remarks: {str(e)}")
        return JsonResponse({"success": False, "error": str(e)})

@login_required
def get_lead_status_history(request):
    lead_id = request.GET.get("lead_id")
    
    if not lead_id:
        return JsonResponse({"success": False, "error": "Missing lead ID."})

    try:
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
        elif lead_id.startswith('forex_'):
            model = ForexTrade
            original_id = lead_id.replace('forex_', '')
        else:
            return JsonResponse({"success": False, "error": "Invalid lead ID format."})

        # Database se lead fetch karo
        try:
            # ✅ IMPORT ContentType here
            from django.contrib.contenttypes.models import ContentType
            lead_obj = model.objects.get(id=original_id, assigned_to=request.user)
        except model.DoesNotExist:
            try:
                from django.contrib.contenttypes.models import ContentType
                content_type = ContentType.objects.get_for_model(model)
                
                assignment_exists = LeadAssignmentLog.objects.filter(
                    lead_content_type=content_type,
                    lead_object_id=original_id,
                    assigned_to=request.user
                ).exists()
                
                if assignment_exists:
                    lead_obj = model.objects.get(id=original_id)
                else:
                    return JsonResponse({"success": False, "error": "Lead not found or not assigned to you."})
                    
            except model.DoesNotExist:
                return JsonResponse({"success": False, "error": "Lead not found."})
            except Exception as e:
                return JsonResponse({"success": False, "error": "Lead access verification failed."})
        
        # Get status history from LeadStatusHistory - ONLY FOR CURRENT USER
        content_type = ContentType.objects.get_for_model(model)
        status_history = LeadStatusHistory.objects.filter(
            lead_content_type=content_type,
            lead_object_id=original_id,
            changed_by=request.user  # YAHAN FILTER LAGAO - sirf current user ki status changes
        ).order_by('-created_at')
        
        history_list = []
        for history in status_history:
            history_list.append({
                'id': history.id,
                'old_status': history.old_status,
                'new_status': history.new_status,
                'changed_by': history.changed_by.get_full_name() or history.changed_by.username,
                'created_at': history.created_at.strftime("%d %b %Y, %I:%M %p")
            })

        return JsonResponse({
            "success": True,
            "status_history": history_list
        })

    except Exception as e:
        print(f"DEBUG: Error in get_lead_status_history: {str(e)}")
        return JsonResponse({"success": False, "error": str(e)})

    
    

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
import json
from .models import Ticket

# @login_required
# def submit_ticket(request):
#     if request.method == 'POST':
#         try:
#             category = request.POST.get('category')
#             priority = request.POST.get('priority')
#             description = request.POST.get('description')
            
#             # Validate required fields
#             if not all([category, priority, description]):
#                 messages.error(request, 'All fields are required')
#                 return render(request, 'subscribers/submit_ticket.html')
            
#             # Create new ticket
#             ticket = Ticket.objects.create(
#                 user=request.user,
#                 category=category,
#                 priority=priority,
#                 description=description
#             )
            
#             messages.success(request, f'Ticket #{ticket.ticket_id} created successfully! We will get back to you within 24 hours.')
#             return redirect('/subscribers/submit-ticket/')
            
#         except Exception as e:
#             messages.error(request, 'Error creating ticket. Please try again.')
#             return render(request, 'subscribers/submit_ticket.html')
#     user = request.user
#     if user.industry == "trading":
#         return render(request, 'subscribers/submit_ticket_trading.html')
#     return render(request, 'subscribers/submit_ticket.html')




# -----------------------------------Ticket-- starts------------------------------------------
    
@login_required
def submit_ticket(request):
    if request.method == 'POST':
        try:
            category = request.POST.get('category')
            priority = request.POST.get('priority')
            description = request.POST.get('description')
            selected_leads = request.POST.getlist('selected_leads')  # Multiple leads
            
            # Validate required fields
            if not all([category, priority, description]):
                messages.error(request, 'All fields are required')
                return render(request, 'subscribers/submit_ticket.html')
            
            # Create new ticket
            ticket = Ticket.objects.create(
                user=request.user,
                category=category,
                priority=priority,
                description=description
            )
            
            # If lead replacement category and leads selected, save them
            if category == 'lead' and selected_leads:
                # Store selected leads as JSON
                ticket.replacement_leads = selected_leads
                ticket.save()
            
            messages.success(request, f'Ticket #{ticket.ticket_id} created successfully! We will get back to you within 24 hours.')
            return redirect('/subscribers/submit-ticket/')
            
        except Exception as e:
            print(f"Error: {e}")
            messages.error(request, 'Error creating ticket. Please try again.')
            return render(request, 'subscribers/submit_ticket.html')
    
    # GET request - fetch user's leads for dropdown
    user_leads = get_user_leads_data(request.user)
    
    user = request.user
    context = {
        'user_leads': user_leads
    }
    
    if user.industry == "trading":
        return render(request, 'subscribers/submit_ticket_trading.html', context)
    return render(request, 'subscribers/submit_ticket.html', context)

def get_user_leads_data(user):
    """User की सभी leads को एक structured format में return करता है"""
    all_leads = []
    
    # Real Estate Leads
    real_estate_leads = RealEstateLead.objects.filter(assigned_to=user)
    for lead in real_estate_leads:
        all_leads.append({
            'id': f'realestate_{lead.id}',
            'original_id': lead.id,
            'model_type': 'realestate',
            'category': lead.sub_industry or 'Real Estate',
            'name': lead.full_name or 'No Name',
            'phone': lead.phone_number or 'No Phone',
            'email': lead.email or 'No Email',
            'status': lead.status,
            'created_at': lead.created_at.strftime('%Y-%m-%d'),
            'display_text': f"{lead.full_name} - {lead.phone_number} - {lead.sub_industry or 'Real Estate'}"
        })
    
    # Online MBA Leads
    mba_leads = OnlineMBA.objects.filter(assigned_to=user)
    for lead in mba_leads:
        all_leads.append({
            'id': f'mba_{lead.id}',
            'original_id': lead.id,
            'model_type': 'mba',
            'category': 'Online MBA',
            'name': lead.full_name or 'No Name',
            'phone': lead.phone_number or 'No Phone',
            'email': lead.email or 'No Email',
            'status': lead.status,
            'created_at': lead.created_at.strftime('%Y-%m-%d'),
            'display_text': f"{lead.full_name} - {lead.phone_number} - Online MBA"
        })
    
    # Study Abroad Leads
    study_abroad_leads = StudyAbroad.objects.filter(assigned_to=user)
    for lead in study_abroad_leads:
        all_leads.append({
            'id': f'abroad_{lead.id}',
            'original_id': lead.id,
            'model_type': 'abroad',
            'category': 'Study Abroad',
            'name': lead.full_name or 'No Name',
            'phone': lead.phone_number or 'No Phone',
            'email': lead.email or 'No Email',
            'status': lead.status,
            'created_at': lead.created_at.strftime('%Y-%m-%d'),
            'display_text': f"{lead.full_name} - {lead.phone_number} - Study Abroad"
        })
    
    # Forex Trade Leads
    forex_trade_leads = ForexTrade.objects.filter(assigned_to=user)
    for lead in forex_trade_leads:
        all_leads.append({
            'id': f'forex_{lead.id}',
            'original_id': lead.id,
            'model_type': 'forex',
            'category': 'Forex Trade',
            'name': lead.full_name or 'No Name',
            'phone': lead.phone_number or 'No Phone',
            'email': lead.email or 'No Email',
            'status': lead.status,
            'created_at': lead.created_at.strftime('%Y-%m-%d'),
            'display_text': f"{lead.full_name} - {lead.phone_number} - Forex Trade"
        })
    
    return all_leads

@login_required
def search_leads_ajax(request):
    """AJAX endpoint for searching leads by name, email, or phone"""
    search_term = request.GET.get('search', '').strip()
    
    if not search_term:
        return JsonResponse({'leads': []})
    
    user = request.user
    results = []
    
    # Search in all lead types
    # Real Estate
    real_estate_leads = RealEstateLead.objects.filter(
        assigned_to=user
    ).filter(
        Q(full_name__icontains=search_term) |
        Q(email__icontains=search_term) |
        Q(phone_number__icontains=search_term)
    )
    
    for lead in real_estate_leads:
        results.append({
            'id': f'realestate_{lead.id}',
            'display_text': f"{lead.full_name} - {lead.phone_number} - {lead.sub_industry or 'Real Estate'}",
            'name': lead.full_name,
            'phone': lead.phone_number,
            'email': lead.email,
            'category': lead.sub_industry or 'Real Estate'
        })
    
    # Online MBA
    mba_leads = OnlineMBA.objects.filter(
        assigned_to=user
    ).filter(
        Q(full_name__icontains=search_term) |
        Q(email__icontains=search_term) |
        Q(phone_number__icontains=search_term)
    )
    
    for lead in mba_leads:
        results.append({
            'id': f'mba_{lead.id}',
            'display_text': f"{lead.full_name} - {lead.phone_number} - Online MBA",
            'name': lead.full_name,
            'phone': lead.phone_number,
            'email': lead.email,
            'category': 'Online MBA'
        })
    
    # Study Abroad
    study_abroad_leads = StudyAbroad.objects.filter(
        assigned_to=user
    ).filter(
        Q(full_name__icontains=search_term) |
        Q(email__icontains=search_term) |
        Q(phone_number__icontains=search_term)
    )
    
    for lead in study_abroad_leads:
        results.append({
            'id': f'abroad_{lead.id}',
            'display_text': f"{lead.full_name} - {lead.phone_number} - Study Abroad",
            'name': lead.full_name,
            'phone': lead.phone_number,
            'email': lead.email,
            'category': 'Study Abroad'
        })
    
    # Forex Trade
    forex_trade_leads = ForexTrade.objects.filter(
        assigned_to=user
    ).filter(
        Q(full_name__icontains=search_term) |
        Q(email__icontains=search_term) |
        Q(phone_number__icontains=search_term)
    )
    
    for lead in forex_trade_leads:
        results.append({
            'id': f'forex_{lead.id}',
            'display_text': f"{lead.full_name} - {lead.phone_number} - Forex Trade",
            'name': lead.full_name,
            'phone': lead.phone_number,
            'email': lead.email,
            'category': 'Forex Trade'
        })
    
    return JsonResponse({'leads': results})

@login_required
def my_tickets(request):
    tickets = Ticket.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'subscribers/tickets.html', {'tickets': tickets})


# ----------------------------------Tickets logic end-------------------------------

# def celender(request):
#     return render(request,"subscribers/celender.html")

@login_required
def celender(request):
    events = CalendarEvent.objects.filter(user=request.user).select_related('user').order_by('event_date', 'event_time')
    
    # Lead information add karo events mein
    events_data = []
    for event in events:
        events_data.append({
            'title': event.title,
            'description': event.description,
            'event_date': event.event_date.strftime("%d %b %Y"),
            'event_time': event.event_time.strftime("%I:%M %p"),
            'lead_name': f"Lead {event.lead}"  # Aap lead ka name fetch kar sakte hain
        })
    
    return render(request, 'subscribers/celender.html', {'events': events_data})



from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime, timedelta
from .models import CalendarEvent,GoogleCalendarAuth
from optimizedleads.google_calendar_service import GoogleCalendarService
from google.oauth2.credentials import Credentials


@login_required
def create_calendar_event(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method."})
    
    try:
        data = json.loads(request.body)
        lead_id = data.get("lead_id")
        title = data.get("title")
        description = data.get("description", "")
        event_date = data.get("event_date")
        event_time = data.get("event_time")
        duration = int(data.get("duration", 60))
        
        if not all([lead_id, title, event_date, event_time]):
            return JsonResponse({"success": False, "error": "Missing required fields."})
        
        # Calculate end time based on duration
        start_datetime = datetime.strptime(f"{event_date} {event_time}", "%Y-%m-%d %H:%M")
        end_datetime = start_datetime + timedelta(minutes=duration)
        
        # Google Calendar credentials setup (aapko user ke credentials manage karne honge)
        # Yeh example hai - aapko actual credential management implement karna hoga
        credentials = get_user_credentials(request.user)
        
        if not credentials:
            return JsonResponse({"success": False, "error": "Google Calendar not connected. Please connect your account."})
        
        # Google Calendar service
        calendar_service = GoogleCalendarService(credentials)
        
        # Event data for Google Calendar
        event_data = {
            'title': title,
            'description': description,
            'start_time': start_datetime.isoformat(),
            'end_time': end_datetime.isoformat(),
        }
        
        # Create event in Google Calendar
        google_result = calendar_service.create_event(event_data)
        
        if not google_result['success']:
            return JsonResponse({"success": False, "error": google_result['error']})
        
        # Save event to our database
        calendar_event = CalendarEvent.objects.create(
            user=request.user,
            lead=lead_id,
            title=title,
            description=description,
            event_date=event_date,
            event_time=event_time,
            google_calendar_event_id=google_result['event_id']
        )
        
        return JsonResponse({
            "success": True,
            "event_id": str(calendar_event.id),
            "google_event_id": google_result['event_id']
        })
        
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

@login_required
def get_calendar_events(request):
    try:
        lead_id = request.GET.get("lead_id")
        
        if lead_id:
            events = CalendarEvent.objects.filter(user=request.user, lead=lead_id).order_by('event_date', 'event_time')
        else:
            events = CalendarEvent.objects.filter(user=request.user).order_by('event_date', 'event_time')[:10]
        
        events_data = []
        for event in events:
            events_data.append({
                'id': str(event.id),
                'title': event.title,
                'description': event.description,
                'event_date': event.event_date.strftime("%d %b %Y"),
                'event_time': event.event_time.strftime("%I:%M %p"),
                'google_event_id': event.google_calendar_event_id
            })
        
        return JsonResponse({
            "success": True,
            "events": events_data
        })
        
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

# Helper function for Google credentials (aapko implement karna hoga)
# def get_user_credentials(user):
#     """
#     User ke Google credentials fetch karta hai
#     Aapko yeh function implement karna hoga based on your auth system
#     """
#     # Example - aapko actual implementation karna hoga
#     try:
#         # Assuming you have a UserProfile model with google_credentials
#         credentials_json = user.userprofile.google_credentials
#         if credentials_json:
#             return Credentials.from_authorized_user_info(json.loads(credentials_json))
#     except:
#         pass
#     return None



# # Helper function update karo
def get_user_credentials(user):
    """
    User ke Google credentials fetch karta hai
    """
    try:
        from .models import GoogleCalendarAuth
        auth = GoogleCalendarAuth.objects.filter(user=user).first()
        if auth and auth.credentials:
            creds_data = json.loads(auth.credentials)
            return Credentials(
                token=creds_data['token'],
                refresh_token=creds_data['refresh_token'],
                token_uri=creds_data['token_uri'],
                client_id=creds_data['client_id'],
                client_secret=creds_data['client_secret'],
                scopes=creds_data['scopes']
            )
    except Exception as e:
        print(f"Error getting credentials: {e}")
    return None


from google_auth_oauthlib.flow import Flow
from django.conf import settings

# Google OAuth Configuration
GOOGLE_CLIENT_CONFIG = {
    "web": {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "project_id": settings.GOOGLE_PROJECT_ID,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
        
        # "redirect_uris": ["https://127.0.0.1:8000/subscribers/google-auth-callback/"]
    }
}

@login_required
def connect_google_calendar(request):
    """Google Calendar connect karne ka flow start karta hai"""
    try:
        # Create OAuth flow
        flow = Flow.from_client_config(
            GOOGLE_CLIENT_CONFIG,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        flow.redirect_uri = 'https://optimizedleads.in/subscribers/google-auth-callback/'
        # flow.redirect_uri = 'https://127.0.0.1:8000/subscribers/google-auth-callback/'

        # Generate authorization URL
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        # State store karo session mein
        request.session['google_oauth_state'] = state
        
        return redirect(authorization_url)
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def google_auth_callback(request):
    """Google OAuth callback handle karta hai"""
    try:
        state = request.session.get('google_oauth_state')
        if not state:
            return JsonResponse({'success': False, 'error': 'Invalid state'})
        
        flow = Flow.from_client_config(
            GOOGLE_CLIENT_CONFIG,
            scopes=['https://www.googleapis.com/auth/calendar'],
            state=state
        )
        flow.redirect_uri = 'https://optimizedleads.in/subscribers/google-auth-callback/'
        # flow.redirect_uri = 'https://127.0.0.1:8000/subscribers/google-auth-callback/'
        
        # Authorization response se tokens fetch karo
        flow.fetch_token(authorization_response=request.build_absolute_uri())
        
        # Credentials save karo
        credentials = flow.credentials
        
        # User ke liye save karo
        auth, created = GoogleCalendarAuth.objects.get_or_create(user=request.user)
        auth.credentials = json.dumps({
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        })
        auth.is_connected = True
        auth.save()
        
        # Success page par redirect karo
        return redirect('/subscribers/my-leads/?connected=success')
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# --------------------------------------------------------------------------------------------

