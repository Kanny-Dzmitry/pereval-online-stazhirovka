from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction, IntegrityError
from .models import User, Coords, Level, Pass, Image
from .serializers import PassSerializer, SubmitDataResponseSerializer
import logging

# Create your views here.

# Настраиваем логирование
logger = logging.getLogger(__name__)


class PassDataHandler:
    """
    Класс для работы с данными перевалов.
    Реализует методы для добавления новых записей в БД.
    """
    
    @staticmethod
    def create_pass(data):
        """
        Создает новую запись о перевале.
        Автоматически устанавливает status = "new" для новых записей.
        Обрабатывает все связанные сущности (пользователь, координаты, фотографии).
        
        Args:
            data (dict): Данные о перевале в формате JSON
            
        Returns:
            tuple: (success: bool, result: Pass|str, pass_id: int|None)
        """
        try:
            with transaction.atomic():
                # Используем сериализатор для валидации и создания
                serializer = PassSerializer(data=data)
                
                if serializer.is_valid():
                    pass_instance = serializer.save()
                    logger.info(f"Создан новый перевал ID: {pass_instance.id}")
                    return True, pass_instance, pass_instance.id
                else:
                    error_message = "Недостаточно полей или некорректные данные"
                    logger.error(f"Ошибка валидации: {serializer.errors}")
                    return False, error_message, None
                    
        except IntegrityError as e:
            error_message = f"Ошибка целостности данных: {str(e)}"
            logger.error(error_message)
            return False, error_message, None
            
        except Exception as e:
            error_message = f"Ошибка сервера/БД: {str(e)}"
            logger.error(error_message)
            return False, error_message, None


@api_view(['POST'])
def submit_data(request):
    """
    REST API метод POST submitData.
    
    Получает и сохраняет информацию о перевале от мобильного приложения туриста.
    
    Endpoint: POST /submitData
    
    Returns:
        JSON response with status, message and id fields
    """
    try:
        # Получаем данные из запроса
        data = request.data
        
        # Логируем входящий запрос
        logger.info(f"Получен запрос submitData: {data}")
        
        # Проверяем наличие обязательных полей
        required_fields = ['title', 'user', 'coords', 'level']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            response_data = {
                'status': 400,
                'message': f"Недостаточно полей. Отсутствуют: {', '.join(missing_fields)}",
                'id': None
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        # Создаем запись через класс работы с данными
        success, result, pass_id = PassDataHandler.create_pass(data)
        
        if success:
            # Успешное сохранение
            response_data = {
                'status': 200,
                'message': None,
                'id': pass_id
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # Ошибка при сохранении
            if "Недостаточно полей" in str(result):
                response_data = {
                    'status': 400,
                    'message': str(result),
                    'id': None
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            else:
                response_data = {
                    'status': 500,
                    'message': str(result),
                    'id': None
                }
                return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
    except Exception as e:
        # Обработка непредвиденных ошибок
        error_message = f"Ошибка сервера: {str(e)}"
        logger.error(error_message)
        response_data = {
            'status': 500,
            'message': error_message,
            'id': None
        }
        return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
