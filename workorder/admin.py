from django.contrib import admin
from .models import WorkOrder, WorkOrderItem


class WorkOrderAdmin(admin.ModelAdmin):
    model = WorkOrder
    list_display = ['workorder_name', 'property', 'apartment', 'short_desc', 'skill_set', 'severity', 'status',
                    'promised_date', 'completed_date', 'estimated_cost', 'actual_cost', 'work_order_date',
                    'get_user_username']
    list_filter = ['apartment__apartment_name', 'skill_set', 'severity', 'status', 'promised_date',
                   'work_order_date', 'completed_date', 'user__username']
    fieldset = (
        ('Work Order', {
            'fields': ('workorder_name', 'property_id', 'apartment_id', 'short_desc', 'skill_set', 'severity',
                       'status', 'promised_date', 'completed_date', 'estimated_cost',
                       'actual_cost', 'work_order_date', 'user_id')
        })
    )
    add_fieldset = (
        ('Work Order', {
            'fields': ('workorder_name', 'property_id', 'apartment_id', 'short_desc', 'skill_set', 'severity',
                       'status', 'promised_date', 'completed_date', 'estimated_cost',
                       'actual_cost', 'work_order_date', 'user_id')
        })
    )

    def get_apartment_name(self, obj):
        return obj.apartment.apartment_name

    get_apartment_name.admin_order_field = 'apartment_name'
    get_apartment_name.short_description = 'Apartment Name'

    def get_user_username(self, obj):
        return obj.user.username

    get_user_username.admin_order_field = 'user_name'
    get_user_username.short_description = 'User Name'


class WorkOrderItemAdmin(admin.ModelAdmin):
    model = WorkOrderItem
    list_display = ['item_name', 'item_cost', 'item_quantity', 'get_workorder', 'work_order_id']
    list_filter = ['item_name', 'work_order_id']
    fieldset = (
        ('Work Order Item Information', {
            'fields': ('item_name', 'item_cost', 'item_quantity', 'work_order_id')
        })
    )
    add_fieldset = (
        ('Work Order Item Information', {
            'fields': ('item_name', 'item_cost', 'item_quantity', 'work_order_id')
        })
    )

    def get_workorder(self, obj):
        return obj.workorder.workorder_name

    get_workorder.admin_order_field = 'workorder_name'
    get_workorder.short_description = 'Work Order'


admin.site.register(WorkOrder, WorkOrderAdmin)
admin.site.register(WorkOrderItem, WorkOrderItemAdmin)
