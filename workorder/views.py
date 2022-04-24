from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from workorder.forms import WorkOrderForm, ItemForm
from workorder.models import WorkOrder, WorkOrderItem
from django.db.models import Count
from django.forms import ModelForm, DateInput
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
import csv
from django.shortcuts import render
from django.http import HttpResponse
from .models import WorkOrder, WorkOrderItem
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required


class DateInput(DateInput):
    input_type = 'date'


class WorkOrderList(LoginRequiredMixin, ListView):
    template_name = "workorder_list.html"
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
        fields = ('status', 'user', 'property', 'completed_date')
        widgets = {
            'completed_date': DateInput(),
        }


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
        assigned_property = form.cleaned_data['property']
        assigned_completed_date = form.cleaned_data['completed_date']
    writer = csv.writer(response)
    writer.writerow(['ID', 'Title', 'Apartment Number', 'Description', 'Skill Set Required'
                        , 'Severity Level', 'Current Status', 'Desired Completion Date', 'Estimated Cost'
                        , 'Assigned Employee', 'Actual Completion Date', 'Actual Cost'])
    if assigned_user and assigned_completed_date and assigned_property is None:
        wo_object = WorkOrder.objects.filter(status=cs_value)
    else:
        wo_object = WorkOrder.objects.filter(status=cs_value, user=assigned_user)

    for wo in wo_object.values_list('id', 'workorder_name', 'apartment__apt_num', 'short_desc', 'skill_set', 'severity',
                                    'status'
            , 'promised_date', 'estimated_cost', 'user__username'
            , 'completed_date', 'actual_cost'):
        writer.writerow(wo)

    response['Content-Disposition'] = 'attachment; filename="workorders.csv"'

    return response


@login_required
def view_pdf(request):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    textobj = c.beginText()
    textobj.setTextOrigin(inch, inch)
    textobj.setFont("Helvetica", 14)

    # orders = WorkOrder.objects.filter(workorder_name=request.user.id)

    orders = WorkOrder.objects.all()

    lines = []

    lines.append("Here is your generated Report!")
    for order in orders:
        # print(order.customer_name)
        lines.append(" ")
        lines.append("Work Order Name: " + "       " + str(order.workorder_name))
        lines.append("Property: " + "              " + str(order.property))
        lines.append("Apartment: " + "             " + str(order.apartment))
        lines.append("Short Description: " + "     " + str(order.short_desc))
        lines.append("Skill Set: " + "             " + str(order.skill_set))
        lines.append("Severity: " + "              " + str(order.severity))
        lines.append("Status: " + "                " + str(order.status))
        lines.append("Promised Date: " + "         " + str(order.promised_date))
        lines.append("Completed Date: " + "        " + str(order.completed_date))
        lines.append("Estimated Cost: " + "        " + str(order.estimated_cost))
        lines.append("Actual Cost: " + "           " + str(order.actual_cost))
        lines.append("Work Order Date: " + "       " + str(order.work_order_date))
        lines.append(" ")

    for line in lines:
        textobj.textLine(line)

    c.drawText(textobj)
    c.showPage()
    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename='report.pdf')
