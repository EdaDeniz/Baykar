# Aircraft Manufacturing API

## Overview

This project is an aircraft manufacturing API built using Django and Django REST Framework. It manages aircraft components, teams, and the assembly process, ensuring each team produces only the components they are responsible for. The assembly team combines these components into completed aircraft.

## Features

User authentication with Django's built-in admin panel.

CRUD operations for teams and components.

Restriction: Teams can only produce specific components.

Assembly team can manufacture aircraft using available parts.

Inventory management to track parts and prevent duplicate usage.

API documentation available via Swagger.

Docker support for easy deployment.

## Installation

### Prerequisites
- Python 3.8+
- Django & Django REST Framework
- PostgreSQL
- Docker (optional for containerized deployment)

### Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/EdaDeniz/Baykar.git
   cd Baykar
   ```
2. Create a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\\Scripts\\activate`
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the development server:
   ```sh
   python manage.py runserver
   ```

## API Endpoints

### Aircraft Endpoints
- `GET /api/aircraft/` - Retrieve all aircraft.
- `POST /api/aircraft/` - Create a new aircraft.
- `GET /api/aircraft/{id}/` - Retrieve a specific aircraft by ID.
- `PUT /api/aircraft/{id}/` - Update a specific aircraft by ID.
- `PATCH /api/aircraft/{id}/` - Partially update an aircraft.
- `DELETE /api/aircraft/{id}/` - Delete an aircraft.
- `GET /api/aircraft/assembly_status/` - Retrieve assembly status of aircraft.

### Parts Endpoints
- `GET /api/parts/` - Retrieve all parts.
- `POST /api/parts/` - Create a new part.
- `GET /api/parts/{id}/` - Retrieve a specific part by ID.
- `PUT /api/parts/{id}/` - Update a specific part by ID.
- `PATCH /api/parts/{id}/` - Partially update a part.
- `DELETE /api/parts/{id}/` - Delete (recycle) a part.
- `GET /api/parts/available_parts/` - Retrieve available parts by aircraft type.
- `GET /api/parts/inventory_status/` - Retrieve inventory status for all aircraft.

## Access the API at:

Swagger API docs: http://127.0.0.1:8000/swagger/

Django Admin Panel: http://127.0.0.1:8000/admin/

## Authentication

You can log in using the following default credentials:

Username: `admin`

Password: `123`


## Running with Docker
1. Build the Docker container:
   ```sh
   docker build -t aircraft-api .
   ```
2. Run the container:
   ```sh
   docker run -p 8000:8000 aircraft-api
   ```

## Additional Features

Swagger Documentation: API documentation is available at /swagger/.

Admin Panel: Manage users and database records from /admin/.

DataTables Integration: Frontend tables support sorting, filtering, and pagination.

Asynchronous Frontend: AJAX and Fetch API are used for smoother UI interactions.
