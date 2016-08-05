from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from hijack_admin.admin import HijackUserAdminMixin


class IdsUserAdmin(UserAdmin, HijackUserAdminMixin):

    list_display = ('username',
                    'email',
                    'first_name',
                    'last_name',
                    'is_staff',
                    'hijack_field',)

admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), IdsUserAdmin)
