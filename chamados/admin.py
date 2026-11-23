from django.contrib import admin

from .models import Anexo, Categoria, Chamado, Comentario, HistoricoStatus


class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 0


@admin.register(Chamado)
class ChamadoAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo", "status", "prioridade", "solicitante", "tecnico", "aberto_em")
    list_filter = ("status", "prioridade", "categoria")
    search_fields = ("titulo", "descricao")
    inlines = [ComentarioInline]


admin.site.register(Categoria)
admin.site.register(Anexo)
admin.site.register(HistoricoStatus)
