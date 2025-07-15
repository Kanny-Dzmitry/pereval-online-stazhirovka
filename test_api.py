#!/usr/bin/env python3
"""
Тестовый скрипт для проверки REST API метода submitData
"""

import requests
import json

# URL для тестирования (локальный сервер)
BASE_URL = "http://localhost:8000"
SUBMIT_DATA_URL = f"{BASE_URL}/submitData/"

# Тестовые данные согласно ТЗ
test_data = {
    "beauty_title": "пер. ",
    "title": "Пхия",
    "other_titles": "Триев", 
    "connect": "соединяет долины А и Б",
    "user": {
        "email": "qwerty@mail.ru",
        "fam": "Пупкин", 
        "name": "Василий",
        "otc": "Иванович",
        "phone": "+7 555 55 55"
    },
    "coords": {
        "latitude": "45.3842",
        "longitude": "7.1525", 
        "height": "1200"
    },
    "level": {
        "winter": "",
        "summer": "1А", 
        "autumn": "1А",
        "spring": ""
    },
    "images": [
        {"data": "base64encoded_image_data_1", "title": "Седловина"}, 
        {"data": "base64encoded_image_data_2", "title": "Подъём"}
    ]
}

def test_submit_data():
    """Тестирует метод POST /submitData/"""
    try:
        print(f"Отправка запроса на {SUBMIT_DATA_URL}")
        print(f"Данные: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(
            SUBMIT_DATA_URL,
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\nСтатус ответа: {response.status_code}")
        print(f"Ответ: {response.json()}")
        
        # Проверяем ожидаемую структуру ответа
        response_data = response.json()
        required_fields = ['status', 'message', 'id']
        
        for field in required_fields:
            if field not in response_data:
                print(f"ОШИБКА: Отсутствует поле '{field}' в ответе")
                return False
        
        if response.status_code == 200 and response_data['status'] == 200:
            print(f"✅ Тест пройден! Создан перевал с ID: {response_data['id']}")
            return True
        else:
            print(f"❌ Тест не пройден. Статус: {response_data['status']}, Сообщение: {response_data['message']}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ОШИБКА: Не удается подключиться к серверу. Убедитесь, что сервер запущен на localhost:8000")
        return False
    except Exception as e:
        print(f"❌ ОШИБКА: {str(e)}")
        return False

def test_missing_fields():
    """Тестирует обработку недостающих полей"""
    print("\n" + "="*50)
    print("Тест с недостающими полями")
    print("="*50)
    
    incomplete_data = {
        "title": "Тестовый перевал"
        # Отсутствуют обязательные поля user, coords, level
    }
    
    try:
        response = requests.post(
            SUBMIT_DATA_URL,
            json=incomplete_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Статус ответа: {response.status_code}")
        print(f"Ответ: {response.json()}")
        
        response_data = response.json()
        if response.status_code == 400 and response_data['status'] == 400:
            print("✅ Тест обработки ошибок пройден!")
            return True
        else:
            print("❌ Тест обработки ошибок не пройден")
            return False
            
    except Exception as e:
        print(f"❌ ОШИБКА: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск тестов REST API")
    print("="*50)
    
    # Основной тест
    success1 = test_submit_data()
    
    # Тест обработки ошибок
    success2 = test_missing_fields()
    
    print("\n" + "="*50)
    if success1 and success2:
        print("🎉 Все тесты пройдены успешно!")
    else:
        print("❌ Некоторые тесты не пройдены")
    print("="*50) 