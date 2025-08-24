from django.core.management.base import BaseCommand
from core.models import Product

class Command(BaseCommand):
    help = "Fix image filenames with .PNG → .png"

    def handle(self, *args, **options):
        for obj in Product.objects.all():
            if obj.image and str(obj.image).endswith(".PNG"):
                old = obj.image.name
                obj.image.name = obj.image.name.replace(".PNG", ".png")
                obj.save(update_fields=["image"])
                self.stdout.write(f"Updated {old} → {obj.image.name}")
