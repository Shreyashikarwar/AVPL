from django.db import models
from django.contrib.auth.models import User, AbstractUser
from vendor_app.models import *
from main_app.models import *
from admin_app.models import *
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor.fields import RichTextField
from  user_app.models import *
class HomeBanner(models.Model):
	title = models.CharField(max_length=50)
	sub_title = models.CharField(max_length=50)
	description = models.CharField(max_length=150)
	link = models.CharField(max_length=500, default='NONE')
	image = models.FileField(upload_to='banners')
	class Meta:
		db_table="HomeBanner"
	def __str__(self):
		return self.title

class HomeFooterBanner(models.Model):
	title = models.CharField(max_length=50)
	image = models.FileField(upload_to='banners')
	class Meta:
		db_table="HomeFooterBanner"
	def __str__(self):
		return self.title

class ProductCategory(models.Model):
	name = models.CharField(max_length=50)
	tax = models.FloatField(default=5.0)
	commission = models.FloatField(default=10.0) #admin charge
	image = models.FileField(upload_to='categories', default="products_images/banner_2_product.png")
	class Meta:
		db_table="ProductCategory"
	def __str__(self):
		return self.name

class ProductSubCategory(models.Model):
	category = models.ForeignKey(to=ProductCategory, on_delete=models.CASCADE)
	name = models.CharField(max_length=50)
	image = models.FileField(upload_to='categories', default="products_images/banner_2_product.png")
	class Meta:
		db_table="ProductSubCategory"
	def __str__(self):
		return self.name

class ProductSubSubCategory(models.Model):
	subcategory = models.ForeignKey(to=ProductSubCategory, on_delete=models.CASCADE)
	name = models.CharField(max_length=50)
	image = models.FileField(upload_to='categories', default="products_images/banner_2_product.png")
	class Meta:
		db_table="ProductSubSubCategory"
	def __str__(self):
		return self.name

class PointValue(models.Model):
	category = models.ForeignKey(to=ProductCategory, on_delete=models.CASCADE)
	percentage = models.FloatField(default=10.0)
	class Meta:
		db_table="PointValue"
	def __str__(self):
		return str(self.percentage)

class Brand(models.Model):
	category = models.ForeignKey(to=ProductCategory, on_delete=models.CASCADE)
	name = models.CharField(max_length=50)
	class Meta:
		db_table="Brand"
	def __str__(self):
		return str(self.name)

class DeliveryCharge(models.Model):
	amount = models.FloatField()
	class Meta:
		db_table="DeliveryCharge"
	def __str__(self):
		return str(self.amount)

class Variant(models.Model):
	name = models.CharField(max_length=50)
	class Meta:
		db_table="Variant"
	def __str__(self):
		return self.name

class VariantValue(models.Model):
	variant = models.ForeignKey(to=Variant, on_delete=models.CASCADE, related_name='value')
	value = models.CharField(max_length=50)
	class Meta:
		db_table="VariantValue"
	def __str__(self):
		return self.variant.name+' - '+self.value


#Admin Wallet Transactions
class CommissionTransaction(models.Model):
	transaction_date = models.DateTimeField()
	transaction_type = models.CharField(max_length=20)
	transaction_amount = models.FloatField()
	previous_amount = models.FloatField()
	remaining_amount = models.FloatField()
	class Meta:
		db_table="CommissionTransaction"
	def __str__(self):
		return str(self.transaction_date)+' Commission Transaction'

#Admin Wallet
class Commission(models.Model):
	current_balance = models.FloatField(default=0.0)
	class Meta:
		db_table="Commission"
	def __str__(self):
		return 'Rs '+str(self.current_balance)+'/- Admin Commission'

class Savings(models.Model):
	savings = models.FloatField(default=0.0)
	class Meta:
		db_table="savings"
	def __str__(self):
		return 'Rs '+str(self.savings)+'/- Admin Savings'

class PVPairValue(models.Model):
	pair_value = models.FloatField(default=0.0)
	class Meta:
		db_table="PVPairValue"
	def __str__(self):
		return 'PV Pair Value -> '+str(self.pair_value)

class PVConversionValue(models.Model):
	conversion_value = models.FloatField(default=0.0)
	class Meta:
		db_table="PVConversionValue"
	def __str__(self):
		return 'PV Conversion Value -> '+str(self.conversion_value)

class Query(models.Model):
	user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, blank=True)
	query_date = models.DateTimeField(auto_now=True, null=True, blank=True)
	anonymous = models.BooleanField(default=False)
	name = models.CharField(max_length=100, null=True, blank=True)
	email = models.CharField(max_length=100, null=True, blank=True)
	mobile = models.CharField(max_length=15, null=True, blank=True)
	subject = models.CharField(max_length=200)
	message = models.TextField()
	reply = models.TextField(default="No-Reply")
	status = models.IntegerField(default=0)
	class Meta:
		db_table="Query"
	def __str__(self):
		return  self.name

