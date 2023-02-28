from django.contrib import admin
from .models import *
from django.utils.html import format_html

class BannerAdmin(admin.ModelAdmin):
	list_display = ['title', 'sub_title', 'description', 'link', 'image']

class VariantAdmin(admin.ModelAdmin):
	list_display = ['name']

class VariantValueAdmin(admin.ModelAdmin):
	list_display = ['variant', 'value']

class CategoryAdmin(admin.ModelAdmin):
	list_display = ['name', 'tax', 'image']
	def image_tag(self,obj):
		image_str = '<img src="{0}" style="width: 45px; height:45px;" />'.format(obj.image.url)

class SubCategoryAdmin(admin.ModelAdmin):
	list_display = ['category', 'name', 'image']
	def image_tag(self,obj):
		image_str = '<img src="{0}" style="width: 45px; height:45px;" />'.format(obj.image.url)

class SubSubCategoryAdmin(admin.ModelAdmin):
	list_display = ['subcategory', 'name', 'image']
	def image_tag(self,obj):
		image_str = '<img src="{0}" style="width: 45px; height:45px;" />'.format(obj.image.url)

class PointValueAdmin(admin.ModelAdmin):
	list_display = ['category', 'percentage']

class BrandAdmin(admin.ModelAdmin):
	list_display = ['category', 'name']

admin.site.register(Variant,VariantAdmin)
admin.site.register(VariantValue,VariantValueAdmin)
admin.site.register(Query)
admin.site.register(ProductCategory,CategoryAdmin)
admin.site.register(ProductSubCategory,SubCategoryAdmin)
admin.site.register(ProductSubSubCategory,SubSubCategoryAdmin)
admin.site.register(PointValue, PointValueAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(HomeBanner, BannerAdmin)
admin.site.register(UserVendorCommission)
admin.site.register(UserLeadershipBonusCommission)
admin.site.register(CarFund)
admin.site.register(TravelFund)
admin.site.register(HouseFund)
admin.site.register(DirectorshipFund)
admin.site.register(SubscriptionCharge)
admin.site.register(Commission)
admin.site.register(Savings)
admin.site.register(PVConversionValue)
admin.site.register(CommissionTransaction)
admin.site.register(AboutUs)
admin.site.register(Blog)
admin.site.register(Gallery)
admin.site.register(Billing_Config)
admin.site.register(HomeFooterBanner)
admin.site.register(Yearly_PV)
admin.site.register(Monthly_PV)


