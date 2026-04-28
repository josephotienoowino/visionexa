# Visionexa Profile Website

A modern Flask web application for creating and managing a professional profile website with SQLite database support.

## Features

- **Profile Management**: Create and manage your professional profile
- **Skills Tracking**: Add and manage your technical and professional skills
- **Project Showcase**: Display your projects and portfolio
- **Responsive Design**: Mobile-friendly interface
- **REST API**: JSON API endpoints for programmatic access
- **SQLite Database**: Lightweight database for data persistence

## Project Structure

```
visionexa/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── routes.py            # Application routes and blueprints
│   ├── templates/           # HTML templates
│   │   ├── base.html        # Base template
│   │   ├── index.html       # Home page
│   │   └── about.html       # About page
│   └── static/              # Static files
│       ├── css/
│       │   └── style.css    # Main stylesheet
│       └── js/
│           └── main.js      # Main JavaScript
├── instance/                # Instance folder (SQLite DB)
├── config.py                # Configuration settings
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
└── .gitignore              # Git ignore rules
```

## Installation

1. **Clone the repository** (or navigate to the project directory):
   ```bash
   cd visionexa
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your configuration.

   If you want the contact form to send email, configure the mail settings in `.env`.

## Running the Application

1. **Start the Flask development server**:
   ```bash
   python run.py
   ```

2. **Access the application**:
   Open your browser and navigate to `http://localhost:5000`

## API Endpoints

### Profile
- `GET /profile/` - Get profile information
- `POST /profile/add` - Create or update profile

### Skills
- `POST /profile/skill/add` - Add a new skill

### Projects
- `POST /profile/project/add` - Add a new project

## Sample API Requests

### Create Profile
```bash
curl -X POST http://localhost:5000/profile/add \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Your Name",
    "title": "Your Title",
    "bio": "Your bio",
    "email": "your@email.com",
    "phone": "+1234567890",
    "location": "Your City, Country"
  }'
```

### Add Skill
```bash
curl -X POST http://localhost:5000/profile/skill/add \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Python",
    "level": "Expert"
  }'
```

### Add Project
```bash
curl -X POST http://localhost:5000/profile/project/add \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Project Name",
    "description": "Project description",
    "url": "https://project.example.com",
    "github_url": "https://github.com/user/project"
  }'
```

## Configuration

The application supports multiple configurations via `config.py`:
- **Development**: Debug mode enabled, local SQLite database
- **Testing**: In-memory SQLite database
- **Production**: Debug disabled, secure settings

Set the `FLASK_ENV` environment variable to switch between configurations:
```bash
export FLASK_ENV=production
```

## Database

The application uses SQLite for data persistence. The database file is stored in the `instance/` folder as `visionexa.db`.

Models include:
- **Profile**: User profile information
- **Skill**: Professional skills
- **Project**: Portfolio projects

## Development

For development with auto-reload:
```bash
FLASK_DEBUG=True python run.py
```

## Production Deployment

Before deploying to production:
1. Change `SECRET_KEY` in `.env`
2. Set `FLASK_ENV=production`
3. Update database credentials if needed
4. Use a production WSGI server (e.g., Gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## License

MIT License

## Support

For issues and questions, please open an issue in the repository.
