import numpy as np


def summary(self, normalize=False, decimals=5):
    results = []
    data = self.boxes.data.cpu().tolist()
    h, w = self.orig_shape if normalize else (1, 1)
    for i, row in enumerate(data):
        box = {
            "x1": round(row[0] / w, decimals),
            "y1": round(row[1] / h, decimals),
            "x2": round(row[2] / w, decimals),
            "y2": round(row[3] / h, decimals),
        }
        conf = round(row[-2], decimals)
        class_id = int(row[-1])
        result = {"name": self.names[class_id], "class": class_id, "confidence": conf, "box": box}
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
        shelf['name'] = f"Shelf_{i}"
    return sorted_shelves


def assign_items_to_shelves(sorted_shelves, detections):
    for item in detections:
        if not item['name'].startswith("Shelf") and not item['name'].startswith(
                "Fridge"):  # Vérifie si l'élément n'est pas une étagère ou un réfrigérateur
            assigned = False
            for shelf in sorted_shelves:
                shelf_y1 = shelf['box']['y1']
                shelf_y2 = shelf['box']['y2']
                item_y1 = item['box']['y1']
                item_y2 = item['box']['y2']
                # Vérifie si les coordonnées `y1` et `y2` de l'article correspondent approximativement à celles de l'étagère
                if shelf_y1 <= item_y1 <= shelf_y2 and shelf_y1 <= item_y2 <= shelf_y2:
                    if "items" not in shelf:
                        shelf[
                            "items"] = []  # Crée une liste d'articles pour cette étagère si elle n'existe pas encore
                    shelf["items"].append(item)  # Ajoute l'article à la liste d'articles de l'étagère
                    assigned = True
                    break  # Sort de la boucle dès que l'article est attribué à une étagère
            if not assigned:
                # Si l'article n'est pas attribué à une étagère, l'ajoute directement aux résultats triés
                sorted_shelves.append(item)
    return sorted_shelves


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
