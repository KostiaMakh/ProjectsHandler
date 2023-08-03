from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView, TemplateView

from config.constants import EQUIPMENT_TYPES
from .models import Location, Equipment, Position, TechnologicalNode, Complectation, Manufacture
from .forms import (
    CreatePositionForm,
    CreateLocationForm,
    CreateNodeForm,
    CreateEquipmentForm,
    CreateManufactureForm,
    UpdateCompensationForm,
)


class CustomLoginView(LoginView):
    template_name = "login.html"


class ProjectsListView(ListView):
    model = Location
    template_name = 'projects.html'
    context_object_name = 'projects'

    def get_queryset(self):
        queryset = Location.objects.all()
        return queryset


class ProjectsDetailsView(DetailView):
    model = Location
    template_name = 'project_detail.html'
    context_object_name = 'project'

    def get_queryset(self):
        object_slug = self.kwargs.get('slug')
        object_det = Location.objects.filter(slug=object_slug).prefetch_related('nodes')
        return object_det

    def get_context_data(self, **kwargs):
        object_slug = self.kwargs.get('slug')
        context = super().get_context_data(**kwargs)
        context['create_equipment_form'] = CreateEquipmentForm
        context['positions_list'] = Position.objects. \
            filter(technological_node__location__slug=object_slug). \
            prefetch_related('equipment'). \
            order_by('name')
        return context


class DestroyProjectView(DeleteView):
    model = Location
    success_url = reverse_lazy('projects_list')


class EquipmentDetailsView(DetailView):
    model = Equipment
    template_name = 'equipment_details.html'
    context_object_name = 'position'

    def get_queryset(self):
        queryset = Equipment.objects.all().select_related('position')
        return queryset


class EquipmentUpdateView(UpdateView):
    model = Equipment
    template_name = 'update_equipment.html'
    form_class = CreateEquipmentForm
    context_object_name = 'position'

    def get_queryset(self):
        equipment_slug = self.kwargs.get('slug')
        queryset = Equipment.objects.filter(slug=equipment_slug).select_related('position')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['manufactures'] = Manufacture.objects.all()
        context['equipment_type'] = EQUIPMENT_TYPES

        return context

    def post(self, request, *args, **kwargs):
        print(request.POST)
        equipment_slug = self.kwargs.get('slug')
        print(equipment_slug)
        equipment = Equipment.objects.get(slug=equipment_slug)
        equipment_form = CreateEquipmentForm(request.POST, instance=equipment)
        complectation_form = UpdateCompensationForm(request.POST, instance=equipment.complectation)

        if equipment_form.is_valid() and complectation_form.is_valid():
            equipment_form.save()
            complectation_form.save()
            equipment.refresh_from_db()

            return HttpResponseRedirect(reverse_lazy('equipment_details', args=[equipment.slug]))


class CreatePositionView(CreateView):
    model = Position
    form_class = CreatePositionForm
    template_name = 'tt.html'

    def post(self, request, *args, **kwargs):
        form = CreatePositionForm(request.POST)
        if form.is_valid():
            form.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class DestroyPositionView(DeleteView):
    model = Position
    template_name = 'tt.html'
    success_url = reverse_lazy('projects_list')

    def post(self, request, *args, **kwargs):
        position_pk = kwargs.get('pk')
        equipment = Equipment.objects.select_related('position').filter(position__pk=position_pk)
        if equipment:
            equipment.delete()

        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        self.success_url = self.request.META.get('HTTP_REFERER')
        return super().get_success_url()


class CreateLocationView(CreateView):
    model = Location
    form_class = CreateLocationForm
    template_name = 'add_project.html'

    def post(self, request, *args, **kwargs):
        print(request.POST)
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('projects_list'))

        return render(request, self.template_name, {'form': form})


class CreateNodeView(CreateView):
    model = TechnologicalNode
    form_class = CreateNodeForm
    template_name = 'add_project.html'

    def post(self, request, *args, **kwargs):
        print(request.POST)
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class CreateEquipmentView(CreateView):
    model = Equipment
    form_class = CreateEquipmentForm
    template_name = 'create_equipment.html'

    def post(self, request, *args, **kwargs):
        position_pk = kwargs.get('pk')
        position = Position.objects.filter(pk=position_pk).first()
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            complectation = Complectation.objects.create()
            form.instance.complectation = complectation
            form.instance.save()
            position.equipment = form.instance
            position.save()

        print(position.technological_node.location.slug)
        return HttpResponseRedirect(reverse_lazy('project_details', kwargs={'slug': position.technological_node.location.slug}))


class RemoveEquipmentView(DeleteView):
    model = Equipment
    template_name = 'tt.html'

    def get_success_url(self):
        self.success_url = self.request.META.get('HTTP_REFERER')
        return super().get_success_url()


class ManufacturesListView(ListView):
    model = Manufacture
    context_object_name = 'manufactures'
    queryset = Manufacture.objects.all()
    template_name = 'manufacture/manufacture_list.html'


class ManufactureDetailsView(DetailView):
    model = Manufacture
    context_object_name = 'manufacture'
    template_name = 'manufacture/manufacture_details.html'


class ManufactureCreateView(CreateView):
    model = Manufacture
    form_class = CreateManufactureForm
    template_name = 'manufacture/manufacture_create.html'
    success_url = reverse_lazy('manufactures')


class DestroyManufactureView(DeleteView):
    model = Manufacture
    success_url = reverse_lazy('manufactures')


class UpdateLocationView(UpdateView):
    model = Location
    form_class = CreateLocationForm
    template_name = 'add_project.html'


class EquipmentList(ListView):
    model = Equipment
    template_name = 'equipment_list.html'
    context_object_name = 'equipments'

    def get_queryset(self):
        queryset = Equipment.objects.all().prefetch_related('position')

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['locations'] = Location.objects.all()
        context['nodes'] = TechnologicalNode.objects.all().order_by('node_number', 'name')
        context['marks'] = Equipment.objects.all().values('name').distinct().order_by('name')

        return context


class RawSqlView(TemplateView):
    template_name = 'rawsQl.html'


class RawSqlQuery(View):
    def post(self, request, *args, **kwargs):
        sql_code = request.POST.get('sql_code')
        if sql_code:
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute(sql_code)
            row = cursor.fetchall()
            return JsonResponse({'result': row, 'headers': [desc[0] for desc in cursor.description]}, status=200)

        return JsonResponse({}, status=400)
