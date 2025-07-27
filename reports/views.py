from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import RepairJob
from decimal import Decimal
from .forms import DateRangeFilterForm
import openpyxl
from django.http import HttpResponse
from openpyxl.utils import get_column_letter
from accounting.models import SalarySlip, Expense, Attendance

@login_required
def operational_report_view(request):
    form = DateRangeFilterForm(request.GET or None)
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
            'active_page': 'operational',

    }
    return render(request, 'reports/operational_report.html', context)

@login_required
def financial_report_view(request):
    form = DateRangeFilterForm(request.GET or None)
    jobs = RepairJob.objects.select_related('car').filter(
        status='archived', 
        deal__isnull=False
    ).order_by('-approved_at')

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        if start_date:
            jobs = jobs.filter(approved_at__gte=start_date)
        if end_date:
            jobs = jobs.filter(approved_at__lte=end_date)

    # Calculate totals
    grand_total_deal = sum(job.deal for job in jobs if job.deal)
    grand_total_vat = grand_total_deal * Decimal('0.05')
    grand_total_final = grand_total_deal + grand_total_vat

    # Add calculated fields to each object for the template
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
        'active_page': 'financial', 

    }
    return render(request, 'reports/financial_report.html', context)
@login_required
def export_operational_report_excel(request):
    """Exports the operational report to an Excel file, respecting date filters."""
    jobs = RepairJob.objects.select_related('car').all().order_by('-car__registered_at')
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        jobs = jobs.filter(car__registered_at__gte=start_date)
    if end_date:
        jobs = jobs.filter(car__registered_at__lte=end_date)

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Operational Report'

    headers = ['Car Make', 'Model', 'Plate', 'Color', 'Status', 'Entry Date', 'Expert Visit', 'Approve Date']
    sheet.append(headers)

    for job in jobs:
        row = [
            job.car.brand, job.car.model, job.car.plate_number, job.car.color,
            job.get_status_display(),
            job.car.registered_at.strftime('%Y-%m-%d') if job.car.registered_at else '',
            job.expert_inspected_at.strftime('%Y-%m-%d') if job.expert_inspected_at else '',
            job.approved_at.strftime('%Y-%m-%d') if job.approved_at else '',
        ]
        sheet.append(row)
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="operational_report.xlsx"'
    workbook.save(response)
    return response
# --- END: New Export View ---

login_required
def export_financial_report_excel(request):
    """
    Exports the financial report to an Excel file,
    respecting the date filters from the request.
    """
    jobs = RepairJob.objects.select_related('car').filter(status='archived', deal__isnull=False).order_by('-approved_at')
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        jobs = jobs.filter(approved_at__gte=start_date)
    if end_date:
        jobs = jobs.filter(approved_at__lte=end_date)

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Financial Report'

    # --- START: Updated Headers ---
    headers = ['Car', 'Model', 'Plate', 'LPO', 'Sign', 'Claim No', 'Deal', 'VAT (5%)', 'Total', 'Approve Date']
    sheet.append(headers)
    # --- END: Updated Headers ---

    for job in jobs:
        vat = job.deal * Decimal('0.05') if job.deal else 0
        total = job.deal + vat if job.deal else 0
        lpo_status = "YES" if job.lpo_confirmed else "NO"
        sign_status = "YES" if job.sign_confirmed else "NO" # <-- Get sign status
        
        # --- START: Updated Row Data ---
        row = [
            job.car.brand, job.car.model, job.car.plate_number,
            lpo_status, sign_status, job.car.claim_number, # <-- Added sign status
            job.deal, vat, total,
            job.approved_at.strftime('%Y-%m-%d') if job.approved_at else '',
        ]
        sheet.append(row)
        # --- END: Updated Row Data ---
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="financial_report.xlsx"'
    workbook.save(response)
    
    return response

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounting.models import SalarySlip, Attendance 
from .forms import DateRangeFilterForm

@login_required
def payroll_report_view(request):
    form = DateRangeFilterForm(request.GET or None)
    slips = SalarySlip.objects.select_related('employee').all().order_by('-pay_period_end')

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        if start_date:
            slips = slips.filter(pay_period_end__gte=start_date)
        if end_date:
            slips = slips.filter(pay_period_end__lte=end_date)
            
    # --- START: منطق جدید برای خواندن جزئیات هزینه‌ها ---
    for slip in slips:
        # شمارش غیبت‌ها
        slip.absence_count = Attendance.objects.filter(
            employee=slip.employee,
            date__range=(slip.pay_period_start, slip.pay_period_end)
        ).count()
        
        # گرفتن لیست تمام هزینه‌های شخصی در این دوره حقوقی
        slip.personal_expenses = Expense.objects.filter(
            employee=slip.employee,
            expense_type='personal',
            transaction_date__range=(slip.pay_period_start, slip.pay_period_end)
        )
    # --- END: منطق جدید ---

    total_cost_sum = sum(slip.cost for slip in slips)

    context = {
        'form': form,
        'salary_slips': slips,
        'total_cost_sum': total_cost_sum,
        'active_page': 'payroll',
    }
    return render(request, 'reports/payroll_report.html', context)
