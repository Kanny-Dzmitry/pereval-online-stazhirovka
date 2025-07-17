#!/usr/bin/env python3
"""
Тесты для новых API методов спринта 2
"""

import requests
import json


# Конфигурация
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/submitData"


def test_get_pass_by_id(pass_id):
    """Тест GET /submitData/<id> - получение перевала по ID"""
    print(f"\n=== Тест GET /submitData/{pass_id} ===")
    
    url = f"{API_URL}/{pass_id}/"
    response = requests.get(url)
    
    print(f"URL: {url}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response


def test_patch_pass(pass_id, update_data):
    """Тест PATCH /submitData/<id> - редактирование перевала"""
    print(f"\n=== Тест PATCH /submitData/{pass_id} ===")
    
    url = f"{API_URL}/{pass_id}/"
    headers = {'Content-Type': 'application/json'}
    
    response = requests.patch(url, json=update_data, headers=headers)
    
    print(f"URL: {url}")
    print(f"Update Data: {json.dumps(update_data, indent=2, ensure_ascii=False)}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response


def test_get_passes_by_user_email(email):
    """Тест GET /submitData/?user__email=<email> - получение перевалов пользователя"""
    print(f"\n=== Тест GET /submitData/?user__email={email} ===")
    
    url = f"{API_URL}/"
    params = {'user__email': email}
    
    response = requests.get(url, params=params)
    
    print(f"URL: {url}?user__email={email}")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Найдено перевалов: {len(data)}")
        for i, pass_item in enumerate(data):
            print(f"  {i+1}. ID: {pass_item.get('id', 'N/A')}, Название: {pass_item.get('title', 'N/A')}, Статус: {pass_item.get('status', 'N/A')}")
    else:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response


def test_create_pass():
    """Тест создания нового перевала для тестирования"""
    print("\n=== Создание тестового перевала ===")
    
    test_data = {
        "beauty_title": "Тестовый перевал",
        "title": "Перевал Тестовый",
        "other_titles": "Test Pass",
        "connect": "Соединяет долину А с долиной Б",
        "user": {
            "email": "test@example.com",
            "fam": "Тестов",
            "name": "Тест",
            "otc": "Тестович",
            "phone": "+7-900-000-00-00"
        },
        "coords": {
            "latitude": "45.3842",
            "longitude": "7.1729",
            "height": 2574
        },
        "level": {
            "winter": "1А",
            "summer": "н/к",
            "autumn": "1А",
            "spring": "1А"
        },
        "images": [
            {
                "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
                "title": "Тестовое изображение"
            }
        ]
    }
    
    headers = {'Content-Type': 'application/json'}
    response = requests.post(API_URL + "/", json=test_data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response


def main():
    """Основная функция для запуска тестов"""
    print("🚀 Начало тестирования API методов спринта 2")
    print("=" * 50)
    
    try:
        # 1. Создаем тестовый перевал
        create_response = test_create_pass()
        
        if create_response.status_code == 200:
            pass_id = create_response.json().get('id')
            print(f"\n✅ Перевал создан с ID: {pass_id}")
            
            # 2. Тестируем получение перевала по ID
            test_get_pass_by_id(pass_id)
            
            # 3. Тестируем редактирование перевала
            update_data = {
                "title": "Обновленный перевал",
                "beauty_title": "Красивый обновленный перевал",
                "coords": {
                    "latitude": "45.4000",
                    "longitude": "7.2000", 
                    "height": 2600
                }
            }
            test_patch_pass(pass_id, update_data)
            
            # 4. Тестируем получение перевалов пользователя
            test_get_passes_by_user_email("test@example.com")
            
            # 5. Тестируем попытку редактирования с недопустимыми полями
            forbidden_update = {
                "user": {
                    "email": "new@example.com",  # Попытка изменить email
                    "fam": "Новый"  # Попытка изменить фамилию
                }
            }
            print("\n=== Тест запрещенного редактирования ===")
            test_patch_pass(pass_id, forbidden_update)
            
        else:
            print(f"❌ Не удалось создать тестовый перевал: {create_response.json()}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения! Убедитесь, что сервер запущен на localhost:8000")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n🏁 Тестирование завершено")


if __name__ == "__main__":
    main() 