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
    REST API методы для submitData.
    
    POST /submitData - Получает и сохраняет информацию о перевале
    GET /submitData?user__email=<email> - Получает все перевалы пользователя
    
    Returns:
        JSON response 
    """
    # Обработка GET запроса для получения перевалов пользователя
    if request.method == 'GET':
        try:
            # Получаем email из параметров запроса
            user_email = request.GET.get('user__email')
            
            if not user_email:
                return Response({
                    'error': 'Параметр user__email обязателен'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Получаем все перевалы пользователя с указанным email
            passes = Pass.objects.filter(user__email=user_email).order_by('-add_time')
            
            if not passes.exists():
                logger.info(f"Пользователь с email {user_email} не найден или у него нет перевалов")
                return Response([], status=status.HTTP_200_OK)
            
            # Сериализуем данные
            serializer = PassSerializer(passes, many=True)
            
            logger.info(f"Запрошены все перевалы пользователя с email: {user_email}, найдено: {passes.count()}")
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            error_message = f"Ошибка при получении перевалов пользователя: {str(e)}"
            logger.error(error_message)
            return Response(
                {'error': error_message}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # Обработка POST запроса для создания нового перевала
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
def pass_detail(request, pk):
    """
    REST API методы для работы с отдельным перевалом.
    
    GET /submitData/<id> - Получает одну запись по её id
    PATCH /submitData/<id> - Редактирует запись, если статус 'new'
    
    Returns:
        JSON response
    """
    # Получаем перевал по ID или возвращаем 404
    pass_instance = get_object_or_404(Pass, pk=pk)
    
    # Обработка GET запроса
    if request.method == 'GET':
        try:
            # Сериализуем данные
            serializer = PassSerializer(pass_instance)
            
            logger.info(f"Запрошена информация о перевале ID: {pk}")
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            error_message = f"Ошибка при получении перевала: {str(e)}"
            logger.error(error_message)
            return Response(
                {'error': error_message}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # Обработка PATCH запроса
    elif request.method == 'PATCH':
        try:
            # Проверяем статус - можно редактировать только записи со статусом 'new'
            if pass_instance.status != 'new':
                return Response({
                    'state': 0,
                    'message': f'Редактирование невозможно. Статус записи: {pass_instance.status}. Можно редактировать только записи со статусом "new".'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            data = request.data.copy()
            
            # Проверяем и блокируем изменение пользовательских данных (ФИО, email, телефон)
            if 'user' in data:
                current_user_data = {
                    'email': pass_instance.user.email,
                    'fam': pass_instance.user.fam,
                    'name': pass_instance.user.name,
                    'otc': pass_instance.user.otc,
                    'phone': pass_instance.user.phone
                }
                
                # Проверяем, пытается ли пользователь изменить запрещенные поля
                user_data = data['user']
                forbidden_changes = []
                
                if user_data.get('email') != current_user_data['email']:
                    forbidden_changes.append('email')
                if user_data.get('fam') != current_user_data['fam']:
                    forbidden_changes.append('fam')
                if user_data.get('name') != current_user_data['name']:
                    forbidden_changes.append('name')
                if user_data.get('otc') != current_user_data['otc']:
                    forbidden_changes.append('otc')
                if user_data.get('phone') != current_user_data['phone']:
                    forbidden_changes.append('phone')
                
                if forbidden_changes:
                    return Response({
                        'state': 0,
                        'message': f'Нельзя изменять поля пользователя: {", ".join(forbidden_changes)}. Можно редактировать только данные о перевале.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Убираем данные пользователя из обновления, так как они не должны изменяться
                data.pop('user')
            
            with transaction.atomic():
                # Обновляем координаты если они переданы
                if 'coords' in data:
                    coords_data = data.pop('coords')
                    for field, value in coords_data.items():
                        setattr(pass_instance.coords, field, value)
                    pass_instance.coords.save()
                
                # Обновляем уровень сложности если он передан
                if 'level' in data:
                    level_data = data.pop('level')
                    for field, value in level_data.items():
                        setattr(pass_instance.level, field, value)
                    pass_instance.level.save()
                
                # Обрабатываем изображения если они переданы
                if 'images' in data:
                    images_data = data.pop('images')
                    # Удаляем старые изображения
                    pass_instance.images.all().delete()
                    # Создаем новые изображения
                    for image_data in images_data:
                        Image.objects.create(
                            title=image_data.get('title', ''),
                            data=image_data.get('data', ''),
                            pass_instance=pass_instance
                        )
                
                # Обновляем основные поля перевала
                for field, value in data.items():
                    if hasattr(pass_instance, field):
                        setattr(pass_instance, field, value)
                
                pass_instance.save()
                
                logger.info(f"Перевал ID {pk} успешно обновлен")
                
                return Response({
                    'state': 1,
                    'message': None
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            error_message = f"Ошибка при обновлении перевала: {str(e)}"
            logger.error(error_message)
            return Response({
                'state': 0,
                'message': error_message
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






