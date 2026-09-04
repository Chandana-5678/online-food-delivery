# FoodFlow Python project reference

Keep this document as the first place to check when returning to the Python/Django project later.

## Project locations

| Project | Local folder |
|---|---|
| Python/Django version | `D:\01 - PROJECTS\01 - NOTES\FULL STACK PYTHON NOTES\FULL STACK PYTHON PROJECT 1\food_delivery_app` |
| ASP.NET Core version | `D:\01 - PROJECTS\01 - NOTES\DOT NET NOTES\DOT NET FULL STACK PROJECT` |
| Python GitHub repository | `https://github.com/ravitejacmr/online-food-delivery` |

The Python and .NET projects are independent implementations. Changes made in one project do not automatically appear in the other.

## Port assignments

Two applications cannot listen on the same IP address and port simultaneously.

### Recommended when running only the Python stack

| Service | URL or port |
|---|---|
| Angular frontend | `http://localhost:4200/` |
| Django REST API | `http://127.0.0.1:8000/` |
| XAMPP MariaDB/MySQL | `3306` |

### Recommended when running Python and .NET together

| Service | URL |
|---|---|
| Python Angular frontend | `http://localhost:4200/` |
| Django REST API | `http://127.0.0.1:8000/` |
| .NET Angular frontend | `http://localhost:4201/` |
| ASP.NET Core API | `http://127.0.0.1:5000/` |

Both Angular projects default to port `4200`. Run the .NET frontend on `4201` when both are needed:

```powershell
cd "D:\01 - PROJECTS\01 - NOTES\DOT NET NOTES\DOT NET FULL STACK PROJECT\frontend"
npm start -- --port 4201
```

The Python Angular API URL is configured in `frontend/src/environments/environment.ts` and must point to `http://127.0.0.1:8000/api`.

## Database

- Database name: `food_delivery_db`
- Test database name: `test_food_delivery_db`
- Server: XAMPP MariaDB/MySQL
- Default host and port: `127.0.0.1:3306`
- Default development user: `root`

Start MySQL in XAMPP before running Django. Create the database by importing `database/create_database.sql` in phpMyAdmin or run:

```powershell
C:\xampp\mysql\bin\mysql.exe -u root < database\create_database.sql
```

The custom backend in `backend/food_delivery/db_backend/` supports the installed XAMPP MariaDB 10.4 while keeping Django's MySQL behavior conservative. Do not remove it unless the database version and Django compatibility have been reviewed.

## Starting the Python application

### Backend terminal

```powershell
cd backend
venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Do not overwrite an existing `.env` when it already contains the correct local database settings.

### Frontend terminal

```powershell
cd frontend
npm install
npm start
```

Important URLs:

- Home: `http://localhost:4200/`
- API: `http://127.0.0.1:8000/api/`
- Django Admin: `http://127.0.0.1:8000/admin/`
- Swagger: `http://127.0.0.1:8000/api/docs/`
- OpenAPI schema: `http://127.0.0.1:8000/api/schema/`
- phpMyAdmin: `http://localhost/phpmyadmin/`

## Demo accounts

All local demo accounts use the password `FoodFlow@123`.

| Role | Email |
|---|---|
| Administrator | `admin@example.com` |
| Customer | `customer@example.com` |
| Restaurant owner | `owner@example.com` |
| Delivery partner | `delivery@example.com` |

Additional seeded accounts include `customer2@example.com`, `customer3@example.com`, `owner2@example.com`, `owner3@example.com`, `burger1@example.com` through `burger5@example.com`, and `delivery2@example.com`.

These credentials are only for local development. Never reuse them in a hosted environment.

## Backend structure

