from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required 
from django.contrib import messages
from django.utils import timezone 
from datetime import timedelta
from .models import Car, RepairJob, Part
from .forms import DealUpdateForm, PartForm, LPOConfirmationForm, CarRegistrationForm

def index(request):
    return render(request, 'core/index.html')


@login_required
def job_detail_view(request, job_id):
    job = get_object_or_404(RepairJob, id=job_id)
    parts = Part.objects.filter(repair_job=job)

    if request.method == 'POST':
        # Existing forms
        deal_form = DealUpdateForm(request.POST, instance=job)
        part_form = PartForm(request.POST, request.FILES)
        # New LPO form
        lpo_form = LPOConfirmationForm(request.POST, instance=job)

        if 'update_deal' in request.POST:
            if deal_form.is_valid():
                deal_form.save()
                messages.success(request, 'Deal amount updated.')
        
        elif 'add_part' in request.POST:
            if part_form.is_valid():
                new_part = part_form.save(commit=False)
                new_part.repair_job = job
                new_part.save()
                messages.success(request, 'New part added.')
        
        # Handle the new LPO form submission
        elif 'confirm_lpo' in request.POST:
            if lpo_form.is_valid():
                lpo_form.save()
                messages.success(request, 'LPO status confirmed.')

        return redirect('core:job_detail', job_id=job.id)

    else:
        deal_form = DealUpdateForm(instance=job)
        part_form = PartForm()
        lpo_form = LPOConfirmationForm(instance=job)

    context = {
        'job': job,
        'parts': parts,
        'deal_form': deal_form,
        'part_form': part_form,
        'lpo_form': lpo_form, 
    }
    return render(request, 'core/job_detail.html', context)

@login_required
def car_management_view(request):
    if request.method == 'POST':
        form = CarRegistrationForm(request.POST)
        if form.is_valid():
            new_car = form.save()
            RepairJob.objects.create(car=new_car)
            
            messages.success(request, f'Car with plate number {new_car.plate_number} was successfully registered.')
            return redirect('core:car_list')
    else:
        form = CarRegistrationForm()

    jobs = RepairJob.objects.exclude(status='archived').order_by('-car__registered_at')
    
    context = {
        'form': form,
        'jobs': jobs,
    }
    return render(request, 'core/cars.html', context)

@login_required
def update_job_status_view(request, job_id, next_status):
    job = get_object_or_404(RepairJob, id=job_id)
    
    if request.method == 'POST':
        job.status = next_status
        
        if next_status == 'pending_approval':
            job.expert_inspected_at = timezone.now()
        
        elif next_status == 'pending_start':
            job.approved_at = timezone.now()
            duration_map = {
                'nodamage': 1, 'cheap': 4, 'lite': 7, 'mid': 10, 'heavy': 14
            }
            days = duration_map.get(job.car.estimated_cost, 10) 
            job.timer_start_time = timezone.now()
            job.timer_end_time = job.timer_start_time + timedelta(days=days)

        elif next_status == 'pending_part':
            job.parts_pending_at = timezone.now()

        elif next_status == 'working':
            job.work_started_at = timezone.now()
        
        elif next_status == 'ready_exit':
            job.work_finished_at = timezone.now()
            if job.lpo_confirmed:
                job.status = 'archived'
                job.exited_at = timezone.now()
                messages.success(request, f"Job for {job.car} finished and archived.")
            else:
                messages.warning(request, f"Job for {job.car} is finished but waiting for LPO confirmation.")
        
        job.save()
        if not (job.status == 'archived' and next_status == 'ready_exit'):
            messages.success(request, f"Job status updated to '{job.get_status_display()}'")

    return redirect('core:job_detail', job_id=job.id)
@login_required
def edit_car_view(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    if request.method == 'POST':
        form = CarRegistrationForm(request.POST, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, 'Car information updated successfully.')
            latest_job = car.jobs.order_by('-registered_at').first()
            if latest_job:
                return redirect('core:job_detail', job_id=latest_job.id)
            return redirect('core:car_list') 
    else:
        form = CarRegistrationForm(instance=car)

    context = {
        'form': form,
        'car': car
    }
    return render(request, 'core/edit_car.html', context)