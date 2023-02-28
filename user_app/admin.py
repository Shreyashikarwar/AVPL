from django.contrib import admin
from user_app.models import *

class UserDataAdmin(admin.ModelAdmin):
	list_display = ['user', 'first_name', 'last_name', 'phone', 'address', 'zipcode', 'gender', 'pv', 'status','subscribed']

class PVTransAdmin(admin.ModelAdmin):
	list_display = ['user', 'transaction_date', 'previous_pv', 'pv', 'total_pv']

admin.site.register(UserData, UserDataAdmin)
admin.site.register(PVTransactions, PVTransAdmin)
#model for user vendor relation
admin.site.register(UserVendorRelation)
admin.site.register(Membership)
admin.site.register(Memberip_Receipt)
admin.site.register(UserSubscription)
admin.site.register(CartItemVariant)
admin.site.register(Address)
admin.site.register(UserPV)
admin.site.register(Cart)
admin.site.register(CartItems)
admin.site.register(Wishlist)
admin.site.register(WishlistItems)
admin.site.register(WishlistItemVariant)
admin.site.register(UserWithdrawRequest)