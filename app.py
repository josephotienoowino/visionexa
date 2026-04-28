import os
from app import create_app

# Create app for Vercel deployment (always use production)
app = create_app('production')

# Vercel expects the app to be exposed as 'app'
if __name__ == '__main__':
    app.run()