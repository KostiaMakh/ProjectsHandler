import csv
from datetime import datetime

from django.contrib.auth.views import LoginView
from django.db.models import (
    Sum,
    Count,
    Avg,
    Max,
    Min,
    F,
    ExpressionWrapper,
    DecimalField,
    DateTimeField,
)
from django.db.models.functions import TruncMonth
from django.http import (
    HttpResponseRedirect,
    JsonResponse, HttpResponse,
)
from django.shortcuts import (
    redirect,
    render,
)
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    DeleteView,
    UpdateView,
    TemplateView,
)

from config.constants import EQUIPMENT_TYPES
from .filters import (
    EquipmentFilter,
    EquipmentStatisticFilter
)
from .models import (
    Location,
    Equipment,
    Position,
    TechnologicalNode,
    Complectation,
    Manufacture,
)
from .forms import (
    CreatePositionForm,
    CreateLocationForm,
    CreateNodeForm,
    CreateEquipmentForm,
    CreateManufactureForm,
    UpdateCompensationForm,
)
from .tasks import send_report


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
        equipment_slug = self.kwargs.get('slug')
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
            send_report.delay(
                subject='Position created',
                message=f'Position {form.cleaned_data["name"]} created',
            )

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class DestroyPositionView(DeleteView):
    model = Position
    template_name = 'tt.html'
    success_url = reverse_lazy('projects_list')

    def post(self, request, *args, **kwargs):
        position_pk = kwargs.get('pk')
        position = Position.objects.filter(pk=position_pk).first()
        equipment = Equipment.objects.select_related('position').filter(position__pk=position_pk)

        send_report.delay(
            subject='Position deleted',
            message=f'Position {position.name} deleted',
        )

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
        form = self.form_class(request.POST)
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
            position.status = Position.DONE
            position.save()
            send_report.delay(
                subject='Equipment created',
                message=f'Equipment {form.cleaned_data["name"]} created',
            )

        return HttpResponseRedirect(
            reverse_lazy('project_details', kwargs={'slug': position.technological_node.location.slug}))


class RemoveEquipmentView(DeleteView):
    model = Equipment
    template_name = 'tt.html'

    def get_success_url(self):
        self.success_url = self.request.META.get('HTTP_REFERER')
        return super().get_success_url()

    def form_valid(self, form):
        equipment_pk = self.kwargs.get('pk')
        equipment = Equipment.objects.filter(pk=equipment_pk).first()
        position = Position.objects.filter(equipment__pk=equipment_pk).first()
        position.status = Position.NOT_STARTED
        position.save()

        send_report.delay(
            subject='Equipment deleted',
            message=f'Equipment {equipment.name} deleted',
        )

        return super().form_valid(form)


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
        filtered_queryset = EquipmentFilter(self.request.GET, queryset=self.get_queryset())
        print(self.request.GET)

        context['equipments'] = filtered_queryset.qs
        context['filter'] = filtered_queryset
        context['locations'] = Location.objects.all()
        context['nodes'] = TechnologicalNode.objects.all().order_by('node_number', 'name')
        context['marks'] = Equipment.objects.all().values('name').distinct().order_by('name')

        return context

    def post(self, request, *args, **kwargs):
        filtered_queryset = EquipmentFilter(request.GET, queryset=self.get_queryset()).qs
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="exported_data.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Country',
            'City',
            'Node number',
            'Technological node',
            'Position',
            'Quantity, pcs',
            'Mark',
            'Power, kW',
            'Weight, kg',
            'Price, USD',
            'Created',
        ])

        for item in filtered_queryset:
            writer.writerow([
                item.position.technological_node.location.country,
                item.position.technological_node.location.city,
                item.position.technological_node.node_number,
                item.position.technological_node.name,
                item.position.name,
                item.position.quantity,
                item.name,
                item.power,
                item.weight,
                item.price,
                item.created_at.strftime('%Y.%m.%d %H:%M:%S')
            ])

        return response


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


class StatisticView(TemplateView):
    template_name = 'statistic.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = (Equipment.objects.all()
        .select_related('position')
        .values('type')
        .annotate(
            count=Count('id'),
            avg_price=Avg('price'),
            max_price=Max('price'),
            min_price=Min('price'),
            quantity=Sum('position__quantity'),
            projects=Count('position__technological_node__location', distinct=True)
        ))

        filtered_queryset = EquipmentStatisticFilter(self.request.GET, queryset=data)
        context['filter'] = filtered_queryset
        context['data'] = filtered_queryset.qs
        return context

    def post(self, request, *args, **kwargs):
        filtered_queryset = self.get_context_data()['data']
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="exported_data.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Equipment type',
            'Projects, pcs',
            'Positions, pcs',
            'Equipment quantity, pcs',
            'Average price, USD',
            'Max price, USD',
            'Min price, USD',
        ])

        for item in filtered_queryset:
            writer.writerow([
                item['type'],
                item['projects'],
                item['count'],
                item['quantity'],
                item['avg_price'],
                item['max_price'],
                item['min_price'],
            ])

        return response


class ProjectsSpecificationView(TemplateView):
    template_name = 'specification.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_slug = self.kwargs['slug']
        project = Location.objects.get(slug=project_slug)
        technological_nodes = (TechnologicalNode.objects
                               .filter(location=project)
                               .prefetch_related('positions')
                               .annotate(
            power_total=Sum('positions__equipment__power'),
            weight_total=Sum('positions__equipment__weight'),
            quantity_total=Sum('positions__quantity')
        )
                               .order_by('node_number'))

        context['technological_nodes'] = technological_nodes
        context['project'] = project

        return context


class ProjectsPriceView(TemplateView):
    template_name = 'price.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_slug = self.kwargs['slug']
        project = Location.objects.filter(slug=project_slug).prefetch_related(
            'nodes',
            'nodes__positions'
        ).annotate(
            equipment_count=Sum('nodes__positions__quantity'),
            price_total=ExpressionWrapper(
                Sum(F('nodes__positions__equipment__price') * F('nodes__positions__quantity')),
                output_field=DecimalField()
            ),
        ).first()
        technological_nodes = (TechnologicalNode.objects
                               .filter(location=project)
                               .prefetch_related('positions')
                               .annotate(
            quantity_total=Sum('positions__quantity'),
            price_total=ExpressionWrapper(
                Sum(F('positions__equipment__price') * F('positions__quantity')),
                output_field=DecimalField()
            ),
        )
                               .order_by('node_number'))
        context['technological_nodes'] = technological_nodes
        context['project'] = project

        return context


class StatisticByMonthView(TemplateView):
    template_name = 'statistic_by_month.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = (Equipment.objects.all()
                .select_related('position')
                .annotate(month=TruncMonth('created_at', output_field=DateTimeField()))
                .values('month')
                .annotate(quantity=Sum('position__quantity'))
                .order_by('month'))
        context['data'] = data
        return context
