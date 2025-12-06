from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Expense, Category
from .forms import ExpenseForm, CategoryForm
from django.db.models import Sum

class ExpenseListView(LoginRequiredMixin, ListView):
    model = Expense
    template_name = 'expenses/expense_list.html'
    context_object_name = 'expenses'
    ordering = ['-date']

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expenses = self.get_queryset()
        context['total_expenses'] = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

        # Chart Data
        category_expenses = expenses.values('category__name').annotate(total=Sum('amount')).order_by('total')
        context['category_labels'] = [entry['category__name'] for entry in category_expenses if entry['category__name']]
        context['category_data'] = [float(entry['total']) for entry in category_expenses if entry['category__name']]
        
        return context

class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    success_url = reverse_lazy('expense-list')
    template_name = 'expenses/expense_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    model = Expense
    form_class = ExpenseForm
    success_url = reverse_lazy('expense-list')
    template_name = 'expenses/expense_form.html'

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
    model = Expense
    success_url = reverse_lazy('expense-list')
    template_name = 'expenses/expense_confirm_delete.html'

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'expenses/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        # Show global (null user) and user specific categories
        return Category.objects.filter(models.Q(user=None) | models.Q(user=self.request.user))

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('expense-list') # Or category-list
    template_name = 'expenses/category_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
