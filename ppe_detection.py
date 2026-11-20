import boto3
import os

def analyze_worker_safety(image_path):
    """
    Відправляє зображення до Amazon Rekognition для перевірки наявності каски та захисних окулярів/маски.
    """
    print(f"🔍 Аналіз зображення: {image_path}...\n")
    
    # Ініціалізація клієнта AWS (використовує налаштування з aws configure)
    try:
        rekognition = boto3.client('rekognition', region_name='eu-central-1')
    except Exception as e:
        print("Помилка ініціалізації AWS клієнта. Перевірте ключі доступу.")
        return

    # Зчитування файлу
    if not os.path.exists(image_path):
        print(f"❌ Помилка: Файл '{image_path}' не знайдено. Покладіть фото поруч зі скриптом.")
        return

    with open(image_path, 'rb') as image_file:
        image_bytes = image_file.read()

    # Запит до API
    try:
        response = rekognition.detect_protective_equipment(
            Image={'Bytes': image_bytes},
            SummarizationAttributes={
                'MinConfidence': 80, # Мінімальна точність розпізнавання 80%
                'RequiredEquipmentTypes': ['HEAD_COVER', 'FACE_COVER']
            }
        )
    except Exception as e:
        print(f"❌ Помилка API: {e}")
        return

    # Аналіз та виведення результатів
    persons = response.get('Persons', [])
    print(f"👥 Знайдено осіб на фото: {len(persons)}\n")

    for idx, person in enumerate(persons, 1):
        print(f"--- Аналіз екіпірування: Особа {idx} ---")
        
        head_protected = False
        face_protected = False

        for part in person.get('BodyParts', []):
            # Перевірка голови (Каска)
            if part['Name'] == 'HEAD' and part.get('EquipmentDetections'):
                head_protected = True
                conf = part['EquipmentDetections'][0]['Confidence']
                print(f"✅ Каска: ПРИСУТНЯ (Точність: {conf:.1f}%)")
            
            # Перевірка обличчя (Окуляри/Маска)
            if part['Name'] == 'FACE' and part.get('EquipmentDetections'):
                face_protected = True
                conf = part['EquipmentDetections'][0]['Confidence']
                print(f"✅ Захист обличчя: ПРИСУТНІЙ (Точність: {conf:.1f}%)")

        if not head_protected:
            print("🚨 АЛАРМ: Каска ВІДСУТНЯ!")
        if not face_protected:
            print("🚨 АЛАРМ: Захисні окуляри/маска ВІДСУТНІ!")
        print("-" * 35 + "\n")

if __name__ == "__main__":
    # Назва тестового файлу (змініть на свою картинку)
    TEST_IMAGE = "worker_photo.jpg" 
    analyze_worker_safety(TEST_IMAGE)