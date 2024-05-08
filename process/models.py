from django.db import models

# Create your models here.
class Process(models.Model):
    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Produits"
        verbose_name = "Process"
        db_table = "process_process"

    name = models.CharField(max_length=32, verbose_name="Nom")
    image = models.ImageField(upload_to='process_images/', null=True, blank=True, verbose_name='Image')

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