| Location | Purpose |
|---|---|
| `backend/food_delivery/settings.py` | Database, JWT, CORS, pagination, uploads, email, and tax configuration |
| `backend/food_delivery/urls.py` | Root API, Django Admin, Swagger, and OpenAPI routes |
| `backend/food_delivery/permissions.py` | Shared role and ownership permissions |
| `backend/food_delivery/exceptions.py` | Consistent API error responses |
| `backend/accounts/` | User accounts, JWT login/logout, profiles, passwords, and addresses |
| `backend/restaurants/` | Restaurants and customer favourites |
| `backend/menu/` | Categories and food items |
| `backend/cart/` | One-restaurant cart and totals |
| `backend/coupons/` | Coupon validation and discounts |
| `backend/orders/` | Checkout, order snapshots, status changes, and cancellation |
| `backend/payments/` | COD and mock online payment workflows |
| `backend/delivery/` | Delivery-partner profile, assignment, progress, and earnings |
| `backend/reviews/` | Delivered-order reviews and ratings |
| `backend/notifications/` | Database-backed user notifications |
| `backend/dashboard/` | Role-specific customer, owner, rider, and administrator metrics |
| `backend/accounts/management/commands/seed_data.py` | Demo data and accounts |
| `frontend/src/app/core/services/` | Angular authentication and API clients |
| `frontend/src/app/core/guards/` | Angular authentication and role guards |

## Main business rules

- Email is the login identifier and authentication uses JWT access and rotating refresh tokens.
- Backend authorization checks both role and object ownership; frontend guards are only a user-experience layer.
- A cart may contain items from only one restaurant at a time.
- Checkout stores food, price, and delivery-address snapshots so future edits do not rewrite old orders.
- Tax is controlled centrally by `FOOD_DELIVERY_TAX_PERCENT` and defaults to 5%.
- Restaurant flow: `pending` or `confirmed` → `accepted` → `preparing` → `ready`.
- Delivery flow: `ready` → `assigned` → `picked_up` → `on_the_way` → `delivered`.
- Customers may cancel only during allowed early stages and review only delivered orders.
- The online checkout is a simulator and never charges real money.
- Real email, payment gateway, object storage, and live GPS remain extension points.

## Environment configuration

Local settings belong in `backend/.env`, created from `backend/.env.example`.

Important variables:

```env
DJANGO_SECRET_KEY=change-this-for-non-local-use
DJANGO_DEBUG=True
DB_NAME=food_delivery_db
DB_USER=root
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=3306
TEST_DB_NAME=test_food_delivery_db
CORS_ALLOWED_ORIGINS=http://localhost:4200
FOOD_DELIVERY_TAX_PERCENT=5.00
```

- `.env` is ignored by Git and must never contain credentials that are committed.
- Set `DJANGO_DEBUG=False`, use a strong secret, enable HTTPS, and configure secure origins before deployment.
- If the Angular frontend runs on port `4201`, add `http://localhost:4201` to `CORS_ALLOWED_ORIGINS`.

## Build and verification commands

Run from `backend` with the virtual environment activated and XAMPP MySQL running:

```powershell
python manage.py check
python manage.py makemigrations --check
python manage.py migrate
python manage.py test --verbosity 2
python manage.py spectacular --file schema.yml --validate
```

Run the frontend production build:

```powershell
cd frontend
npm install
npm run build
```

## Common problems

### `ERR_CONNECTION_REFUSED` on port 4200

The Angular development server is not running. Run `npm start` inside `frontend` and wait for compilation to finish.

### API connection refused on port 8000

Activate the virtual environment and run `python manage.py runserver` inside `backend`.

### `Can't connect to MySQL server`

Start MySQL in XAMPP and confirm that port `3306` is available.

### `Access denied for user 'root'`

Put the correct XAMPP root password in `backend/.env`. Do not commit the password.

### Test database permission error

The configured database user must be able to create and drop `test_food_delivery_db`. XAMPP's local root account is suitable for disposable local development.

### CORS error

Add the frontend's exact origin, including its port, to `CORS_ALLOWED_ORIGINS` in `backend/.env`, then restart Django.

### Port already in use

Stop the other service or select another port. When running both projects, keep Django on `8000`, ASP.NET Core on `5000`, Python Angular on `4200`, and .NET Angular on `4201`.

### Stale Angular dependencies

Remove only `frontend/node_modules`, run `npm install`, and rebuild. Do not delete the project folder.

## Git workflow

Before pushing future changes:

```powershell
git status
cd backend
venv\Scripts\Activate.ps1
python manage.py check
python manage.py test
cd ..\frontend
npm run build
cd ..
git add .
git commit -m "Describe the change"
git push
```

The `.gitignore` excludes `.env`, virtual environments, `node_modules`, generated builds, uploads, logs, coverage, and local IDE files.
