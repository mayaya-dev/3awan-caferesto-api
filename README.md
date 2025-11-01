# 3awan CafeResto API

Simple FastAPI app for cafe/restaurant with tables: menus, categories, orders, order_items.

Run locally (Windows PowerShell):

```powershell
.\.venv\Scripts\activate
uvicorn main:app --reload
```

Create DB tables:

```powershell
.\.venv\Scripts\activate
python -m app.config.init_db
```

Endpoints (menus implemented, plus categories, orders, order_items):
- GET /api/menus
- GET /api/menus/{id}
- POST /api/menus
- PUT /api/menus/{id}
- DELETE /api/menus/{id}

- GET /api/categories
- GET /api/categories/{id}
- POST /api/categories
- PUT /api/categories/{id}
- DELETE /api/categories/{id}

- GET /api/orders
- GET /api/orders/{id}
- POST /api/orders
- PUT /api/orders/{id}
- DELETE /api/orders/{id}

- GET /api/order_items
- GET /api/order_items/{id}
- POST /api/order_items
- PUT /api/order_items/{id}
- DELETE /api/order_items/{id}

Database URL is configured in `app/config/database.py`.
