#!/usr/bin/env python3
"""
Тестовый скрипт для проверки REST API методов Спринта 2
Проверяет:
- GET /submitData/<id> — получение перевала по ID
- PATCH /submitData/<id> — редактирование перевала
- GET /submitData/?user__email=<email> — список перевалов пользователя
"""

import requests
import json

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
        "phone": "+7 999 999 99 99"
    },
    "coords": {
        "latitude": "55.7558",
        "longitude": "37.6176", 
        "height": "1500"
    },
    "level": {
        "winter": "2А",
        "summer": "1Б", 
        "autumn": "1Б",
        "spring": "2А"
    },
    "images": [
        {"data": "base64encoded_test_image_1", "title": "Вид на седловину"}, 
        {"data": "base64encoded_test_image_2", "title": "Подъём по склону"}
    ]
}

# Данные для обновления перевала
update_data = {
    "title": "Обновленное название перевала",
    "beauty_title": "пер. Обновленный",
    "other_titles": "Новое альтернативное название",
    "connect": "соединяет обновленные долины А и Б",
    "coords": {
        "latitude": "56.0000",
        "longitude": "38.0000", 
        "height": "1600"
    },
    "level": {
        "winter": "3А",
        "summer": "2А", 
        "autumn": "2А",
        "spring": "3А"
    }
}

def test_create_pass():
    """Создает тестовый перевал для дальнейших тестов"""
    print("📝 Создание тестового перевала...")
    try:
        response = requests.post(
            SUBMIT_DATA_URL,
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Статус: {response.status_code}")
        response_data = response.json()
        print(f"Ответ: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200 and response_data.get('status') == 200:
            pass_id = response_data.get('id')
            print(f"✅ Перевал создан с ID: {pass_id}")
            return pass_id
        else:
            print(f"❌ Ошибка создания перевала")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return None


def test_get_pass_by_id(pass_id):
    """Тестирует получение перевала по ID"""
    print(f"\n🔍 Тест GET /submitData/{pass_id}")
    try:
        response = requests.get(f"{SUBMIT_DATA_URL}{pass_id}/")
        
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Перевал получен:")
            print(f"   Название: {data.get('title')}")
            print(f"   Статус: {data.get('status')}")
            print(f"   Пользователь: {data.get('user', {}).get('email')}")
            print(f"   Координаты: {data.get('coords')}")
            return True
        else:
            print(f"❌ Ошибка: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return False


def test_update_pass(pass_id):
    """Тестирует редактирование перевала"""
    print(f"\n✏️ Тест PATCH /submitData/{pass_id}")
    try:
        response = requests.patch(
            f"{SUBMIT_DATA_URL}{pass_id}/",
            json=update_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Статус: {response.status_code}")
        response_data = response.json()
        print(f"Ответ: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200 and response_data.get('state') == 1:
            print("✅ Перевал успешно обновлен")
            return True
        else:
            print(f"❌ Ошибка обновления: {response_data.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return False


def test_update_pass_forbidden_fields(pass_id):
    """Тестирует попытку редактирования запрещенных полей"""
    print(f"\n🚫 Тест PATCH /submitData/{pass_id} (запрещенные поля)")
    
    forbidden_data = {
        "title": "Новое название",
        "user": {
            "email": "newemail@example.com",  # Запрещено!
            "fam": "Новая Фамилия"           # Запрещено!
        }
    }
    
    try:
        response = requests.patch(
            f"{SUBMIT_DATA_URL}{pass_id}/",
            json=forbidden_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Статус: {response.status_code}")
        response_data = response.json()
        print(f"Ответ: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 400 and response_data.get('state') == 0:
            print("✅ Запрещенные поля корректно заблокированы")
            return True
        else:
            print("❌ Ошибка: запрещенные поля не заблокированы")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return False


def test_get_passes_by_user_email():
    """Тестирует получение перевалов пользователя по email"""
    print(f"\n📋 Тест GET /submitData/?user__email=test@example.com")
    try:
        response = requests.get(f"{SUBMIT_DATA_URL}?user__email=test@example.com")
        
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Найдено {len(data)} перевалов пользователя:")
            for i, pass_item in enumerate(data, 1):
                print(f"   {i}. {pass_item.get('title')} (ID: {pass_item.get('id')}) - статус: {pass_item.get('status')}")
            return True
        else:
            print(f"❌ Ошибка: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return False


def test_get_passes_by_nonexistent_email():
    """Тестирует получение перевалов несуществующего пользователя"""
    print(f"\n🔍 Тест GET /submitData/?user__email=nonexistent@example.com")
    try:
        response = requests.get(f"{SUBMIT_DATA_URL}?user__email=nonexistent@example.com")
        
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if len(data) == 0:
                print("✅ Для несуществующего пользователя возвращен пустой список")
                return True
            else:
                print(f"❌ Неожиданно найдено {len(data)} перевалов")
                return False
        else:
            print(f"❌ Ошибка: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return False


def test_get_nonexistent_pass():
    """Тестирует получение несуществующего перевала"""
    print(f"\n🔍 Тест GET /submitData/99999 (несуществующий ID)")
    try:
        response = requests.get(f"{SUBMIT_DATA_URL}99999/")
        
        print(f"Статус: {response.status_code}")
        if response.status_code == 404:
            print("✅ Для несуществующего ID корректно возвращен 404")
            return True
        else:
            print(f"❌ Неожиданный статус: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return False


if __name__ == "__main__":
    print("🚀 Запуск тестов API Спринта 2")
    print("=" * 60)
    
    # Проверяем подключение
    try:
        response = requests.get(BASE_URL, timeout=5)
        print("✅ Сервер доступен")
    except:
        print("❌ Сервер недоступен. Убедитесь, что он запущен на localhost:8000")
        exit(1)
    
    results = []
    
    # 1. Создаем тестовый перевал
    pass_id = test_create_pass()
    if not pass_id:
        print("❌ Невозможно продолжить тесты без созданного перевала")
        exit(1)
    
    # 2. Тестируем получение перевала по ID
    results.append(test_get_pass_by_id(pass_id))
    
    # 3. Тестируем редактирование перевала
    results.append(test_update_pass(pass_id))
    
    # 4. Тестируем блокировку запрещенных полей
    results.append(test_update_pass_forbidden_fields(pass_id))
    
    # 5. Тестируем получение перевалов пользователя
    results.append(test_get_passes_by_user_email())
    
    # 6. Тестируем несуществующего пользователя
    results.append(test_get_passes_by_nonexistent_email())
    
    # 7. Тестируем несуществующий перевал
    results.append(test_get_nonexistent_pass())
    
    # Итоги
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 Все тесты пройдены! ({passed}/{total})")
    else:
        print(f"⚠️ Пройдено тестов: {passed}/{total}")
    print("=" * 60) 