from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.core.paginator import Paginator

from .models import Leave
from accounts.models import Notification

from datetime import datetime, date, timedelta
import csv

# 📊 Charts
from django.db.models.functions import TruncMonth
from django.db.models import Count

# 📄 PDF
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet


# =========================================
# 👤 PROFILE
# =========================================
@login_required
def profile(request):
    return render(request, 'accounts/profile.html')


# =========================================
# 📝 APPLY LEAVE
# =========================================
@login_required
def apply_leave(request):

    if request.method == 'POST':

        leave_type = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')

        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

        except:
            messages.error(request, "Invalid date format")
            return redirect('apply_leave')

        # ✅ Validation
        if start_date_obj > end_date_obj:
            messages.error(request, "End date must be after start date")
            return redirect('apply_leave')

        if start_date_obj < date.today():
            messages.error(request, "Start date cannot be in past")
            return redirect('apply_leave')

        days = (end_date_obj - start_date_obj).days + 1

        profile = request.user.profile

        # ✅ Balance check
        if profile.leave_balance < days:
            messages.error(request, "Insufficient leave balance")
            return redirect('apply_leave')

        # ✅ Conflict check
        conflict = Leave.objects.filter(
            user=request.user,
            start_date__lte=end_date_obj,
            end_date__gte=start_date_obj
        ).exists()

        if conflict:
            messages.error(request, "You already applied in this range")
            return redirect('apply_leave')

        # 🤖 AUTO APPROVAL
        status = 'Pending'

        if leave_type == "Sick" and days <= 2:
            status = 'Approved'

            profile.leave_balance -= days
            profile.save()

        # ✅ Save Leave
        leave = Leave.objects.create(
            user=request.user,
            leave_type=leave_type,
            start_date=start_date_obj,
            end_date=end_date_obj,
            reason=reason,
            status=status
        )

        # 🔔 Notification
        Notification.objects.create(
            user=request.user,
            message=f"Leave applied ({status})"
        )

        # 📩 Email
        if request.user.email:
            send_mail(
                'Leave Application Submitted',
                f'Your leave request is {status}.',
                'admin@gmail.com',
                [request.user.email],
                fail_silently=True
            )

        messages.success(request, f"Leave applied ({status})!")
        return redirect('my_leaves')

    return render(request, 'leave/apply_leave.html')


# =========================================
# 📋 MY LEAVES
# =========================================
@login_required
def my_leaves(request):

    # ✅ Latest leave first
    leaves = Leave.objects.filter(
        user=request.user
    ).order_by('-start_date', '-id')

    return render(request, 'leave/my_leaves.html', {
        'leaves': leaves
    })


# =========================================
# ❌ CANCEL LEAVE
# =========================================
@login_required
def cancel_leave(request, id):

    leave = get_object_or_404(
        Leave,
        id=id,
        user=request.user
    )

    if leave.status != 'Pending':
        messages.error(request, "Only pending leave can be cancelled")
        return redirect('my_leaves')

    leave.status = 'Cancelled'
    leave.save()

    Notification.objects.create(
        user=request.user,
        message="Leave cancelled"
    )

    messages.success(request, "Leave cancelled successfully!")
    return redirect('my_leaves')


# =========================================
# 👨‍💼 ADMIN VIEW LEAVES
# =========================================
@login_required
def view_leaves(request):

    if request.user.profile.role != 'admin':
        return redirect('staff_dashboard')

    # ✅ Latest first
    leaves = Leave.objects.all().order_by('-start_date', '-id')

    # 🔍 Search
    q = request.GET.get('q')

    if q:
        leaves = leaves.filter(
            user__username__icontains=q
        )

    # 🎯 Filter
    status = request.GET.get('status')

    if status:
        leaves = leaves.filter(status=status)

    # 📄 Pagination
    paginator = Paginator(leaves, 5)

    page = request.GET.get('page')

    leaves = paginator.get_page(page)

    return render(request, 'leave/view_leaves.html', {
        'leaves': leaves
    })


# =========================================
# ✅ APPROVE
# =========================================
@login_required
def approve_leave(request, id):

    if request.user.profile.role != 'admin':
        return redirect('staff_dashboard')

    leave = get_object_or_404(Leave, id=id)

    if leave.status != 'Pending':
        messages.warning(request, "Already processed")
        return redirect('view_leaves')

    profile = leave.user.profile

    days = leave.total_days

    if profile.leave_balance < days:
        messages.error(request, "Insufficient balance")
        return redirect('view_leaves')

    # ✅ Update balance
    profile.leave_balance -= days
    profile.save()

    leave.status = 'Approved'
    leave.admin_note = "Approved by admin"
    leave.save()

    # 🔔 Notification
    Notification.objects.create(
        user=leave.user,
        message="Your leave was approved"
    )

    # 📩 Email
    if leave.user.email:
        send_mail(
            'Leave Approved',
            'Your leave request has been approved.',
            'admin@gmail.com',
            [leave.user.email],
            fail_silently=True
        )

    messages.success(request, "Leave approved successfully!")
    return redirect('view_leaves')


