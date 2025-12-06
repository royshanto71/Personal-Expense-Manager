from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Expense, Category, Income, Budget
from .forms import ExpenseForm, CategoryForm, IncomeForm, BudgetForm
from django.db.models import Sum
from django.db import models
from django.utils import timezone
from datetime import timedelta

class ExpenseListView(LoginRequiredMixin, ListView):
    model = Expense
    template_name = 'expenses/expense_list.html'
    context_object_name = 'expenses'
    ordering = ['-date']

    def get_queryset(self):
        queryset = Expense.objects.filter(user=self.request.user).order_by('-date')
        
        # Filtering
        category_id = self.request.GET.get('category')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
            
        return queryset

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['expenses/partials/expense_rows.html']
        return ['expenses/expense_list.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass categories for filter dropdown
        context['categories'] = Category.objects.filter(models.Q(user=None) | models.Q(user=self.request.user), type='expense')
        
        # Totals
        expenses_qs = self.get_queryset()
        total_expenses = expenses_qs.aggregate(Sum('amount'))['amount__sum'] or 0
        context['total_expenses'] = total_expenses
        
        income_qs = Income.objects.filter(user=self.request.user)
        total_income = income_qs.aggregate(Sum('amount'))['amount__sum'] or 0
        context['total_income'] = total_income
        context['net_balance'] = total_income - total_expenses

        # Category Chart Data
        category_expenses = expenses_qs.values('category__name', 'category__color').annotate(total=Sum('amount')).order_by('total')
        context['category_labels'] = [entry['category__name'] for entry in category_expenses if entry['category__name']]
        context['category_data'] = [float(entry['total']) for entry in category_expenses if entry['category__name']]
        context['category_colors'] = [entry['category__color'] for entry in category_expenses if entry['category__name']]
        
        # Trend Chart Data (Last 30 days)
        from django.db.models.functions import TruncDate
        last_30_days = timezone.now().date() - timedelta(days=30)
        daily_trend = expenses_qs.filter(date__gte=last_30_days)\
            .annotate(day=TruncDate('date'))\
            .values('day')\
            .annotate(total=Sum('amount'))\
            .order_by('day')
            
        context['trend_labels'] = [entry['day'].strftime('%Y-%m-%d') for entry in daily_trend]
        context['trend_data'] = [float(entry['total']) for entry in daily_trend]
        
        return context

class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    success_url = reverse_lazy('expense-list')
    template_name = 'expenses/expense_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['expenses/partials/expense_form_modal.html']
        return ['expenses/expense_form.html']

    def form_valid(self, form):
        form.instance.user = self.request.user
        self.object = form.save()
        
        if self.request.headers.get('HX-Request'):
             # Return just the new row to prepend to the table, or triggers a refresh
             # For simplicity, we can return a trigger to refresh the list
             from django.http import HttpResponse
             response = HttpResponse(status=204)
             response['HX-Trigger'] = 'expenseListUpdated'
             return response
             
        return super().form_valid(form)

class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    model = Expense
    form_class = ExpenseForm
    success_url = reverse_lazy('expense-list')
    template_name = 'expenses/expense_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
    model = Expense
    success_url = reverse_lazy('expense-list')
    template_name = 'expenses/expense_confirm_delete.html'

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

# --- Income Views ---

class IncomeListView(LoginRequiredMixin, ListView):
    model = Income
    template_name = 'expenses/income_list.html'
    context_object_name = 'incomes'
    ordering = ['-date']

    def get_queryset(self):
        return Income.objects.filter(user=self.request.user).order_by('-date')

class IncomeCreateView(LoginRequiredMixin, CreateView):
    model = Income
    form_class = IncomeForm
    success_url = reverse_lazy('income-list')
    template_name = 'expenses/income_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['expenses/partials/income_form_modal.html']
        return ['expenses/income_form.html']

    def form_valid(self, form):
        form.instance.user = self.request.user
        self.object = form.save()
        
        if self.request.headers.get('HX-Request'):
            from django.http import HttpResponse
            response = HttpResponse(status=204)
            response['HX-Trigger'] = 'incomeAdded'
            return response
            
        return super().form_valid(form)

class IncomeUpdateView(LoginRequiredMixin, UpdateView):
    model = Income
    form_class = IncomeForm
    success_url = reverse_lazy('income-list')
    template_name = 'expenses/income_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        return Income.objects.filter(user=self.request.user)

class IncomeDeleteView(LoginRequiredMixin, DeleteView):
    model = Income
    success_url = reverse_lazy('income-list')
    template_name = 'expenses/income_confirm_delete.html'

    def get_queryset(self):
        return Income.objects.filter(user=self.request.user)


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'expenses/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(models.Q(user=None) | models.Q(user=self.request.user))

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('dashboard') 
    template_name = 'expenses/category_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

# --- Budget Views ---

class BudgetListView(LoginRequiredMixin, ListView):
    model = Budget
    template_name = 'expenses/budget_list.html'
    context_object_name = 'budgets'

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calculate spending vs budget
        budgets = self.get_queryset()
        budget_data = []
        for budget in budgets:
            spent = Expense.objects.filter(
                user=self.request.user, 
                category=budget.category,
                date__range=[budget.start_date, budget.end_date]
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            
            progress = (spent / budget.amount) * 100 if budget.amount > 0 else 0
            budget_data.append({
                'budget': budget,
                'spent': spent,
                'progress': min(progress, 100),
                'is_over': spent > budget.amount
            })
        context['budget_data'] = budget_data
        return context

class BudgetCreateView(LoginRequiredMixin, CreateView):
    model = Budget
    form_class = BudgetForm
    success_url = reverse_lazy('budget-list')
    template_name = 'expenses/budget_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class BudgetUpdateView(LoginRequiredMixin, UpdateView):
    model = Budget
    form_class = BudgetForm
    success_url = reverse_lazy('budget-list')
    template_name = 'expenses/budget_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

class BudgetDeleteView(LoginRequiredMixin, DeleteView):
    model = Budget
    success_url = reverse_lazy('budget-list')
    template_name = 'expenses/budget_confirm_delete.html'

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

# --- Reports Views ---

import csv
from django.http import HttpResponse

class ReportsView(LoginRequiredMixin, ListView):
    model = Expense
    template_name = 'expenses/reports.html'
    context_object_name = 'expenses'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expenses = Expense.objects.filter(user=self.request.user)
        
        # Heatmap Data (YYYY-MM-DD -> Count/Amount)
        from django.db.models.functions import TruncDate
        daily_stats = expenses.annotate(day=TruncDate('date'))\
            .values('day')\
            .annotate(count=models.Count('id'), total=Sum('amount'))\
            .order_by('day')
            
        heatmap_data = {}
        for entry in daily_stats:
            heatmap_data[entry['day'].strftime('%Y-%m-%d')] = float(entry['total'])
            
        context['heatmap_data'] = heatmap_data
        
        # Monthly Comparison (This Year)
        from django.db.models.functions import TruncMonth
        monthly_stats = expenses.filter(date__year=timezone.now().year)\
            .annotate(month=TruncMonth('date'))\
            .values('month')\
            .annotate(total=Sum('amount'))\
            .order_by('month')
            
        context['monthly_labels'] = [entry['month'].strftime('%B') for entry in monthly_stats]
        context['monthly_data'] = [float(entry['total']) for entry in monthly_stats]
        
        return context

def export_expenses_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Title', 'Category', 'Amount', 'Description'])

    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    for expense in expenses:
        category_name = expense.category.name if expense.category else 'Uncategorized'
        writer.writerow([expense.date, expense.title, category_name, expense.amount, expense.description])

    return response
