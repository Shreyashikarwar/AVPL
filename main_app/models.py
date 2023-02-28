from django.db import models
from django.contrib.auth.models import User, AbstractUser
from user_app.models import *
from vendor_app.models import *
from ckeditor.fields import RichTextField

class Levels(models.Model):
	level = models.CharField(max_length=50, primary_key=True)
	class Meta:
		db_table="Levels"
	def __str__(self):
		return self.level

class Role(models.Model):
	user = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name='role')
	level = models.ForeignKey(to=Levels, on_delete=models.CASCADE)
	class Meta:
		db_table="Role"
	def __str__(self):
		return str(self.user)+' Role'


################# MLM Models ##############################################

############## Below model denotes the users under admin ##################
class MLMAdmin(models.Model):
	child = models.ForeignKey(User,on_delete=models.CASCADE, related_name='child')
	class Meta:
		db_table="MLMAdmin"
	def __str__(self):
		return str(self.child)

################## User MLM Model #########################################
class MLM(models.Model):
	parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='parent')
	node = models.ForeignKey(User, on_delete=models.CASCADE, related_name='node')
	left = models.ForeignKey(User, on_delete=models.CASCADE, related_name='left', null=True, blank=True)
	right = models.ForeignKey(User, on_delete=models.CASCADE, related_name='right', null=True, blank=True)
	class Meta:
		db_table="MLM"
	def __str__(self):
		return self.node.username

class RazorpayOrder(models.Model):
	cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	address = models.ForeignKey(Address,on_delete=models.CASCADE)
	razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
	class Meta:
		db_table="RazorpayOrder"
	def __str__(self):
		return 'Razorpay Order ID '+str(self.razorpay_order_id)

class RazorpayTransaction(models.Model):
	payment_id = models.CharField(max_length=100)
	order_id = models.CharField(max_length=100)
	signature = models.CharField(max_length=300)
	class Meta:
		db_table="RazorpayTransaction"
	def __str__(self):
		return 'Razorpay '+str(self.payment_id)

class Orders(models.Model):
	order_date = models.DateTimeField()
	user = models.ForeignKey(User,on_delete=models.CASCADE, null=True)
	razorpaytransaction = models.ForeignKey(RazorpayTransaction,on_delete=models.CASCADE, null=True, blank=True)
	address = models.ForeignKey(Address,on_delete=models.CASCADE)
	delivery_charges = models.FloatField(default=0.0)
	subtotal = models.FloatField()
	tax = models.FloatField()
	total = models.FloatField()
	point_value = models.FloatField(default=0.0)
	self_pickup = models.BooleanField(default=False)
	paid = models.BooleanField(default=False)

	class Meta:
		db_table="Orders"
	def __str__(self):
		return 'Order ID  '+str(self.id) +  '  ' +str(self.user.id)

