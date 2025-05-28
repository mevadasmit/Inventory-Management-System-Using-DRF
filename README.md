# 🏥 Hospital Inventory Management System – DRF + JWT + PostgreSQL + Celery + Docker

A full-featured, role-based inventory tracking and request/return management system built using Django REST Framework and PostgreSQL, tailored specifically for hospital environments. It supports role-based workflows for Nurses, Suppliers, and Inventory Managers, with secure JWT authentication, background task handling via Celery, import/export functionalities, and containerized deployment using Docker.

---

## ✨ Features

### 🔐 Authentication & JWT Security

* User Registration, Login, Logout with JWT
* Password Reset, Change Password, Forgot Password (with email notifications)
* Profile Update & Access with token-based authentication
* Role-based permissions (Admin, Nurse, Supplier, Inventory Manager)

### 📆 Inventory & Stock Management

* Supplier-side product and category CRUD
* Org-level inventory visibility for managers
* Returnable item tracking and stock restoration on confirmed returns

### 🧾 Requests & Approvals

* Nurses create requests for inventory
* Inventory Managers can approve, reject, or process returns
* Emergency request auto-approval with validation

### 🛏️ Orders & Cart System

* Nurses manage cart, create orders from cart
* Supplier updates delivery status
* Inventory Manager confirms fulfillment, triggering stock updates

### ⚙️ Background Tasks with Celery

* Email notifications for password changes
* Scheduled tasks using django-celery-beat (e.g., exporting CSV every 2 hours)

### 🗃️ Import/Export Support

* Periodic task exporting organization inventory data to CSV
* CSV logs stored in mounted Docker volume

---

## 💠 Tech Stack

* **Backend**: Django, Django REST Framework (DRF)
* **Authentication**: JWT (djangorestframework-simplejwt)
* **Database**: PostgreSQL
* **Background Tasks**: Celery, django-celery-beat, Redis
* **Containerization**: Docker, Docker Compose
* **Utilities**: Django signals, crispy-forms, custom permissions

---

## 🔐 User Roles

| Role              | Permissions                                               |
| ----------------- | --------------------------------------------------------- |
| Admin             | Full user/org management                                  |
| Nurse             | Request inventory, manage cart, create orders             |
| Supplier          | Manage products, update order delivery                    |
| Inventory Manager | Approve/reject requests, confirm orders, manage inventory |

---

## 📆 API Highlights

### Authentication (JWT)

* `POST /api/token/` – Obtain JWT token
* `POST /api/token/refresh/` – Refresh JWT token
* `POST /user-register/`, `/user-login/`, `/forgot-password/`
* `PUT /user-profile-update/`, `GET /get-user-profile/`

### Request & Return Flow

* `POST /create-new-request/`, `PUT /approve-request/`, `PUT /reject-request/`
* `GET /returnable-inventory/`, `POST /return-inventory/`, `GET /return-status/`

### Order & Cart

* `POST /add-to-cart/`, `PUT /update-quantity/`, `POST /create-order/`
* `PUT /order-update-status-delivered/`, `PUT /order-update-status-confirmed/`

### Product & Inventory

* `POST /add-products/`, `GET /list-of-products/`, `PUT /update-product/`
* `GET /available-inventory/`, `GET /supplier-inventory/`

---

## ⚙️ Setup & Installation

### 🧱 Prerequisites

* Python 3.9+
* PostgreSQL
* pip, virtualenv
* Docker & Docker Compose

### 1️⃣ Clone the Repository

```bash
git clone <repo_url>
cd inventory-management-system
```

### 2️⃣ Environment Configuration

Create a `.env` file in the project root with the following contents:

```env
# Django
SECRET_KEY=your_generated_secret_key
DEBUG=1

# Database
DATABASE_NAME=IMS_TEST
DATABASE_USER_NAME=postgres
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=db
DATABASE_PORT=5432

# Redis / Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Email
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

Also create a `docker.env` file:

```env
POSTGRES_DB=IMS_TEST
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_db_password
```

### 3️⃣ Run with Docker

```bash
docker-compose up --build
```

This will start:

* Django app (with Gunicorn)
* PostgreSQL database
* Redis server
* Celery worker
* Celery beat for scheduled tasks

Static files are collected automatically. Celery will handle background tasks and email sending.

CSV exports are stored in `/home/root491/csv_logs` (volume mounted to host).

---

### 🥪 Dev Testing Locally (Optional, Non-Docker)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 🧼 Tips

* To clean up Docker volumes/images:

```bash
docker system prune -a
```

* To view logs from Celery or beat:

```bash
docker-compose logs -f celery
```

---

## ✅ Final Setup Summary

* 🐋 Fully containerized using Docker Compose
* 🔄 Asynchronous tasks via Celery (email + periodic CSV export)
* 🗏️ Custom permission-based API for hospital roles
* 📄 Scheduled CSV export stored in volume
* 📧 Email confirmation after password change

---

## 👨‍💼 Contributors

* Smit Mevada

---

## 📜 License

MIT License
