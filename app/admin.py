# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import *


@admin.register(InvestigationType)
class InvestigationTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass


@admin.register(ElementType)
class ElementTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Element)
class ElementAdmin(admin.ModelAdmin):
    pass


@admin.register(ElementFieldDescriptor)
class ElementFieldDescriptorAdmin(admin.ModelAdmin):
    pass


@admin.register(ElementCharFieldValue)
class ElementCharFieldValueAdmin(admin.ModelAdmin):
    pass


@admin.register(ElementTextFieldValue)
class ElementTextFieldValueAdmin(admin.ModelAdmin):
    pass


@admin.register(ElementDateFieldValue)
class ElementDateFieldValueAdmin(admin.ModelAdmin):
    pass


@admin.register(ElementUrlFieldValue)
class ElementUrlFieldValueAdmin(admin.ModelAdmin):
    pass
