from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense, MonthlyEarning
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, IntegerField
from django.views.decorators.cache import cache_control
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth
import datetime
from datetime import datetime, date
import calendar










# Create your views here.

def error_404_view(request, exception):
    return render(request, '404.html', status=404)

def index(request):
    return render(request, "index.html")

def SignupPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        errors = []
        if User.objects.filter(username=username).exists():
            errors.append("Username is already taken.")
        if User.objects.filter(email=email).exists():
            errors.append("Email is already taken.")
        if not errors:
            # Create the user
            user = User.objects.create(username=username, email=email)
            user.set_password(password)  # Use set_password method to hash the password
            user.save()
            messages.success(request, 'Account created successfully')
            return redirect('login-page')  # Redirect to  a login view
        else:
            for error in errors:
                messages.error(request, error)
    return render(request, 'Authentication/signup.html')



def LoginPage(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            # Authenticate using email and password
            authenticated_user = authenticate(request, username=user.username, password=password)
            if authenticated_user is not None:
                login(request, authenticated_user)
                # Set session variables
                request.session['email'] = user.email
                return redirect('home')  # Redirect to homepage
            else:
                messages.error(request, 'Invalid email or password')
        except User.DoesNotExist:
            messages.error(request, 'Email does not exist!')
    return render(request, "Authentication/login.html")



def logout(request):
     if 'email' in request.session:
        del request.session['email']
        logout(request)
        return redirect('home')  # Redirect to home page


def home_view(request):
    if 'email' in request.session:
        email = request.session['email']
        user = User.objects.get(email=email)
        expenseData = Expense.objects.filter(user_id=user.id)
        total_expense = expenseData.aggregate(total=Sum('amount'))['total'] or 0
        try:
            # Filter MonthlyEarning objects for the current month and user
            current_month = datetime.now().month
            month_name = calendar.month_name[current_month]
            monthly_earnings = MonthlyEarning.objects.filter(
            user_id=user.id,
            month=month_name
            )
            print(monthly_earnings)
        except MonthlyEarning.DoesNotExist:
            Earning_Monthly = None
        return render(request, 'base.html', {'email': email, "expenseData": expenseData, "total_expense": total_expense, "monthly_earnings": monthly_earnings})

    if "email" not in request.session:
         return render(request, 'base.html')
    else:
        return redirect('authentication/login')




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def add_monthly_earning(request):
    if 'email' not in request.session:
        return redirect('login-page')
    
    user = User.objects.get(email=request.session['email'])
    
    if request.method == 'POST':
        month = request.POST.get('month')
        amount = request.POST.get('amount')
        
        # Validate data
        if month and amount:
            try:
                amount = float(amount)
                
                # Check if there is already an entry for this user and month
                try:
                    monthly_earning = MonthlyEarning.objects.get(user=user, month=month)
                    monthly_earning.amount = amount
                    monthly_earning.save()
                    messages.success(request, 'Monthly earning updated successfully.')
                except MonthlyEarning.DoesNotExist:
                    # Create new entry if it doesn't exist
                    MonthlyEarning.objects.create(user=user, month=month, amount=amount)
                    messages.success(request, 'Monthly earning added successfully.')

                return redirect('home')  # Redirect to success page or another URL

            except ValueError:
                messages.error(request, "Amount must be a valid number.")
        else:
            messages.error(request, "All fields are required.")
    
    return render(request, 'add_monthly_earning.html')  # Render the form template if not a POST request or if validation fails



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def expensesForm(request):
    if "email" not in request.session:
        return redirect('authentication/login')
    if 'email' in request.session:
        if request.method == 'POST':
            amount = request.POST.get('amount')
            description = request.POST.get('description')
            category = request.POST.get('category')
            date = request.POST.get('date')

            # Create and save the expense object
            expense = Expense(user=request.user, amount=amount, description=description, category=category, date=date)
            expense.save()
            return redirect('home')  # Redirect to the home page after saving
    
        return render(request, 'expense-form.html')
    


def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == "POST":
        # Get data from POST request
        amount = request.POST.get('amount')
        category = request.POST.get('category')
        description = request.POST.get('description')
        date = request.POST.get('date')
        # Update only the fields that are provided in the POST data
        if amount:
            expense.amount = amount
        if category:
            expense.category = category
        if description:
            expense.description = description
        if date:
            expense.date = date
        # Validate the data and save the expense object
        try:
            expense.save()
            messages.success(request, 'Expense updated successfully.')
            return redirect('home')
        except Exception as e:
            messages.error(request, f'Failed to update expense: {str(e)}')

    # Render the edit form with current expense data
    return render(request, 'expense-edit-form.html', {'expense': expense})


def expense_delete(request, pk):
    obj = get_object_or_404(Expense, pk=pk)
    if request.method == 'GET':
        obj.delete()
        return redirect('home')
    

def pie_chart_data(request):
    if 'email' in request.session:
        user = User.objects.get(email=request.session['email'])
        category_data = Expense.objects.filter(user_id=user.id).values('description').annotate(total_amount=Sum('amount'))
        data = [{'description': item['description'], 'total_amount': item['total_amount']} for item in category_data]
        return JsonResponse(data={
            'data': data,
        })
    else:
        return JsonResponse(data={
            'error': 'User not logged in.'
        }, status=401)


def line_chart_data(request):
    if 'email' in request.session:
        user = User.objects.get(email=request.session['email'])
        
        # Calculate expenses aggregated by month for the logged-in user
        expenses_by_month = Expense.objects.filter(
            user_id=user.id,
            date__year=2024  # Adjust as per your filtering needs
        ).annotate(
            month=ExtractMonth('date')
        ).values('month').annotate(
            total_amount=Sum('amount', output_field=IntegerField())
        )

        # Prepare labels (months) and data (total amounts)
        labels = []
        data = []

        # Generate labels for each month of 2024

        current_date = date.today()
        for i in range(12):
            month_label = current_date.strftime('%b %Y')
            labels.append(month_label)
            current_date = current_date.replace(month=current_date.month + 1 if current_date.month < 12 else 1)

        # Initialize data array with zeros for the months of 2024
        data = [0] * 12

        # Populate data array with total amounts by month
        for expense in expenses_by_month:
            month_index = expense['month'] - 1  # January is 0, December is 11
            if 0 <= month_index < 12:
                data[month_index] = float(expense['total_amount'])

        return JsonResponse({
            'labels': labels,
            'data': data,
        })
    else:
        return JsonResponse(data={
            'error': 'User not logged in.'
        }, status=401)
    

def expenseTableData(request):
    if 'email' not in request.session:
        return redirect("login-page")
    email = request.session['email']
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return redirect("login-page")
    expenseData = Expense.objects.filter(user_id=user.id)
    return render(request, "expense-table-data.html", {"expenseData": expenseData})

def salarySummaryData(request):
    if 'email' not in request.session:
        return redirect("login-page")
    email = request.session['email']
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return redirect("login-page")
    totalSalary = MonthlyEarning.objects.filter(user_id=user.id)
    return render(request, "my_income_total.html", {"totalSalary": totalSalary})


