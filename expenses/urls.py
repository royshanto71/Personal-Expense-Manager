from django.urls import path
from . import views

urlpatterns = [
    path('', views.ExpenseListView.as_view(), name='dashboard'), # Dashboard is the home of expenses
    path('expenses/', views.ExpenseListView.as_view(), name='expense-list'),
    path('expense/new/', views.ExpenseCreateView.as_view(), name='expense-create'),
    path('expense/<int:pk>/update/', views.ExpenseUpdateView.as_view(), name='expense-update'),
    path('expense/<int:pk>/delete/', views.ExpenseDeleteView.as_view(), name='expense-delete'),
    
    # Income URLs
    path('income/', views.IncomeListView.as_view(), name='income-list'),
    path('income/new/', views.IncomeCreateView.as_view(), name='income-create'),
    path('income/<int:pk>/update/', views.IncomeUpdateView.as_view(), name='income-update'),
    path('income/<int:pk>/delete/', views.IncomeDeleteView.as_view(), name='income-delete'),

    # Budget URLs
    path('budgets/', views.BudgetListView.as_view(), name='budget-list'),
    path('budget/new/', views.BudgetCreateView.as_view(), name='budget-create'),
    path('budget/<int:pk>/update/', views.BudgetUpdateView.as_view(), name='budget-update'),
    path('budget/<int:pk>/delete/', views.BudgetDeleteView.as_view(), name='budget-delete'),

    # Reports
    path('reports/', views.ReportsView.as_view(), name='reports'),
    path('export/', views.export_expenses_csv, name='export-csv'),

    path('category/new/', views.CategoryCreateView.as_view(), name='category-create'),
]
