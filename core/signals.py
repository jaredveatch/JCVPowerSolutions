from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import (
    Job,
    JobMaterial,
    ServiceTemplateMaterial,
)


@receiver(post_save, sender=Job)
def copy_template_materials_to_job(
    sender,
    instance,
    created,
    **kwargs
):
    """
    Automatically copy materials from the selected
    ServiceTemplate into the Job.
    """

    if not created:
        return

    if not instance.template:
        return

    template_materials = ServiceTemplateMaterial.objects.filter(
        service_template=instance.template
    )

    for template_material in template_materials:
        material = template_material.material

        JobMaterial.objects.create(
            job=instance,
            material=material,
            quantity=template_material.quantity or Decimal("1.00"),
            unit_cost=material.unit_cost or Decimal("0.00"),
            labor_hours=material.labor_hours or Decimal("0.00"),
            material_markup=material.default_markup if hasattr(material, "default_markup") and material.default_markup is not None else Decimal("0.00"),
        )