class Tax(models.Model):
	current_tax = models.FloatField(default=0.0)
	class Meta:
		db_table="Tax"
	def __str__(self):
		return 'Current Tax '+str(self.current_tax)

class TaxPay(models.Model):
	transaction_date = models.DateTimeField()
	tax_current = models.FloatField(default=0.0)
	tax_paid = models.FloatField(default=0.0)
	tax_remaining = models.FloatField(default=0.0)
	class Meta:
		db_table="TaxPay"
	def __str__(self):
		return +str(self.transaction_date)
#Below for user commission for refered Vendor
class UserVendorCommission(models.Model):
	percentage = models.FloatField(default=10.0)
	class Meta:
		db_table="UserVendorCommission"
	def __str__(self):
		return str(self.percentage)

class DirectReferalCommission(models.Model):
	percentage = models.FloatField(default=10.0)
	class Meta:
		db_table="DirectReferalCommission"
	def __str__(self):
		return str(self.percentage)

class SubscriptionCharge(models.Model):
	one_month_subscription_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
	three_month_subscription_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
	six_month_subscription_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
	twelve_month_subscription_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
	pv_percentage = models.FloatField(default=10.0)
	vendor_percentage = models.FloatField(default=10.0)
	class Meta:
		db_table="SubscriptionCharge"
	def __str__(self):
		return 'Click here to change'

class Level_Settings(models.Model):
	configured_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)
	levels = models.PositiveIntegerField()
	groups = models.PositiveIntegerField()
	class Meta:
		db_table="Level_Settings"

class Level_Group(models.Model):
	configured_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)
	level = models.ForeignKey(Level_Settings, on_delete=models.CASCADE)
	percent_per_level = models.FloatField(default=1)
	no_of_levels = models.PositiveIntegerField(default=1)
	class Meta:
		db_table="Level_Group"

class Billing_Config(models.Model):
	configured_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)
	admin_commission = models.FloatField(default=1)
	pv_percent = models.FloatField(default=1)
	class Meta:
		db_table="Billing_Config"

class Yearly_PV(models.Model):
	pv = models.FloatField(default=0.0)
	updated_on = models.DateTimeField(auto_now=True)
	class Meta:
		db_table = "Yearly PV"

class Monthly_PV(models.Model):
	pv = models.FloatField(default=0.0)
	created_at = models.DateTimeField(auto_now_add= True)
	updated_on = models.DateTimeField(auto_now=True)
	class Meta:
		db_table = "Monthly PV"

class UserLeadershipBonusCommission(models.Model):
	percentage = models.FloatField(default=10.0)
	target = models.PositiveIntegerField(default=100000)
	class Meta:
		db_table="UserLeadershipBonusCommission"
	def __str__(self):
		return str(self.percentage)

class TravelFund(models.Model):
	target = models.PositiveIntegerField(default=100000)
	percentage = models.FloatField(default=10.0)
	class Meta:
		db_table="TravelFund"
	def __str__(self):
		return str(self.percentage)

class CarFund(models.Model):
	target = models.PositiveIntegerField(default=100000)
	percentage = models.FloatField(default=10.0)
	class Meta:
		db_table="CarFund"
	def __str__(self):
		return str(self.percentage)

class HouseFund(models.Model):
	target = models.PositiveIntegerField(default=100000)
	percentage = models.FloatField(default=10.0)
	class Meta:
		db_table="HouseFund"
	def __str__(self):
		return str(self.percentage)

class DirectorshipFund(models.Model):
	target = models.PositiveIntegerField(default=100000)
	percentage = models.FloatField(default=10.0)
	class Meta:
		db_table="DirectorshipFund"
	def __str__(self):
		return str(self.percentage)

class AboutUs(models.Model):
	title = models.CharField(max_length=200)
	content = RichTextUploadingField(null=True, blank=True)
	image = models.ImageField(upload_to='about_us', null=True)
	created_at = models.DateTimeField(auto_now=True)
	class Meta:
		db_table="About Us"
	def __str__(self):
		return str(self.title)

class Blog(models.Model):
	title = models.CharField(max_length=200)
	content = RichTextUploadingField(null=True, blank=True)
	image = models.ImageField(upload_to='blog', null=True)
	created_at = models.DateTimeField(auto_now=True)
	class Meta:
		db_table="Blog"
	def __str__(self):
		return str(self.title)

class Gallery(models.Model):
	title = models.CharField(max_length=200)
	content = models.TextField(null=True)
	image = models.ImageField(upload_to='gallery', null=True)
	created_at = models.DateTimeField(auto_now=True)
	class Meta:
		db_table="Gallery"
	def __str__(self):
		return str(self.title)

