from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app, session
from flask_mail import Message
from app import db, mail
from app.models import Profile, Skill, Project

# Create blueprints
main_bp = Blueprint('main', __name__)
profile_bp = Blueprint('profile', __name__, url_prefix='/profile')
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Main routes
@main_bp.route('/')
def index():
    profile = Profile.query.first()
    return render_template('index.html', profile=profile)

@main_bp.route('/about')
def about():
    profile = Profile.query.first()
    return render_template('about.html', profile=profile)

@main_bp.route('/services')
def services():
    profile = Profile.query.first()
    return render_template('services.html', profile=profile)

@main_bp.route('/pricing')
def pricing():
    profile = Profile.query.first()
    return render_template('pricing.html', profile=profile)

@main_bp.route('/highlights')
def highlights():
    profile = Profile.query.first()
    return render_template('highlights.html', profile=profile)

@main_bp.route('/commitments')
def commitments():
    profile = Profile.query.first()
    return render_template('commitments.html', profile=profile)

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    profile = Profile.query.first()
    form = request.form if request.method == 'POST' else {}

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        if not name or not email or not subject or not message:
            flash('Please complete all fields before sending your message.', 'error')
            return render_template('contact.html', profile=profile, form=form)

        recipient = current_app.config.get('MAIL_USERNAME')
        if recipient:
            mail_message = Message(
                subject=f'Visionexa Contact: {subject}',
                sender=current_app.config.get('MAIL_DEFAULT_SENDER') or email,
                recipients=[recipient],
                body=f'Name: {name}\nEmail: {email}\n\n{message}',
            )
            try:
                mail.send(mail_message)
                flash('Your message has been sent successfully. Thank you!', 'success')
            except Exception as exc:
                current_app.logger.error('Mail send failed: %s', exc)
                flash('Unable to send your message right now. Please try again later.', 'error')
        else:
            flash('Email service is not configured. Your message was not delivered.', 'info')

        return redirect(url_for('main.contact'))

    return render_template('contact.html', profile=profile, form=form)

# Profile routes
@profile_bp.route('/')
def view_profile():
    profile = Profile.query.first()
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404

    skills = Skill.query.filter_by(profile_id=profile.id).all()
    projects = Project.query.filter_by(profile_id=profile.id).all()

    return jsonify({
        'profile': profile.to_dict(),
        'skills': [skill.to_dict() for skill in skills],
        'projects': [project.to_dict() for project in projects],
    })

@profile_bp.route('/add', methods=['POST'])
def add_profile():
    data = request.get_json()

    profile = Profile.query.first()
    if not profile:
        profile = Profile(
            name=data.get('name'),
            title=data.get('title'),
            bio=data.get('bio'),
            email=data.get('email'),
            phone=data.get('phone'),
            location=data.get('location'),
        )
    else:
        profile.name = data.get('name', profile.name)
        profile.title = data.get('title', profile.title)
        profile.bio = data.get('bio', profile.bio)
        profile.email = data.get('email', profile.email)
        profile.phone = data.get('phone', profile.phone)
        profile.location = data.get('location', profile.location)

    db.session.add(profile)
    db.session.commit()

    return jsonify(profile.to_dict()), 201

@profile_bp.route('/skill/add', methods=['POST'])
def add_skill():
    data = request.get_json()
    profile = Profile.query.first()

    if not profile:
        return jsonify({'error': 'Profile not found'}), 404

    skill = Skill(
        name=data.get('name'),
        level=data.get('level'),
        profile_id=profile.id
    )

    db.session.add(skill)
    db.session.commit()

    return jsonify(skill.to_dict()), 201

@profile_bp.route('/project/add', methods=['POST'])
def add_project():
    data = request.get_json()
    profile = Profile.query.first()

    if not profile:
        return jsonify({'error': 'Profile not found'}), 404

    project = Project(
        title=data.get('title'),
        description=data.get('description'),
        url=data.get('url'),
        github_url=data.get('github_url'),
        image_url=data.get('image_url'),
        start_date=data.get('start_date'),
        end_date=data.get('end_date'),
        profile_id=profile.id
    )

    db.session.add(project)
    db.session.commit()

    return jsonify(project.to_dict()), 201

@profile_bp.route('/skill/<int:skill_id>', methods=['PUT', 'DELETE'])
def manage_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    
    if request.method == 'DELETE':
        db.session.delete(skill)
        db.session.commit()
        return jsonify({'message': 'Skill deleted'}), 200
    
    elif request.method == 'PUT':
        data = request.get_json()
        skill.name = data.get('name', skill.name)
        skill.level = data.get('level', skill.level)
        db.session.commit()
        return jsonify(skill.to_dict()), 200

