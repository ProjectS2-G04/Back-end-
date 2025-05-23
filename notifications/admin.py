from django.contrib import admin
from .models import Notification


admin.site.register(Notification)
# class NotificationAdmin(admin.ModelAdmin):
#     list_display = (
#         "user",
#         "type",
#         "is_read",
#         "created_at",
#         "rendez_vous_link",
#     )
#     list_filter = ("type", "is_read", "created_at")
#     search_fields = ("user__username", "message", "type")
#     readonly_fields = ("created_at", "updated_at")

#     def rendez_vous_link(self, obj):
#         if obj.rendez_vous:
#             return f"Rdv #{obj.rendez_vous.id}"
#         return "-"

#     rendez_vous_link.short_description = "Rendez-vous"
