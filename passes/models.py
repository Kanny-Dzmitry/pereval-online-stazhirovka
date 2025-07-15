from django.db import models


class User(models.Model):
    """Модель пользователя системы"""
    email = models.EmailField(max_length=255, unique=True)
    fam = models.CharField(max_length=100, verbose_name='Фамилия')
    name = models.CharField(max_length=100, verbose_name='Имя')
    otc = models.CharField(max_length=100, verbose_name='Отчество', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон')

    class Meta:
        db_table = 'pereval_users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.fam} {self.name}"


class Coords(models.Model):
    """Модель координат перевала"""
    latitude = models.DecimalField(
        max_digits=10, decimal_places=7,
        verbose_name='Широта'
    )
    longitude = models.DecimalField(
        max_digits=10, decimal_places=7,
        verbose_name='Долгота'
    )
    height = models.IntegerField(verbose_name='Высота')

    class Meta:
        db_table = 'pereval_coords'
        verbose_name = 'Координаты'
        verbose_name_plural = 'Координаты'

    def __str__(self):
        return f"lat: {self.latitude}, lon: {self.longitude}, h: {self.height}"


class Level(models.Model):
    """Модель уровня сложности перевала"""
    winter = models.CharField(max_length=10, blank=True, verbose_name='Зима')
    summer = models.CharField(max_length=10, blank=True, verbose_name='Лето')
    autumn = models.CharField(max_length=10, blank=True, verbose_name='Осень')
    spring = models.CharField(max_length=10, blank=True, verbose_name='Весна')

    class Meta:
        db_table = 'pereval_level'
        verbose_name = 'Уровень сложности'
        verbose_name_plural = 'Уровни сложности'

    def __str__(self):
        levels = []
        if self.winter:
            levels.append(f"зима: {self.winter}")
        if self.summer:
            levels.append(f"лето: {self.summer}")
        if self.autumn:
            levels.append(f"осень: {self.autumn}")
        if self.spring:
            levels.append(f"весна: {self.spring}")
        return ", ".join(levels) if levels else "Не указано"


class Pass(models.Model):
    """Модель горного перевала"""
    
    # Статусы модерации
    STATUS_CHOICES = [
        ('new', 'Новая запись'),
        ('pending', 'Взято в работу модератором'),
        ('accepted', 'Модерация прошла успешно'),
        ('rejected', 'Модерация не прошла'),
    ]

    beauty_title = models.CharField(
        max_length=255, 
        verbose_name='Красивое название',
        blank=True
    )
    title = models.CharField(max_length=255, verbose_name='Название')
    other_titles = models.CharField(
        max_length=255, 
        verbose_name='Альтернативные названия',
        blank=True
    )
    connect = models.TextField(
        verbose_name='Что соединяет',
        blank=True
    )
    add_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время добавления'
    )
    
    # Связи с другими моделями
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    coords = models.OneToOneField(
        Coords,
        on_delete=models.CASCADE,
        verbose_name='Координаты'
    )
    level = models.OneToOneField(
        Level,
        on_delete=models.CASCADE,
        verbose_name='Уровень сложности'
    )
    
    # Статус модерации (обязательное поле по ТЗ)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус модерации'
    )

    class Meta:
        db_table = 'pereval_added'
        verbose_name = 'Перевал'
        verbose_name_plural = 'Перевалы'
        ordering = ['-add_time']

    def __str__(self):
        return f"{self.beauty_title} {self.title}"


class Image(models.Model):
    """Модель изображения перевала"""
    title = models.CharField(max_length=255, verbose_name='Название')
    data = models.ImageField(
        upload_to='passes/',
        verbose_name='Изображение'
    )
    pass_instance = models.ForeignKey(
        Pass,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Перевал'
    )

    class Meta:
        db_table = 'pereval_images'
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'

    def __str__(self):
        return f"{self.title} для {self.pass_instance}"
