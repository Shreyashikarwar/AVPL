from django.contrib import admin
from .models import *
from django.utils.html import format_html
	
class LevelsAdmin(admin.ModelAdmin):
	list_display = ['level']

class RoleAdmin(admin.ModelAdmin):
	list_display = ['user', 'level']

class AdminMLM(admin.ModelAdmin):
	list_display = ['child']

class MLM_Admin(admin.ModelAdmin):
	list_display = ['parent', 'node', 'left', 'right']

class RazorpayAdmin(admin.ModelAdmin):
	list_display = ['payment_id', 'order_id', 'signature']

admin.site.register(Levels,LevelsAdmin)
admin.site.register(Role,RoleAdmin)
admin.site.register(MLMAdmin,AdminMLM)
admin.site.register(MLM,MLM_Admin)
admin.site.register(RazorpayTransaction,RazorpayAdmin)

admin.site.register(RazorpayOrder)
admin.site.register(Wallet)
admin.site.register(WalletTransaction)
admin.site.register(Min_Amount_For_Free_Delivery)
admin.site.register(contact_us)

admin.site.register(GST_Log)
admin.site.register(OrderItems)
admin.site.register(Orders)
admin.site.register(TDS_Log)
admin.site.register(termsandcondition)
admin.site.register(privacypolicy)
admin.site.register(PV_data)
admin.site.register(WalletTransfer)
admin.site.register(WalletTransferApproval)








