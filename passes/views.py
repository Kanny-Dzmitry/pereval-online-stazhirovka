from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction, IntegrityError
from .models import User, Coords, Level, Pass, Image
from .serializers import (
    PassSerializer, SubmitDataResponseSerializer,
    CoordsSerializer, LevelSerializer, ImageSerializer
)
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
def submit_data_list(request):
    """
    REST API методы для работы со списком перевалов.
    
    POST /submitData - создание нового перевала
    GET /submitData?user__email=<email> - получение списка перевалов пользователя
    """
    if request.method == 'POST':
        return submit_data_post(request)
    elif request.method == 'GET':
        return get_passes_by_user_email(request)


def submit_data_post(request):
    """
    Создание нового перевала (POST метод).
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


@api_view(['GET', 'PATCH'])
def submit_data_detail(request, pk):
    """
    REST API методы для работы с отдельным перевалом.
    
    GET /submitData/<id> - получение информации о перевале
    PATCH /submitData/<id> - редактирование перевала (если статус 'new')
    """
    if request.method == 'GET':
        return get_pass_by_id(request, pk)
    elif request.method == 'PATCH':
        return update_pass(request, pk)


# Оставляю старую функцию submit_data для совместимости, но она будет вызывать новую
@api_view(['POST'])
def submit_data(request):
    """
    Устаревшая функция для обратной совместимости.
    Перенаправляет на submit_data_post.
    """
    return submit_data_post(request)


@api_view(['GET'])
def get_pass_by_id(request, pk):
    """
    REST API метод GET submitData/<id>.
    
    Получает информацию о перевале по его ID, включая статус модерации.
    
    Endpoint: GET /submitData/<id>
    
    Args:
        pk (int): ID перевала
        
    Returns:
        JSON response с полной информацией о перевале
    """
    try:
        # Получаем перевал по ID
        pass_instance = get_object_or_404(Pass, pk=pk)
        
        # Сериализуем данные
        serializer = PassSerializer(pass_instance)
        
        logger.info(f"Запрошена информация о перевале ID: {pk}")
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        error_message = f"Ошибка при получении данных: {str(e)}"
        logger.error(error_message)
        return Response(
            {'error': error_message}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PATCH'])
def update_pass(request, pk):
    """
    REST API метод PATCH submitData/<id>.
    
    Редактирует существующую запись перевала, если она в статусе 'new'.
    Редактировать можно все поля, кроме ФИО, адреса почты и номера телефона.
    
    Endpoint: PATCH /submitData/<id>
    
    Args:
        pk (int): ID перевала для редактирования
        
    Returns:
        JSON response с результатом операции:
        - state: 1 если успешно, 0 если не удалось
        - message: сообщение об ошибке (если есть)
    """
    try:
        # Получаем перевал по ID
        pass_instance = get_object_or_404(Pass, pk=pk)
        
        # Проверяем статус перевала
        if pass_instance.status != 'new':
            response_data = {
                'state': 0,
                'message': f'Редактирование невозможно. Текущий статус: {pass_instance.get_status_display()}'
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        # Получаем данные из запроса
        data = request.data.copy()
        
        # Проверяем, что не пытаются изменить пользовательские данные
        if 'user' in data:
            current_user_data = {
                'email': pass_instance.user.email,
                'fam': pass_instance.user.fam,
                'name': pass_instance.user.name,
                'otc': pass_instance.user.otc,
                'phone': pass_instance.user.phone
            }
            
            # Проверяем, изменились ли запрещенные поля
            new_user_data = data['user']
            forbidden_changes = []
            
            if new_user_data.get('email') != current_user_data['email']:
                forbidden_changes.append('email')
            if new_user_data.get('fam') != current_user_data['fam']:
                forbidden_changes.append('fam')
            if new_user_data.get('name') != current_user_data['name']:
                forbidden_changes.append('name')
            if new_user_data.get('otc') != current_user_data['otc']:
                forbidden_changes.append('otc')
            if new_user_data.get('phone') != current_user_data['phone']:
                forbidden_changes.append('phone')
                
            if forbidden_changes:
                response_data = {
                    'state': 0,
                    'message': f'Нельзя изменять поля пользователя: {", ".join(forbidden_changes)}'
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        # Выполняем обновление в транзакции
        with transaction.atomic():
            # Обновляем координаты если переданы
            if 'coords' in data:
                coords_serializer = CoordsSerializer(
                    pass_instance.coords, 
                    data=data['coords'], 
                    partial=True
                )
                if coords_serializer.is_valid():
                    coords_serializer.save()
                else:
                    response_data = {
                        'state': 0,
                        'message': f'Ошибка в данных координат: {coords_serializer.errors}'
                    }
                    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            # Обновляем уровень сложности если передан
            if 'level' in data:
                level_serializer = LevelSerializer(
                    pass_instance.level,
                    data=data['level'],
                    partial=True
                )
                if level_serializer.is_valid():
                    level_serializer.save()
                else:
                    response_data = {
                        'state': 0,
                        'message': f'Ошибка в данных уровня сложности: {level_serializer.errors}'
                    }
                    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            # Обновляем основную информацию о перевале
            allowed_fields = ['beauty_title', 'title', 'other_titles', 'connect']
            pass_data = {field: data[field] for field in allowed_fields if field in data}
            
            if pass_data:
                for field, value in pass_data.items():
                    setattr(pass_instance, field, value)
                pass_instance.save()
            
            # Обрабатываем изображения если переданы
            if 'images' in data:
                # Удаляем старые изображения
                pass_instance.images.all().delete()
                
                # Создаем новые изображения
                images_data = data['images']
                for image_data in images_data:
                    image_serializer = ImageSerializer(data=image_data)
                    if image_serializer.is_valid():
                        image_serializer.save(pass_instance=pass_instance)
                    else:
                        response_data = {
                            'state': 0,
                            'message': f'Ошибка в данных изображений: {image_serializer.errors}'
                        }
                        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        response_data = {
            'state': 1,
            'message': None
        }
        
        logger.info(f"Успешно обновлен перевал ID: {pk}")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        error_message = f"Ошибка при обновлении: {str(e)}"
        logger.error(error_message)
        response_data = {
            'state': 0,
            'message': error_message
        }
        return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_passes_by_user_email(request):
    """
    REST API метод GET submitData/?user__email=<email>.
    
    Получает список всех объектов, которые пользователь отправил на сервер.
    
    Endpoint: GET /submitData/?user__email=<email>
    
    Returns:
        JSON response со списком перевалов пользователя
    """
    try:
        # Получаем email из параметров запроса
        user_email = request.GET.get('user__email')
        
        if not user_email:
            return Response(
                {'error': 'Параметр user__email обязателен'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Находим перевалы пользователя
        passes = Pass.objects.filter(user__email=user_email)
        
        # Сериализуем данные
        serializer = PassSerializer(passes, many=True)
        
        logger.info(f"Запрошены перевалы пользователя: {user_email}, найдено: {passes.count()}")
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        error_message = f"Ошибка при получении списка перевалов: {str(e)}"
        logger.error(error_message)
        return Response(
            {'error': error_message}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
