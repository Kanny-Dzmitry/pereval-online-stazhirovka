from rest_framework import serializers
from .models import User, Coords, Level, Pass, Image
import base64
from django.core.files.base import ContentFile


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя"""
    
    class Meta:
        model = User
        fields = ['email', 'fam', 'name', 'otc', 'phone']


class CoordsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели координат"""
    
    class Meta:
        model = Coords
        fields = ['latitude', 'longitude', 'height']


class LevelSerializer(serializers.ModelSerializer):
    """Сериализатор для модели уровня сложности"""
    
    class Meta:
        model = Level
        fields = ['winter', 'summer', 'autumn', 'spring']


class ImageSerializer(serializers.ModelSerializer):
    """Сериализатор для модели изображения"""
    data = serializers.CharField()  # Принимаем base64 строку
    
    class Meta:
        model = Image
        fields = ['data', 'title']
    
    def create(self, validated_data):
        # Обработка base64 данных изображения
        data = validated_data.pop('data')
        title = validated_data.pop('title', '')
        
        try:
            # Декодируем base64, если это необходимо
            if data.startswith('data:image'):
                format, imgstr = data.split(';base64,')
                ext = format.split('/')[-1]
                decoded_data = base64.b64decode(imgstr)
                data = ContentFile(decoded_data, name=f'{title}.{ext}')
            elif data:
                # Если это простая base64 строка
                # Добавляем padding если необходимо
                missing_padding = len(data) % 4
                if missing_padding:
                    data += '=' * (4 - missing_padding)
                decoded_data = base64.b64decode(data)
                data = ContentFile(decoded_data, name=f'{title}.jpg')
            else:
                # Если данных нет, создаем пустой файл
                data = ContentFile(b'', name=f'{title}.jpg')
        except Exception as e:
            # Если декодирование не удалось, создаем пустой файл
            data = ContentFile(b'', name=f'{title}.jpg')
        
        image = Image.objects.create(
            data=data,
            title=title,
            **validated_data
        )
        return image


class PassSerializer(serializers.ModelSerializer):
    """Сериализатор для модели перевала"""
    user = UserSerializer()
    coords = CoordsSerializer()
    level = LevelSerializer() 
    images = ImageSerializer(many=True)
    
    class Meta:
        model = Pass
        fields = [
            'beauty_title', 'title', 'other_titles', 'connect',
            'add_time', 'user', 'coords', 'level', 'images', 'status'
        ]
        read_only_fields = ['add_time', 'status']
    
    def create(self, validated_data):
        # Извлекаем данные для связанных моделей
        user_data = validated_data.pop('user')
        coords_data = validated_data.pop('coords')
        level_data = validated_data.pop('level')
        images_data = validated_data.pop('images')
        
        # Создаем или получаем пользователя
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults=user_data
        )
        
        # Создаем координаты
        coords = Coords.objects.create(**coords_data)
        
        # Создаем уровень сложности
        level = Level.objects.create(**level_data)
        
        # Создаем перевал
        pass_instance = Pass.objects.create(
            user=user,
            coords=coords,
            level=level,
            status='new',  # Согласно ТЗ, по умолчанию статус "new"
            **validated_data
        )
        
        # Создаем изображения
        for image_data in images_data:
            image_serializer = ImageSerializer(data=image_data)
            if image_serializer.is_valid():
                image_serializer.save(pass_instance=pass_instance)
        
        return pass_instance


class SubmitDataResponseSerializer(serializers.Serializer):
    """Сериализатор для ответа метода submitData"""
    status = serializers.IntegerField()
    message = serializers.CharField(allow_null=True)
    id = serializers.IntegerField(allow_null=True) 