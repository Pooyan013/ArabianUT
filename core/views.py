from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required 
from django.contrib import messages
from django.utils import timezone 
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import timedelta
import json
from decimal import Decimal

# Import all your final models and forms
from .models import Car, RepairJob, QuotationItem, PurchasedPart
from .forms import (
    CarRegistrationForm, 
    JobFilterForm, 
    DealUpdateForm, 
    QuotationItemForm,
    PurchasedPartForm,
    FinalConfirmationForm
)

# --- Main/Home View ---
def index(request):
    """Renders the homepage."""
    return render(request, 'core/index.html')

# --- Car & Job List View ---
@login_required
def car_management_view(request):
    """Displays a list of jobs with filtering and handles new car registration."""
    filter_form = JobFilterForm(request.GET)
    jobs = RepairJob.objects.exclude(status='archived').select_related('car').order_by('-car__registered_at')

    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        plate_number = filter_form.cleaned_data.get('plate_number')
        estimated_cost = filter_form.cleaned_data.get('estimated_cost')
        if status:
            jobs = jobs.filter(status=status)
        if plate_number:
            jobs = jobs.filter(car__plate_number__icontains=plate_number)
        if estimated_cost:
            jobs = jobs.filter(car__estimated_cost=estimated_cost)

    if request.method == 'POST':
        form = CarRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            new_car = form.save(commit=False)
            new_car.registered_by = request.user
            new_car.save()
            RepairJob.objects.create(car=new_car)
            messages.success(request, f'Car with plate number {new_car.plate_number} was successfully registered.')
            return redirect('core:car_list')
    else:
        form = CarRegistrationForm()
    
    context = {
        'form': form,
        'jobs': jobs,
        'filter_form': filter_form, 
    }
    return render(request, 'core/car_management.html', context)

# --- Job Detail & Workflow View ---
@login_required
def job_detail_view(request, job_id):
    """Displays details for a single job and handles all related forms."""
    job = get_object_or_404(RepairJob, id=job_id)
    quotation_items = QuotationItem.objects.filter(repair_job=job)
    purchased_parts = PurchasedPart.objects.filter(repair_job=job)

    if request.method == 'POST':
        # Determine which form was submitted and process it
        if 'add_quotation_item' in request.POST:
            form = QuotationItemForm(request.POST, request.FILES)
            if form.is_valid():
                item = form.save(commit=False)
                item.repair_job = job
                item.save()
                messages.success(request, 'Quotation item added.')
        elif 'add_purchased_part' in request.POST:
            form = PurchasedPartForm(request.POST, request.FILES)
            if form.is_valid():
                part = form.save(commit=False)
                part.repair_job = job
                part.save()
                messages.success(request, 'Purchased part logged.')
        elif 'update_deal' in request.POST:
            form = DealUpdateForm(request.POST, instance=job)
            if form.is_valid():
                form.save()
                messages.success(request, 'Deal amount updated.')
        elif 'confirm_final' in request.POST:
            form = FinalConfirmationForm(request.POST, instance=job)
            if form.is_valid():
                updated_job = form.save()
                if updated_job.lpo_confirmed and updated_job.sign_confirmed:
                    updated_job.status = 'archived'
                    updated_job.exited_at = timezone.now()
                    updated_job.save()
                    messages.success(request, 'Job confirmed and archived successfully!')
                else:
                    messages.warning(request, 'Both LPO and Signature must be confirmed to archive.')
        
        return redirect('core:job_detail', job_id=job.id)

    # For GET requests, create instances of all forms
    context = {
        'job': job,
        'quotation_items': quotation_items,
        'purchased_parts': purchased_parts,
        'quotation_item_form': QuotationItemForm(),
        'purchased_part_form': PurchasedPartForm(),
        'deal_form': DealUpdateForm(instance=job),
        'final_form': FinalConfirmationForm(instance=job),
    }
    return render(request, 'core/job_detail.html', context)

# --- Status & Data Update Views ---
@login_required
def update_job_status_view(request, job_id, next_status):
    """Handles simple status changes triggered by buttons."""
    if request.method == 'POST':
        job = get_object_or_404(RepairJob, id=job_id)
        current_status = job.status
        
        # --- Full Workflow Logic ---
        if next_status == 'quotation' and current_status == 'pending_expert':
            job.status = 'quotation'
            job.expert_inspected_at = timezone.now()
        elif next_status == 'pending_approval' and current_status == 'quotation':
            job.status = 'pending_approval'
        elif next_status == 'pending_start' and current_status == 'pending_approval':
            job.status = 'pending_start'
            job.approved_at = timezone.now()
            duration_map = {'nodamage': 1, 'cheap': 4, 'lite': 7, 'mid': 10, 'heavy': 14}
            days = duration_map.get(job.car.estimated_cost, 10)
            job.timer_start_time = timezone.now()
            job.timer_end_time = job.timer_start_time + timedelta(days=days)
        elif next_status == 'pending_part':
            job.status = 'pending_part'
            job.parts_pending_at = timezone.now()
        elif next_status == 'working':
            job.status = 'working'
            job.work_started_at = timezone.now()
        elif next_status == 'ready_to_exit' and current_status == 'working':
            job.status = 'ready_to_exit'
            job.work_finished_at = timezone.now()
        elif next_status == 'exit' and current_status == 'ready_to_exit':
            job.status = 'exit'
        
        job.save()
        messages.success(request, f"Job status updated to '{job.get_status_display()}'")

    return redirect('core:job_detail', job_id=job.id)

@login_required
def edit_car_view(request, car_id):
    """Handles editing the information of an existing car."""
    car = get_object_or_404(Car, id=car_id)
    if request.method == 'POST':
        form = CarRegistrationForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, 'Car information updated successfully.')
            latest_job = car.jobs.order_by('-registered_at').first()
            return redirect('core:job_detail', job_id=latest_job.id) if latest_job else redirect('core:car_list')
    else:
        form = CarRegistrationForm(instance=car)
    context = {'form': form, 'car': car}
    return render(request, 'core/edit_car.html', context)

# --- Views for Quotation Items and Purchased Parts ---
@login_required
def delete_quotation_item_view(request, item_id):
    item = get_object_or_404(QuotationItem, id=item_id)
    job_id = item.repair_job.id
    if request.method == 'POST':
        item.delete()
        messages.success(request, f'Item "{item.name}" deleted from quotation.')
    return redirect('core:job_detail', job_id=job_id)

@login_required
def delete_purchased_part_view(request, part_id):
    part = get_object_or_404(PurchasedPart, id=part_id)
    job_id = part.repair_job.id
    if request.method == 'POST':
        part.delete()
        messages.success(request, f'Purchased part "{part.name}" deleted.')
    return redirect('core:job_detail', job_id=job_id)

@login_required
def generate_quotation_pdf(request, job_id):
    """
    Generates a PDF by fetching QuotationItem objects directly from the database.
    """
    job = get_object_or_404(RepairJob, id=job_id)
    
    # Get items directly from the database, not from a POST request
    items = QuotationItem.objects.filter(repair_job=job)
    
    total_price = sum(item.price for item in items)
    
    template_path = 'reports/quotation_pdf.html'
    context = {
        'job': job,
        'items': items,
        'total_price': total_price,
    }
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="quotation_{job.car.plate_number}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
       return HttpResponse('We had some errors creating the PDF.')
    return response