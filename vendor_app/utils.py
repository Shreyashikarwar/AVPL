from main_app.models import *

def get_order_details(order_id):
	order = OrderItems.objects.get(id=order_id)
	print(order.total)
	image = ProductImages.objects.filter(product=order.product)[0]
	variants = OrderItemVariant.objects.filter(orderitem=order)
	dic = {'order':order, 'image':image.image.url, 'variants':variants}
	return dic
