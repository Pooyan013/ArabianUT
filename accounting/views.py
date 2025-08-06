from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator
from itertools import chain
from operator import attrgetter
from decimal import Decimal
import openpyxl
from io import BytesIO

# Import models from your apps
from .models import Income, Expense, ExpenseCategory
from core.models import Part, Car, RepairJob 

# Import forms from your app
from .forms import IncomeForm, BuyPartForm, SimpleExpenseForm

@login_required
def accounting_dashboard_view(request):
    """
    Handles the main accounting dashboard, including displaying transactions
    and processing forms for adding income, expenses, and buying parts.
    """
    # Initialize forms for GET request or if a POST form is invalid
    income_form = IncomeForm()
    buy_part_form = BuyPartForm()
    simple_expense_form = SimpleExpenseForm(user=request.user)

    if request.method == 'POST':
        # --- Handle Add Income Form ---
        if 'add_income' in request.POST:
            income_form = IncomeForm(request.POST)
            if income_form.is_valid():
                income = income_form.save(commit=False)
                income.recorded_by = request.user
                income.save()
                messages.success(request, "Income record added successfully.")
                return redirect('accounting:dashboard')
            else:
                messages.error(request, "Please correct the errors in the income form.")

        # --- Handle Buy Part Form ---
        elif 'buy_part' in request.POST:
            buy_part_form = BuyPartForm(request.POST)
            if buy_part_form.is_valid():
                part = buy_part_form.cleaned_data['part']
                price = buy_part_form.cleaned_data['price']
                
                part.price = price
                part.is_bought = True
                part.save()
                
                Expense.objects.create(
                    expense_type='part',
                    description=f"Purchase of part: {part.name} for {part.repair_job.car}",
                    amount=price * -1,
                    related_part=part,
                    recorded_by=request.user,
                    payment_source='garage' # Assuming parts are always bought from garage funds
                )
                messages.success(request, "Part purchased and expense recorded.")
                return redirect('accounting:dashboard')
            else:
                messages.error(request, "Please correct the errors in the buy part form.")

        # --- Handle Add Simple Expense Form ---
        elif 'add_simple_expense' in request.POST:
            simple_expense_form = SimpleExpenseForm(request.POST, user=request.user)
            if simple_expense_form.is_valid():
                cd = simple_expense_form.cleaned_data
                
                recorder = request.user
                if request.user.has_perm('accounting.can_change_expense_recorder') and cd.get('recorded_by'):
                    recorder = cd.get('recorded_by')
                
                expense = Expense(
                    expense_type=cd.get('expense_type'),
                    amount=cd.get('amount') * -1,
                    payment_source=cd.get('payment_source'),
                    recorded_by=recorder
                )
                
                if expense.expense_type == 'garage':
                    expense.category = cd.get('category')
                    expense.description = expense.category.name
                else: # For 'personal' and 'other' types
                    expense.description = cd.get('description')
                
                expense.save()
                messages.success(request, "Expense added successfully.")
                return redirect('accounting:dashboard')
            else:
                messages.error(request, "Please correct the errors in the expense form.")
    
    # --- GET Request Logic ---
    income_list = Income.objects.all()
    expense_list = Expense.objects.all()
    
    type_filter = request.GET.get('type')
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')

    if type_filter == 'income':
        expense_list = expense_list.none()
    elif type_filter == 'expense':
        income_list = income_list.none()

    if from_date:
        income_list = income_list.filter(transaction_date__date__gte=from_date)
        expense_list = expense_list.filter(transaction_date__date__gte=from_date)
    if to_date:
        income_list = income_list.filter(transaction_date__date__lte=to_date)
        expense_list = expense_list.filter(transaction_date__date__lte=to_date)

    transactions = sorted(
        chain(income_list, expense_list),
        key=attrgetter('transaction_date'),
        reverse=True
    )

    paginator = Paginator(transactions, 15) # Show 15 transactions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'income_form': income_form,
        'buy_part_form': buy_part_form,
        'simple_expense_form': simple_expense_form,
    }
    return render(request, 'accounting/dashboard.html', context)


@login_required
def get_parts_for_car(request):
    car_id = request.GET.get('car_id')
    if not car_id:
        return JsonResponse({'parts': []})
    
    try:
        car = Car.objects.get(id=car_id)
        parts_queryset = Part.objects.filter(
            repair_job__car=car, 
            is_bought=False 
        ).values('id', 'name', 'picture')
        
        parts_list = list(parts_queryset)
        return JsonResponse({'parts': parts_list})
        
    except Car.DoesNotExist:
        return JsonResponse({'parts': []})


@login_required
def export_excel_view(request):
    # This logic is duplicated. For larger projects, consider refactoring into a helper function.
    income_list = Income.objects.all()
    expense_list = Expense.objects.all()

    type_filter = request.GET.get('type')
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')

    if type_filter == 'income':
        expense_list = expense_list.none()
    elif type_filter == 'expense':
        income_list = income_list.none()

    if from_date:
        income_list = income_list.filter(transaction_date__date__gte=from_date)
        expense_list = expense_list.filter(transaction_date__date__gte=from_date)
    if to_date:
        income_list = income_list.filter(transaction_date__date__lte=to_date)
        expense_list = expense_list.filter(transaction_date__date__lte=to_date)

    transactions = sorted(
        chain(income_list, expense_list),
        key=attrgetter('transaction_date'),
        reverse=True
    )

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Transactions"
    ws.append(["Date", "Type", "Description", "Source / Category", "Recorded By", "Amount"])

    for tx in transactions:
        tx_type = "Income" if tx.amount > 0 else "Expense"
        source_category = "-"
        if hasattr(tx, 'repair_job') and tx.repair_job: source_category = str(tx.repair_job.car)
        elif hasattr(tx, 'related_part') and tx.related_part and tx.related_part.repair_job: source_category = str(tx.related_part.repair_job.car)
        elif hasattr(tx, 'source') and tx.source: source_category = tx.source
        elif hasattr(tx, 'category') and tx.category: source_category = tx.category.name
        recorded_by = tx.recorded_by.get_full_name() or tx.recorded_by.username if tx.recorded_by else "-"
        
        ws.append([
            tx.transaction_date.strftime("%Y-%m-%d %H:%M"),
            tx_type,
            tx.description,
            source_category,
            recorded_by,
            float(tx.amount)
        ])

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=transactions.xlsx'
    return response