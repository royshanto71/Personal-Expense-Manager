from django.urls import path
from . import views

urlpatterns = [
    path('', views.ExpenseListView.as_view(), name='dashboard'), # Dashboard is the home of expenses
    path('expenses/', views.ExpenseListView.as_view(), name='expense-list'),
    path('expense/new/', views.ExpenseCreateView.as_view(), name='expense-create'),
    path('expense/<int:pk>/update/', views.ExpenseUpdateView.as_view(), name='expense-update'),
    path('expense/<int:pk>/delete/', views.ExpenseDeleteView.as_view(), name='expense-delete'),
    path('category/new/', views.CategoryCreateView.as_view(), name='category-create'),
]
