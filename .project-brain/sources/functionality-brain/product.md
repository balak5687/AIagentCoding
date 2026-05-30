# Product Overview

# GreasyNuts ERP

Complete ERP system for automotive repair shops and garages.

## Features

### Customer Management
- Customer profiles with contact information and service history
- Vehicle registration and tracking (VIN, make, model, year)
- Customer portal access for viewing work orders and invoices

### Work Order Management
- Create and track repair jobs from start to finish
- Labor time tracking and technician assignments
- Parts usage tracking with automatic inventory deduction
- Status workflow: New → Estimate → Approved → In Progress → Completed
- Photo and notes attachments

### Inventory Management
- Parts catalog with SKU, pricing, and stock levels
- Automatic reorder alerts when stock is low
- Supplier management and purchase orders
- Stock adjustments and audit trails

### Invoicing & Billing
- Automatic invoice generation from work orders
- Labor and parts breakdown
- Tax calculations
- Payment tracking (unpaid, partial, paid)
- PDF invoice export (future)

### Reporting & Analytics
- Revenue reports by date range
- Work order statistics and completion metrics
- Technician performance tracking
- Inventory value and turnover reports

### Security & Access Control
- JWT-based authentication
- Role-based permissions (Admin, Technician, Customer)
- Password hashing with bcrypt
- Secure API with rate limiting

---

## Tech Stack

- **Backend**: Flask (Python 3.12+)
- **Database**: DynamoDB (Local for dev, AWS for production)
- **Authentication**: JWT tokens with bcrypt
- **Validation**: Pydantic models
- **Web Server**: Gunicorn + Nginx
- **SSL/TLS**: Let's Encrypt (Certbot)

---

## Quick Start

### Development
```bash
git clone https://github.com/aravindmk1011/GreasyNuts.git
cd GreasyNuts
./deploy.sh
```

Access: `http://localhost:5000/api/health`

### Production
```bash
./deploy_production.sh --domain your-domain.com
```

Access: `https://your-domain.com/api/health`

**See [DEPLOYMENT.md](DEPLOYMENT.md) for complete setup instructions.**

---

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/refresh` - Refresh token
- `POST /api/auth/change-password` - Change password

### Customers (Coming Soon)
- `GET /api/customers` - List customers
- `POST /api/customers` - Create customer
- `GET /api/customers/:id` - Get customer details
- `PUT /api/customers/:id` - Update customer
- `DELETE /api/customers/:id` - Delete customer

### Vehicles (Coming Soon)
- `GET /api/vehicles` - List vehicles
- `POST /api/vehicles` - Register vehicle
- `GET /api/vehicles/:id` - Get vehicle details

### Work Orders (Coming Soon)
- `GET /api/work-orders` - List work orders
- `POST /api/work-orders` - Create work order
- `GET /api/work-orders/:id` - Get work order
- `PUT /api/work-orders/:id/status` - Update status

### Inventory (Coming Soon)
- `GET /api/inventory/parts` - List parts
- `POST /api/inventory/parts` - Add part
- `PUT /api/inventory/parts/:id` - Update part

### Invoices (Coming Soon)
- `GET /api/invoices` - List invoices
- `POST /api/invoices` - Create invoice
- `GET /api/invoices/:id` - Get invoice

### Reports (Coming Soon)
- `GET /api/reports/revenue` - Revenue report
- `GET /api/reports/work-orders` - Work order statistics

---

## Testing

Run all API tests:
```bash
./test_api.sh
```

Default test credentials:
- **Admin**: `admin@greasynuts.com` / `Admin123!`
- **Technician**: `tech@greasynuts.com` / `Tech123!`
- **Customer**: `customer@example.com` / `Customer123!`

---

## Project Structure

```
GreasyNuts/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── config.py             # Configuration
│   ├── middleware/
│   │   └── auth.py           # JWT authentication
│   ├── models/               # Pydantic models
│   │   ├── user.py
│   │   ├── customer.py
│   │   ├── vehicle.py
│   │   ├── work_order.py
│   │   ├── inventory.py
│   │   └── invoice.py
│   ├── routes/               # API endpoints
│   │   └── auth.py
│   ├── services/             # Business logic
│   │   └── auth_service.py
│   ├── repositories/         # Data access layer
│   │   ├── base_repository.py
│   │   └── user_repository.py
│   └── utils/                # Helper functions
│       ├── dynamodb.py
│       ├── jwt_utils.py
│       └── responses.py
├── scripts/
│   ├── init_db.py            # Database initialization
│   └── seed_data.py          # Test data seeding
├── main.py                   # Application entry point
├── deploy.sh                 # Development deployment
├── deploy_production.sh      # Production deployment
├── stop.sh                   # Stop application
└── test_api.sh               # API test suite
```

---

## Development

### Prerequisites
- Python 3.12+
- Docker (for DynamoDB Local)
- Git

### Setup
```bash
# Clone repository
git clone <repository-url>
cd GreasyNuts

# Start DynamoDB Local
docker run -d -p 8000:8000 --name dynamodb-local amazon/dynamodb-local

# Initialize database
source .venv/bin/activate
python scripts/init_db.py --seed

# Deploy
./deploy.sh

# Test
./test_api.sh
```

### Making Changes
```bash
# Pull latest
git pull origin main

# Make changes
# ... edit files ...

# Test
./test_api.sh

# Commit
git add .
git commit -m "Description of changes"
git push origin main
```

---

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Production deployment instructions
- HTTPS/SSL setup
- Nginx configuration
- Database setup (DynamoDB Local vs AWS)
- Security best practices
- Monitoring and maintenance

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `./test_api.sh`
5. Submit a pull request

---

## License

Proprietary - All rights reserved

---

## Support

- **Documentation**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Testing**: Run `./test_api.sh`
- **Issues**: Check logs in `app.log`

---

## Roadmap

### ✅ Phase 1: Foundation (Complete)
- [x] Flask application structure
- [x] DynamoDB connection
- [x] JWT authentication
- [x] User management
- [x] Database initialization

### 🚧 Phase 2: Core Features (In Progress)
- [ ] Customer CRUD
- [ ] Vehicle management
- [ ] Work order system
- [ ] Inventory management
- [ ] Invoice generation

### 📋 Phase 3: Advanced Features (Planned)
- [ ] Reporting dashboard
- [ ] PDF export
- [ ] Email notifications
- [ ] API documentation (Swagger)
- [ ] Comprehensive tests

### 🎯 Phase 4: Polish (Future)
- [ ] Frontend application
- [ ] Mobile app
- [ ] Payment gateway integration
- [ ] Advanced analytics

---

**Status**: Phase 1 Complete • 9/24 Tasks Done (37.5%)
