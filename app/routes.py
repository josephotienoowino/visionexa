import os
import uuid
from datetime import datetime

from flask import (Blueprint, render_template, request, jsonify, flash,
                   redirect, url_for, current_app, session)
from flask_mail import Message
from werkzeug.utils import secure_filename

from app import db, mail
from app.models import Profile, Skill, Project, Content, COURSE_TAGS, Admin

# ── Blueprints ────────────────────────────────────────────────────────────────
main_bp    = Blueprint('main',    __name__)
profile_bp = Blueprint('profile', __name__, url_prefix='/profile')
admin_bp   = Blueprint('admin',   __name__, url_prefix='/admin')
learn_bp   = Blueprint('learn',   __name__, url_prefix='/learn')

# ── Helpers ───────────────────────────────────────────────────────────────────
def _admin_required():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

def _current_admin():
    admin_id = session.get('admin_id')
    if admin_id:
        return Admin.query.get(admin_id)
    return None

def _superuser_required():
    admin = _current_admin()
    if not admin or not admin.is_superuser:
        flash('Only the superuser can manage admin users.', 'error')
        return redirect(url_for('admin.dashboard'))

def _allowed_file(filename):
    exts = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in exts

def _save_pdf(file):
    """Save an uploaded PDF to the uploads folder; return its static URL."""
    filename    = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    dest        = os.path.join(current_app.config['UPLOAD_FOLDER'], 'pdfs', unique_name)
    file.save(dest)
    return url_for('static', filename=f'uploads/pdfs/{unique_name}')

@admin_bp.before_request
def require_admin():
    if request.endpoint in ('admin.admin_login', 'admin.logout'):
        return
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