class OrderItems(models.Model):
	store = models.ForeignKey(Store,on_delete=models.CASCADE)
	order = models.ForeignKey(Orders,on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orderproduct')
	quantity = models.PositiveIntegerField()
	per_item_cost = models.FloatField()
	subtotal = models.FloatField()
	tax = models.FloatField()
	total = models.FloatField()
	delivery_status = models.CharField(max_length=50, default='Order Placed')
	delivered_on = models.DateTimeField(null=True, blank=True)
	cancellation_reason = models.CharField(max_length=500, null=True)
	cancelled_on = models.DateTimeField(null=True, blank=True)
	class Meta:
		db_table="OrderItems"
	def __str__(self):
		return self.product.name + 'order' + str(self.order.id) + 'orderitem' + str(self.id)

class OrderItemVariant(models.Model):
	order = models.ForeignKey(Orders, on_delete=models.CASCADE)
	orderitem = models.ForeignKey(OrderItems, on_delete=models.CASCADE)
	product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
	class Meta:
		db_table="OrderItemVariant"
	def __str__(self):
		return 'Order Item '+self.orderitem.product.name+' Variant '+self.product_variant.variant.name+' '+self.product_variant.variant_value.value

class Wallet(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	current_balance = models.FloatField(default=0.0)
	class Meta:
		db_table="Wallet"
	def __str__(self):
		return 'Wallet of '+self.user.email

class WalletTransaction(models.Model):
	wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
	transaction_date = models.DateTimeField()
	transaction_type = models.CharField(max_length=20)
	transaction_amount = models.FloatField()
	previous_amount = models.FloatField()
	remaining_amount = models.FloatField()
	class Meta:
		db_table="WalletTransaction"
	def __str__(self):
		return 'Wallet Transaction ID '+str(self.id)

class Notification(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	notification_date = models.DateTimeField(auto_now=True)
	text = models.CharField(max_length=200)
	read = models.BooleanField(default=False)
	class Meta:
		db_table="Notification"
	def __str__(self):
		return 'Notification '+self.text

class Min_Amount_For_Free_Delivery(models.Model):
	amount = models.FloatField()
	class Meta:
		db_table="Min_Amount_For_Free_Delivery"
	def __str__(self):
		return 'Minimum Amount for Free Delivery is Rs '+str(self.amount)+' (Click Here to Change)'

class GST_Log(models.Model):
	transaction_date = models.DateTimeField(auto_now_add=True)
	orders = models.ForeignKey(OrderItems, on_delete=models.CASCADE, null=True, blank=True)
	gst_amt = models.FloatField(default=0.0)
	class Meta:
		db_table="GST_Log"
	def __str__(self):
		return str(self.transaction_date)

class TDS_Log(models.Model):
	transaction_date = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	amount = models.FloatField(default=0.0)
	tds_amt = models.FloatField(default=0.0)
	class Meta:
		db_table="TDS_Log"
	def __str__(self):
		return str(self.transaction_date)

class contact_us(models.Model):
	address = models.CharField(max_length=200)
	contact_no = models.PositiveIntegerField()
	gmail_id = models.CharField(max_length=200)
	facbook_id = models.CharField(max_length=200)
	instagram_id = models.CharField(max_length=200)
	twitter_id = models.CharField(max_length=200)
	class Meta:
		db_table='Company_Details'
	def __str__(self):
		return 'Onlinedukan details'


class termsandcondition(models.Model):
	title = models.CharField(max_length=200)
	content = RichTextField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now=True)
	class Meta:
		db_table="Terms and Condition"
	def __str__(self):
		return str(self.title)


class privacypolicy(models.Model):
	title = models.CharField(max_length=200)
	content = RichTextField(null=True,blank=True)
	created_at = models.DateTimeField(auto_now=True)
	class Meta:
		db_table="Privacy and Policy"
	def __str__(self):
		return str(self.title)

class PV_data(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	match_pv = models.CharField(max_length=15, null=True, blank=True)
	created_at = models.DateTimeField(auto_now=True)
	class Meta:
		db_table="PV data"
	def __str__(self):
		return str(self.user)


	# 	def get_my_orders(user, store=None):
	# items = []
	# for order in Orders.objects.filter(user=user).order_by('-order_date'):
	# 	if store:
	# 		for item in OrderItems.objects.values().filter(order=order, store=store):
	# 			dic = {'item':item, 'rating_flag':False}
	# 			variants = []
	# 			for x in OrderItemVariant.objects.values().filter(orderitem=item):
	# 				variants.append(x)
	# 			dic.update({'variants':variants})
	# 			for x in ProductImages.objects.filter(product=item.product):
	# 				dic.update({'image':x.image.url})
	# 				break
	# 			if ProductRating.objects.filter(product=item.product, user=user).exists():
	# 				dic.update({'rating_flag':True, 'rating':ProductRating.objects.get(product=item.product, user=user).rating})
	# 			else:
	# 				dic.update({'rating_flag':False})
	# 			dic.update({'date':order.order_date})
	# 			items.append(dic)
	# 	else:
	# 		for item in OrderItems.objects.values().filter(order=order):
	# 			dic = {'item':item, 'rating_flag':False}
	# 			variants = []
	# 			for x in OrderItemVariant.objects.values().filter(orderitem__id=item['id']):
	# 				variants.append(x)
	# 			dic.update({'variants':variants})
	# 			for x in ProductImages.objects.filter(product__id=item['id']):
	# 				dic.update({'image':x.image.url})
	# 				break
	# 			# if ProductRating.objects.filter(product=item.product, user=user).exists():
	# 			# 	dic.update({'rating_flag':True, 'rating':ProductRating.objects.get(product=item.product, user=user).rating})
	# 			# else:
	# 			# 	dic.update({'rating_flag':False})
	# 			dic.update({'date':order.order_date})
	# 			items.append(dic)
	# return items


from django.utils.timezone import now


class WalletTransfer(models.Model):
	user = models.ForeignKey(to=User,on_delete=models.CASCADE,default='')
	senderusername = models.CharField(max_length=256)
	reciverusername = models.CharField(max_length=256)
	transection_id = models.CharField(max_length=256,unique=True)
	amount = models.IntegerField(default=0)
	transection_time = models.DateTimeField(auto_now=False,auto_now_add=False,default=now)

	def __str__(self):
		return str(self.senderusername) + ' | ' + str(self.transection_time)


class WalletTransferApproval(models.Model):
	customer = models.BooleanField(default = True)
	vendor = models.BooleanField(default = True)
	lastupdate_time = models.DateTimeField(auto_now=False,auto_now_add=False,default=now)

	def __str__(self) -> str:
		return str(self.customer) + ' | ' + str(self.vendor)  + " | " + str(self.lastupdate_time)



















