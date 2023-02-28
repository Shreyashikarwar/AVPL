from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.db.models.fields import DateTimeField
from vendor_app.models import *
from main_app.models import *
class UserData(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='usr')
	first_name = models.CharField(max_length=50, null=True, blank=True)
	last_name = models.CharField(max_length=50, null=True, blank=True)
	phone = models.CharField(max_length=10, null=True, blank=True)
	address = models.CharField(max_length=100, null=True, blank=True)
	zipcode = models.CharField(max_length=20, null=True, blank=True)
	latitude = models.FloatField(null=True, blank=True)
	longitude = models.FloatField(null=True, blank=True)
	gender = models.CharField(max_length=20, null=True, blank=True)
	question = models.CharField(max_length=200, null=True, blank=True)
	answer = models.CharField(max_length=200, null=True, blank=True)
	
	#Personal User PV
	pv = models.FloatField(default=0.0)
	
	status = models.BooleanField(default=False)
	subscribed = models.BooleanField(default=False)
	class Meta:
		db_table="UserData"
	def __str__(self):
		if self.first_name != None and self.last_name != None:
			return str(self.first_name+' '+self.last_name)
		else:
			return 'This is a Admin or Vendor User Type'

class PVTransactions(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pv')
	transaction_date = models.DateTimeField()
	previous_pv = models.FloatField(default=0.0)
	pv = models.FloatField()
	total_pv = models.FloatField()
	plan = models.CharField(max_length=100, default='Binary')
	class Meta:
		db_table="PVTransactions"
	def __str__(self):
		return 'Transaction ID '+str(self.id)

#PV Under User
class UserPV(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userpv')
	right_pv = models.FloatField(default=0.0)
	left_pv = models.FloatField(default=0.0)
	level_pv = models.FloatField(default=0.0)
	class Meta:
		db_table="UserPV"
	def __str__(self):
		return str(self.user) +' Right PV '+str(self.right_pv)+' Left PV '+str(self.left_pv)

class PaymentInfo(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payinfo')
	account_no = models.CharField(max_length=50)
	bank_name = models.CharField(max_length=50)
	ifsc = models.CharField(max_length=50)
	pan = models.FileField(upload_to='user_pancard_image')
	aadhar = models.FileField(upload_to='user_pancard_image')
	class Meta:
		db_table="PaymentInfo"
	def __str__(self):
		return 'Payment Info of '+str(self.user)

class UserWithdrawRequest(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdraw_request')
	request_date = models.DateTimeField()
	amount = models.FloatField()
	tds = models.FloatField(default=0.0)
	status = models.PositiveIntegerField(default=0)
	class Meta:
		db_table="UserWithdrawRequest"
	def __str__(self):
		return 'Withdraw Request of '+str(self.user)

class Cart(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
	subtotal = models.FloatField(default=0)
	delivery_charges = models.FloatField(default=0)
	tax = models.FloatField(default=0)
	total = models.FloatField(default=0)
	self_pickup = models.BooleanField(default=False)
	class Meta:
		db_table="Cart"
	def __int__(self):
		return self.id

class CartItems(models.Model):
	cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product')
	quantity = models.PositiveIntegerField()
	per_item_cost = models.FloatField()
	total_cost = models.FloatField()
	class Meta:
		db_table="CartItems"
	def __str__(self):
		return self.product.name+' in Cart'

class CartItemVariant(models.Model):
	cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
	cartitem = models.ForeignKey(CartItems, on_delete=models.CASCADE)
	product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
	class Meta:
		db_table="CartItemVariant"
	def __str__(self):
		return 'Cart Item '+self.cartitem.product.name+' Variant '+self.product_variant.variant.name+' '+self.product_variant.variant_value.value


class Wishlist(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
	subtotal = models.FloatField(default=0)
	delivery_charges = models.FloatField(default=0)
	tax = models.FloatField(default=0)
	total = models.FloatField(default=0)
	self_pickup = models.BooleanField(default=False)
	class Meta:
		db_table="Wishlist"
	def __int__(self):
		return self.id

class WishlistItems(models.Model):
	wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlistproduct')
	quantity = models.PositiveIntegerField()
	per_item_cost = models.FloatField()
	total_cost = models.FloatField()
	class Meta:
		db_table="WishlistItems"
	def __str__(self):
		return self.product.name+' in Wishlist'

class WishlistItemVariant(models.Model):
	wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE)
	wishlistitem = models.ForeignKey(WishlistItems, on_delete=models.CASCADE)
	product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
	class Meta:
		db_table="WishlistItemVariant"
	def __str__(self):
		return 'Wishlist Item '+self.wishlistitem.product.name+' Variant '+self.product_variant.variant.name+' '+self.product_variant.variant_value.value


class Address(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='address')
	latitude = models.FloatField()
	longitude = models.FloatField()
	name = models.CharField(max_length=100)
	home_no = models.CharField(max_length=100)
	landmark = models.CharField(max_length=100)
	city = models.CharField(max_length=100)
	pincode = models.CharField(max_length=100)
	state = models.CharField(max_length=100)
	address_type = models.CharField(max_length=30,default='Home', choices=(('Home', 'Home'), ('Work', 'Work'),('Other','Other')))
	contact = models.CharField(max_length=15)
	default = models.BooleanField(default=True)
	class Meta:
		db_table="Address"
	def __str__(self):
		return self.name+' Address'

#showing User Vendor Relation
class UserVendorRelation(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	vendor = models.OneToOneField(Vendor,on_delete=models.CASCADE,primary_key=True,)
	class Meta:
		db_table="UserVendorRelation"
	def __str__(self):
		return self.vendor.first_name+' is related '+self.user.usr.first_name

class Membership(models.Model):
	user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True, related_name="member")
	subscribed_on = DateTimeField(auto_now=True)
	class Meta:
		db_table="Membership"
	def __str__(self):
		return self.user.usr.first_name
#bellow fn holds subscription payment details
class Memberip_Receipt(models.Model):
	receipt_date = models.DateTimeField(auto_now=True)
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	razorpay_order_id = models.CharField(max_length=100)
	payment_id = models.CharField(max_length=200, null=True, blank=True)
	amount = models.FloatField()
	status = models.BooleanField(default=False)
	class Meta:
			db_table ="Memberip_Receipt"
	def __str__(self):
			return "Receipt ID "+str(self.id)

# to calculate year
class UserSubscription(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscribed_usr')
	subscrbe_on = models.DateTimeField(auto_now=True)
	months = models.PositiveIntegerField(default=1)
	class Meta:
		db_table= "UserSubscription"
	def __str__(self):
		return str(self.user)

class Billing_Request(models.Model):
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	store = models.ForeignKey(Store, on_delete=models.CASCADE)
	amount = models.FloatField(default=0.0)
	plan = models.CharField(max_length=100, default="Level")
	status = models.BooleanField(default=False)
	class Meta:
		db_table= "Billing_Request"
	def __str__(self):
		return str(self.user)