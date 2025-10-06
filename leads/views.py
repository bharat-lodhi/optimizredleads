from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from .models import Lead
from accounts.models import CustomUser
from django.http import HttpResponse
import io
import pandas as pd
from reportlab.pdfgen import canvas

def leads_list(request):
    user_id = request.session.get('user_id')
    user_role = request.session.get('user_role')
    if not user_id:
        return redirect('accounts:login')
    user = CustomUser.objects.get(id=user_id)
    if user_role == 'central_admin':
        leads = Lead.objects.all()
    elif user_role == 'sub_admin':
        # basic: sub-admin sees all leads (customize per rules)
        leads = Lead.objects.all()
    else:
        leads = Lead.objects.filter(assigned_to=user)
    return render(request, 'leads/leads_list.html', {'leads': leads})

def add_lead(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        source = request.POST.get('source')
        Lead.objects.create(name=name, email=email, phone=phone, source=source)
        return redirect('leads:list')
    return render(request, 'leads/add_lead.html')

def assign_leads(request):
    if request.method == 'POST':
        target_id = request.POST.get('target_id')
        mode = request.POST.get('mode')
        user = CustomUser.objects.get(id=target_id)
        if mode == 'single':
            lead_id = request.POST.get('lead_id')
            lead = Lead.objects.get(id=lead_id)
            lead.assigned_to = user
            lead.save()
        elif mode == 'multiple':
            ids = request.POST.getlist('lead_ids')
            Lead.objects.filter(id__in=ids).update(assigned_to=user)
        elif mode == 'all':
            Lead.objects.all().update(assigned_to=user)
    return redirect('leads:list')

def export_leads_csv(request):
    leads = Lead.objects.all()
    df = pd.DataFrame(list(leads.values('id','name','email','phone','source','status','assigned_to','created_at')))
    response = HttpResponse(df.to_csv(index=False), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=leads.csv'
    return response

def export_leads_excel(request):
    leads = Lead.objects.all()
    df = pd.DataFrame(list(leads.values('id','name','email','phone','source','status','assigned_to','created_at')))
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Leads')
    response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=leads.xlsx'
    return response

def export_leads_pdf(request):
    leads = Lead.objects.all()
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    y = 800
    for lead in leads:
        p.drawString(50, y, f"{lead.id} | {lead.name} | {lead.email} | {lead.phone} | {lead.status}")
        y -= 20
        if y < 50:
            p.showPage(); y = 800
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')
