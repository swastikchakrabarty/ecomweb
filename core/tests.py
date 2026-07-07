from django.test import TestCase
from django.urls import reverse
from core.models import User, Employee, Product, ContactMessage, Blog, ProductMedia, Order, OrderItem
from core.forms import ContactForm


class CoreModelsTestCase(TestCase):
    def setUp(self):
        # Create users
        self.admin = User.objects.create_user(username='admin_test', password='password', role='admin')
        self.employee_user = User.objects.create_user(username='employee_test', password='password', role='employee')
        self.regular_user = User.objects.create_user(username='user_test', password='password', role='user')
        
        # Create employee profile
        self.employee = Employee.objects.create(
            user=self.employee_user,
            employee_id='EMP999',
            designation='Field Associate'
        )

        # Create product
        self.product = Product.objects.create(
            name='Test Tea',
            subtitle_tagline='Healthy Drink',
            description='A test tea description.',
            total_quantity_info='100g',
            ingredients='Ingredient 1, Ingredient 2',
            key_benefits='Benefit 1\nBenefit 2',
            price=299.00,
            is_active=True
        )

    def test_user_roles(self):
        self.assertEqual(self.admin.role, 'admin')
        self.assertEqual(self.employee_user.role, 'employee')
        self.assertEqual(self.regular_user.role, 'user')
        self.assertIn('admin', str(self.admin))

    def test_employee_profile(self):
        self.assertEqual(self.employee.employee_id, 'EMP999')
        self.assertEqual(self.employee.designation, 'Field Associate')
        self.assertEqual(self.employee.user.username, 'employee_test')
        self.assertIn('EMP999', str(self.employee))

    def test_product_fields(self):
        self.assertEqual(self.product.name, 'Test Tea')
        self.assertEqual(self.product.subtitle_tagline, 'Healthy Drink')
        self.assertTrue(self.product.is_active)
        self.assertEqual(str(self.product), 'Test Tea')

    def test_product_price_and_media(self):
        self.assertEqual(self.product.price, 299.00)
        
        # Test additional media association
        media = ProductMedia.objects.create(
            product=self.product,
            media_type='video',
            embed_url='https://www.youtube.com/embed/dQw4w9WgXcQ'
        )
        self.assertEqual(self.product.additional_media.count(), 1)
        self.assertEqual(self.product.additional_media.first().embed_url, 'https://www.youtube.com/embed/dQw4w9WgXcQ')
        
        # Test media_list_json property
        import json
        media_list = json.loads(self.product.media_list_json)
        self.assertEqual(len(media_list), 1)
        self.assertEqual(media_list[0]['type'], 'video')
        self.assertEqual(media_list[0]['url'], 'https://www.youtube.com/embed/dQw4w9WgXcQ')