# ── Main public routes ────────────────────────────────────────────────────────
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
        name    = request.form.get('name',    '').strip()
        email   = request.form.get('email',   '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        if not all([name, email, subject, message]):
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

# ── Profile API routes ────────────────────────────────────────────────────────
@profile_bp.route('/')
def view_profile():
    profile = Profile.query.first()
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    skills   = Skill.query.filter_by(profile_id=profile.id).all()
    projects = Project.query.filter_by(profile_id=profile.id).all()
    return jsonify({
        'profile':  profile.to_dict(),
        'skills':   [s.to_dict() for s in skills],
        'projects': [p.to_dict() for p in projects],
    })

@profile_bp.route('/add', methods=['POST'])
def add_profile():
    data    = request.get_json()
    profile = Profile.query.first()
    if not profile:
        profile = Profile(
            name=data.get('name'), title=data.get('title'), bio=data.get('bio'),
            email=data.get('email'), phone=data.get('phone'), location=data.get('location'),
        )
    else:
        for field in ('name', 'title', 'bio', 'email', 'phone', 'location'):
            if field in data:
                setattr(profile, field, data[field])
    db.session.add(profile)
    db.session.commit()
    return jsonify(profile.to_dict()), 201

@profile_bp.route('/skill/add', methods=['POST'])
def add_skill():
    data    = request.get_json()
    profile = Profile.query.first()
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    skill = Skill(name=data.get('name'), level=data.get('level'), profile_id=profile.id)
    db.session.add(skill)
    db.session.commit()
    return jsonify(skill.to_dict()), 201

@profile_bp.route('/project/add', methods=['POST'])
def add_project():
    data    = request.get_json()
    profile = Profile.query.first()
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    project = Project(
        title=data.get('title'), description=data.get('description'),
        url=data.get('url'), github_url=data.get('github_url'),
        image_url=data.get('image_url'),
        start_date=data.get('start_date'), end_date=data.get('end_date'),
        profile_id=profile.id,
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
    data = request.get_json()
    skill.name  = data.get('name',  skill.name)
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
    data = request.get_json()
    for field in ('title', 'description', 'url', 'github_url', 'image_url', 'start_date', 'end_date'):
        if field in data:
            setattr(project, field, data[field])
    db.session.commit()
    return jsonify(project.to_dict()), 200

# ── Admin — auth ──────────────────────────────────────────────────────────────
@admin_bp.route('/', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        admin = Admin.query.filter_by(email=email).first()

        if admin and admin.check_password(password):
            session['admin_logged_in'] = True
            session['admin_id'] = admin.id
            session['admin_is_superuser'] = admin.is_superuser
            return redirect(url_for('admin.dashboard'))

        if Admin.query.count() == 0 and email == current_app.config.get('ADMIN_EMAIL') and password == current_app.config.get('ADMIN_PASSWORD'):
            admin = Admin(email=email, is_superuser=True)
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            session['admin_logged_in'] = True
            session['admin_id'] = admin.id
            session['admin_is_superuser'] = True
            return redirect(url_for('admin.dashboard'))

        flash('Incorrect email or password.', 'error')
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_id', None)
    session.pop('admin_is_superuser', None)
    return redirect(url_for('main.index'))

# ── Admin — dashboard ─────────────────────────────────────────────────────────
@admin_bp.route('/dashboard')
def dashboard():
    redir = _admin_required()
    if redir:
        return redir
    profile  = Profile.query.first()
    skills   = Skill.query.all()
    projects = Project.query.all()
    recent   = Content.query.order_by(Content.created_at.desc()).limit(5).all()
    counts   = {
        'total':  Content.query.count(),
        'video':  Content.query.filter_by(content_type='video').count(),
        'meet':   Content.query.filter_by(content_type='meet').count(),
        'pdf':    Content.query.filter_by(content_type='pdf').count(),
        'active': Content.query.filter_by(is_active=True).count(),
    }
    return render_template('admin/dashboard.html',
        profile=profile, skills=skills, projects=projects,
        recent=recent, counts=counts, is_superuser=session.get('admin_is_superuser', False))

@admin_bp.route('/users')
def admin_users():
    redir = _superuser_required()
    if redir:
        return redir
    return render_template('admin/users.html', admins=Admin.query.order_by(Admin.email).all())

@admin_bp.route('/users/add', methods=['GET', 'POST'])
def add_admin():
    redir = _superuser_required()
    if redir:
        return redir
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        if not email or not password:
            flash('Admin email and password are required.', 'error')
            return redirect(url_for('admin.add_admin'))
        if Admin.query.filter_by(email=email).first():
            flash('An admin with that email already exists.', 'error')
            return redirect(url_for('admin.add_admin'))
        admin = Admin(email=email, is_superuser=False)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        flash('Admin user added successfully.', 'success')
        return redirect(url_for('admin.admin_users'))
    return render_template('admin/add_user.html')

# ── Admin — profile / skills / projects (unchanged logic, new templates) ──────
@admin_bp.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    redir = _admin_required()
    if redir:
        return redir
    profile = Profile.query.first()
    if request.method == 'POST':
        if not profile:
            profile = Profile()
        for field in ('name', 'title', 'bio', 'email', 'phone', 'location', 'profile_image_url'):
            setattr(profile, field, request.form.get(field))
        db.session.add(profile)
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/edit_profile.html', profile=profile)

@admin_bp.route('/skills')
def manage_skills():
    redir = _admin_required()
    if redir:
        return redir
    return render_template('admin/skills.html', skills=Skill.query.all())

@admin_bp.route('/skills/add', methods=['GET', 'POST'])
def add_skill():
    redir = _admin_required()
    if redir:
        return redir
    if request.method == 'POST':
        profile = Profile.query.first()
        if not profile:
            flash('Create a profile first.', 'error')
            return redirect(url_for('admin.dashboard'))
        db.session.add(Skill(
            name=request.form.get('name'),
            level=request.form.get('level'),
            profile_id=profile.id,
        ))
        db.session.commit()
        flash('Skill added.', 'success')
        return redirect(url_for('admin.manage_skills'))
    return render_template('admin/add_skill.html')

@admin_bp.route('/skills/<int:skill_id>/edit', methods=['GET', 'POST'])
def edit_skill(skill_id):
    redir = _admin_required()
    if redir:
        return redir
    skill = Skill.query.get_or_404(skill_id)
    if request.method == 'POST':
        skill.name  = request.form.get('name')
        skill.level = request.form.get('level')
        db.session.commit()
        flash('Skill updated.', 'success')
        return redirect(url_for('admin.manage_skills'))
    return render_template('admin/edit_skill.html', skill=skill)

@admin_bp.route('/skills/<int:skill_id>/delete', methods=['POST'])
def delete_skill(skill_id):
    redir = _admin_required()
    if redir:
        return redir
    db.session.delete(Skill.query.get_or_404(skill_id))
    db.session.commit()
    flash('Skill deleted.', 'success')
    return redirect(url_for('admin.manage_skills'))

@admin_bp.route('/projects')
def manage_projects():
    redir = _admin_required()
    if redir:
        return redir
    return render_template('admin/projects.html', projects=Project.query.all())

@admin_bp.route('/projects/add', methods=['GET', 'POST'])
def add_project():
    redir = _admin_required()
    if redir:
        return redir
    if request.method == 'POST':
        profile = Profile.query.first()
        if not profile:
            flash('Create a profile first.', 'error')
            return redirect(url_for('admin.dashboard'))
        db.session.add(Project(
            title=request.form.get('title'),
            description=request.form.get('description'),
            url=request.form.get('url'),
            github_url=request.form.get('github_url'),
            image_url=request.form.get('image_url'),
            start_date=request.form.get('start_date') or None,
            end_date=request.form.get('end_date') or None,
            profile_id=profile.id,
        ))
        db.session.commit()
        flash('Project added.', 'success')
        return redirect(url_for('admin.manage_projects'))
    return render_template('admin/add_project.html')

@admin_bp.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
def edit_project(project_id):
    redir = _admin_required()
    if redir:
        return redir
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        for field in ('title', 'description', 'url', 'github_url', 'image_url'):
            setattr(project, field, request.form.get(field))
        project.start_date = request.form.get('start_date') or None
        project.end_date   = request.form.get('end_date')   or None
        db.session.commit()
        flash('Project updated.', 'success')
        return redirect(url_for('admin.manage_projects'))
    return render_template('admin/edit_project.html', project=project)

@admin_bp.route('/projects/<int:project_id>/delete', methods=['POST'])
def delete_project(project_id):
    redir = _admin_required()
    if redir:
        return redir
    db.session.delete(Project.query.get_or_404(project_id))
    db.session.commit()
    flash('Project deleted.', 'success')
    return redirect(url_for('admin.manage_projects'))

# ── Admin — content management ────────────────────────────────────────────────
@admin_bp.route('/content')
def content_list():
    redir = _admin_required()
    if redir:
        return redir
    filter_type = request.args.get('type', '')
    query = Content.query.order_by(Content.created_at.desc())
    if filter_type:
        query = query.filter_by(content_type=filter_type)
    items = query.all()
    return render_template('admin/content.html', items=items, filter_type=filter_type)

@admin_bp.route('/content/add', methods=['GET', 'POST'])
def add_content():
    redir = _admin_required()
    if redir:
        return redir
    if request.method == 'POST':
        content_type = request.form.get('content_type', 'video')
        url          = request.form.get('url', '').strip()

        # Handle PDF file upload (overrides URL if a file is given)
        if content_type == 'pdf':
            f = request.files.get('pdf_file')
            if f and f.filename and _allowed_file(f.filename):
                url = _save_pdf(f)

        scheduled_at = None
        raw_sched = request.form.get('scheduled_at', '').strip()
        if raw_sched:
            try:
                scheduled_at = datetime.strptime(raw_sched, '%Y-%m-%dT%H:%M')
            except ValueError:
                pass

        item = Content(
            title        = request.form.get('title', '').strip(),
            content_type = content_type,
            url          = url,
            description  = request.form.get('description', '').strip(),
            course_tag   = request.form.get('course_tag', 'general'),
            scheduled_at = scheduled_at,
            is_active    = bool(request.form.get('is_active')),
        )
        db.session.add(item)
        db.session.commit()
        flash('Content posted successfully.', 'success')
        return redirect(url_for('admin.content_list'))

    return render_template('admin/add_content.html', item=None, course_tags=COURSE_TAGS)

@admin_bp.route('/content/<int:item_id>/edit', methods=['GET', 'POST'])
def edit_content(item_id):
    redir = _admin_required()
    if redir:
        return redir
    item = Content.query.get_or_404(item_id)
    if request.method == 'POST':
        item.title        = request.form.get('title', '').strip()
        item.content_type = request.form.get('content_type', item.content_type)
        item.description  = request.form.get('description', '').strip()
        item.course_tag   = request.form.get('course_tag', 'general')
        item.is_active    = bool(request.form.get('is_active'))

        # PDF upload may replace URL
        new_url = request.form.get('url', '').strip()
        if item.content_type == 'pdf':
            f = request.files.get('pdf_file')
            if f and f.filename and _allowed_file(f.filename):
                new_url = _save_pdf(f)
        if new_url:
            item.url = new_url

        raw_sched = request.form.get('scheduled_at', '').strip()
        if raw_sched:
            try:
                item.scheduled_at = datetime.strptime(raw_sched, '%Y-%m-%dT%H:%M')
            except ValueError:
                pass
        else:
            item.scheduled_at = None

        db.session.commit()
        flash('Content updated.', 'success')
        return redirect(url_for('admin.content_list'))

    return render_template('admin/add_content.html', item=item, course_tags=COURSE_TAGS)

@admin_bp.route('/content/<int:item_id>/delete', methods=['POST'])
def delete_content(item_id):
    redir = _admin_required()
    if redir:
        return redir
    db.session.delete(Content.query.get_or_404(item_id))
    db.session.commit()
    flash('Content deleted.', 'success')
    return redirect(url_for('admin.content_list'))

@admin_bp.route('/content/<int:item_id>/toggle', methods=['POST'])
def toggle_content(item_id):
    redir = _admin_required()
    if redir:
        return redir
    item = Content.query.get_or_404(item_id)
    item.is_active = not item.is_active
    db.session.commit()
    return redirect(request.referrer or url_for('admin.content_list'))

# ── Learner portal ────────────────────────────────────────────────────────────
@learn_bp.route('/')
def index():
    filter_type   = request.args.get('type',   '').strip()
    filter_course = request.args.get('course', '').strip()
    query = Content.query.filter_by(is_active=True).order_by(Content.created_at.desc())
    if filter_type:
        query = query.filter_by(content_type=filter_type)
    if filter_course:
        query = query.filter_by(course_tag=filter_course)
    items = query.all()
    counts = {
        'all':   Content.query.filter_by(is_active=True).count(),
        'video': Content.query.filter_by(is_active=True, content_type='video').count(),
        'meet':  Content.query.filter_by(is_active=True, content_type='meet').count(),
        'pdf':   Content.query.filter_by(is_active=True, content_type='pdf').count(),
    }
    return render_template('learn/index.html',
        items=items, filter_type=filter_type, filter_course=filter_course,
        counts=counts, course_tags=COURSE_TAGS)
