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

        JobMaterial.objects.create(
            job=instance,
            material=template_material.material,
            quantity=template_material.quantity,
            unit_cost=template_material.material.unit_cost,
            labor_hours=template_material.material.labor_hours,
        )