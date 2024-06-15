from django.contrib import admin
from django.urls import path
from app import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),  # Home page
    path("home", views.index),


    path("authentication/signup", views.SignupPage, name="signup-page"),
    path("authentication/login", views.LoginPage, name="login-page"),
    path('authentication/logout', views.logout, name='logout'),  # Add logout URL


    path('earning-monthly/', views.add_monthly_earning, name='add_monthly_earning'),

    path("expenses", views.expensesForm, name="expenses-form"),
    path('expense-edit/<int:pk>/', views.expense_edit, name='expense_edit'),
    path('expense-delete/<int:pk>/', views.expense_delete, name='expense_delete'),

    path('api/pie_chart_data/', views.pie_chart_data, name='pie_chart_data'),
    path('api/line_chart_data/', views.line_chart_data, name='line_chart_data'),

    path("expense-summary", views.expenseTableData, name="expense-summary"),
    path("salary-summary", views.salarySummaryData, name="salary-summary")

]

handler404 = views.error_404_view





