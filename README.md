# 🏢 Staff Leave Management System

> A full-stack web application designed to simplify and manage staff leave requests through a centralized Django-based system.

## 🌟 Overview

The **Staff Leave Management System** is a database-driven web application developed using **Python and Django**.

The application provides separate workflows for staff and administrators, allowing staff members to manage their leave requests while administrators can review and take action on those requests.

The project focuses on **authentication, CRUD operations, database management, role-based workflows, and responsive web interfaces**.

---

## 🚀 Key Features

### 👤 Staff Management

- Staff registration and login
- Staff profile management
- Staff dashboard
- View personal leave information

### 📝 Leave Management

- Submit leave requests
- View submitted leave requests
- Manage leave information
- Track leave status

### 👨‍💼 Admin Management

- Admin dashboard
- View staff leave requests
- Approve or reject leave requests
- Manage staff-related information

### 🔔 Additional Functionality

- Notification functionality
- Leave balance management
- Responsive user interface
- Database-driven data management

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| **Frontend** | HTML5, CSS3, JavaScript |
| **Backend** | Python, Django |
| **Database** | MySQL |
| **Development** | Django Templates, CRUD Operations |
| **Version Control** | Git, GitHub |


## 🏗️ Project Structure

```text
staff-leave-management-system/
│
├── accounts/               # User and staff management
├── leave/                  # Leave management functionality
├── slms_project/           # Django project configuration
├── templates/              # HTML templates
├── .gitignore              # Ignored files and folders
└── manage.py               # Django management script
```

## 🔄 Application Workflow

```text
            
            ┌─────────────────────┐
            │      User Login     │
            └──────────┬──────────┘
                       │
             ┌─────────▼─────────┐
             │  Staff Dashboard  │
             └─────────┬─────────┘
                       │
              ┌────────▼─────────┐
              │ Submit Leave     │
              │     Request      │
              └────────┬─────────┘
                       │
              ┌────────▼─────────┐
              │ Admin Dashboard  │
              └────────┬─────────┘
                       │
             ┌─────────▼─────────┐
             │  Review Request   │
             └──────┬───────┬────┘
                    │       │
                Approve    Reject
                    │       │
                    └───┬───┘
                        ▼
                  Update Status

```


## 💻 Getting Started


### 1. Clone the Repository

```bash
git clone https://github.com/MITALI-CP/staff-leave-management-system.git


```
### 2. Navigate to the Project

```bash
cd staff-leave-management-system


```
### 3. Install Django

```bash
pip install django
```

### 4. Configure the Database

Update the database configuration in:

```text
slms_project/settings.py

```
### 5. Run Database Migrations

```bash
python manage.py migrate

```
### 6. Start the Development Server

```bash
python manage.py runserver

```
### 7. Open the Application

Open your browser and visit:

```text
http://127.0.0.1:8000/
```


## 📚 What I Learned

Through this project, I gained practical experience in:

- Building web applications using Django
- Implementing CRUD operations
- Working with MySQL databases
- Creating authentication workflows
- Developing responsive frontend interfaces
- Connecting Django applications with databases
- Organizing a Django project into separate applications
- Using Git and GitHub for version control

## 🔮 Future Improvements
- REST API integration
- Email notifications for leave requests
- Advanced role-based access control
- Improved reporting and analytics
- Cloud deployment
