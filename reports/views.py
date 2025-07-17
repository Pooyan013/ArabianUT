from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import RepairJob
from decimal import Decimal
from .forms import DateRangeFilterForm
import openpyxl
from django.http import HttpResponse
from openpyxl.utils import get_column_letter

@login_required
def operational_report_view(request):
    form = DateRangeFilterForm(request.GET)
    jobs = RepairJob.objects.select_related('car').all().order_by('-car__registered_at')

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        if start_date:
            jobs = jobs.filter(car__registered_at__gte=start_date)
        if end_date:
            jobs = jobs.filter(car__registered_at__lte=end_date)

    context = {
        'form': form,
        'report_jobs': jobs,
    }
    return render(request, 'reports/operational_report.html', context)

@login_required
def financial_report_view(request):
    form = DateRangeFilterForm(request.GET)
    jobs = RepairJob.objects.select_related('car').filter(deal__isnull=False).order_by('-car__registered_at')

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        if start_date:
            jobs = jobs.filter(approved_at__gte=start_date)
        if end_date:
            jobs = jobs.filter(approved_at__lte=end_date)

    grand_total_deal = sum(job.deal for job in jobs if job.deal)
    grand_total_vat = grand_total_deal * Decimal('0.05')
    grand_total_final = grand_total_deal + grand_total_vat

 
    for job in jobs:
        if job.deal:
            job.vat = job.deal * Decimal('0.05')
            job.total = job.deal + job.vat

    context = {
        'form': form,
        'report_jobs': jobs,
        'grand_total_deal': grand_total_deal,
        'grand_total_vat': grand_total_vat,
        'grand_total_final': grand_total_final,
    }
    return render(request, 'reports/financial_report.html', context)


@login_required
def export_financial_report_excel(request):

    jobs = RepairJob.objects.select_related('car').filter(deal__isnull=False).order_by('-approved_at')
    
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Financial Report'

    # Write headers
    headers = ['Car', 'Model', 'Plate', 'LPO', 'Claim No', 'Deal', 'VAT (5%)', 'Total', 'Approve Date', 'Note']
    sheet.append(headers)

    # Write data
    for job in jobs:
        vat = job.deal * Decimal('0.05') if job.deal else 0
        total = job.deal + vat if job.deal else 0
        lpo_status = "YES" if job.lpo_confirmed else "NO"
        
        row = [
            job.car.brand, job.car.model, job.car.plate_number,
            lpo_status, job.car.claim_number, job.deal, vat, total,
            job.approved_at.strftime('%Y-%m-%d') if job.approved_at else '',
            '' # Placeholder for notes
        ]
        sheet.append(row)
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="financial_report.xlsx"'
    workbook.save(response)
    
    return response