class CoreViewsTestCase(TestCase):
    def setUp(self):
        # Create users
        self.admin = User.objects.create_user(username='admin_user', password='password123', role='admin')
        self.employee_user = User.objects.create_user(username='emp_user', password='password123', role='employee')
        self.regular_user = User.objects.create_user(username='reg_user', password='password123', role='user')
        
        # Create profile
        Employee.objects.create(user=self.employee_user, employee_id='EMP888', designation='Tester')

        # Create product
        self.product = Product.objects.create(
            name='Tulsi Tea',
            description='Organic Tulsi',
            ingredients='Tulsi',
            key_benefits='Anti-stress',
            is_active=True,
            stock=10,
            is_best_seller=True
        )

    def test_home_page_renders(self):
        from django.conf import settings
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tulsi Tea')
        self.assertContains(response, 'Empower Your')
        self.assertContains(response, 'Sleep Optimization')
        self.assertEqual(response.context['upi_id'], settings.UPI_ID)
        self.assertEqual(response.context['merchant_name'], settings.MERCHANT_NAME)

    def test_contact_form_submission(self):
        post_data = {
            'name': 'John Doe',
            'email': 'john@test.com',
            'phone': '1234567890',
            'message': 'Hello, I want to inquire about Tulsi Tea.'
        }
        response = self.client.post(reverse('home'), post_data)
        self.assertEqual(response.status_code, 302)  # Redirects to home on success
        
        # Check DB
        msg = ContactMessage.objects.first()
        self.assertIsNotNone(msg)
        self.assertEqual(msg.name, 'John Doe')
        self.assertEqual(msg.email, 'john@test.com')

    def test_contact_form_validation(self):
        # Invalid email
        post_data = {
            'name': 'John Doe',
            'email': 'not-an-email',
            'phone': '1234567890',
            'message': 'Hello'
        }
        form = ContactForm(data=post_data)
        self.assertFalse(form.is_valid())

    def test_login_and_dashboard_redirects(self):
        # Unauthenticated users accessing dashboard should redirect to login
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

        # Regular user dashboard access
        self.client.login(username='reg_user', password='password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Customer Account')
        self.client.logout()

        # Admin user dashboard access
        self.client.login(username='admin_user', password='password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin Workspace')
        self.assertContains(response, 'Product Inventory')
        self.client.logout()

    def test_staff_dashboard_crud_permissions(self):
        # Regular user should not be able to access product creation
        self.client.login(username='reg_user', password='password123')
        response = self.client.get(reverse('product_create'))
        self.assertEqual(response.status_code, 403) # PermissionDenied returns 403
        self.client.logout()

        # Admin user can access product creation page
        self.client.login(username='admin_user', password='password123')
        response = self.client.get(reverse('product_create'))
        self.assertEqual(response.status_code, 200)
        self.client.logout()


