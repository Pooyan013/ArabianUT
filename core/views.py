from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required 
from django.contrib import messages
from django.utils import timezone 
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import timedelta
from decimal import Decimal
from django.contrib.auth.decorators import permission_required
from django.template.loader import render_to_string
import io
import os
from django.conf import settings
from markdownx.models import MarkdownxField
from pathlib import Path
from weasyprint import HTML

# Import all the final, correct models and forms
from .models import Car, RepairJob, Part, QuotationItem
from .forms import (
    CarRegistrationForm, 
    JobFilterForm, 
    DealUpdateForm, 
    PartItemForm,
    QuotationItemForm, 
    SignConfirmationForm,
    LpoConfirmationForm,
    OwnerForm,
    BuyPartForm
)

# --- Main/Home View ---
def index(request):
    """Renders the homepage."""
    return render(request, 'core/index.html')

# --- Car & Job List View ---
@login_required
def car_management_view(request):
    sort_field = request.GET.get('sort', '-car__registered_at')
    allowed_sorts = ['plate_number', 'brand', 'model', 'claim_number', 'registered_at']
    if sort_field.lstrip('-').split('__')[-1] not in allowed_sorts:
        sort_field = '-car__registered_at'

    filter_form = JobFilterForm(request.GET)
    jobs = RepairJob.objects.exclude(status='archived').select_related('car').order_by(sort_field)

    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        plate_number = filter_form.cleaned_data.get('plate_number')
        estimated_cost = filter_form.cleaned_data.get('estimated_cost')
        claim_number = filter_form.cleaned_data.get('claim_number')
        if status:
            jobs = jobs.filter(status=status)
        if plate_number:
            jobs = jobs.filter(car__plate_number__icontains=plate_number)
        if estimated_cost:
            jobs = jobs.filter(car__estimated_cost=estimated_cost)
        if claim_number:
            jobs = jobs.filter(car__claim_number__icontains=claim_number)

    if request.method == 'POST':
        car_form = CarRegistrationForm(request.POST, request.FILES)
        owner_form = OwnerForm(request.POST)

        if car_form.is_valid() and owner_form.is_valid():
            new_owner = owner_form.save()
            new_car = car_form.save(commit=False)
            new_car.owner = new_owner
            new_car.registered_by = request.user
            new_car.save()

            RepairJob.objects.create(car=new_car)
            messages.success(request, f'Car with plate number {new_car.plate_number} was successfully registered.')
            return redirect('core:car_list')
    else:
        car_form = CarRegistrationForm()
        owner_form = OwnerForm()

    context = {
        'car_form': car_form,
        'owner_form': owner_form,
        'jobs': jobs,
        'filter_form': filter_form,
    }
    return render(request, 'core/cars.html', context)

# --- Job Detail & Workflow View ---
@login_required
def job_detail_view(request, job_id):
    job = get_object_or_404(RepairJob, id=job_id)
    parts = Part.objects.filter(repair_job=job)
    quotation_items = QuotationItem.objects.filter(repair_job=job) # Added query

    if request.method == 'POST':
        # --- START: Added logic for QuotationItemForm ---
        if 'add_quotation_item' in request.POST:
            form = QuotationItemForm(request.POST, request.FILES)
            if form.is_valid():
                item = form.save(commit=False)
                item.repair_job = job
                item.save()
                messages.success(request, 'Quotation item added.')
        # --- END: Added logic ---
        elif 'add_part' in request.POST:
            form = PartItemForm(request.POST, request.FILES)
            if form.is_valid():
                part = form.save(commit=False)
                part.repair_job = job
                part.save()
                messages.success(request, 'Part added successfully.')
        elif 'update_deal' in request.POST:
            form = DealUpdateForm(request.POST, instance=job)
            if form.is_valid():
                form.save()
                messages.success(request, 'Deal amount updated.')
        elif 'confirm_sign' in request.POST:
            form = SignConfirmationForm(request.POST, instance=job)
            if form.is_valid():
                signed_job = form.save()
                signed_job.status = 'exit'
                signed_job.save()
                messages.success(request, 'Signature information saved. Proceeding to LPO confirmation.')
                return redirect('core:job_detail', job_id=job.id)

        elif 'confirm_lpo' in request.POST:
            form = LpoConfirmationForm(request.POST, instance=job)
            if form.is_valid():
                lpo_job = form.save()
                lpo_job.status = 'archived'
                lpo_job.exited_at = timezone.now()
                lpo_job.save()
                messages.success(request, 'LPO information saved and job archived.')
                return redirect('core:job_detail', job_id=job.id)
    # For GET requests, create instances of all forms
    context = {
        'job': job,
        'parts': parts,
        'quotation_items': quotation_items, 
        'part_form': PartItemForm(),
        'quotation_item_form': QuotationItemForm(), 
        'deal_form': DealUpdateForm(instance=job),
        'sign_form': SignConfirmationForm(instance=job),
        'lpo_form': LpoConfirmationForm(instance=job),
    }
    return render(request, 'core/job_detail.html', context)

@login_required
def pause_timer_view(request, job_id):
    if request.method == 'POST':
        job = get_object_or_404(RepairJob, id=job_id)
        if job.timer_start_time and not job.timer_paused_at:
            job.timer_paused_at = timezone.now()
            job.save()
            messages.info(request, 'Timer has been paused.')
    return redirect('core:job_detail', job_id=job_id)

