import razorpay
from main_app.models import *
from vendor_app.models import *

# client = razorpay.Client(auth=("rzp_live_x7PnIDVsQs52F2", "suxN8QoVA16C6QeRV0hjexWU"))
# client = razorpay.Client(auth=("rzp_test_OcvfBakbfEdBxL", "tLlVOve6xEK1DwoqYgjVBI8i"))
client = razorpay.Client(auth=("rzp_test_hpJq2nYr2dg8WT", "hswI4ZKUKC3mIUN6gfmgvETq"))

def create_online_order(cart, address, user):
	RazorpayOrder.objects.all().delete()
	order_amount = int(cart.total)
	order_currency = 'INR'
	order_receipt = str(cart.id)
	print('jhgbjhgbjh', order_amount,order_currency, order_receipt)
	address_val = address.name+', '+address.home_no+', '+address.landmark+' '+address.city+' '+address.state 
	notes = {'Shipping address': address_val}   # OPTIONAL
	dic = {
	'amount' : order_amount,
	'currency' : order_currency,
	'receipt' : order_receipt,
	'notes' : notes,
	'payment_capture': 0
	}
	data = client.order.create(data=dic)
	order_id = data['id']
	print(order_id)
	RazorpayOrder.objects.create(cart=cart, user=user, address=address, razorpay_order_id=data['id'])
	return data

def create_razorpay_order(receipt_id, user, amount):
	order_amount = amount
	order_currency = 'INR'
	order_receipt = str(receipt_id)
	notes = {}   # OPTIONAL
	dic = {
	'amount' : order_amount,
	'currency' : order_currency,
	'receipt' : order_receipt,
	'notes' : notes,
	'payment_capture': 0
	}
	print('loading...')
	data = client.order.create(data=dic)
	Recharge_Receipt.objects.filter(id=receipt_id).update(razorpay_order_id=data['id'])
	return data


# def create_razorpay_order2(receipt_id, user, amount):
# 	order_amount = amount
# 	order_currency = 'INR'
# 	order_receipt = str(receipt_id)
# 	notes = {}   # OPTIONAL
# 	dic = {
# 	'amount' : order_amount,
# 	'currency' : order_currency,
# 	'receipt' : order_receipt,
# 	'notes' : notes,
# 	'payment_capture': 0
# 	}
# 	print('loading...')
# 	data = client.order.create(data=dic)
# 	Memberip_Receipt.objects.filter(id=receipt_id).update(razorpay_order_id=data['id'])
# 	return data
# def fetch_all_orders():
# 	print('hello')