class EmployeeCrudAndRbacTestCase(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin_staff', password='password', role='admin')
        self.employee_user = User.objects.create_user(username='emp_staff', password='password', role='employee')
        self.regular_user = User.objects.create_user(username='user_staff', password='password', role='user')
        
        self.employee = Employee.objects.create(
            user=self.employee_user,
            employee_id='EMP001',
            designation='Specialist'
        )

    def test_admin_can_create_employee(self):
        self.client.login(username='admin_staff', password='password')
        post_data = {
            'username': 'new_emp',
            'first_name': 'New',
            'last_name': 'Employee',
            'email': 'new@kaanuro.com',
            'password': 'password123',
            'employee_id': 'EMP100',
            'designation': 'Specialist'
        }
        response = self.client.post(reverse('employee_create'), post_data)
        self.assertEqual(response.status_code, 302)  # Redirects to dashboard
        
        # Verify db
        user_exists = User.objects.filter(username='new_emp').exists()
        emp_exists = Employee.objects.filter(employee_id='EMP100').exists()
        self.assertTrue(user_exists)
        self.assertTrue(emp_exists)
        
        user = User.objects.get(username='new_emp')
        self.assertEqual(user.role, 'employee')
        self.assertEqual(user.employee.designation, 'Specialist')
        self.client.logout()

    def test_employee_cannot_create_employee(self):
        self.client.login(username='emp_staff', password='password')
        post_data = {
            'username': 'bad_emp',
            'first_name': 'Bad',
            'last_name': 'Employee',
            'email': 'bad@kaanuro.com',
            'password': 'password123',
            'employee_id': 'EMP200',
            'designation': 'Specialist'
        }
        response = self.client.post(reverse('employee_create'), post_data)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(User.objects.filter(username='bad_emp').exists())
        self.client.logout()

    def test_regular_user_cannot_create_employee(self):
        self.client.login(username='user_staff', password='password')
        post_data = {
            'username': 'bad_emp2',
            'first_name': 'Bad2',
            'last_name': 'Employee2',
            'email': 'bad2@kaanuro.com',
            'password': 'password123',
            'employee_id': 'EMP300',
            'designation': 'Specialist'
        }
        response = self.client.post(reverse('employee_create'), post_data)
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_admin_can_delete_employee(self):
        self.client.login(username='admin_staff', password='password')
        response = self.client.post(reverse('employee_delete', args=[self.employee.pk]))
        self.assertEqual(response.status_code, 302)  # Redirects to dashboard
        
        # Verify both Employee and associated User are deleted
        self.assertFalse(Employee.objects.filter(pk=self.employee.pk).exists())
        self.assertFalse(User.objects.filter(pk=self.employee_user.pk).exists())
        self.client.logout()

    def test_employee_cannot_delete_employee(self):
        self.client.login(username='emp_staff', password='password')
        response = self.client.get(reverse('employee_delete', args=[self.employee.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Employee.objects.filter(pk=self.employee.pk).exists())
        self.client.logout()


class OrderCheckoutTestCase(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin_staff_test', password='password', role='admin')
        self.regular_user = User.objects.create_user(username='user_staff_test', password='password', role='user')
        self.product1 = Product.objects.create(name='Test Tea 1', price=299.00, is_active=True)
        self.product2 = Product.objects.create(name='Test Tea 2', price=299.00, is_active=True)
        
    def test_order_creation_success(self):
        self.client.login(username='user_staff_test', password='password')
        import uuid
        order_uuid = str(uuid.uuid4())
        payload = {
            'order_id': order_uuid,
            'customer_name': 'Rajesh Kumar',
            'phone_number': '+919999999999',
            'shipping_address': 'Street 1, Locality 2, Udaipurwati, Rajasthan - 333307',
            'total_amount': '598.00',
            'utr_number': '123456789012',
            'items': [
                {'id': f"prod_{self.product1.pk}", 'name': 'Test Tea 1', 'quantity': 1, 'price': 299.00},
                {'id': f"prod_{self.product2.pk}", 'name': 'Test Tea 2', 'quantity': 1, 'price': 299.00}
            ]
        }
        import json
        response = self.client.post(
            reverse('checkout_order_create'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verify db
        order = Order.objects.get(order_id=order_uuid)
        self.assertEqual(order.customer_name, 'Rajesh Kumar')
        self.assertEqual(order.utr_number, '123456789012')
        self.assertEqual(order.items.count(), 2)
        self.assertEqual(order.items.first().product_name, 'Test Tea 1')
        self.client.logout()

    def test_order_creation_invalid_payload(self):
        self.client.login(username='user_staff_test', password='password')
        # Missing utr_number
        import uuid
        payload = {
            'order_id': str(uuid.uuid4()),
            'customer_name': 'Rajesh Kumar',
            'phone_number': '+919999999999',
            'shipping_address': 'Street 1, Locality 2, Udaipurwati, Rajasthan - 333307',
            'items': [
                {'id': f"prod_{self.product1.pk}", 'name': 'Test Tea 1', 'quantity': 1, 'price': 299.00}
            ]
        }
        import json
        response = self.client.post(
            reverse('checkout_order_create'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Order.objects.exists())
        self.client.logout()

    def test_order_phone_normalization_and_dashboard_sync(self):
        import uuid
        import json
        
        # Create a user representing a customer that logs in via OTP
        customer_phone = '9876543210'
        customer_username = f"cust_{customer_phone}"
        customer_user = User.objects.create_user(username=customer_username, password='password123', role='user')
        
        # Log in customer
        self.client.login(username=customer_username, password='password123')

        # Create an order with country prefix and spaces
        order_uuid = str(uuid.uuid4())
        payload = {
            'order_id': order_uuid,
            'customer_name': 'Rajesh Kumar',
            'phone_number': ' +91 98765 43210 ',
            'shipping_address': 'Street 1, Locality 2, Udaipurwati, Rajasthan - 333307',
            'total_amount': '299.00',
            'utr_number': '123456789012',
            'items': [
                {'id': f"prod_{self.product1.pk}", 'name': 'Test Tea 1', 'quantity': 1, 'price': 299.00}
            ]
        }
        
        # Submit the order
        response = self.client.post(
            reverse('checkout_order_create'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        
        # Verify it was normalized in the database
        order = Order.objects.get(order_id=order_uuid)
        self.assertEqual(order.phone_number, '9876543210')
        
        # Verify dashboard sync
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Assert dashboard context has the normalized order
        orders_in_context = response.context['orders']
        self.assertEqual(len(orders_in_context), 1)
        self.assertEqual(orders_in_context[0].order_id, order.order_id)
        
        self.client.logout()

    def test_order_status_update_rbac(self):
        import uuid
        order = Order.objects.create(
            order_id=uuid.uuid4(),
            customer_name='Rajesh Kumar',
            phone_number='+919999999999',
            shipping_address='Udaipurwati',
            total_amount=299.00,
            utr_number='123456789012',
            status='pending'
        )
        
        # Unauthorized update
        self.client.login(username='user_staff_test', password='password')
        response = self.client.post(
            reverse('order_update_status', args=[order.pk]),
            {'status': 'processing'}
        )
        self.assertEqual(response.status_code, 403)
        order.refresh_from_db()
        self.assertEqual(order.status, 'pending')
        self.client.logout()

        # Authorized update
        self.client.login(username='admin_staff_test', password='password')
        response = self.client.post(
            reverse('order_update_status', args=[order.pk]),
            {'status': 'processing'}
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, 'processing')
        self.client.logout()


from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from core.models import CustomerProfile, Invoice, Order, OrderItem

class CustomerAuthAndInvoiceTestCase(TestCase):
    def setUp(self):
        # Create users
        self.admin = User.objects.create_user(username='admin_customer_test', password='password', role='admin')
        self.employee_user = User.objects.create_user(username='employee_customer_test', password='password', role='employee')
        
        # Create a regular customer user
        self.customer_user = User.objects.create_user(username='cust_9876543210', password='password', role='user')
        self.customer_profile = CustomerProfile.objects.create(user=self.customer_user, phone_number='9876543210', shipping_address='Test Lane, Delhi')
        
        # Create another regular customer user
        self.other_customer = User.objects.create_user(username='cust_8888888888', password='password', role='user')
        self.other_profile = CustomerProfile.objects.create(user=self.other_customer, phone_number='8888888888')

        # Create products
        self.product = Product.objects.create(
            name='Test Herbal Tea',
            price=150.00,
            is_active=True
        )

    def test_customer_profile_and_invoice_models(self):
        # Check profiles
        self.assertEqual(self.customer_profile.phone_number, '9876543210')
        self.assertEqual(self.customer_profile.shipping_address, 'Test Lane, Delhi')
        self.assertEqual(str(self.customer_profile), 'Customer profile: 9876543210')
        
        # Check invoice
        import uuid
        o_uuid = uuid.uuid4()
        order = Order.objects.create(
            order_id=o_uuid,
            customer_name='Test Cust',
            phone_number='9876543210',
            shipping_address='Test Lane',
            total_amount=150.00,
            utr_number='123456789012',
            status='pending'
        )
        invoice = Invoice.objects.create(invoice_number='INV-TEST-001', order=order)
        self.assertEqual(invoice.invoice_number, 'INV-TEST-001')
        self.assertEqual(invoice.order, order)
        self.assertEqual(str(invoice), f'Receipt INV-TEST-001 for Order {o_uuid}')

    def test_otp_send_view(self):
        # Invalid phone
        response = self.client.post(reverse('otp_send'), {'phone': '123'}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        # Valid phone (New)
        response = self.client.post(reverse('otp_send'), {'phone': '9999999999'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('code', data)
        self.assertTrue(data['is_new'])
        
        # Valid phone (Existing customer - self.customer_profile phone is '9876543210')
        response = self.client.post(reverse('otp_send'), {'phone': '9876543210'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertFalse(data['is_new'])
        
        # Check session
        session = self.client.session
        self.assertEqual(session['otp_code'], data['code'])
        self.assertEqual(session['otp_phone'], '9876543210')

    def test_otp_verify_view_success_creates_user(self):
        # First send OTP
        self.client.post(reverse('otp_send'), {'phone': '7777777777'}, content_type='application/json')
        session = self.client.session
        code = session['otp_code']
        
        # Verify with wrong code
        response = self.client.post(reverse('otp_verify'), {'phone': '7777777777', 'code': '0000'}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        # Verify with correct code
        response = self.client.post(reverse('otp_verify'), {'phone': '7777777777', 'code': code}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['redirect_url'], '/dashboard/')
        
        # Assert user and profile exist
        user = User.objects.get(username='cust_7777777777')
        self.assertEqual(user.role, 'user')
        profile = CustomerProfile.objects.get(user=user)
        self.assertEqual(profile.phone_number, '7777777777')
        
        # Check that user is logged in
        self.assertIn('_auth_user_id', self.client.session)

    def test_otp_verify_view_with_fullname(self):
        # Send OTP
        self.client.post(reverse('otp_send'), {'phone': '7777777700'}, content_type='application/json')
        session = self.client.session
        code = session['otp_code']
        
        # Verify with correct code and fullname
        response = self.client.post(reverse('otp_verify'), {
            'phone': '7777777700',
            'code': code,
            'fullname': 'Rahul Sharma'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Assert user exists with first name and last name
        user = User.objects.get(username='cust_7777777700')
        self.assertEqual(user.first_name, 'Rahul')
        self.assertEqual(user.last_name, 'Sharma')
        self.assertEqual(user.get_full_name(), 'Rahul Sharma')

    def test_checkout_automated_invoice_generation(self):
        import uuid
        o_uuid = str(uuid.uuid4())
        post_data = {
            'order_id': o_uuid,
            'customer_name': 'Test Checkout Cust',
            'phone_number': '9876543210',
            'shipping_address': 'Delhi, India',
            'total_amount': 300.00,
            'utr_number': '123456789012',
            'items': [
                {'id': f"prod_{self.product.pk}", 'name': 'Test Herbal Tea', 'quantity': 2, 'price': 150.00}
            ]
        }
        self.client.login(username='cust_9876543210', password='password')
        response = self.client.post(reverse('checkout_order_create'), post_data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        
        # Check that Order, OrderItem and Invoice exist
        order = Order.objects.get(order_id=o_uuid)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().product_name, 'Test Herbal Tea')
        
        self.assertEqual(order.status, 'confirmed')
        self.assertTrue(hasattr(order, 'invoice'))
        invoice = order.invoice
        self.assertTrue(invoice.invoice_number.startswith('INV-'))
        self.assertTrue(invoice.pdf_file.name.endswith('.pdf'))
        
        # Read the file content
        content = invoice.pdf_file.read().decode('utf-8')
        self.assertIn('Test Checkout Cust', content)
        self.assertIn('9876543210', content)
        self.assertIn('123456789012', content)

    def test_download_invoice_view_permissions(self):
        # Create an order and invoice (no pdf_file needed — view now returns HTML)
        import uuid
        order = Order.objects.create(
            order_id=uuid.uuid4(),
            customer_name='Rajesh',
            phone_number='9876543210',
            shipping_address='Udaipurwati',
            total_amount=150.00,
            utr_number='123456789012',
            status='confirmed',
            user=self.customer_user
        )
        invoice = Invoice.objects.create(invoice_number='INV-DOWNLOAD-123', order=order)

        # Case 1: Unauthenticated user -> redirect to login
        response = self.client.get(reverse('download_invoice', args=[order.pk]))
        self.assertEqual(response.status_code, 302)

        # Case 2: Different customer user -> Forbidden (PermissionDenied returns 403)
        self.client.login(username='cust_8888888888', password='password')
        response = self.client.get(reverse('download_invoice', args=[order.pk]))
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        # Case 3: Matching customer user -> Success (returns HTML invoice page, status 200)
        self.client.login(username='cust_9876543210', password='password')
        response = self.client.get(reverse('download_invoice', args=[order.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response['Content-Type'])
        self.assertContains(response, 'INV-DOWNLOAD-123')
        self.client.logout()

        # Case 4: Employee user -> Success (returns HTML invoice page, status 200)
        self.client.login(username='employee_customer_test', password='password')
        response = self.client.get(reverse('download_invoice', args=[order.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response['Content-Type'])
        self.client.logout()

        # Case 5: Admin user -> Success (returns HTML invoice page, status 200)
        self.client.login(username='admin_customer_test', password='password')
        response = self.client.get(reverse('download_invoice', args=[order.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response['Content-Type'])
        self.client.logout()

    def test_dashboard_view_isolation(self):
        # Case 1: Admin log in -> can see customer profiles in context
        self.client.login(username='admin_customer_test', password='password')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('customer_profiles', response.context)
        self.assertEqual(len(response.context['customer_profiles']), 2)
        self.client.logout()

        # Case 2: Employee log in -> can NOT see customer profiles in context
        self.client.login(username='employee_customer_test', password='password')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('customer_profiles', response.context)
        self.client.logout()


class LegalDocumentTestCase(TestCase):
    def test_legal_document_model(self):
        from core.models import LegalDocument
        doc = LegalDocument.objects.create(
            doc_type='PRIVACY_POLICY',
            title='Privacy Policy',
            content='# Heading 1\nSome paragraph.'
        )
        self.assertEqual(str(doc), 'Privacy Policy')

    def test_legal_document_view_fallback_seeding(self):
        # View should auto-create document if it doesn't exist
        response = self.client.get(reverse('legal_document', args=['privacy-policy']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Privacy Policy')
        
        # Verify markdown parsing worked (should render as HTML heading/paragraph)
        self.assertContains(response, '<h1>Privacy Policy</h1>')

    def test_legal_document_view_with_content(self):
        from core.models import LegalDocument
        LegalDocument.objects.create(
            doc_type='TERMS_OF_SERVICE',
            title='Custom Terms',
            content='## 1. Rules\n* First rule\n* Second rule'
        )
        response = self.client.get(reverse('legal_document', args=['terms-of-service']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Custom Terms')
        self.assertContains(response, '<h2>1. Rules</h2>')
        self.assertContains(response, '<li>First rule</li>')


class NavbarGreetingTestCase(TestCase):
    def setUp(self):
        # 1. Superuser
        self.superuser = User.objects.create_superuser(username='super_user_test', email='super@test.com', password='password')
        
        # 2. Staff user
        self.staff_with_name = User.objects.create_user(
            username='staff_name_test',
            first_name='Vikram',
            password='password',
            is_staff=True
        )
        self.staff_without_name = User.objects.create_user(
            username='staff_noname_test',
            password='password',
            is_staff=True
        )
        
        # 3. Regular customer (is_staff=False, is_superuser=False)
        self.customer_with_name = User.objects.create_user(
            username='cust_name_test',
            first_name='Amit',
            password='password'
        )
        self.customer_without_name = User.objects.create_user(
            username='cust_noname_test',
            password='password'
        )

    def test_navbar_greeting_guest(self):
        # Unauthenticated user
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello, Guest')

    def test_navbar_greeting_superuser(self):
        # Logged in as superuser
        self.client.login(username='super_user_test', password='password')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello, Admin')
        self.client.logout()

    def test_navbar_greeting_staff(self):
        # Logged in as staff with first name
        self.client.login(username='staff_name_test', password='password')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello, Vikram')
        self.client.logout()

        # Logged in as staff without first name (should fallback to username)
        self.client.login(username='staff_noname_test', password='password')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello, staff_noname_test')
        self.client.logout()

    def test_navbar_greeting_customer(self):
        # Logged in as regular customer with first name
        self.client.login(username='cust_name_test', password='password')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello, Amit')
        self.client.logout()

        # Logged in as regular customer without first name
        self.client.login(username='cust_noname_test', password='password')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello, Customer')
        self.client.logout()







