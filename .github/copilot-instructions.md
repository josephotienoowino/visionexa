# Visionexa Project Setup Instructions

## Project Overview

Visionexa is a Flask-based profile website with SQLite database support for managing professional profiles, skills, and projects.

## Completed Setup

- [x] Created Flask application structure
- [x] Configured SQLAlchemy ORM with SQLite
- [x] Set up database models (Profile, Skill, Project)
- [x] Created Flask blueprints for routing
- [x] Designed responsive HTML templates
- [x] Created CSS styling
- [ ] Install dependencies and run application
- [ ] Test database and API endpoints

## Next Steps

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Environment File

```bash
cp .env.example .env
```

### 3. Run the Application

```bash
python run.py
```

The application will be available at `http://localhost:5000`

### 4. Initialize Database

The database is automatically created on first run with the following tables:
- `profile` - User profile information
- `skill` - Professional skills
- `project` - Portfolio projects

### 5. Create Initial Profile

Use the API endpoint to create a profile:

```bash
curl -X POST http://localhost:5000/profile/add \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Your Name",
    "title": "Your Professional Title",
    "bio": "Your professional biography",
    "email": "your@email.com",
    "phone": "+1234567890",
    "location": "City, Country"
  }'
```

## Technology Stack

- **Backend**: Flask 3.0.0
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Configuration**: Environment variables

## Key Files

- `run.py` - Application entry point
- `app/__init__.py` - Flask app factory
- `app/models.py` - Database models
- `app/routes.py` - API routes and blueprints
- `config.py` - Configuration settings
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variables template

## Environment Variables

Available configuration options in `.env`:
- `FLASK_ENV` - Environment (development/production/testing)
- `SECRET_KEY` - Flask secret key
- `DATABASE_URL` - Database connection string
- `FLASK_HOST` - Server host
- `FLASK_PORT` - Server port
- `FLASK_DEBUG` - Enable debug mode

## Troubleshooting

### Database Issues
If you encounter database errors, delete the `instance/visionexa.db` file and restart the app.

### Port Already in Use
Change the port in `.env`:
```
FLASK_PORT=5001
```

### Missing Dependencies
Ensure all packages are installed:
```bash
pip install -r requirements.txt
```

## Further Development

Consider adding:
- User authentication
- Admin dashboard for profile management
- Contact form
- Blog/articles section
- Image upload functionality
- Search functionality
- Social media integration
