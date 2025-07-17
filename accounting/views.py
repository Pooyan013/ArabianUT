from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from itertools import chain
from operator import attrgetter
from .models import Income, Expense
from .forms import IncomeForm, ExpenseForm

@login_required
def accounting_dashboard_view(request):
    # Handle form submissions
    if request.method == 'POST':
        # Check which form was submitted
        if 'add_income' in request.POST:
            income_form = IncomeForm(request.POST)
            if income_form.is_valid():
                new_income = income_form.save(commit=False)
                new_income.recorded_by = request.user
                new_income.save()
                messages.success(request, 'Income record added successfully.')
            else:
                messages.error(request, 'Please correct the errors in the income form.')
        
        elif 'add_expense' in request.POST:
            expense_form = ExpenseForm(request.POST)
            if expense_form.is_valid():
                new_expense = expense_form.save(commit=False)
                new_expense.recorded_by = request.user
                new_expense.save()
                messages.success(request, 'Expense record added successfully.')
            else:
                messages.error(request, 'Please correct the errors in the expense form.')
        
        return redirect('accounting:dashboard')

    # For GET requests
    income_form = IncomeForm()
    expense_form = ExpenseForm()

    # Get and combine transactions
    income_list = Income.objects.all()
    expense_list = Expense.objects.all()
    
    # Combine and sort all transactions by date
    all_transactions = sorted(
        chain(income_list, expense_list),
        key=attrgetter('transaction_date'),
        reverse=True
    )

    context = {
        'income_form': income_form,
        'expense_form': expense_form,
        'transactions': all_transactions,
    }
    return render(request, 'accounting/dashboard.html', context)