@profile_bp.route('/project/<int:project_id>', methods=['PUT', 'DELETE'])
def manage_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'DELETE':
        db.session.delete(project)
        db.session.commit()
        return jsonify({'message': 'Project deleted'}), 200
    
    elif request.method == 'PUT':
        data = request.get_json()
        project.title = data.get('title', project.title)
        project.description = data.get('description', project.description)
        project.url = data.get('url', project.url)
        project.github_url = data.get('github_url', project.github_url)
        project.image_url = data.get('image_url', project.image_url)
        project.start_date = data.get('start_date', project.start_date)
        project.end_date = data.get('end_date', project.end_date)
        db.session.commit()
        return jsonify(project.to_dict()), 200

# Admin routes
@admin_bp.route('/', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        # Simple password check - in production, use proper authentication
        if password == current_app.config.get('ADMIN_PASSWORD', 'admin123'):
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid password', 'error')
    
    return render_template('admin/login.html')

@admin_bp.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    profile = Profile.query.first()
    skills = Skill.query.all()
    projects = Project.query.all()
    
    return render_template('admin/dashboard.html', profile=profile, skills=skills, projects=projects)

@admin_bp.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    profile = Profile.query.first()
    
    if request.method == 'POST':
        if not profile:
            profile = Profile()
        
        profile.name = request.form.get('name')
        profile.title = request.form.get('title')
        profile.bio = request.form.get('bio')
        profile.email = request.form.get('email')
        profile.phone = request.form.get('phone')
        profile.location = request.form.get('location')
        profile.profile_image_url = request.form.get('profile_image_url')
        
        db.session.add(profile)
        db.session.commit()
        
        flash('Profile updated successfully', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/edit_profile.html', profile=profile)

@admin_bp.route('/skills')
def manage_skills():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    skills = Skill.query.all()
    return render_template('admin/skills.html', skills=skills)

@admin_bp.route('/skills/add', methods=['GET', 'POST'])
def add_skill():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    if request.method == 'POST':
        profile = Profile.query.first()
        if not profile:
            flash('Profile not found', 'error')
            return redirect(url_for('admin.dashboard'))
        
        skill = Skill(
            name=request.form.get('name'),
            level=request.form.get('level'),
            profile_id=profile.id
        )
        
        db.session.add(skill)
        db.session.commit()
        
        flash('Skill added successfully', 'success')
        return redirect(url_for('admin.manage_skills'))
    
    return render_template('admin/add_skill.html')

@admin_bp.route('/skills/<int:skill_id>/edit', methods=['GET', 'POST'])
def edit_skill(skill_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    skill = Skill.query.get_or_404(skill_id)
    
    if request.method == 'POST':
        skill.name = request.form.get('name')
        skill.level = request.form.get('level')
        
        db.session.commit()
        
        flash('Skill updated successfully', 'success')
        return redirect(url_for('admin.manage_skills'))
    
    return render_template('admin/edit_skill.html', skill=skill)

@admin_bp.route('/skills/<int:skill_id>/delete', methods=['POST'])
def delete_skill(skill_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    skill = Skill.query.get_or_404(skill_id)
    db.session.delete(skill)
    db.session.commit()
    
    flash('Skill deleted successfully', 'success')
    return redirect(url_for('admin.manage_skills'))

@admin_bp.route('/projects')
def manage_projects():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    projects = Project.query.all()
    return render_template('admin/projects.html', projects=projects)

@admin_bp.route('/projects/add', methods=['GET', 'POST'])
def add_project():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    if request.method == 'POST':
        profile = Profile.query.first()
        if not profile:
            flash('Profile not found', 'error')
            return redirect(url_for('admin.dashboard'))
        
        project = Project(
            title=request.form.get('title'),
            description=request.form.get('description'),
            url=request.form.get('url'),
            github_url=request.form.get('github_url'),
            image_url=request.form.get('image_url'),
            start_date=request.form.get('start_date') or None,
            end_date=request.form.get('end_date') or None,
            profile_id=profile.id
        )
        
        db.session.add(project)
        db.session.commit()
        
        flash('Project added successfully', 'success')
        return redirect(url_for('admin.manage_projects'))
    
    return render_template('admin/add_project.html')

@admin_bp.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
def edit_project(project_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        project.title = request.form.get('title')
        project.description = request.form.get('description')
        project.url = request.form.get('url')
        project.github_url = request.form.get('github_url')
        project.image_url = request.form.get('image_url')
        project.start_date = request.form.get('start_date') or None
        project.end_date = request.form.get('end_date') or None
        
        db.session.commit()
        
        flash('Project updated successfully', 'success')
        return redirect(url_for('admin.manage_projects'))
    
    return render_template('admin/edit_project.html', project=project)

@admin_bp.route('/projects/<int:project_id>/delete', methods=['POST'])
def delete_project(project_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    
    flash('Project deleted successfully', 'success')
    return redirect(url_for('admin.manage_projects'))

@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('main.index'))
