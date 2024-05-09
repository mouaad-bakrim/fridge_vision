import json

from django.db import models


# Create your models here.
class Process(models.Model):
    class Meta:
        ordering = ["usability"]
        verbose_name_plural = "Produits"
        verbose_name = "Process"
        db_table = "process_process"

    usability = models.CharField(max_length=100, null=True, blank=True, verbose_name="Usability")

    brand = models.CharField(max_length=150, null=True, blank=True, verbose_name="Brand")

    etat = models.CharField(max_length=150, null=True, blank=True, verbose_name="Etat")

    score = models.CharField(max_length=150, null=True, blank=True, verbose_name="Note")

    image = models.ImageField(upload_to='process_images/', null=True, blank=True, verbose_name='Image')

    def __str__(self):
        return f"{self.usability} - {self.brand}"

    def clean(self):
        super().clean()

    import json

    def evaluate_json(json_data):

        # Vérification de l'utilisabilité de l'image
        usable_result = json_data.get("Usability", {})
        if usable_result.get("predicted_class") == "unusable":
            return 0  # Image unusable, note directe de 0/5

        # Évaluation de la marque
        brand_result = json_data.get("Brand", {})
        brand_class = brand_result.get("predicted_class", "unknown")
        brand_score = 1 if brand_class != "unknown" else 0  # Attribuer 1 si la marque est reconnue, sinon 0

        # Évaluation de l'état du réfrigérateur
        condition_result = json_data.get("Condition", {})
        if condition_result.get("predicted_class") == "good":
            condition_score = 1
        elif condition_result.get("predicted_class") == "bad":
            condition_score = 0
        else:
            condition_score = 0.5

        # Évaluation du statut de la porte
        door_status_result = json_data.get("Doorstatus", {})
        door_status_score = 1 if door_status_result.get("predicted_class") == "open" else 0

        # Évaluation de chaque étagère
        shelf_results = json_data.get("Shelves", [])
        num_shelves = len(json_data.get("Shelves", []))

        shelf_alignment_total = 0
        shelf_profile_total = 0
        shelf_fond_total = 0
        item_detection_total = 0

        for shelf in shelf_results:
            alignment_result = shelf.get("alignment_result", {})
            shelf_alignment_total += 1 if alignment_result.get("predicted_class") == "ranged" else 0

            profile_result = shelf.get("shelf_profil_result", {})
            shelf_profile_total += 1 if profile_result.get("predicted_class") == "available" else 0

            fond_result = shelf.get("shelf_fond_result", {})
            shelf_fond_total += 1 if fond_result.get("predicted_class") == "present" else 0

            item_results = shelf.get("items", [])
            if item_results:
                item_detection_total += 1  # Marquer positivement la détection d'articles

        # Calcul de la note moyenne par étagère
        total_shelf_score = shelf_alignment_total + shelf_profile_total + shelf_fond_total + item_detection_total
        avg_shelf_score = total_shelf_score / (4 * num_shelves) if num_shelves > 0 else 0

        # Calcul de la note globale
        total_score = brand_score + condition_score + door_status_score + avg_shelf_score
        global_score = (total_score / 4) * 5  # Conversion en note sur 5

        return global_score

    # Exemple d'utilisation avec un fichier JSON
    with open('saved_models/testImg_results.json', 'r') as json_file:
        data = json.load(json_file)
        note = evaluate_json(data)

    def save(self, *args, **kwargs):
        self.full_clean()

        # Charger les données depuis le fichier JSON
        with open('saved_models/testImg_results.json', 'r') as json_file:
            data = json.load(json_file)

        # Utiliser les données du fichier JSON pour définir les valeurs
        self.usability = data.get('Usability', {}).get('predicted_class', 'default_value_usability')
        self.brand = data.get('Brand', {}).get('predicted_class', 'default_value_brand')
        self.etat = data.get('Condition', {}).get('predicted_class', 'default_value_condition')
        self.score = self.note

        return super().save(*args, **kwargs)
