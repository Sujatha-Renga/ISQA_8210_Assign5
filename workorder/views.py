from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from workorder.forms import WorkOrderForm, ItemForm
from workorder.models import WorkOrder, WorkOrderItem
from django.db.models import Count

import csv
from django.shortcuts import render
from django.http import HttpResponse
from .models import WorkOrder, WorkOrderItem

from django.contrib.admin.views.decorators import staff_member_required


class WorkOrderList(LoginRequiredMixin, ListView):
    template_name = "workorder/workorder_list.html"
    model = WorkOrder

    def get_context_data(self, **kwargs):
        context = super(WorkOrderList, self).get_context_data(**kwargs)
        context["orders"] = WorkOrder.objects.all()
        return context


class CreateWorkOrder(LoginRequiredMixin, CreateView):
    template_name = "workorder/create_workorder.html"
    model = WorkOrder
    form_class = WorkOrderForm
    success_url = reverse_lazy("workorder_list")


class UpdateWorkOrder(LoginRequiredMixin, UpdateView):
    template_name = "workorder/update_workorder.html"
    model = WorkOrder
    form_class = WorkOrderForm
    success_url = reverse_lazy("workorder_list")


class WorkOrderDetail(LoginRequiredMixin, DetailView):
    template_name = "workorder/workorder_detail.html"
    model = WorkOrder

    def get_context_data(self, **kwargs):
        context = super(WorkOrderDetail, self).get_context_data(**kwargs)
        context["items"] = WorkOrderItem.objects.filter(work_order=self.object)
        return context


class DeleteWorkOrder(LoginRequiredMixin, DeleteView):
    template_name = "workorder/delete_workorder.html"
    model = WorkOrder
    fields = "__all__"
    success_url = reverse_lazy("workorder_list")


class CreateWorkOrderItems(LoginRequiredMixin, CreateView):
    template_name = "workorder/items/create.html"
    model = WorkOrderItem
    form_class = ItemForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request, 'work_id': self.kwargs['work_order_id']})
        return kwargs

    def get_success_url(self, **kwargs):
        return reverse_lazy('order_detail', kwargs={'pk': self.kwargs['work_order_id']})


class UpdateWorkOrderItems(LoginRequiredMixin, UpdateView):
    template_name = "workorder/items/update.html"
    model = WorkOrderItem
    fields = ('item_name', 'item_cost', 'item_quantity')
    success_url = reverse_lazy("home")

    def get_success_url(self, **kwargs):
        return reverse_lazy('order_detail', kwargs={'pk': self.object.work_order_id})


class DeleteWorkOrderItems(LoginRequiredMixin, DeleteView):
    template_name = "workorder/items/delete.html"
    model = WorkOrderItem
    fields = "__all__"

    def get_success_url(self, **kwargs):
        return reverse_lazy('order_detail', kwargs={'pk': self.object.work_order.id})


class ExportFilterForms(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = ('status', 'user')


@staff_member_required
def export_filter_work(request):
    template_name = "workorder/workorderfilter.html"
    form_class = ExportFilterForms()
    return render(request, template_name, {'form': form_class})


@staff_member_required
def export_work_orders(request):
    form = ExportFilterForms(request.POST)
    response = HttpResponse(content_type='text/csv')
    if form.is_valid():
        cs_value = form.cleaned_data['status']
        assigned_user = form.cleaned_data['user']

    writer = csv.writer(response)
    writer.writerow(['ID', 'Title', 'Apartment Number', 'Description', 'Skill Set Required'
                        , 'Severity Level', 'Current Status', 'Desired Completion Date', 'Estimated Cost'
                        , 'Assigned Employee', 'Actual Completion Date', 'Actual Cost'])
    if assigned_user is None:
        wo_object = WorkOrder.objects.filter(current_status=cs_value)
    else:
        wo_object = WorkOrder.objects.filter(current_status=cs_value, user=assigned_user)

    for wo in wo_object.values_list('id', 'work_order_name', 'apartment__apt_num', 'description'
            , 'skillset_required', 'severity_level', 'current_status'
            , 'desired_completion_date', 'estimated_cost', 'user__username'
            , 'actual_completion_date', 'actual_cost'):
        writer.writerow(wo)

    response['Content-Disposition'] = 'attachment; filename="workorders.csv"'

    return response


@staff_member_required
def export_work_order_items(request):
    response = HttpResponse(content_type='text/csv')

    writer = csv.writer(response)
    writer.writerow(['Work Order Id', 'Work Order Title', 'Item ID', 'Item Name', 'Cost', 'Quantity'])

    for woi in WorkOrderItem.objects.all().values_list('work_order__id', 'work_order__work_order_name', 'id',
                                                       'item_name', 'item_cost', 'item_quantity'):
        writer.writerow(woi)

    response['Content-Disposition'] = 'attachment; filename="workorderitems.csv"'

    return response
