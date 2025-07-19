from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.db import transaction
import json
import base64
from .models import User, Coords, Level, Pass, Image
from .views import PassDataHandler
from .serializers import PassSerializer


class PassDataHandlerTestCase(TestCase):
    """Тесты для класса PassDataHandler"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.valid_data = {
            "beauty_title": "пер. ",
            "title": "Тестовый перевал",
            "other_titles": "Альтернативное название",
            "connect": "соединяет долины А и Б",
            "user": {
                "email": "test@example.com",
                "fam": "Тестов",
                "name": "Тест",
                "otc": "Тестович",
                "phone": "+7 900 000 00 00"
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
                {"data": base64.b64encode(b"fake_image_data").decode(), "title": "Тестовое изображение"}
            ]
        }
    
    def test_create_pass_success(self):
        """Тест успешного создания перевала"""
        success, result, pass_id = PassDataHandler.create_pass(self.valid_data)
        
        self.assertTrue(success)
        self.assertIsInstance(result, Pass)
        self.assertIsNotNone(pass_id)
        self.assertEqual(result.title, "Тестовый перевал")
        self.assertEqual(result.status, "new")
        
    def test_create_pass_missing_fields(self):
        """Тест создания перевала с недостающими полями"""
        invalid_data = {"title": "Только название"}
        
        success, result, pass_id = PassDataHandler.create_pass(invalid_data)
        
        self.assertFalse(success)
        self.assertIsNone(pass_id)
        self.assertIn("Недостаточно полей", str(result))
        
    def test_create_pass_invalid_email(self):
        """Тест создания перевала с некорректным email"""
        data = self.valid_data.copy()
        data['user']['email'] = "invalid_email"
        
        success, result, pass_id = PassDataHandler.create_pass(data)
        
        self.assertFalse(success)
        self.assertIsNone(pass_id)


class SubmitDataAPITestCase(APITestCase):
    """Тесты для API endpoint /submitData/"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.client = Client()
        self.url = reverse('submit_data')
        
        self.valid_data = {
            "beauty_title": "пер. ",
            "title": "API Тестовый перевал",
            "other_titles": "API Альтернативное название",
            "connect": "соединяет долины API А и API Б",
            "user": {
                "email": "api_test@example.com",
                "fam": "API Тестов",
                "name": "API Тест",
                "otc": "API Тестович",
                "phone": "+7 900 000 00 01"
            },
            "coords": {
                "latitude": "46.3842",
                "longitude": "8.1525",
                "height": "1300"
            },
            "level": {
                "winter": "1А",
                "summer": "1Б",
                "autumn": "1А",
                "spring": ""
            },
            "images": []
        }
        
        # Создаем тестового пользователя и перевал для тестов GET
        self.test_user = User.objects.create(
            email="existing@example.com",
            fam="Существующий",
            name="Пользователь",
            otc="Тестович",
            phone="+7 900 000 00 02"
        )
        
        self.test_coords = Coords.objects.create(
            latitude=47.1234,
            longitude=8.5678,
            height=1400
        )
        
        self.test_level = Level.objects.create(
            winter="1А",
            summer="1Б",
            autumn="1А",
            spring=""
        )
        
        self.test_pass = Pass.objects.create(
            beauty_title="пер. ",
            title="Существующий перевал",
            other_titles="Альтернативное",
            connect="соединяет долины X и Y",
            user=self.test_user,
            coords=self.test_coords,
            level=self.test_level,
            status="new"
        )
    
    def test_post_submit_data_success(self):
        """Тест успешного создания перевала через POST"""
        response = self.client.post(
            self.url,
            json.dumps(self.valid_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.json()
        self.assertEqual(response_data['status'], 200)
        self.assertIsNone(response_data['message'])
        self.assertIsNotNone(response_data['id'])
        
        # Проверяем что перевал создался в БД
        created_pass = Pass.objects.get(id=response_data['id'])
        self.assertEqual(created_pass.title, "API Тестовый перевал")
        self.assertEqual(created_pass.status, "new")
    
    def test_post_submit_data_missing_fields(self):
        """Тест POST с недостающими полями"""
        incomplete_data = {"title": "Только название"}
        
        response = self.client.post(
            self.url,
            json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response_data = response.json()
        self.assertEqual(response_data['status'], 400)
        self.assertIn("Недостаточно полей", response_data['message'])
        self.assertIsNone(response_data['id'])
    
    def test_get_passes_by_email_success(self):
        """Тест получения перевалов пользователя по email"""
        response = self.client.get(f"{self.url}?user__email={self.test_user.email}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.json()
        self.assertIsInstance(response_data, list)
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]['title'], "Существующий перевал")
    
    def test_get_passes_by_email_missing_param(self):
        """Тест GET без параметра user__email"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response_data = response.json()
        self.assertIn("user__email обязателен", response_data['error'])
    
    def test_get_passes_by_email_no_results(self):
        """Тест GET для несуществующего пользователя"""
        response = self.client.get(f"{self.url}?user__email=nonexistent@example.com")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.json()
        self.assertEqual(response_data, [])


class PassDetailAPITestCase(APITestCase):
    """Тесты для API endpoint /submitData/<id>/"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.client = Client()
        
        # Создаем тестовые данные
        self.test_user = User.objects.create(
            email="detail_test@example.com",
            fam="Детальный",
            name="Тест",
            otc="Тестович",
            phone="+7 900 000 00 03"
        )
        
        self.test_coords = Coords.objects.create(
            latitude=48.1234,
            longitude=9.5678,
            height=1500
        )
        
        self.test_level = Level.objects.create(
            winter="1Б",
            summer="2А",
            autumn="1Б",
            spring="1А"
        )
        
        self.test_pass = Pass.objects.create(
            beauty_title="пер. ",
            title="Детальный перевал",
            other_titles="Подробный",
            connect="соединяет долины M и N",
            user=self.test_user,
            coords=self.test_coords,
            level=self.test_level,
            status="new"
        )
        
        self.url = reverse('pass_detail', kwargs={'pk': self.test_pass.id})
    
    def test_get_pass_detail_success(self):
        """Тест получения информации о перевале по ID"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.json()
        self.assertEqual(response_data['title'], "Детальный перевал")
        self.assertEqual(response_data['status'], "new")
        self.assertEqual(response_data['user']['email'], "detail_test@example.com")
    
    def test_get_pass_detail_not_found(self):
        """Тест получения несуществующего перевала"""
        url = reverse('pass_detail', kwargs={'pk': 99999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_patch_pass_success(self):
        """Тест успешного редактирования перевала"""
        update_data = {
            "title": "Обновленный детальный перевал",
            "coords": {
                "latitude": "49.0000",
                "longitude": "10.0000",
                "height": "1600"
            }
        }
        
        response = self.client.patch(
            self.url,
            json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.json()
        self.assertEqual(response_data['state'], 1)
        self.assertIsNone(response_data['message'])
        
        # Проверяем что данные обновились
        updated_pass = Pass.objects.get(id=self.test_pass.id)
        self.assertEqual(updated_pass.title, "Обновленный детальный перевал")
        self.assertEqual(float(updated_pass.coords.height), 1600)
    
    def test_patch_pass_forbidden_user_fields(self):
        """Тест блокировки изменения пользовательских данных"""
        update_data = {
            "title": "Новое название",
            "user": {
                "email": "new_email@example.com",
                "fam": "Новая фамилия"
            }
        }
        
        response = self.client.patch(
            self.url,
            json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response_data = response.json()
        self.assertEqual(response_data['state'], 0)
        self.assertIn("Нельзя изменять поля пользователя", response_data['message'])
    
    def test_patch_pass_wrong_status(self):
        """Тест блокировки редактирования при неправильном статусе"""
        # Меняем статус на 'accepted'
        self.test_pass.status = 'accepted'
        self.test_pass.save()
        
        update_data = {"title": "Попытка обновления"}
        
        response = self.client.patch(
            self.url,
            json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response_data = response.json()
        self.assertEqual(response_data['state'], 0)
        self.assertIn("Редактирование невозможно", response_data['message'])


class ModelsTestCase(TestCase):
    """Тесты для моделей"""
    
    def test_user_model(self):
        """Тест модели User"""
        user = User.objects.create(
            email="model_test@example.com",
            fam="Модельный",
            name="Тест",
            otc="Тестович",
            phone="+7 900 000 00 04"
        )
        
        self.assertEqual(str(user), "Модельный Тест")
        self.assertEqual(user.email, "model_test@example.com")
    
    def test_coords_model(self):
        """Тест модели Coords"""
        coords = Coords.objects.create(
            latitude=50.1234,
            longitude=11.5678,
            height=1700
        )
        
        expected_str = f"lat: {coords.latitude}, lon: {coords.longitude}, h: {coords.height}"
        self.assertEqual(str(coords), expected_str)
    
    def test_level_model(self):
        """Тест модели Level"""
        level = Level.objects.create(
            winter="2А",
            summer="1Б",
            autumn="2А",
            spring="1А"
        )
        
        self.assertIn("зима: 2А", str(level))
        self.assertIn("лето: 1Б", str(level))
    
    def test_pass_model_default_status(self):
        """Тест что у Pass по умолчанию статус 'new'"""
        user = User.objects.create(
            email="status_test@example.com",
            fam="Статусный",
            name="Тест",
            phone="+7 900 000 00 05"
        )
        
        coords = Coords.objects.create(latitude=51, longitude=12, height=1800)
        level = Level.objects.create(summer="1А")
        
        pass_instance = Pass.objects.create(
            title="Тест статуса",
            user=user,
            coords=coords,
            level=level
        )
        
        self.assertEqual(pass_instance.status, "new")
