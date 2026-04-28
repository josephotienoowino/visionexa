import os
from app import create_app, db
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create app
app = create_app(os.environ.get('FLASK_ENV', 'development'))

# Database shell context for flask shell
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Profile': __import__('app.models', fromlist=['Profile']).Profile,
        'Skill': __import__('app.models', fromlist=['Skill']).Skill,
        'Project': __import__('app.models', fromlist=['Project']).Project,
    }

if __name__ == '__main__':
    app.run(
        host=os.environ.get('FLASK_HOST', '0.0.0.0'),
        port=int(os.environ.get('FLASK_PORT', 5000)),
        debug=os.environ.get('FLASK_DEBUG', True)
    )
