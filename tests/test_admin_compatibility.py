import unittest
from app import create_app, db
from app.models import Profile

class AdminCompatibilityTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
            db.session.remove()

    def test_admin_dashboard_requires_login(self):
        response = self.client.get('/admin/dashboard', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/', response.headers['Location'])

    def test_admin_login_with_correct_password(self):
        response = self.client.post('/admin/', data={
            'email': 'joseyusuf0@gmail.com',
            'password': 'admin@1234',
        }, follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/dashboard', response.headers['Location'])

    def test_admin_login_with_bad_password_shows_error(self):
        response = self.client.post('/admin/', data={
            'email': 'joseyusuf0@gmail.com',
            'password': 'wrongpass',
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Incorrect email or password.', response.data)

    def test_public_profile_api_still_works(self):
        profile_payload = {
            'name': 'Test User',
            'title': 'Software Engineer',
            'bio': 'Testing backward compatibility.',
            'email': 'test@example.com',
            'phone': '123-456-7890',
            'location': 'Test City',
        }

        response = self.client.post('/profile/add', json=profile_payload)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['name'], profile_payload['name'])
        self.assertEqual(data['email'], profile_payload['email'])

        skill_response = self.client.post('/profile/skill/add', json={'name': 'Python', 'level': 'Advanced'})
        self.assertEqual(skill_response.status_code, 201)
        skill_data = skill_response.get_json()
        self.assertEqual(skill_data['name'], 'Python')
        self.assertEqual(skill_data['level'], 'Advanced')

        project_response = self.client.post('/profile/project/add', json={
            'title': 'Test Project',
            'description': 'A backwards compatible project.',
            'url': 'https://example.com',
            'github_url': 'https://github.com/example',
            'image_url': None,
            'start_date': None,
            'end_date': None,
        })
        self.assertEqual(project_response.status_code, 201)
        project_data = project_response.get_json()
        self.assertEqual(project_data['title'], 'Test Project')

        self.assertEqual(self.client.get('/profile/').status_code, 200)
        payload = self.client.get('/profile/').get_json()
        self.assertIn('profile', payload)
        self.assertIn('skills', payload)
        self.assertIn('projects', payload)
        self.assertEqual(len(payload['skills']), 1)
        self.assertEqual(len(payload['projects']), 1)

    def test_admin_routes_require_login_after_successful_login(self):
        with self.client as client:
            login = client.post('/admin/', data={
                'email': 'joseyusuf0@gmail.com',
                'password': 'admin@1234',
            }, follow_redirects=True)
            self.assertEqual(login.status_code, 200)
            self.assertIn(b'Dashboard', login.data)

            response = client.get('/admin/skills')
            self.assertEqual(response.status_code, 200)

    def test_superuser_can_add_admin_and_new_admin_can_login(self):
        with self.client as client:
            login = client.post('/admin/', data={
                'email': 'joseyusuf0@gmail.com',
                'password': 'admin@1234',
            }, follow_redirects=True)
            self.assertEqual(login.status_code, 200)
            self.assertIn(b'Dashboard', login.data)

            add_response = client.post('/admin/users/add', data={
                'email': 'newadmin@example.com',
                'password': 'newpass123',
            }, follow_redirects=True)
            self.assertEqual(add_response.status_code, 200)
            self.assertIn(b'Admin user added successfully.', add_response.data)

            logout = client.get('/admin/logout', follow_redirects=True)
            self.assertEqual(logout.status_code, 200)

            new_login = client.post('/admin/', data={
                'email': 'newadmin@example.com',
                'password': 'newpass123',
            }, follow_redirects=True)
            self.assertEqual(new_login.status_code, 200)
            self.assertIn(b'Dashboard', new_login.data)

if __name__ == '__main__':
    unittest.main()