# =========================================
# ❌ REJECT
# =========================================
@login_required
def reject_leave(request, id):

    if request.user.profile.role != 'admin':
        return redirect('staff_dashboard')

    leave = get_object_or_404(Leave, id=id)

    if leave.status != 'Pending':
        messages.warning(request, "Already processed")
        return redirect('view_leaves')

    leave.status = 'Rejected'
    leave.admin_note = "Rejected by admin"
    leave.save()

    # 🔔 Notification
    Notification.objects.create(
        user=leave.user,
        message="Your leave was rejected"
    )

    # 📩 Email
    if leave.user.email:
        send_mail(
            'Leave Rejected',
            'Your leave request has been rejected.',
            'admin@gmail.com',
            [leave.user.email],
            fail_silently=True
        )

    messages.error(request, "Leave rejected")
    return redirect('view_leaves')


# =========================================
# 📄 EXPORT CSV
# =========================================
@login_required
def export_leaves_csv(request):

    if request.user.profile.role != 'admin':
        return redirect('staff_dashboard')

    leaves = Leave.objects.all().order_by('-start_date')

    status = request.GET.get('status')

    if status:
        leaves = leaves.filter(status=status)

    response = HttpResponse(content_type='text/csv')

    response['Content-Disposition'] = (
        'attachment; filename="leaves.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        'User',
        'Type',
        'Start',
        'End',
        'Days',
        'Status'
    ])

    for leave in leaves:

        writer.writerow([
            leave.user.username,
            leave.leave_type,
            leave.start_date,
            leave.end_date,
            leave.total_days,
            leave.status
        ])

    return response


# =========================================
# 📄 EXPORT PDF
# =========================================
@login_required
def export_leaves_pdf(request):

    if request.user.profile.role != 'admin':
        return redirect('staff_dashboard')

    leaves = Leave.objects.all().order_by('-start_date')

    response = HttpResponse(content_type='application/pdf')

    response['Content-Disposition'] = (
        'attachment; filename="leaves.pdf"'
    )

    doc = SimpleDocTemplate(response, pagesize=A4)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph("Leave Report", styles['Title'])
    )

    elements.append(Spacer(1, 12))

    data = [[
        'User',
        'Type',
        'Start',
        'End',
        'Days',
        'Status'
    ]]

    for leave in leaves:

        data.append([
            leave.user.username,
            leave.leave_type,
            str(leave.start_date),
            str(leave.end_date),
            leave.total_days,
            leave.status
        ])

    table = Table(data)

    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)
    ]))

    elements.append(table)

    doc.build(elements)

    return response


# =========================================
# 📅 CALENDAR
# =========================================
@login_required
def leave_calendar(request):

    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return render(request, 'leave/leave_calendar.html')

    leaves = Leave.objects.all()

    events = []

    for l in leaves:

        events.append({
            'title': l.user.username,

            'start': l.start_date.strftime('%Y-%m-%d'),

            'end': (
                l.end_date + timedelta(days=1)
            ).strftime('%Y-%m-%d'),

            'color': {
                'Pending': '#ffc107',
                'Approved': '#198754',
                'Rejected': '#dc3545',
                'Cancelled': '#6c757d'
            }.get(l.status),

            'extendedProps': {
                'status': l.status,
                'reason': l.reason
            }
        })

    return JsonResponse(events, safe=False)


# =========================================
# 📊 LEAVE HISTORY
# =========================================
@login_required
def leave_history(request):

    leaves = Leave.objects.filter(
        user=request.user
    ).order_by('-start_date', '-id')

    total = leaves.count()

    approved = leaves.filter(
        status='Approved'
    ).count()

    rejected = leaves.filter(
        status='Rejected'
    ).count()

    pending = leaves.filter(
        status='Pending'
    ).count()

    cancelled = leaves.filter(
        status='Cancelled'
    ).count()

    return render(request, 'leave/history.html', {
        'leaves': leaves,
        'total': total,
        'approved': approved,
        'rejected': rejected,
        'pending': pending,
        'cancelled': cancelled
    })