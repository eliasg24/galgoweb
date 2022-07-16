from django.contrib import admin

from calendario.models import Calendario

# Register your models here.

@admin.register(Calendario)
class CalendarioAdmin(admin.ModelAdmin):
    # Admin de los Talleres
    list_display = ('start', 'end', 'title_current')
    search_fields= ('start', 'end', 'title_current')
    list_filter = ('start', 'end', 'title_current')
    verbose_name_plural = "Calendario"
    