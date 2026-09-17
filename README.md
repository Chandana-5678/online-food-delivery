# FoodFlow — Full-stack food delivery platform

FoodFlow is a working multi-role food delivery application built with Django REST Framework, XAMPP MariaDB/MySQL, JWT authentication, and Angular. Customers can browse and order, restaurant owners can manage menus and kitchen orders, delivery partners can accept and complete runs, and administrators can monitor the marketplace.

## Stack and architecture

- Backend: Python, Django 5.2, Django REST Framework, SimpleJWT, django-filter, CORS headers, Pillow, drf-spectacular and PyMySQL.
- Frontend: Angular 20 standalone components, TypeScript, Router, Reactive Forms, HttpClient, RxJS and responsive custom CSS.
- Database: `food_delivery_db` on XAMPP MariaDB/MySQL only. SQLite is not configured.
- Structure: `backend/` contains separated domain apps, `frontend/` contains the Angular SPA, and `database/` contains SQL bootstrap files.

Core backend apps are `accounts`, `restaurants`, `menu`, `cart`, `coupons`, `orders`, `payments`, `delivery`, `reviews`, `notifications`, and `dashboard`. Complex cart, coupon, order, payment and notification work is kept in service modules and critical writes use database transactions.

For port assignments, daily startup steps, architecture notes, test accounts, and troubleshooting, see [docs/PROJECT_REFERENCE.md](docs/PROJECT_REFERENCE.md).

## Features

- Email registration/login, JWT access and rotating refresh tokens, token blacklist logout, password validation/change/recovery architecture, profiles, role guards and object ownership checks.
- Restaurant/category/food CRUD, uploads, availability, opening status, search, filters, sorting, pagination and favorites.
- One-restaurant cart, quantity updates, cart replacement confirmation, coupons, configurable tax, delivery fee and totals.
- Address book, checkout, food/price snapshots, human-readable order numbers, validated status transitions and cancellation rules.
- Cash on delivery and success/failure mock online checkout with generated transaction IDs.
- Delivery assignment, pickup, on-the-way and delivery workflow with status history suitable for future GPS integration.
- Delivered-order-only reviews, computed ratings, database notifications and optimized customer/owner/rider/admin dashboards.
- Responsive role-aware Angular navigation, cards, tables, forms, loading/empty/error states, toasts and tracking timeline.
- Django Admin and OpenAPI/Swagger documentation.

## Prerequisites

- Python 3.13 (the project also supports current Python 3.x versions supported by Django)
- Node.js 20+ and npm
- XAMPP with MySQL/MariaDB running

## XAMPP and database setup

1. Open XAMPP Control Panel.
2. Start **MySQL**. Start **Apache** only if you want phpMyAdmin.
3. Open `http://localhost/phpmyadmin/`.
4. Import `database/create_database.sql`, create `food_delivery_db` manually, or run:

```powershell
C:\xampp\mysql\bin\mysql.exe -u root < database\create_database.sql
```

The installed XAMPP release in this environment uses MariaDB 10.4. Django 5.2 normally gates MariaDB at 10.5; `backend/food_delivery/db_backend/` is a deliberately narrow compatibility backend that keeps Django's MySQL engine but disables unsupported `INSERT ... RETURNING` and permits the conservative project schema on 10.4. Strict transactional SQL mode remains enabled.

## Backend setup

```powershell
cd food_delivery_app\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py makemigrations --check
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Edit `.env` if the XAMPP root user has a password:

```env
DB_NAME=food_delivery_db
DB_USER=root
DB_PASSWORD=your-xampp-password
DB_HOST=127.0.0.1
DB_PORT=3306
```

Never commit `.env`. Tax is centralized through `FOOD_DELIVERY_TAX_PERCENT`.

Create another administrator when needed:

```powershell
python manage.py createsuperuser
```

## Frontend setup

```powershell
cd food_delivery_app\frontend
npm install
npm start
```

The backend base URL is centralized in `frontend/src/environments/environment.ts`. Production deployments should add a production environment replacement and HTTPS origins.

## Demo accounts

All development accounts use `FoodFlow@123`. These credentials are for local development only and must be changed outside a disposable environment.

| Role | Email |
|---|---|
| Administrator | `admin@example.com` |
| Customer | `customer@example.com` |
| Restaurant owner | `owner@example.com` |
| Delivery partner | `delivery@example.com` |

Additional seed users are `customer2@example.com`, `customer3@example.com`, `owner2@example.com`, `owner3@example.com`, `burger1@example.com` through `burger5@example.com`, and `delivery2@example.com`.

## Tests and verification

With XAMPP MySQL running:

```powershell
cd food_delivery_app\backend
python manage.py check
python manage.py makemigrations --check
python manage.py test --verbosity 2
python manage.py spectacular --file schema.yml --validate
```

Angular production build:

```powershell
cd food_delivery_app\frontend
npm run build
```

## Important URLs

| Service | URL |
|---|---|
| Angular | http://localhost:4200/ |
| REST API | http://127.0.0.1:8000/api/ |
| Django Admin | http://127.0.0.1:8000/admin/ |
| Swagger | http://127.0.0.1:8000/api/docs/ |
| OpenAPI schema | http://127.0.0.1:8000/api/schema/ |
| phpMyAdmin | http://localhost/phpmyadmin/ |

## API overview

- Authentication: `/api/auth/register/`, `/api/auth/login/`, `/api/auth/token/refresh/`, `/api/auth/logout/`, `/api/auth/profile/`.
- Shopping: `/api/restaurants/`, `/api/categories/`, `/api/foods/`, `/api/cart/`, `/api/cart/items/`, `/api/cart/coupon/`.
- Fulfilment: `/api/orders/`, `/api/payments/`, `/api/delivery/available/`, `/api/delivery/assigned/`.
- Engagement: `/api/reviews/`, `/api/favorites/`, `/api/notifications/`.
- Reporting: `/api/dashboard/` and `/api/dashboard/users/`.

Use Swagger for the complete generated contract and request schemas.

## Troubleshooting

- `Can't connect to MySQL server`: start MySQL in XAMPP and confirm port `3306` is free.
- `Access denied for user root`: put the XAMPP password in `backend/.env`.
- Test database permission error: grant the configured user permission to create/drop `test_food_delivery_db` or use XAMPP's local `root` user for development.
- CORS error: the example allows both `http://localhost:4200` and `http://127.0.0.1:4200`; add any different exact origin to `CORS_ALLOWED_ORIGINS`.
- Port already used: run `python manage.py runserver 8001` and update the Angular environment URL, or stop the conflicting process.
- Stale frontend dependencies: remove only `frontend/node_modules`, then run `npm install` again.

## Screenshots

Place portfolio captures in `screenshots/`. Recommended views: home, restaurant menu, checkout, order tracker, and each role dashboard.

## Production notes

Set `DJANGO_DEBUG=False`, use strong secrets and database credentials, configure HTTPS/secure cookies, use managed media/object storage, and replace the console email backend. The mock payment and latitude/longitude fields intentionally provide extension points for a real gateway and live GPS provider without pretending those external services are active.
