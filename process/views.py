from uuid import uuid4
from django.shortcuts import render
from django.views import View
from .forms import FridgeForm
import numpy as np
import random
import os, cv2
import json
from PIL import Image
from ultralytics import YOLO
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import nltk
from nltk.metrics.distance import edit_distance


from django.conf import settings

class Upload_image(View):

    def get(self, request):
        form = FridgeForm()  # Crée un formulaire vide pour affichage initial
        return render(request, 'upload_image.html', {'form': form})

    def post(self, request):
        form = FridgeForm(request.POST, request.FILES)



        if form.is_valid():
            form.save()
            fridge_obj = form.instance
            print("img_obj", fridge_obj, fridge_obj.image.url)
            base_path = settings.BASE_DIR
            print("base_path", base_path)
            relative_path = fridge_obj.image.url
            IMAGE_PATH = os.path.join(base_path, relative_path.lstrip('/'))


            def summary(boxes, names, orig_shape, normalize=False, decimals=5):
                results = []
                h, w = orig_shape if normalize else (1, 1)
                for row in boxes:
                    box = {
                        "x1": round(row[0] / w, decimals),
                        "y1": round(row[1] / h, decimals),
                        "x2": round(row[2] / w, decimals),
                        "y2": round(row[3] / h, decimals),
                    }
                    conf = round(row[-2], decimals)
                    class_id = int(row[-1])
                    result = {"name": names[class_id], "class": class_id, "confidence": conf, "box": box}
                    results.append(result)
                return results

            def process_results(results):
                predictions = []
                for result in results:
                    summary = result.summary()
                    predictions.extend(summary)
                return predictions

            def sort_shelves(predictions):

                sorted_shelves = sorted(predictions, key=lambda x: x['box']['y1'])

                for i, shelf in enumerate(sorted_shelves, start=1):
                    shelf['name'] = (f"Étagère_{i}")

                return sorted_shelves

            # def assign_items_to_shelves(sorted_shelves, detections):
            #     for item in detections:
            #
            #         if not item['name'].startswith("Shelf") and not item['name'].startswith("Fridge"):
            #
            #             assigned = False
            #
            #             for shelf in sorted_shelves:
            #
            #                 shelf_y1 = shelf['box']['y1']
            #
            #                 shelf_y2 = shelf['box']['y2']
            #
            #                 item_y1 = item['box']['y1']
            #
            #                 item_y2 = item['box']['y2']
            #
            #                 # Vérifie si les coordonnées `y1` et `y2` de l'article correspondent approximativement à celles de l'étagère
            #
            #                 if shelf_y1 <= item_y1 <= shelf_y2 and shelf_y1 <= item_y2 <= shelf_y2:
            #
            #                     if "items" not in shelf:
            #                         shelf[
            #                             "items"] = []  # Crée une liste d'articles pour cette étagère si elle n'existe pas encore
            #
            #                     shelf["items"].append(item)  # Ajoute l'article à la liste d'articles de l'étagère
            #
            #                     assigned = True
            #
            #                     break  # Sort de la boucle dès que l'article est attribué à une étagère
            #
            #             if not assigned:
            #                 # Si l'article n'est pas attribué à une étagère, l'ajoute directement aux résultats triés
            #
            #                 sorted_shelves.append(item)
            #
            #     return sorted_shelves
            def calculate_intersection_area(box1, box2):
                x_left = max(box1['x1'], box2['x1'])
                y_top = max(box1['y1'], box2['y1'])
                x_right = min(box1['x2'], box2['x2'])
                y_bottom = min(box1['y2'], box2['y2'])

                if x_right < x_left or y_bottom < y_top:
                    return 0.0
                intersection_area = (x_right - x_left) * (y_bottom - y_top)
                return intersection_area
            def assign_items_to_shelves(sorted_shelves, detections):
                for item in detections:
                    if not item['name'].startswith("Shelf") and not item['name'].startswith("Fridge"):
                        max_intersection = 0
                        assigned_shelf = None

                        for shelf in sorted_shelves:
                            intersection_area = calculate_intersection_area(shelf['box'], item['box'])
                            if intersection_area > max_intersection:
                                max_intersection = intersection_area
                                assigned_shelf = shelf

                        if assigned_shelf:
                            if "items" not in assigned_shelf:
                                assigned_shelf["items"] = []
                            assigned_shelf["items"].append(item)
                        else:
                            hors_shelf = next((s for s in sorted_shelves if s['name'] == "hors_shelf"), None)
                            if not hors_shelf:
                                hors_shelf = {"name": "hors_shelf", "items": []}
                                sorted_shelves.append(hors_shelf)
                            hors_shelf["items"].append(item)
                return sorted_shelves


            ALIGNMENT_MODEL_PATH = "saved_models/articles_alignment.keras"

            Alignment_class_names = ['Mal rangé', 'Bien rangé']

            PROFILPLASTIC_MODEL_PATH = "saved_models/profil_platic.keras"

            profilplastic_class_names = ['Present', 'Absent']

            FONDARTICLES_MODEL_PATH = "saved_models/fond_articles.keras"

            Fondarticlesclass_names = ['Indisponible', 'Disponible']

           #Suppression des detections doubles

            def remove_duplicate_items(detections):
                unique_detections = []
                seen_boxes = set()
                for item in detections:
                    box_tuple = (
                    item['box']['x1'], item['box']['y1'], item['box']['x2'], item['box']['y2'], item['name'])
                    if box_tuple not in seen_boxes:
                        seen_boxes.add(box_tuple)
                        unique_detections.append(item)
                return unique_detections



            def Shelves_and_Items_detection(shelves_model_path, items_model_path, image_path):

                # Détection des étagères

                shelves_model = YOLO(shelves_model_path)

                shelves_results = shelves_model(image_path)

                shelves_detections = process_results(shelves_results)

                sorted_shelves = sort_shelves([d for d in shelves_detections if d['name'].startswith("Shelf")])

                # Détection des articles

                items_model = YOLO(items_model_path)

                items_results = items_model(image_path)

                items_detections = process_results(items_results)
                items_detections = remove_duplicate_items(items_detections)
                # Classifier les articles pour chaque étagère détectée

                for shelf in sorted_shelves:
                    shelf_image = crop_shelf_image(image_path, shelf['box'])

                    shelf_alignment_result = classify_shelf_alignment(ALIGNMENT_MODEL_PATH, shelf_image,
                                                                      Alignment_class_names)

                    shelf['alignment_result'] = shelf_alignment_result

                    shelf_profil_result = classify_shelf_profil(PROFILPLASTIC_MODEL_PATH, shelf_image,
                                                                profilplastic_class_names)

                    shelf['shelf_profil_result'] = shelf_profil_result

                    shelf_fond_result = classify_shelf_fond(FONDARTICLES_MODEL_PATH, shelf_image,
                                                            Fondarticlesclass_names)

                    shelf['shelf_fond_result'] = shelf_fond_result

                # Associer les articles détectés aux étagères correspondantes

                sorted_shelves_with_items = assign_items_to_shelves(sorted_shelves, items_detections)

                return sorted_shelves_with_items, items_detections

            class_names = [
                "SA200", "SA150", "SA100", "SA50", "SA33", "SA33KRZ", "SA33KRG", "SA33KB", "SA33KV", "SA33KO", "SA33FT",
                "SA33DISF", "SA33DISG", "SA75V", "AAT150", "AAT50", "AAT33", "B200", "B150", "B60", "OUL100", "OUL100L",
                "OUL50", "OUL50L", "OUL33", "OUL25OW", "OUL25MJT", "OUL25TRP", "OUL25OR", "OUL75P", "VTL150", "VTL33",
                "ORG100", "ORG100Z", "ORG50", "ORG50Z", "ORG25", "BG100TRP", "BG100AGR", "BG100POM", "BG100LM",
                "BG25TRPL",
                "BG25AGRM", "BG25POM", "GLS150C", "GLS33C", "GLS150TRP", "GLS33TRP", "GLS150PM", "GLS33PM", "Shelf"
            ]

            # Génération des couleurs aléatoires pour chaque classe
            class_colors = {class_name: (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for
                            class_name in class_names}

            # Couleur rouge par défaut pour les classes non détectées
            default_color = (0, 0, 255)  # Rouge

            # Fonction pour dessiner les boîtes avec les noms de classe et les couleurs associées
            def draw_boxes(image_path, detections):
                img = cv2.imread(image_path)

                for detection in detections:
                    name = detection['name']
                    box = detection['box']
                    x1, y1, x2, y2 = box['x1'], box['y1'], box['x2'], box['y2']
                    color = class_colors.get(name, default_color)
                    cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    # Ajouter le nom de classe avec un fond coloré pour une meilleure visibilité
                    text_size = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                    cv2.rectangle(img, (int(x1), int(y1) - text_size[1] - 5), (int(x1) + text_size[0], int(y1)), color,
                                  -1)
                    cv2.putText(img, name, (int(x1), int(y1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                return img

            def Fridge_Classification(model_path, image_path, class_names):

                img_height = 600

                img_width = 449

                model = load_model(model_path)

                image_file = image_path

                img = image.load_img(image_file, target_size=(img_height, img_width))

                img_array = image.img_to_array(img)

                img_array = np.expand_dims(img_array, axis=0)

                prediction = model.predict(img_array)

                predicted_class = np.argmax(prediction)

                class_name = class_names[predicted_class]

                score = 100 * np.max(prediction)

                result = {

                    "predicted_class": class_name,

                    "confidence_score": score

                }

                return result

            def classify_shelf_alignment(model_path, shelf_image, class_name):

                img_height = 100

                img_width = 200

                model = load_model(model_path)

                img_array = image.img_to_array(shelf_image)

                img_array = np.expand_dims(img_array, axis=0)

                prediction = model.predict(img_array)

                predicted_class = np.argmax(prediction)

                class_name = Alignment_class_names[predicted_class]

                score = 100 * np.max(prediction)

                result = {

                    "predicted_class": class_name,

                    "confidence_score": score

                }

                return result

            def classify_shelf_profil(model_path, shelf_image, class_name):

                img_height = 100

                img_width = 200

                model = load_model(model_path)

                img_array = image.img_to_array(shelf_image)

                img_array = np.expand_dims(img_array, axis=0)

                prediction = model.predict(img_array)

                predicted_class = np.argmax(prediction)

                class_name = profilplastic_class_names[predicted_class]

                score = 100 * np.max(prediction)

                result = {

                    "predicted_class": class_name,

                    "confidence_score": score

                }

                return result

            def classify_shelf_fond(model_path, shelf_image, class_name):

                img_height = 100

                img_width = 200

                model = load_model(model_path)

                img_array = image.img_to_array(shelf_image)

                img_array = np.expand_dims(img_array, axis=0)

                prediction = model.predict(img_array)

                predicted_class = np.argmax(prediction)

                class_name = Fondarticlesclass_names[predicted_class]

                score = 100 * np.max(prediction)

                result = {

                    "predicted_class": class_name,

                    "confidence_score": score

                }

                return result

            def crop_shelf_image(image_path, box_coordinates):

                # Chargement de l'image

                image = Image.open(image_path)

                # Récupération des coordonnées de la boîte englobante

                x1, y1, x2, y2 = box_coordinates['x1'], box_coordinates['y1'], box_coordinates['x2'], box_coordinates[
                    'y2']

                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                # Recadrage de l'image selon les coordonnées de la boîte englobante

                cropped_image = image.crop((x1, y1, x2, y2))

                # Enregistrement de l'image recadrée

                return cropped_image

            SHELVES_PREDICTION_MODEL = 'saved_models/shelves_detection.pt'

            ITEM_PREDICTION_MODEL = 'saved_models/Item_detection.pt'

            FRIDGE_CLASSIFICATION_MODEL_1 = 'saved_models/usage_model.keras'

            FRIDGE_CLASSIFICATION_MODEL_2 = 'saved_models/brand_model.keras'

            FRIDGE_CLASSIFICATION_MODEL_3 = "saved_models/model_c.keras"

            FRIDGE_CLASSIFICATION_MODEL_4 = 'saved_models/DoorStatus_model.keras'

            Usableclass_names = ['Inexploitable', 'Exploitable']

            Brandclass_names = ['Orangina', 'Sidi ali', 'Inconnu']

            Stateclass_names = ['Mauvais', 'Bon', 'Inconnu']

            DoorStatusclass_names = ['Fermé', 'Ouvert']

            usable_result = Fridge_Classification(FRIDGE_CLASSIFICATION_MODEL_1, IMAGE_PATH, Usableclass_names)

            Brand_result = Fridge_Classification(FRIDGE_CLASSIFICATION_MODEL_2, IMAGE_PATH, Brandclass_names)

            condition_result = Fridge_Classification(FRIDGE_CLASSIFICATION_MODEL_3, IMAGE_PATH, Stateclass_names)

            DoorSatatus_result = Fridge_Classification(FRIDGE_CLASSIFICATION_MODEL_4, IMAGE_PATH, DoorStatusclass_names)

            # Détection des étagères

            # Détection des étagères et des articles

            shelf_results, item_results = Shelves_and_Items_detection(SHELVES_PREDICTION_MODEL, ITEM_PREDICTION_MODEL,
                                                                      IMAGE_PATH)

            def token_based_levenshtein_similarity(list1, list2):
                """Calculer la similarité basée sur la distance de Levenshtein entre deux listes."""
                str1 = ' '.join(list1)
                str2 = ' '.join(list2)
                distance = edit_distance(str1, str2)
                max_len = max(len(str1), len(str2))
                similarity = 1 - (distance / max_len)
                return similarity

            def compare_shelves(fridge_shelves, planogram):
                """Compare les étagères du frigo avec celles du planogramme."""
                similarities = []
                num_shelves = min(len(fridge_shelves), len(planogram))

                for i in range(num_shelves):
                    fridge_shelf_items = [item['name'] for item in fridge_shelves[i].get('items', [])]
                    planogram_shelf_items = planogram[i]

                    similarity = token_based_levenshtein_similarity(fridge_shelf_items, planogram_shelf_items)
                    similarities.append((i + 1, similarity))

                return similarities

            def calculate_overall_similarity(similarities, total_shelves_in_fridge):
                if not similarities:
                    return 0.0
                total_similarity = sum(similarity for _, similarity in similarities)
                return (total_similarity / total_shelves_in_fridge)*100

            # Liste des articles du planogramme

            planogram_str = """ORG100Z,OG100Z,OR100Z,GL150POM,GL150TRP,GL150C
            SA33,SA33,SA50,SA50,AAT33,AAT50,VT33,OUL25OW,OUL50
            SA33KORG,SA33KV,SA33KRZ,GL33C,GL33TRP,GL33POM,OUL25TRP,ORG50,OUL33
            SA150,AAT150,AAT150,AAT150,SA150,OUL100
            SA150,SA150,SA150,SA150,SA150,SA150"""
            planogram = [shelf.split(',') for shelf in planogram_str.split('\n')]

            # Calculate shelf similarities
            shelf_similarities = compare_shelves(shelf_results, planogram)

            # Calculate overall similarity
            overall_similarity = calculate_overall_similarity(shelf_similarities, len(shelf_results))

            # Update each shelf with its similarity
            for shelf, (shelf_num, similarity) in zip(shelf_results, shelf_similarities):
                shelf['similarity'] = similarity*100


            # Combinaison des résultats

            combined_result = {

                "Usability": usable_result,

                "Brand": Brand_result,

                "Condition": condition_result,

                "Doorstatus": DoorSatatus_result,

                "Overall_Similarity": overall_similarity,

                "Shelves": shelf_results,

                # "item_results": item_results

            }

            # Générer un identifiant unique pour l'image
            image_uuid = str(uuid4())

            # Enregistrement dans un fichier JSON

            json_results_path = f'upload/JSON/test_results_{image_uuid}.json'
            with open(json_results_path, 'w') as json_file:
                json.dump(combined_result, json_file, indent=4)


            # Dessiner les boîtes englobantes sur l'image originale
            image_with_boxes = draw_boxes(IMAGE_PATH, shelf_results + item_results)
            image_with_boxes_path = f'upload/image/Img_with_boxes_{image_uuid}.jpg'
            cv2.imwrite(image_with_boxes_path, image_with_boxes)


            with open(json_results_path, 'r') as json_file:
                json_data = json.load(json_file)



            return render(request, 'upload_image.html',
                          {'form': form, 'img_obj': fridge_obj, 'image_with_boxes_path': image_with_boxes_path,
                           'json_data': json_data})
        else:

            return render(request, 'upload_image.html', {'form': form})





def Dashboard(request):
    with open('saved_models/testImg_results.json') as json_file:
        json_data = json.load(json_file)

    return render(request, 'dashboard.html', {'json_data': json_data})





def token_based_levenshtein_similarity(list1, list2):
    """Calculer la similarité basée sur la distance de Levenshtein entre deux listes."""
    str1 = ' '.join(list1)
    str2 = ' '.join(list2)
    distance = edit_distance(str1, str2)
    max_len = max(len(str1), len(str2))
    similarity = 1 - (distance / max_len)
    return similarity

def compare_shelves(fridge_shelves, planogram):
    """Compare les étagères du frigo avec celles du planogramme."""
    similarities = []
    num_shelves = min(len(fridge_shelves), len(planogram))

    for i in range(num_shelves):
        fridge_shelf_items = [item['name'] for item in fridge_shelves[i].get('items', [])]
        planogram_shelf_items = planogram[i]

        similarity = token_based_levenshtein_similarity(fridge_shelf_items, planogram_shelf_items)
        similarities.append((i + 1, similarity))

    return similarities

def calculate_overall_similarity(similarities, total_shelves_in_fridge):
    """Calcule la similarité globale en pourcentage entre les étagères du frigo et le planogramme."""
    if not similarities:
        return 0.0
    total_similarity = sum(similarity for _, similarity in similarities)
    return (total_similarity / total_shelves_in_fridge) * 100
