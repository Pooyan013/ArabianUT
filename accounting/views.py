from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from itertools import chain
from operator import attrgetter

from .models import Income, Expense
from .forms import IncomeForm, ExpenseForm, BuyPartForm
from core.models import Part, Car

@login_required
def accounting_dashboard_view(request):
    income_form = IncomeForm()
    expense_form = ExpenseForm()
    buy_part_form = BuyPartForm(request.POST or None)

    if request.method == 'POST':
        if 'add_income' in request.POST:
            income_form = IncomeForm(request.POST)
            if income_form.is_valid():
                income = income_form.save(commit=False)
                income.recorded_by = request.user
                income.save()
                messages.success(request, "Income record added successfully.")
            else:
                messages.error(request, "Please correct the errors in the income form.")
            return redirect('accounting:dashboard')

        elif 'add_expense' in request.POST:
            expense_form = ExpenseForm(request.POST)
            if expense_form.is_valid():
                expense = expense_form.save(commit=False)
                if not request.user.is_superuser:
                    expense.recorded_by = request.user
                expense.save()
                messages.success(request, "Expense record added successfully.")
            else:
                messages.error(request, "Please correct the errors in the expense form.")
            return redirect('accounting:dashboard')

        elif 'buy_part' in request.POST:
            buy_part_form = BuyPartForm(request.POST)
            if buy_part_form.is_valid():
                part = buy_part_form.cleaned_data['part']
                price = buy_part_form.cleaned_data['price']
                part.price = price
                part.is_bought = True
                part.save()
                messages.success(request, "Part bought successfully.")
            else:
                messages.error(request, "Please correct the errors in the buy part form.")
            return redirect('accounting:dashboard')

    income_list = Income.objects.all()
    expense_list = Expense.objects.all()

    transactions = sorted(
        chain(income_list, expense_list),
        key=attrgetter('transaction_date'),
        reverse=True
    )

    context = {
        'income_form': income_form,
        'expense_form': expense_form,
        'buy_part_form': buy_part_form,
        'transactions': transactions,
    }
    return render(request, 'accounting/dashboard.html', context)

@login_required
def get_parts_ajax(request):
    car_id = request.GET.get('car_id')
    parts = []
    if car_id:
        parts_qs = Part.objects.filter(repair_job__car_id=car_id, is_bought=False)
        parts = [{'id': p.id, 'name': p.name} for p in parts_qs]
    return JsonResponse({'parts': parts})
