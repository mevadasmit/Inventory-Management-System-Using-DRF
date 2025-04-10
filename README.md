# 🏥 Hospital Inventory Management System – DRF + JWT + PostgreSQL

A full-featured, role-based inventory tracking and request/return management system built using Django REST Framework and PostgreSQL, tailored specifically for hospital environments. It supports role-based workflows for Nurses, Suppliers, and Inventory Managers, with secure JWT authentication.

---

## 🚀 Features

### 🔐 Authentication & JWT Security
- User Registration, Login, Logout with JWT
- Password Reset, Change Password, Forgot Password
- Profile Update & Access with token-based authentication
- Role-based permissions (Admin, Nurse, Supplier, Inventory Manager)

### 📦 Inventory & Stock Management
- Supplier-side product and category CRUD
- Org-level inventory visibility for managers
- Returnable item tracking and stock restoration on confirmed returns

### 🧾 Requests & Approvals
- Nurses create requests for inventory
- Inventory Managers can approve, reject, or process returns
- Emergency request auto-approval with validation

### 🛒 Orders & Cart System
- Nurses manage cart, create orders from cart
- Supplier updates delivery status
- Inventory Manager confirms fulfillment, triggering stock updates

---

## 🛠️ Tech Stack

- **Backend**: Django, Django REST Framework (DRF)
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: PostgreSQL
- **Utilities**: Django signals, crispy-forms, custom permissions

---

## 🔐 User Roles

| Role              | Permissions |
|-------------------|-------------|
| Admin             | Full user/org management |
| Nurse             | Request inventory, manage cart, create orders |
| Supplier          | Manage products, update order delivery |
| Inventory Manager | Approve/reject requests, confirm orders, manage inventory |

---

## 📦 API Highlights

### Authentication (JWT)
- `POST /api/token/` – Obtain JWT token
- `POST /api/token/refresh/` – Refresh JWT token
- `POST /user-register/`, `/user-login/`, `/forgot-password/`
- `PUT /user-profile-update/`, `GET /get-user-profile/`

### Request & Return Flow
- `POST /create-new-request/`, `PUT /approve-request/`, `PUT /reject-request/`
- `GET /returnable-inventory/`, `POST /return-inventory/`, `GET /return-status/`

### Order & Cart
- `POST /add-to-cart/`, `PUT /update-quantity/`, `POST /create-order/`
- `PUT /order-update-status-delivered/`, `PUT /order-update-status-confirmed/`

### Product & Inventory
- `POST /add-products/`, `GET /list-of-products/`, `PUT /update-product/`
- `GET /available-inventory/`, `GET /supplier-inventory/`

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.9+
- PostgreSQL
- pip, virtualenv

---

### 1️⃣ Clone the Repository

```bash
git clone
cd inventory-management-system

## Create Virtual Environment
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate

##  Install Dependencies
pip install -r requirements.txt

## PostgreSQL Configuration
CREATE DATABASE hospital_inventory;
CREATE USER inv_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE hospital_inventory TO inv_user;


## Migrate and Create Superuser

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser


## Run the Server
python manage.py runserver

##  JWT Authentication Setup
pip install djangorestframework-simplejwt




