from django.db import models

class AboutPage(models.Model):
    banner_image = models.ImageField(upload_to="about/", blank=True, null=True)
    banner_title = models.CharField(max_length=100, default="About Us")

    # images
    image1 = models.ImageField(upload_to="about/", blank=True, null=True)
    image2 = models.ImageField(upload_to="about/", blank=True, null=True)
    image3 = models.ImageField(upload_to="about/", blank=True, null=True)

    # text sections
    description_top = models.TextField()
    description_bottom = models.TextField()

    why_title = models.CharField(max_length=100, default="Why Choose Us?")
    why_collection = models.TextField()
    why_affordable = models.TextField()
    why_hygiene = models.TextField()
    why_convenient = models.TextField()

    def __str__(self):
        return "About Page"


# contact page


class ContactPage(models.Model):
    banner_image = models.ImageField(upload_to="contact/", blank=True, null=True)
    right_side_image = models.ImageField(upload_to="contact/", blank=True, null=True)
    description = models.TextField()
    phone = models.CharField(max_length=20, default="+911234567890")
    fax = models.CharField(max_length=20, default="0421 455 4555")
    email = models.EmailField(default="info@mailjewellery.com")

    def __str__(self):
        return "Contact Page Content"


# products 
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.templatetags.static import static


class ProductCategory(models.Model):
    name = models.CharField(max_length=100)   # e.g. Rings, Necklaces
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    # ownership
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name="products")

    # basic info
    name = models.CharField(max_length=200)                       # product name
    name_description = models.TextField(blank=True, null=True)    # new: paragraph under name
    short_description = models.CharField(max_length=255, blank=True, null=True)  
    description = models.TextField(blank=True, null=True)         # long description section

    # pricing & rating
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rating = models.FloatField(default=4.5)

    # media
    image = models.ImageField(upload_to='products/', blank=True, null=True)   # main image
    thumbnail1 = models.ImageField(upload_to='product_thumbnails/', blank=True, null=True)
    thumbnail2 = models.ImageField(upload_to='product_thumbnails/', blank=True, null=True)
    thumbnail3 = models.ImageField(upload_to='product_thumbnails/', blank=True, null=True)
    video = models.FileField(upload_to='product_videos/', blank=True, null=True)

    # attributes
    size = models.CharField(max_length=50, blank=True, null=True)   # e.g. 12(58.1mm)
    metal = models.CharField(max_length=50, blank=True, null=True)  # e.g. Yellow Gold

    # slug
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.name} - {self.name}"
    
    def get_image_url(self):
        try:
            return self.image.url
        except:
            return static(str(self.image))  


# promo banner and below sections
from django.db import models
from django.utils.text import slugify

class PromoBanner(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.TextField()
    code = models.CharField(max_length=50, blank=True, null=True)
    button_text = models.CharField(max_length=50, default="Rent Now")
    button_link = models.URLField(blank=True, null=True)
    background_image = models.ImageField(upload_to="promo/", blank=True, null=True)
    product_image = models.ImageField(upload_to="promo/", blank=True, null=True)

    def __str__(self):
        return self.title


class FeaturedSection(models.Model):
    title = models.CharField(max_length=200)     # Modern Bold & Beautiful, Bold & Beautiful, Bridal Glow
    subtitle = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField()
    image = models.ImageField(upload_to="featured/")
    button_text = models.CharField(max_length=50, default="Explore")
    button_link = models.URLField(blank=True, null=True)

    position = models.CharField(
        max_length=10,
        choices=[("left", "Image Left"), ("right", "Image Right")],
        default="left"
    )

    order = models.PositiveIntegerField(default=0, help_text="Controls display order")

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title
# services
class Service(models.Model):
    title = models.CharField(max_length=100)   # e.g. Free Shipping
    subtitle = models.CharField(max_length=200)  # e.g. Free Shipping on All Orders
    image = models.ImageField(upload_to="services/")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title
    
# carosal

class Testimonial(models.Model):
    name = models.CharField(max_length=100)   # e.g., Meera Subramanian
    role = models.CharField(max_length=100)   # e.g., Bride | Coimbatore
    photo = models.ImageField(upload_to="testimonials/")
    message = models.TextField()              # The testimonial text
    order = models.PositiveIntegerField(default=0, help_text="Controls display order")

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.name} - {self.role}"
    
# category banner
class CategoryBanner(models.Model):
    category = models.OneToOneField(ProductCategory, on_delete=models.CASCADE, related_name="banner")
    image = models.ImageField(upload_to="category_banners/")
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

