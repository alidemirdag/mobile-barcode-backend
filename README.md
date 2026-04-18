# Backend API - Firebird Database Connection

Flask backend API for mobile barcode application with Firebird database support.

## Features

- Firebird database connection (version 2.5+)
- Configurable connection parameters
- Barcode-based product queries
- CRUD operations for products
- Custom SQL query execution
- CORS support for mobile apps

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Firebird database credentials
```

3. Run the server:
```bash
python app.py
```

## API Endpoints

### Health Check
- `GET /api/health` - Check API status

### Configuration
- `GET /api/config` - Get current database configuration
- `POST /api/config` - Update database configuration
  ```json
  {
    "host": "localhost",
    "port": 3050,
    "database": "C:\\path\\to\\database.fdb",
    "user": "sysdba",
    "password": "masterkey"
  }
  ```

### Connection Test
- `POST /api/test-connection` - Test database connection with provided credentials

### Barcode Operations
- `GET /api/barcode/<barcode>` - Get product by barcode
- `POST /api/barcode` - Create or update product
  ```json
  {
    "barcode": "1234567890",
    "name": "Product Name",
    "price": 99.99,
    "stock": 10
  }
  ```

### Custom Query
- `POST /api/query` - Execute custom SQL query
  ```json
  {
    "query": "SELECT * FROM PRODUCTS WHERE PRICE > ?",
    "params": [50]
  }
  ```

## Database Schema

The API assumes a PRODUCTS table with the following structure:
- ID (integer, primary key)
- BARCODE (varchar)
- NAME (varchar)
- PRICE (decimal)
- STOCK (integer)
- CREATED_AT (timestamp)
- UPDATED_AT (timestamp)

Adjust the table and column names in `app.py` to match your actual database schema.

## Default Configuration

- Host: localhost
- Port: 3050
- User: sysdba
- Password: masterkey
- Database: C:\akinsoft\Wolvox8\Database_FB\01\2018\WOLVOX.FDB

Update these values in the .env file or via the API.
