from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.db.models.base import Model
from django.db.models.fields.related import ForeignKey
from admin_app.models import *
from main_app.models import *
from .models import *
from main_app.models import *
import datetime
from ckeditor.fields import RichTextField

class Vendor(models.Model):
	user = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name='vendor')
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	phone = models.CharField(max_length=10)
	address = models.CharField(max_length=100)
	zipcode = models.CharField(max_length=20)
	latitude = models.FloatField()
	longitude = models.FloatField()
	gender = models.CharField(max_length=20)
	store_created = models.BooleanField(default=False)
	verified = models.BooleanField(default=False)
	doc_submitted = models.BooleanField(default=False)
	status = models.BooleanField(default=False)
	class Meta:
		db_table="Vendor"
	def __str__(self):
		return self.first_name+' '+self.last_name

class Store(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	vendor = models.OneToOneField(to=Vendor, on_delete=models.CASCADE)
	name = models.CharField(max_length=100)
	description = models.CharField(max_length=300)
	registration_number = models.CharField(max_length=50)
	closing_day = models.CharField(max_length=50)
	opening_time = models.CharField(max_length=50)
	closing_time = models.CharField(max_length=50)
	best_seller = models.BooleanField(default=False)
	class Meta:
		db_table="Store"
	def __str__(self):
		return self.name

class StoreImages(models.Model):
	store = models.OneToOneField(to=Store, on_delete=models.CASCADE)
	logo = models.ImageField(upload_to='store_logo')
	banner = models.ImageField(upload_to='store_banner')
	image = models.ImageField(upload_to='store_image')
	class Meta:
		db_table="StoreImages"
	def __str__(self):
		return self.store.name+' Images'

class VendorDocs(models.Model):
	vendor = models.OneToOneField(to=Vendor, on_delete=models.CASCADE)
	vendor_idproof = models.CharField(max_length=20,null=True, blank=True)
	front_idproof = models.FileField(upload_to='store_seller_aadhar_image',null=True, blank=True)
	back_idproof = models.FileField(upload_to='store_seller_aadhar_image',null=True, blank=True)
	store_gst = models.CharField(max_length=50,null=True, blank=True)
	store_msme = models.CharField(max_length=50,null=True, blank=True)
	pancard = models.CharField(max_length=50)
	pancard_image = models.FileField(upload_to='store_seller_pancard_image')
	shiping_policy = models.FileField(upload_to='shiping_policy',null=True)
	return_policy = models.FileField(upload_to='return_policy',null=True)
	bank_account_number = models.CharField(max_length=50)
	bank_name = models.CharField(max_length=100)
	bank_ifsc = models.CharField(max_length=100)
	bank_passbook = models.FileField(upload_to='store_bank_passbook')
	razorpay_id = models.CharField(max_length=200,null=True)
	class Meta:
		db_table="VendorDocs"
	def __str__(self):
		return self.vendor.first_name+' '+self.vendor.last_name

class Product(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	store = models.ForeignKey(Store,on_delete=models.CASCADE)
	category = models.ForeignKey(ProductCategory,on_delete=models.CASCADE)
	subcategory = models.ForeignKey(ProductSubCategory,on_delete=models.CASCADE)
	subsubcategory = models.ForeignKey(ProductSubSubCategory,on_delete=models.CASCADE)
	brand = models.ForeignKey(Brand,on_delete=models.CASCADE, null=True, blank=True)
	name = models.CharField(max_length=200)
	description =RichTextField(null=True, blank=True)
	mrp = models.FloatField(default=0.0)
	price = models.FloatField()
	stock = models.PositiveIntegerField(null=True, default=0)#Total Stock Including all variants
	weight = models.FloatField()
	product_reject_reason = models.TextField(null=True,blank=True)
	product_rejection = models.BooleanField(default=False)
	status = models.BooleanField(default=False)
	offer = models.BooleanField(default=False)
	discount = models.PositiveIntegerField(null=True, default=0)
	featured = models.BooleanField(default=False)
	special_offer = models.BooleanField(default=False)
	
	class Meta:
		db_table="Product"
	def __str__(self):
		return self.name

class ProductImages(models.Model):
	product = models.ForeignKey(Product,on_delete=models.CASCADE)
	image = models.FileField(upload_to='products_images')
	class Meta:
		db_table="ProductImages"
	def __str__(self):
		return self.product.name+ 'Images' + str(self.product.id)

class ProductVariant(models.Model):
	product = models.ForeignKey(Product,on_delete=models.CASCADE)
	variant = models.ForeignKey(Variant,on_delete=models.CASCADE, null=True, blank=True)
	variant_value = models.ForeignKey(VariantValue,on_delete=models.CASCADE, null=True, blank=True)
	variant_stock = models.PositiveIntegerField(default=0)
	class Meta:
		db_table="ProductVariant"
	def __str__(self):
		return self.product.name+' '+self.variant.name+'-'+str(self.variant_value.value)

class ProductRating(models.Model):
	product = models.ForeignKey(Product,on_delete=models.CASCADE)
	# order = models.ForeignKey(OrderItems, null=True, blank= True, on_delete=models.CASCADE)
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	review = models.TextField()
	rating = models.FloatField()
	created_at = models.DateField(auto_now_add=True, null=True)
	class Meta:
		db_table="ProductRating"
	def __str__(self):
		return self.product.name+' Rating '+str(self.rating)

class VendorWithdrawRequest(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_withdraw_request')
	request_date = models.DateTimeField()
	amount = models.FloatField()
	status = models.PositiveIntegerField(default=0)
	class Meta:
		db_table="VendorWithdrawRequest"
	def __str__(self):
		return 'Withdraw Request of '+str(self.user)


#Model For Business Limit Model
class BusinessLimit(models.Model):
	vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE, related_name='business_limit')
	current_balance = models.FloatField(default=0.0)
	class Meta:
		db_table="BusinessLimit"
	def __str__(self):
		return 'BusinessLimit '+str(self.vendor)

class Recharge_Receipt(models.Model):
	receipt_date = models.DateTimeField(auto_now=True)
	vendor = models.ForeignKey(Vendor,on_delete=models.CASCADE)
	razorpay_order_id = models.CharField(max_length=100)
	payment_id = models.CharField(max_length=200, null=True, blank=True)
	amount = models.FloatField()
	status = models.BooleanField(default=False)
	class Meta:
			db_table ="Recharge_Receipt"
	def __str__(self):
			return "Receipt ID "+str(self.id)

#Model for Admin commision amount from Business limit(like wallet) to Admin wallet in case COD 
class BusinessLimitTransaction(models.Model):
	business_limit=models.ForeignKey(BusinessLimit,on_delete=models.CASCADE)
	receipt=models.ForeignKey(Recharge_Receipt,on_delete=models.CASCADE, null=True, blank=True)
	transaction_date = models.DateTimeField()
	transaction_name = models.CharField(max_length=100)
	transaction_type = models.CharField(max_length=20, choices=(('CREDIT', 'CREDIT'), ('DEBIT', 'DEBIT')))
	transaction_amount = models.FloatField()
	previous_amount = models.FloatField()
	remaining_amount = models.FloatField()
	class Meta:
			db_table ="BusinessLimitTransaction"
	def __str__(self):
			return "BusinessLimitTransaction "+str(self.business_limit)

#model for user subscription request
class UserSubscriptionRequest(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
	month = models.PositiveIntegerField(default=1)
	amount = models.FloatField(default=0.0)
	status = models.BooleanField(default=False)
	class Meta:
		db_table = "UserSubscriptionRequest"
	def __str__(self):
		return str(self.user.usr.first_name)+str(self.vendor.first_name)

