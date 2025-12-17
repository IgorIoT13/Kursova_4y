# Kursova_4y

A Flask web application with MySQL database integration.

## Features

- Flask web framework
- MySQL database connection using SQLAlchemy ORM
- Environment-based configuration
- Example User model
- RESTful API endpoints
- Health check endpoint

## Prerequisites

- Python 3.8 or higher
- MySQL Server 5.7 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/IgorIoT13/Kursova_4y.git
cd Kursova_4y
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up MySQL database:
```sql
CREATE DATABASE flask_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

5. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` file with your database credentials:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=flask_db
SECRET_KEY=your-secret-key-here
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

The application will run on `http://localhost:5000`

2. Or use Flask CLI:
```bash
export FLASK_APP=app.py
flask run
```

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check and database connection status
- `GET /users` - Get all users
- `GET /users/create/<username>/<email>` - Create a new user (for testing only - use POST in production)

## Project Structure

```
Kursova_4y/
├── app.py              # Main application file
├── config.py           # Configuration settings
├── models.py           # Database models
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── .gitignore         # Git ignore file
└── README.md          # This file
```

## Configuration

The application supports different configurations:
- **Development**: Debug mode enabled, verbose logging
- **Production**: Debug mode disabled, minimal logging

Set the environment using the `FLASK_ENV` variable in your `.env` file.

## Database Models

### User Model
- `id`: Primary key (Integer)
- `username`: Unique username (String, max 80 chars)
- `email`: Unique email address (String, max 120 chars)
- `created_at`: Timestamp of creation (DateTime)

## Development

To add new models:
1. Create model class in `models.py`
2. Import in `app.py`
3. Restart the application (tables will be created automatically)

## Testing

Test the database connection:
```bash
curl http://localhost:5000/health
```

Create a test user:
```bash
curl http://localhost:5000/users/create/testuser/test@example.com
```

Get all users:
```bash
curl http://localhost:5000/users
```

## Troubleshooting

### Database Connection Error
- Verify MySQL server is running
- Check database credentials in `.env`
- Ensure the database exists
- Check MySQL user permissions

### Module Not Found Error
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

## License

This project is created for educational purposes.