@login_required
def resume_timer_view(request, job_id):
    if request.method == 'POST':
        job = get_object_or_404(RepairJob, id=job_id)
        if job.timer_paused_at and job.timer_end_time:
            pause_duration = timezone.now() - job.timer_paused_at
            
            job.timer_end_time += pause_duration
            
            job.timer_paused_at = None
            job.save()
            messages.info(request, 'Timer has been resumed.')
    return redirect('core:job_detail', job_id=job_id)


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
        
        elif next_status == 'pending_part':
            job.status = 'pending_part'
            job.parts_pending_at = timezone.now()
        
        elif next_status == 'working':
            job.status = 'working'
            job.work_started_at = timezone.now()
            
            if not job.timer_start_time:
                duration_map = {'nodamage': 2, 'cheap': 4, 'lite': 7, 'mid': 14, 'heavy': 21}
                days = duration_map.get(job.car.estimated_cost, 10)
                job.timer_start_time = timezone.now() 
                job.timer_end_time = job.timer_start_time + timedelta(days=days)

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
    """Handles editing car and owner info, and optionally generating a PDF."""
    car = get_object_or_404(Car, id=car_id)
    owner = car.owner

    if request.method == 'POST':
        car_form = CarRegistrationForm(request.POST, request.FILES, instance=car)
        owner_form = OwnerForm(request.POST, instance=owner)

        if car_form.is_valid() and owner_form.is_valid():
            owner_instance = owner_form.save()  
            car_instance = car_form.save(commit=False) 
            car_instance.owner = owner_instance      
            car_instance.save()                       

            messages.success(request, 'Car and owner information updated successfully.')

            if 'generate_pdf' in request.POST:
                html_string = render_to_string('core/car_owner_pdf_template.html', {
                    'car': car_instance,
                    'owner': owner_instance,
                })
                result = io.BytesIO()
                pdf = pisa.CreatePDF(io.BytesIO(html_string.encode('utf-8')), dest=result)
                if pdf.err:
                    return HttpResponse('Error generating PDF', status=500)
                response = HttpResponse(result.getvalue(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename=car_{car_instance.plate_number}_owner.pdf'
                return response

            latest_job = car_instance.jobs.order_by('-registered_at').first()
            return redirect('core:job_detail', job_id=latest_job.id) if latest_job else redirect('core:car_list')
    else:
        car_form = CarRegistrationForm(instance=car)
        owner_form = OwnerForm(instance=owner)

    context = {
        'car_form': car_form,
        'owner_form': owner_form,
        'car': car,
    }
    return render(request, 'core/edit_car.html', context)


@login_required
def delete_part_view(request, part_id):
    """Deletes a part from a repair job."""
    part = get_object_or_404(Part, id=part_id)
    job_id = part.repair_job.id
    if request.method == 'POST':
        part.delete()
        messages.success(request, f'Part "{part.name}" was deleted successfully.')
    return redirect('core:job_detail', job_id=job_id)

# --- START: New View for Deleting Quotation Items ---
@login_required
def delete_quotation_item_view(request, item_id):
    item = get_object_or_404(QuotationItem, id=item_id)
    job_id = item.repair_job.id

    item_display_name = item.custom_name if item.custom_name else (item.item_name.name if item.item_name else 'Unknown Item')

    if request.method == 'POST':
        item.delete()
        messages.success(request, f'Item "{item_display_name}" deleted from quotation.')

    return redirect('core:job_detail', job_id=job_id)


@login_required
def mark_part_as_bought_view(request, part_id):
    part = get_object_or_404(Part, id=part_id)

    if request.method == 'POST':
        price = request.POST.get('price')
        if price:
            part.price = price
            part.is_bought = True
            part.save()
            messages.success(request, f'Part "{part.name}" marked as bought with price {part.price}.')
        else:
            messages.error(request, 'Price is required.')
        return redirect('core:job_detail', job_id=part.repair_job.id)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def generate_quotation_pdf(request, job_id):
    job = get_object_or_404(RepairJob, id=job_id)
    items = QuotationItem.objects.filter(repair_job=job)
    
    sub_total = sum(item.amount for item in items)
    tax_rate = Decimal('0.05') 
    tax_due = sub_total * tax_rate
    total_final = sub_total + tax_due

    context = {
        'job': job,
        'items': items,
        'sub_total': sub_total,
        'tax_rate': int(tax_rate * 100),
        'tax_due': tax_due,
        'total_final': total_final,
    }

    html_string = render_to_string('reports/quotation_pdf_custom.html', context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    pdf_file = html.write_pdf()

    filename = f'quotation_{job.car.plate_number}.pdf'
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def generate_car_owner_pdf(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    header_path = os.path.join(settings.STATICFILES_DIRS[0], 'reports', 'images', 'header.png')
    header_uri = Path(header_path).as_uri()

    context = {
        'car': car,
        'owner': car.owner,
        'header_image_path': header_uri,
    }

    html_string = render_to_string('reports/car_owner_pdf.html', context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="car_details_{car.plate_number}.pdf"'
    return response



from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect
from decimal import Decimal
from .models import RepairJob

@permission_required('core.can_manage_repair_dashboard', raise_exception=True)
def repair_dashboard(request):
    jobs = RepairJob.objects.exclude(lpo_confirmed=True, sign_confirmed=True)

    if request.method == 'POST':
        for job in jobs:
            job.lpo_confirmed = f'lpo_{job.id}' in request.POST

            job.sign_confirmed = f'sign_{job.id}' in request.POST

            deal_val = request.POST.get(f'deal_{job.id}')
            if deal_val:
                try:
                    job.deal = Decimal(deal_val)
                except:
                    pass  

            job.save()

        return redirect('core:repair_dashboard')

    return render(request, 'core/repair_dashboard.html', {'jobs': jobs})
