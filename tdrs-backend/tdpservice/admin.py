from django.contrib.admin import AdminSite


class MyAdminSite(AdminSite):
    login_template = 'backoffice/templates/admin/login.html'


site = MyAdminSite()
