from django.contrib import admin
from .models import User, Coords, Level, Pass, Image


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'fam', 'name', 'phone']
    list_filter = ['fam']
    search_fields = ['email', 'fam', 'name']


@admin.register(Coords)
class CoordsAdmin(admin.ModelAdmin):
    list_display = ['latitude', 'longitude', 'height']


@admin.register(Level)  
class LevelAdmin(admin.ModelAdmin):
    list_display = ['winter', 'summer', 'autumn', 'spring']


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1


@admin.register(Pass)
class PassAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'status', 'add_time']
    list_filter = ['status', 'add_time']
    search_fields = ['title', 'beauty_title', 'user__email']
    readonly_fields = ['add_time']
    inlines = [ImageInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('beauty_title', 'title', 'other_titles', 'connect')
        }),
        ('Связанные данные', {
            'fields': ('user', 'coords', 'level')
        }),
        ('Модерация', {
            'fields': ('status', 'add_time')
        }),
    )


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'pass_instance']
    list_filter = ['pass_instance']
