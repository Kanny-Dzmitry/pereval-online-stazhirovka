#!/usr/bin/env python3
"""
Тестовый скрипт для проверки новых REST API методов второго спринта
"""

import requests
import json
import time

# URL для тестирования (локальный сервер)
BASE_URL = "http://localhost:8000"
SUBMIT_DATA_URL = f"{BASE_URL}/submitData/"

# Тестовые данные для создания перевала
test_data = {
    "beauty_title": "пер. ",
    "title": "Тестовый перевал",
    "other_titles": "Альтернативное название", 
    "connect": "соединяет долины Тест1 и Тест2",
    "user": {
        "email": "test@example.com",
        "fam": "Тестов", 
        "name": "Тест",
        "otc": "Тестович",
        "phone": "+7 900 000 00 00"
    },
    "coords": {
        "latitude": 45.1234,
        "longitude": 7.5678, 
        "height": 1500
    },
    "level": {
        "winter": "1А",
        "summer": "1А", 
        "autumn": "1А",
        "spring": ""
    },
    "images": []
}

def wait_for_server(max_attempts=30):
    """Ожидает запуска сервера"""
    print("Ожидание запуска сервера...")
    for i in range(max_attempts):
        try:
            response = requests.get(BASE_URL, timeout=2)
            print("✅ Сервер запущен!")
            return True
        except requests.exceptions.RequestException:
            print(f"Попытка {i+1}/{max_attempts}...")
            time.sleep(2)
    print("❌ Не удалось дождаться запуска сервера")
    return False

def test_create_pass():
    """Создает новый перевал для тестирования"""
    print("\n" + "="*60)
    print("1. Тест создания нового перевала (POST /submitData/)")
    print("="*60)
    
    try:
        response = requests.post(
            SUBMIT_DATA_URL,
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Статус: {response.status_code}")
        print(f"Ответ: {response.json()}")
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('status') == 200 and response_data.get('id'):
                print(f"✅ Перевал создан с ID: {response_data['id']}")
                return response_data['id']
        
        print("❌ Ошибка создания перевала")
        return None
            
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return None

def test_get_pass_by_id(pass_id):
    """Тестирует получение перевала по ID"""
    print("\n" + "="*60)
    print(f"2. Тест получения перевала по ID (GET /submitData/{pass_id}/)")
    print("="*60)
    
    try:
        response = requests.get(f"{SUBMIT_DATA_URL}{pass_id}/")
        
        print(f"Статус: {response.status_code}")
        response_data = response.json()
        print(f"Название: {response_data.get('title', 'Не найдено')}")
        print(f"Статус модерации: {response_data.get('status', 'Не найдено')}")
        print(f"Email пользователя: {response_data.get('user', {}).get('email', 'Не найдено')}")
        
        if response.status_code == 200:
            print("✅ Получение перевала по ID работает!")
            return True
        else:
            print("❌ Ошибка получения перевала по ID")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return False

def test_get_passes_by_email():
    """Тестирует получение перевалов пользователя по email"""
    print("\n" + "="*60)
    print("3. Тест получения перевалов пользователя (GET /submitData/?user__email=test@example.com)")
    print("="*60)
    
    try:
        email = "test@example.com"
        response = requests.get(f"{SUBMIT_DATA_URL}?user__email={email}")
        
        print(f"Статус: {response.status_code}")
        response_data = response.json()
        
        if response.status_code == 200:
            print(f"Найдено перевалов: {len(response_data)}")
            if response_data:
                for pass_item in response_data:
                    print(f"- ID: {pass_item.get('id', 'Нет')}, Название: {pass_item.get('title', 'Нет')}")
            print("✅ Получение перевалов по email работает!")
            return True
        else:
            print("❌ Ошибка получения перевалов по email")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return False

def test_patch_pass(pass_id):
    """Тестирует редактирование перевала"""
    print("\n" + "="*60)
    print(f"4. Тест редактирования перевала (PATCH /submitData/{pass_id}/)")
    print("="*60)
    
    # Данные для обновления (без пользовательских данных)
    update_data = {
        "title": "Обновленный тестовый перевал",
        "other_titles": "Новое альтернативное название",
        "coords": {
            "latitude": 45.9999,
            "longitude": 7.9999, 
            "height": 2000
        }
    }
    
    try:
        response = requests.patch(
            f"{SUBMIT_DATA_URL}{pass_id}/",
            json=update_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Статус: {response.status_code}")
        response_data = response.json()
        print(f"Ответ: {response_data}")
        
        if response.status_code == 200 and response_data.get('state') == 1:
            print("✅ Редактирование перевала работает!")
            return True
        else:
            print("❌ Ошибка редактирования перевала")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return False

def test_patch_forbidden_fields(pass_id):
    """Тестирует блокировку изменения запрещенных полей"""
    print("\n" + "="*60)
    print("5. Тест блокировки изменения пользовательских данных")
    print("="*60)
    
    # Попытка изменить пользовательские данные
    forbidden_update = {
        "title": "Еще одно обновление",
        "user": {
            "email": "new@example.com",  # Запрещено изменять
            "fam": "Новая фамилия",     # Запрещено изменять
            "name": "Новое имя",        # Запрещено изменять
            "otc": "Новое отчество",    # Запрещено изменять
            "phone": "+7 999 999 99 99" # Запрещено изменять
        }
    }
    
    try:
        response = requests.patch(
            f"{SUBMIT_DATA_URL}{pass_id}/",
            json=forbidden_update,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Статус: {response.status_code}")
        response_data = response.json()
        print(f"Ответ: {response_data}")
        
        if response.status_code == 400 and response_data.get('state') == 0:
            print("✅ Блокировка изменения пользовательских данных работает!")
            return True
        else:
            print("❌ Блокировка не работает - это ошибка!")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск тестов новых API методов второго спринта")
    print("="*60)
    
    # Ожидаем запуска сервера
    if not wait_for_server():
        exit(1)
    
    results = []
    
    # 1. Создаем новый перевал
    pass_id = test_create_pass()
    results.append(pass_id is not None)
    
    if pass_id:
        # 2. Получаем перевал по ID
        results.append(test_get_pass_by_id(pass_id))
        
        # 3. Получаем перевалы пользователя по email
        results.append(test_get_passes_by_email())
        
        # 4. Редактируем перевал
        results.append(test_patch_pass(pass_id))
        
        # 5. Тестируем блокировку запрещенных полей
        results.append(test_patch_forbidden_fields(pass_id))
    else:
        print("⚠️ Пропускаем остальные тесты из-за ошибки создания перевала")
    
    # Результаты
    print("\n" + "="*60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("="*60)
    
    test_names = [
        "POST /submitData/ (создание)",
        "GET /submitData/<id>/ (получение по ID)",
        "GET /submitData/?user__email=<email> (по email)",
        "PATCH /submitData/<id>/ (редактирование)",
        "PATCH блокировка запрещенных полей"
    ]
    
    for i, (test_name, result) in enumerate(zip(test_names, results)):
        status = "✅ ПРОЙДЕН" if result else "❌ НЕ ПРОЙДЕН"
        print(f"{i+1}. {test_name}: {status}")
    
    success_count = sum(results)
    total_count = len(results)
    
    print("\n" + "="*60)
    if success_count == total_count:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ Все новые API методы второго спринта работают корректно")
    else:
        print(f"⚠️ ПРОЙДЕНО {success_count} из {total_count} тестов")
        print("❌ Требуется дополнительная отладка")
    print("="*60) 