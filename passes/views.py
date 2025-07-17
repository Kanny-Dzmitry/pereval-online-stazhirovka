from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404
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


@api_view(['POST', 'GET'])
def submit_data(request):
    """
    REST API метод POST/GET submitData.
    
    POST: Получает и сохраняет информацию о перевале от мобильного приложения туриста.
    GET: Возвращает список перевалов пользователя по email (если указан параметр user__email)
    
    Endpoints: 
    - POST /submitData/
    - GET /submitData/?user__email=<email>
    
    Returns:
        JSON response with status, message and id fields (POST)
        JSON response со списком перевалов пользователя (GET)
    """
    if request.method == 'GET':
        # Обработка GET запроса - получение перевалов пользователя по email
        try:
            # Получаем email из параметров запроса
            user_email = request.GET.get('user__email')
            
            if not user_email:
                return Response(
                    {'error': 'Необходимо указать параметр user__email'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Получаем все перевалы пользователя с данным email
            passes = Pass.objects.filter(user__email=user_email).order_by('-add_time')
            
            # Сериализуем данные
            serializer = PassSerializer(passes, many=True)
            
            logger.info(f"Запрошены перевалы пользователя: {user_email}, найдено: {len(passes)}")
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            error_message = f"Ошибка при получении перевалов пользователя: {str(e)}"
            logger.error(error_message)
            return Response(
                {'error': error_message}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # Обработка POST запроса - создание нового перевала
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


@api_view(['GET', 'PATCH'])
def pass_detail(request, pass_id):
    """
    REST API методы для работы с конкретным перевалом.
    
    GET /submitData/<id> - получение перевала по ID
    PATCH /submitData/<id> - редактирование перевала
    
    Args:
        pass_id (int): ID перевала
        
    Returns:
        JSON response с данными перевала (GET)
        JSON response с результатом операции (PATCH)
    """
    if request.method == 'GET':
        # Обработка GET запроса - получение перевала по ID
        try:
            # Получаем перевал по ID или возвращаем 404
            pass_instance = get_object_or_404(Pass, id=pass_id)
            
            # Сериализуем данные
            serializer = PassSerializer(pass_instance)
            
            logger.info(f"Запрошен перевал ID: {pass_id}")
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            error_message = f"Ошибка при получении перевала: {str(e)}"
            logger.error(error_message)
            return Response(
                {'error': error_message}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # Обработка PATCH запроса - редактирование перевала
    try:
        # Получаем перевал по ID или возвращаем 404
        pass_instance = get_object_or_404(Pass, id=pass_id)
        
        # Проверяем статус перевала
        if pass_instance.status != 'new':
            response_data = {
                'state': 0,
                'message': f'Нельзя редактировать данные перевала со статусом "{pass_instance.get_status_display()}". Редактирование доступно только для статуса "new".'
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        # Получаем данные из запроса
        data = request.data
        
        # Проверяем, что пользователь не пытается изменить запрещенные поля
        user_data = data.get('user', {})
        if any(field in user_data for field in ['fam', 'name', 'otc', 'email', 'phone']):
            response_data = {
                'state': 0,
                'message': 'Нельзя редактировать ФИО, адрес почты и номер телефона пользователя.'
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        # Удаляем user из данных, если он есть (т.к. его нельзя изменять)
        if 'user' in data:
            del data['user']
        
        try:
            with transaction.atomic():
                # Обновляем основные поля перевала
                for field in ['beauty_title', 'title', 'other_titles', 'connect']:
                    if field in data:
                        setattr(pass_instance, field, data[field])
                
                # Обновляем координаты
                if 'coords' in data:
                    coords_data = data['coords']
                    for field in ['latitude', 'longitude', 'height']:
                        if field in coords_data:
                            setattr(pass_instance.coords, field, coords_data[field])
                    pass_instance.coords.save()
                
                # Обновляем уровень сложности
                if 'level' in data:
                    level_data = data['level']
                    for field in ['winter', 'summer', 'autumn', 'spring']:
                        if field in level_data:
                            setattr(pass_instance.level, field, level_data[field])
                    pass_instance.level.save()
                
                # Обновляем изображения (если переданы)
                if 'images' in data:
                    # Удаляем старые изображения
                    pass_instance.images.all().delete()
                    
                    # Создаем новые изображения
                    from .serializers import ImageSerializer
                    for image_data in data['images']:
                        image_serializer = ImageSerializer(data=image_data)
                        if image_serializer.is_valid():
                            image_serializer.save(pass_instance=pass_instance)
                
                # Сохраняем изменения в основной модели
                pass_instance.save()
                
                logger.info(f"Обновлен перевал ID: {pass_id}")
                
                response_data = {
                    'state': 1,
                    'message': 'Данные перевала успешно обновлены.'
                }
                return Response(response_data, status=status.HTTP_200_OK)
                
        except Exception as e:
            error_message = f"Ошибка при обновлении перевала: {str(e)}"
            logger.error(error_message)
            response_data = {
                'state': 0,
                'message': error_message
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        error_message = f"Ошибка сервера: {str(e)}"
        logger.error(error_message)
        response_data = {
            'state': 0,
            'message': error_message
        }
        return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
