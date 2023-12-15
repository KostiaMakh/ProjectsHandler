import os
import uuid

from django.db import models
from django.urls import reverse_lazy, reverse
from django.utils.text import slugify

from config.constants import EQUIPMENT_TYPES


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename_start = filename.replace('.' + ext, '')

    filename = "%s__%s.%s" % (uuid.uuid4(), filename_start, ext)
    return os.path.join('companies', filename)


class Location(models.Model):
    slug = models.SlugField(blank=True)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    customer = models.CharField(max_length=255, unique=True)
    logo = models.ImageField(upload_to=get_file_path, blank=True, null=True)

    class Meta:
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'

    def __str__(self):
        return f'{self.customer} ({self.city}, {self.country})'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.slug = f'{self.pk}-{slugify(str(self.customer))}'
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('project_details', kwargs={'slug': self.slug})


class TechnologicalNode(models.Model):
    slug = models.SlugField(blank=True)
    name = models.CharField(max_length=255)
    node_number = models.PositiveIntegerField(default=0)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='nodes')

    class Meta:
        verbose_name = 'Technological node'
        verbose_name_plural = 'Technological nodes'

    def __str__(self):
        return f'{self.node_number}. {self.name}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.slug = f'{self.pk}-{self.node_number}-{slugify(str(self.name))}'
        super().save()


class Complectation(models.Model):
    control_panel = models.BooleanField(default=False)
    local_control_panel = models.BooleanField(default=False)
    startup_works = models.BooleanField(default=False)
    mounting_kit = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Complectation'
        verbose_name_plural = 'Complectation'

    def __str__(self):
        complectation = ''
        if self.control_panel: complectation += 'control panel, '
        if self.local_control_panel: complectation += 'local control panel, '
        if self.startup_works: complectation += 'startup works, '
        if self.mounting_kit: complectation += 'mounting kit, '

        return complectation[:-2]


class Manufacture(models.Model):
    slug = models.SlugField(blank=True)
    name = models.CharField(max_length=255, unique=True)
    country = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Manufacture'
        verbose_name_plural = 'Manufactures'

    def __str__(self):
        return f'{self.name} ({self.country})'


class Equipment(models.Model):
    slug = models.SlugField(blank=True)
    name = models.CharField(max_length=255)
    price = models.PositiveIntegerField(default=0)
    type = models.CharField(max_length=255, choices=EQUIPMENT_TYPES)
    weight = models.PositiveIntegerField(default=0)
    power = models.FloatField(default=0)
    manufacture = models.ForeignKey(Manufacture, on_delete=models.PROTECT, null=True)
    complectation = models.OneToOneField(Complectation, on_delete=models.CASCADE, related_name='equipment', null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        verbose_name = 'Equipment'
        verbose_name_plural = 'Equipments'

    def __str__(self):
        return f'{self.name} ({self.power} kw, {self.weight} kg.)'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.slug = f'{self.pk}-{self.name}'
        super().save()

    def get_absolute_url(self):
        return reverse('equipment_details', kwargs={'slug': self.slug})


class Position(models.Model):
    DONE = 'done'
    NOT_STARTED = 'not_started'

    STATUS_CHOICES = (
        (DONE, 'Done'),
        (NOT_STARTED, 'Not started')
    )

    slug = models.SlugField(blank=True)
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    equipment = models.OneToOneField(Equipment, on_delete=models.SET_NULL, related_name='position', null=True)
    technological_node = models.ForeignKey(TechnologicalNode, on_delete=models.CASCADE, related_name='positions')
    status = models.CharField(max_length=128, choices=STATUS_CHOICES, default=NOT_STARTED)

    class Meta:
        verbose_name = 'Position'
        verbose_name_plural = 'Positions'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.slug = f'{self.pk}-{self.name}'
        super().save()
