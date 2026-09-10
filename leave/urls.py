from django.urls import path
from . import views

urlpatterns = [
    # 🔹 Apply + View
    path('apply/', views.apply_leave, name='apply_leave'),
    path('my-leaves/', views.my_leaves, name='my_leaves'),
    path('view/', views.view_leaves, name='view_leaves'),

    # 🔹 Admin Actions
    path('approve/<int:id>/', views.approve_leave, name='approve_leave'),
    path('reject/<int:id>/', views.reject_leave, name='reject_leave'),

    # 🔹 Staff Action
    path('cancel/<int:id>/', views.cancel_leave, name='cancel_leave'),

    # 🔹 Export Features
    path('export/csv/', views.export_leaves_csv, name='export_leaves'),      # CSV
    path('export/pdf/', views.export_leaves_pdf, name='export_leaves_pdf'),  # PDF

    # 🔹 Calendar Feature
    path('calendar/', views.leave_calendar, name='leave_calendar'),
    path('profile/', views.profile, name='profile'),
]