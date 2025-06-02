from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import UserSignupForm, AdminSignupForm, ProfileForm, BookForm
from .models import Book, BookRentRequest
from django.http import HttpResponse
import csv
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import requests


def user_signup(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_staff = False  # Regular user
            user.save()
            messages.success(request, "User signup successful. Please log in.")
            return redirect('user_login')
    else:
        form = UserSignupForm()
    return render(request, 'account/user_signup.html', {'form': form})

def admin_signup(request):
    if request.method == 'POST':
        form = AdminSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_staff = True  # Admin user
            user.save()
            messages.success(request, "Admin signup successful. Please log in.")
            return redirect('admin_login')
    else:
        form = AdminSignupForm()
    return render(request, 'account/admin_signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_staff:
                auth_login(request, user)
                return redirect('user_dashboard')
            else:
                messages.error(request, "You do not have user access.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'account/user_login.html', {'form': form})

def admin_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                auth_login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, "You do not have admin access.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'account/admin_login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('user_login')  

@login_required
def user_dashboard(request):

    query = request.GET.get('q', '')

    books = Book.objects.all()

    if query:
        books = books.filter(name__icontains=query)
        
    rent_requests = BookRentRequest.objects.filter(user=request.user, status__in=['pending', 'accepted', 'return_pending'])

    rented_books = [req.book for req in rent_requests if req.status in ['accepted', 'return_pending']]

    if request.method == 'POST':
        if 'rent_book_id' in request.POST:
            book = get_object_or_404(Book, id=request.POST['rent_book_id'])
            if not book.is_rented and not BookRentRequest.objects.filter(user=request.user, book=book, status__in=['pending', 'accepted', 'return_pending']).exists():
                BookRentRequest.objects.create(user=request.user, book=book)
            return redirect('user_dashboard')
        if 'return_book_id' in request.POST:
            book = get_object_or_404(Book, id=request.POST['return_book_id'])

            req = BookRentRequest.objects.filter(user=request.user, book=book, status='accepted').first()
            if req:
                req.status = 'return_pending'
                req.save()
            return redirect('user_dashboard')

    return render(request, 'account/user_dashboard.html', {
        'books': books,
        'rented_books': rented_books,
        'rent_requests': rent_requests,
    })


@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    rent_requests = BookRentRequest.objects.filter(status='pending')
    return_requests = BookRentRequest.objects.filter(status='return_pending')
    all_history = BookRentRequest.objects.all().select_related('user', 'book').order_by('-created_at')
    book_form = BookForm()

    if request.method == 'POST':
        # Add book
        if 'add_book' in request.POST:
            book_form = BookForm(request.POST, request.FILES)
            if book_form.is_valid():
                book_form.save()
                return redirect('admin_dashboard')
        # Download history
        elif 'download_history' in request.POST:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="user_borrow_history.csv"'
            writer = csv.writer(response)
            writer.writerow(['User', 'Book', 'Status', 'Requested At'])
            for req in all_history:
                writer.writerow([
                    req.user.email,
                    req.book.name,
                    req.get_status_display(),
                    req.created_at.strftime('%Y-%m-%d %H:%M')
                ])
            return response
        # Accept rent/return
        elif 'accept_rent_id' in request.POST:
            req = get_object_or_404(BookRentRequest, id=request.POST['accept_rent_id'])
            req.status = 'accepted'
            req.book.is_rented = True
            req.book.save()
            req.save()
            return redirect('admin_dashboard')
        elif 'accept_return_id' in request.POST:
            req = get_object_or_404(BookRentRequest, id=request.POST['accept_return_id'])
            req.status = 'returned'
            req.book.is_rented = False
            req.book.save()
            req.save()
            return redirect('admin_dashboard')

    return render(request, 'account/admin_dashboard.html', {
        'rent_requests': rent_requests,
        'return_requests': return_requests,
        'all_history': all_history,
        'book_form': book_form,
    })


@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = ProfileForm(instance=user)
    return render(request, 'account/profile.html', {'form': form, 'user': user})

'''
Email: mainak@mainak.mainakdey
Name: Mainak
Phone number: 9679259855
Password: 1234
'''


OLLAMA_URL = 'http://localhost:11434/api/generate'  # Ollama API endpoint

@csrf_exempt  # Simplify CSRF for beginners (not safe for production)
def chat(request):
    response_lines = []
    prompt_text = ''

    if request.method == 'POST':
        prompt_text = request.POST.get('prompt')
        
        if prompt_text:
            # Prepare payload
            payload = {
                "model": "granite3-moe",
                "prompt": prompt_text,
                "stream": False  # We'll split into lines later
            }
            try:
                # Send request to Ollama
                r = requests.post(OLLAMA_URL, json=payload)
                data = r.json()
                
                if 'response' in data:
                    full_response = data['response']
                    response_lines = full_response.strip().split('\n')
                else:
                    response_lines = ["[Error] No response from Ollama."]
            except Exception as e:
                response_lines = [f"[Error] {str(e)}"]

    return render(request, 'account/chat.html', {
        'prompt': prompt_text,
        'response_lines': response_lines,
    })
