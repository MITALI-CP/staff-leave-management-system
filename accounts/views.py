from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Profile, Notification
from leave.models import Leave


# 🔹 HOME
def home(request):
    return render(request, 'home.html')


# 🔹 REGISTER
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if not username or not password or not role:
            messages.error(request, "All fields are required!")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('register')

        user = User.objects.create_user(username=username, password=password)

        # Default leave balance
        Profile.objects.create(user=user, role=role, leave_balance=20)

        messages.success(request, "Account created successfully!")
        return redirect('login')

    return render(request, 'register.html')


# 🔹 LOGIN
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            profile = Profile.objects.filter(user=user).first()

            if not profile:
                messages.error(request, "Profile not found!")
                return redirect('login')

            if profile.role == 'admin':
                return redirect('admin_dashboard')
            else:
                return redirect('staff_dashboard')

        else:
            messages.error(request, "Invalid username or password!")

    return render(request, 'login.html')


# 🔹 ADMIN DASHBOARD
@login_required
def admin_dashboard(request):
    profile = request.user.profile

    if profile.role != 'admin':
        return redirect('staff_dashboard')

    total = Leave.objects.count()
    pending = Leave.objects.filter(status='Pending').count()
    approved = Leave.objects.filter(status='Approved').count()
    rejected = Leave.objects.filter(status='Rejected').count()
    cancelled = Leave.objects.filter(status='Cancelled').count()

    return render(request, 'admin_dashboard.html', {
        'total': total,
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
        'cancelled': cancelled,
    })


# 🔹 STAFF DASHBOARD
@login_required
def staff_dashboard(request):
    profile = request.user.profile

    total = 20
    remaining = profile.leave_balance
    used = total - remaining

    pending = Leave.objects.filter(user=request.user, status='Pending').count()
    approved = Leave.objects.filter(user=request.user, status='Approved').count()

    # 🔔 Notifications count
    unread = Notification.objects.filter(user=request.user, is_read=False).count()

    return render(request, 'staff_dashboard.html', {
        'total': total,
        'used': used,
        'remaining': remaining,
        'pending': pending,
        'approved': approved,
        'notifications': unread
    })


# 🔔 NOTIFICATIONS PAGE
@login_required
def notifications(request):
    notes = Notification.objects.filter(user=request.user).order_by('-created_at')

    # mark all as read
    notes.update(is_read=True)

    return render(request, 'accounts/notifications.html', {
        'notes': notes
    })


# 👤 PROFILE
@login_required
def profile(request):
    return render(request, 'accounts/profile.html')


# 🔹 LOGOUT
def logout_view(request):
    logout(request)
    return redirect('home')


# 🔹 MANAGE STAFF
@login_required
def manage_staff(request):
    if request.user.profile.role != 'admin':
        return redirect('staff_dashboard')

    staff_list = User.objects.filter(profile__role='staff')
    return render(request, 'accounts/manage_staff.html', {
        'staff_list': staff_list
    })


# 🔹 ADD STAFF
@login_required
def add_staff(request):
    if request.user.profile.role != 'admin':
        return redirect('staff_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('add_staff')

        user = User.objects.create_user(username=username, password=password)
        Profile.objects.create(user=user, role='staff', leave_balance=20)

        messages.success(request, "Staff added successfully!")
        return redirect('manage_staff')

    return render(request, 'accounts/add_staff.html')


# 🔹 EDIT STAFF
@login_required
def edit_staff(request, id):
    if request.user.profile.role != 'admin':
        return redirect('staff_dashboard')

    user = get_object_or_404(User, id=id)

    if request.method == 'POST':
        new_username = request.POST.get('username')

        if User.objects.filter(username=new_username).exclude(id=user.id).exists():
            messages.error(request, "Username already exists!")
            return redirect('edit_staff', id=id)

        user.username = new_username
        user.save()

        messages.success(request, "Staff updated successfully!")
        return redirect('manage_staff')

    return render(request, 'accounts/edit_staff.html', {
        'user': user
    })


# 🔹 DELETE STAFF
@login_required
def delete_staff(request, id):
    if request.user.profile.role != 'admin':
        return redirect('staff_dashboard')

    user = get_object_or_404(User, id=id)
    user.delete()

    messages.success(request, "Staff deleted successfully!")
    return redirect('manage_staff')