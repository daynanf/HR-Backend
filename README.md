# HR & Employee Management Backend

A production-ready HR management system built with Django, Django REST Framework, and Domain-Driven Design (DDD).

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Setup & Installation](#setup--installation)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Business Rules](#business-rules)
- [Development](#development)
- [Contributing](#contributing)

---

## 📖 Overview

This is a complete HR & Employee Management backend system built following **Domain-Driven Design (DDD)** principles. The system manages:

- **Employees** - Full CRUD with search, filtering, and bulk operations
- **Departments** - Management with deactivation rules
- **Leave Requests** - Submission, approval, rejection, and on-leave tracking

The architecture ensures business logic is isolated, testable, and maintainable.

---

## 🏗️ Architecture

The project follows a strict **4-layer DDD architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│ PRESENTATION LAYER                                          │
│ DRF Views, Serializers, URL Configs, Filters                │
│ - Thin HTTP layer                                           │
│ - Calls application layer only                              │
│ - No ORM access                                             │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ APPLICATION LAYER                                           │
│ Commands, Queries, Use Cases                                │
│ - Orchestrates domain objects and ports                     │
│ - No HTTP concerns                                          │
│ - No ORM access                                             │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ DOMAIN LAYER                                                │
│ Entities, Value Objects, Domain Services, Ports (ABC)      │
│ - Pure business logic                                       │
│ - NO Django imports                                         │
│ - NO DRF imports                                            │
│ - NO database concerns                                      │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ INFRASTRUCTURE LAYER                                        │
│ ORM Models, Repositories, Mappers                           │
│ - Implements port interfaces                                │
│ - Handles persistence                                       │
│ - Converts between ORM and domain entities                  │
└─────────────────────────────────────────────────────────────┘
```

### Architecture Rules (Non-Negotiable)

1. Domain entities are plain Python dataclasses - zero Django/DRF imports
2. Port interfaces are abstract base classes (ABC) in domain/ports/
3. Repository implementations live in infrastructure/ and implement ports
4. Views NEVER import from infrastructure - only application layer
5. Commands/queries NEVER import from presentation layer
6. Repositories are NOT instantiated inside views - inject via commands
7. Every domain business rules raise ValueError or custom DomainException
8. Presentation layer catches domain exceptions, returns DRF Response
9. Mappers in infrastructure/mappers.py handle ALL ORM ↔ entity conversion
10. Call direction: Presentation → Application → Domain/Port ← Infrastructure

---

## 🛠️ Tech Stack

- **Python** 3.11+
- **Django** 4.2.11 - Web framework
- **Django REST Framework** 3.14.0 - API framework
- **django-filter** 23.5 - Filtering
- **pytest** 8.0.0 + **pytest-django** 4.7.0 - Testing
- **python-decouple** 3.8 - Environment configuration
- **SQLite** (development) / **PostgreSQL** (production-ready)

---

## 🚀 Setup & Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- git

### Installation Steps

```bash
# 1. Clone the repository
git clone <repository-url>
cd hr-backend

# 2. Create and activate virtual environment
python -m venv venv

# On Windows:
venv\Scriptsctivate

# On Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
# Create a .env file in the root directory
echo "SECRET_KEY=your-secret-key-here" > .env
echo "DEBUG=True" >> .env

# 5. Run migrations
python manage.py makemigrations
python manage.py migrate

# 6. Create a superuser (optional)
python manage.py createsuperuser

# 7. Run the development server
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

---

## 📡 API Endpoints

### Employees

| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| GET | `/api/employees/` | List all employees (paginated) | BLOCKER |
| GET | `/api/employees/?search=` | Search by first or last name | BLOCKER |
| GET | `/api/employees/?department=` | Filter by department code | BLOCKER |
| GET | `/api/employees/{id}/` | Retrieve a single employee | REQUIRED |
| POST | `/api/employees/` | Create a new employee | BLOCKER |
| PUT | `/api/employees/{id}/` | Full update of an employee | BLOCKER |
| PATCH | `/api/employees/{id}/` | Partial update of an employee | REQUIRED |
| DELETE | `/api/employees/{id}/` | Soft-delete (set is_active=False) | BLOCKER |
| POST | `/api/employees/bulk-delete/` | Deactivate multiple employees | REQUIRED |

### Departments

| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| GET | `/api/departments/` | List all departments | REQUIRED |
| GET | `/api/departments/{id}/` | Retrieve a single department | OPTIONAL |
| POST | `/api/departments/` | Create a department | REQUIRED |
| PUT | `/api/departments/{id}/` | Update a department | OPTIONAL |

### Leave Requests

| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| POST | `/api/leave/` | Submit a leave request | BLOCKER |
| GET | `/api/leave/` | List leave requests (filterable) | BLOCKER |
| PATCH | `/api/leave/{id}/approve/` | Approve a leave request | BLOCKER |
| PATCH | `/api/leave/{id}/reject/` | Reject a leave request | REQUIRED |
| GET | `/api/leave/on-leave-count/` | Count of employees currently on approved leave | BLOCKER |
| GET | `/api/leave/?department=&status=` | Filter by department and status | REQUIRED |

### Example Responses

#### Employee List

```json
{
  "count": 42,
  "next": "http://localhost:8000/api/employees/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid-here",
      "employee_number": "EMP-001",
      "first_name": "Abebe",
      "last_name": "Kebede",
      "email": "abebe@company.com",
      "department": {
        "id": "uuid",
        "code": "ENG",
        "name": "Engineering"
      },
      "job_title": "Software Engineer",
      "employment_type": "FULL_TIME",
      "hire_date": "2023-01-15",
      "is_active": true
    }
  ]
}
```

#### On-Leave Count

```json
{
  "on_leave_count": 7,
  "as_of": "2025-06-27"
}
```

#### Bulk Delete Response

```json
{
  "deactivated": 3,
  "already_inactive": 0,
  "not_found": 0
}
```

---

## 🧪 Testing

### Run All Tests

```bash
python manage.py test
```

### Run Specific Test Suites

```bash
# Unit tests (domain layer - no database)
python manage.py test tests.unit

# Integration tests (repository layer - uses test database)
python manage.py test tests.integration

# API tests (full request-response cycle)
python manage.py test tests.api
```

### Test Coverage

- **Unit Tests:** Domain layer business rules (31+ tests)
- **Integration Tests:** Repository operations with real database (21+ tests)
- **API Tests:** Full request-response cycle (11+ tests)

---

## 📁 Project Structure

```
hr-backend/
├── apps/
│   ├── common/
│   │   ├── exceptions.py          # Domain exceptions
│   │   ├── pagination.py          # Custom pagination
│   │   └── exception_handler.py   # DRF exception handler
│   ├── employees/                 # Employee bounded context
│   │   ├── domain/
│   │   │   ├── entities/          # Employee dataclass
│   │   │   ├── ports/             # EmployeePort ABC
│   │   │   └── services/          # Business rules
│   │   ├── application/
│   │   │   ├── commands/          # Create, Update, Delete
│   │   │   └── queries/           # List, Get
│   │   ├── infrastructure/
│   │   │   ├── models.py          # Django ORM model
│   │   │   ├── mappers.py         # ORM ↔ Entity conversion
│   │   │   └── repository.py      # Implements EmployeePort
│   │   └── presentation/
│   │       ├── views.py           # DRF ViewSet
│   │       ├── serializers.py     # DRF Serializers
│   │       └── urls.py            # URL config
│   ├── departments/               # Department bounded context
│   │   └── (same structure as employees/)
│   └── leave/                     # Leave bounded context
│       └── (same structure as employees/)
├── config/
│   ├── settings.py                # Django settings
│   └── urls.py                    # Main URL config
├── tests/
│   ├── unit/                      # Domain layer tests
│   ├── integration/               # Repository layer tests
│   └── api/                       # API tests
├── manage.py
├── requirements.txt
├── .env                           # Environment variables
└── README.md
```

---

## 📋 Business Rules

### Employee Rules

- Email must be unique across all employees
- Employee number must be unique (auto-generated if not provided)
- Delete is always soft - set is_active=False
- Bulk delete returns structured counts

### Department Rules

- Code must be unique and alphanumeric
- Cannot deactivate a department with active employees

### Leave Rules

- Cannot submit overlapping approved leave
- end_date must be >= start_date
- Only PENDING requests can be approved/rejected
- Approve/reject sets reviewed_by and reviewed_at
- on-leave-count uses today's date (never hardcoded)

---

## 🔧 Development

### Environment Variables

Create a `.env` file with:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database Management

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations

# Reset database
python manage.py flush
```

### Code Quality

```bash
# Check for Django errors
python manage.py check

# Verify no Django imports in domain layer
grep -r "from django" apps/*/domain/ --include="*.py"

# Verify no DRF imports in domain layer
grep -r "from rest_framework" apps/*/domain/ --include="*.py"
```

---

## 🤝 Contributing

Contributions are welcome! Please follow the DDD architecture rules and ensure all tests pass before submitting a pull request.


