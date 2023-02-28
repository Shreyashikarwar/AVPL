from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.http import JsonResponse
import geocoder
import googlemaps
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from django.http import HttpResponse
from vendor_app.models import *
from admin_app.models import *
from user_app.models import *
from main_app.models import *
import uuid
from main_app.utils import *
from main_app.mlm_utils import *
from user_app.utils import *
from main_app.views import send_otp

@csrf_exempt
def create_user(request):
	email = request.POST.get('email')
	password = request.POST.get('password')
	if User.objects.filter(email=email).exists():
		messages.info(request,'User Already Exists')
		return HttpResponse('Error : User Already Registered')
	else:
		#User.objects.create_user(email,email,password)
		User.objects.create_user(email = email, username= email, password =password)
		user = User.objects.get(email=email)
		Role(user=user, level=Levels.objects.get(level='User')).save()
		first_name = request.POST.get('first_name')
		last_name = request.POST.get('last_name')
		gender = request.POST.get('gender')
		phone = request.POST.get('phone')
		question = request.POST.get('question')
		answer = request.POST.get('answer')
		zipcode = request.POST.get('zipcode')
		address = request.POST.get('adrs')
		gmaps = googlemaps.Client(key='AIzaSyBqBF76cMbvE_LREvm1S43LzZGxTsRQ0wA')
		if address:
			add_lat_long = gmaps.geocode(address)
			lat = add_lat_long[0]['geometry']['location']['lat']
			lng = add_lat_long[0]['geometry']['location']['lng']
			# lat = 28.7983
			# lng = 79.0220
			UserData.objects.create(
				user = user,
				first_name = first_name,
				last_name = last_name,
				phone = phone,
				address = address,
				zipcode = zipcode,
				latitude = lat,
				longitude = lng,
				gender = gender,
				question = question,
				answer = answer
			)
			return send_otp(request, 'User', user)

def user_dashboard(request):
	if check_user_authentication(request, 'User'):
		dic = {
			'user':UserData.objects.get(user=request.user),
			'tree':fetch_empty_nodes(request.user),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'user_app/dashboard.html', dic)
	else:
		return render(request, '403.html')

		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def user_create_link(request):
	if check_user_authentication(request, 'User'):
		flag = False
		mlm = MLM.objects.get(node=request.user)
		if mlm.left == None or mlm.right == None:
			flag = True
		dic = {
			'user':UserData.objects.get(user=request.user),
			'flag':flag,
			'tree':fetch_empty_nodes(request.user),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=True))
		}
		return render(request, 'user_app/create-link.html', dic)
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')



# def direct_referal(request):
# 	if request.user.is_authenticated:
# 		referal_pv = 0
# 		mlm = MLM.objects.filter(parent=request.user)
# 		mlm = []
# 		for i in MLM.objects.filter(parent=request.user):
# 			mlm.append(i)
# 		for i in mlm:
# 			print(i)
# 			if UserData.objects.filter(user__username=i):
# 				referal_pv = referal_pv + UserData.objects.get(user__username=i).pv
		
# 		print(referal_pv)
# 		return referal_pv

def direct_referal(request):
	if check_user_authentication(request, 'User'):
		flag = False
		referal_pv = 0
		mlm = MLM.objects.filter(parent=request.user)
		mlm = []
		for i in MLM.objects.filter(parent=request.user):
			mlm.append(i)
		user_data = []
		for i in mlm:
			user_data.append({i:UserData.objects.get(user__username=i).pv})
		for i in mlm:
			if UserData.objects.filter(user__username=i):
				referal_pv = referal_pv + UserData.objects.get(user__username=i).pv
		redeem_amount = referal_pv*(DirectReferalCommission.objects.all()[0].percentage/100)
		dic = {
			'mlm':MLM.objects.filter(parent=request.user),
			'user_data':user_data,
			'flag':flag,
			'redeem_amount':redeem_amount,
			'referal_pv':referal_pv,
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=True))
		}
		return render(request, 'user_app/direct_referal.html', dic)
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def referal_transaction(request):
	if check_user_authentication(request, 'User'):
		flag = False
		referal_pv = 0
		mlm = MLM.objects.filter(parent=request.user)
		mlm = []
		for i in MLM.objects.filter(parent=request.user):
			mlm.append(i)
		user_data = []
		print(mlm)
		for i in mlm:
			user_data.append({i:UserData.objects.get(user__username=i).pv})
		for i in mlm:
			if UserData.objects.filter(user__username=i):
				referal_pv = referal_pv + UserData.objects.get(user__username=i).pv
		redeem_amount = referal_pv*(DirectReferalCommission.objects.all()[0].percentage/100)
		print(redeem_amount)
		make_wallet_transaction(request.user, redeem_amount, 'CREDIT')
		dic = {
			'mlm':MLM.objects.filter(parent=request.user),
			'user_data':user_data,
			'flag':flag,
			'redeem_amount':redeem_amount,
			'referal_pv':referal_pv,
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=True))
		}
		return render(request, 'user_app/direct_referal.html', dic)
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')






def user_generate_link(request):
	if check_user_authentication(request, 'User'):
		data = {'link':generate_link(request.user, 'User')}
		return JsonResponse(data)
	else:
		return JsonResponse({'response':'Error'})

def user_generate_link_2(request):
	if check_user_authentication(request, 'User'):
		user = User.objects.get(id=request.GET.get('user'))
		data = {'link':generate_link(user, 'User')}
		return JsonResponse(data)
	else:
		return JsonResponse({'response':'Error'})

@csrf_exempt
def user_add_to_cart(request):
	if check_user_authentication(request, 'User'):
		print(request.user)
		variants = request.POST.getlist('variants[]')
		quantity = request.POST.get('quantity')
		product = Product.objects.get(id=request.POST.get('product'))
		print(product)
		flag = True
		print(product.stock)
		if product.stock >= int(quantity):
			print('hellllo')
			if True:
					print("fggd")
				
					if Cart.objects.filter(user=request.user).exists():
						print("bjhbjhgjh")
						cart = Cart.objects.get(user=request.user)
						allow = True
						for x in CartItems.objects.filter(cart=cart):
							print("jhvghvgf")
							if x.product.store == product.store:
								
								allow = True
								print(allow)
								break
							else:
								allow = False
								print(allow)
								break
						if allow:
							print("jhvhfty")
							variant_matched = False
							item = ''
							for items in CartItems.objects.filter(cart=cart, product=product):
								cart_variants = []
								print(cart_variants,"cart_variants")
								for x in CartItemVariant.objects.filter(cartitem=items):
									print("cccccc",x)
									cart_variants.append(str(x.product_variant.id))
								if variants == cart_variants:
									variant_matched = True
									item = items
									break
							if variant_matched:
								new_quantity = int(quantity) + item.quantity
								print(new_quantity,'hhhhhhhhhhhhhhhh')
								if new_quantity > product.stock:
									new_quantity = product.stock
								price = item.product.price
								total_price = item.product.price * new_quantity
								CartItems.objects.filter(id=item.id).update(
									quantity = new_quantity,
									per_item_cost = price,
									total_cost = total_price
								)
								subtotal = cart.subtotal + (int(quantity)*item.product.price)
								Cart.objects.filter(user=request.user).update(subtotal=subtotal)
								calculate_cart_tax(request)
							else:
								if int(quantity) > product.stock:
									quantity = product.stock
								item = CartItems.objects.create(
										cart = cart,
										product = product,
										quantity = quantity,
										per_item_cost = product.price,
										total_cost = product.price*int(quantity)
									)
								for x in variants:
									print("xxxxx",x)
									CartItemVariant.objects.create(cart=cart, cartitem=item, product_variant=ProductVariant.objects.get(id=x))
								subtotal = cart.subtotal + (int(quantity)*product.price)
								Cart.objects.filter(user=request.user).update(subtotal=subtotal)
								print("prining here")
								print(subtotal)
								calculate_cart_tax(request)
								return Response({'response':'success', 'cart_len':get_cart_len(request)})
						else:
							if int(quantity) > product.stock:
								quantity = product.stock
							print(quantity)
							item = CartItems.objects.create(
								cart = cart,
								product = product,
								quantity = quantity,
								per_item_cost = product.price,
								total_cost = product.price*int(quantity)
							)
							print(item,'iiiiiiiiiiiiiiiii')
							for x in variants:
								print("xxxxx",x)
								CartItemVariant.objects.create(cart=cart, cartitem=item, product_variant=ProductVariant.objects.get(id=x))
							subtotal = cart.subtotal + (int(quantity)*product.price)
							Cart.objects.filter(user=request.user).update(subtotal=subtotal)
							print("prining here")
							print(subtotal)
							calculate_cart_tax(request)
						return JsonResponse({'response':'success', 'cart_len':get_cart_len(request)})
						# else:
						# 	return JsonResponse({'response':'failed2', 'cart_len':get_cart_len(request)})
					else:
						if int(quantity) > product.stock:
								quantity = product.stock
						cart = Cart.objects.create(user=request.user)
						total = product.price*int(quantity)
						item = CartItems.objects.create(
							cart = Cart.objects.get(user=request.user),
							product = product,
							quantity = quantity,
							per_item_cost = product.price,
							total_cost = total
						)
						for x in variants:
							print("rerwe", x)
							CartItemVariant.objects.create(cart=cart, cartitem=item, product_variant=ProductVariant.objects.get(id=x))
						Cart.objects.filter(user=request.user).update(subtotal=total)
						calculate_cart_tax(request)
						return JsonResponse({'response':'success', 'cart_len':get_cart_len(request)})
		return JsonResponse({'response':'failed'})
	else:
		print('jello')
		return render(request, '403.html')

# wishlist
@csrf_exempt
def add_to_wishlist(request):
	if check_user_authentication(request, 'User'):
		variants = request.POST.getlist('variants[]')
		print("printing variants")
		print(variants)
		quantity = request.POST.get('quantity')
		product = Product.objects.get(id=request.POST.get('product'))
		print(product)
		flag = True
		if product.stock >= int(quantity):
			if True:
					print("fggd")
				
					if Wishlist.objects.filter(user=request.user).exists():
						print("bjhbjhgjh")
						wishlist = Wishlist.objects.get(user=request.user)
						allow = True
						for x in WishlistItems.objects.filter(wishlist=wishlist):
							print("jhvghvgf")
							if x.product.store == product.store:
								allow = True
								break
							else:
								allow = False
								break
						if allow:
							print("jhvhfty")
							variant_matched = False
							item = ''
							print(item)
							for items in WishlistItems.objects.filter(wishlist=wishlist, product=product):
								wishlist_variants = []
								print(wishlist_variants,"wishlist_variants")
								for x in WishlistItemVariant.objects.filter(wishlistitem=items):
									print("cccccc",x)
									wishlist_variants.append(str(x.product_variant.id))
								if variants == wishlist_variants:
									variant_matched = True
									item = items
									break
							if variant_matched:
								new_quantity = int(quantity) + item.quantity
								if new_quantity > product.stock:
									new_quantity = product.stock
								price = item.product.price
								print(price,'KKKKKKKKKKKK')
								total_price = item.product.price * new_quantity
								WishlistItems.objects.filter(id=item.id).update(
									quantity = new_quantity,
									per_item_cost = price,
									total_cost = total_price
								)
								subtotal = wishlist.subtotal + (int(quantity)*item.product.price)
								Wishlist.objects.filter(user=request.user).update(subtotal=subtotal)
							else:
								if int(quantity) > product.stock:
									quantity = product.stock
								item = WishlistItems.objects.create(
									wishlist = wishlist,
									product = product,
									quantity = quantity,
									per_item_cost = product.price,
									total_cost = product.price*int(quantity)
								)
								for x in variants:
									print("xxxxx",x)
									WishlistItemVariant.objects.create(wishlist=wishlist, wishlistitem=item, product_variant=ProductVariant.objects.get(id=x))
								subtotal = wishlist.subtotal + (int(quantity)*product.price)
								Wishlist.objects.filter(user=request.user).update(subtotal=subtotal)
								print("prining here")
								print(subtotal)
								# calculate_wishlist_tax(request)
								return JsonResponse({'response':'success', 'wishlist_len':get_wishlist_len(request)})
								# calculate_wishlist_tax(request)
						else:
							if int(quantity) > product.stock:
								quantity = product.stock
							item = WishlistItems.objects.create(
								wishlist = wishlist,
								product = product,
								quantity = quantity,
								per_item_cost = product.price,
								total_cost = product.price*int(quantity)
							)
							for x in variants:
								print("xxxxx",x)
								WishlistItemVariant.objects.create(wishlist=wishlist, wishlistitem=item, product_variant=ProductVariant.objects.get(id=x))
							subtotal = wishlist.subtotal + (int(quantity)*product.price)
							Wishlist.objects.filter(user=request.user).update(subtotal=subtotal)
							print("prining here")
							print(subtotal)
							# calculate_wishlist_tax(request)
						return JsonResponse({'response':'success', 'wishlist_len':get_wishlist_len(request)})
						# else:
						# 	return JsonResponse({'response':'failed2', 'wishlist_len':get_wishlist_len(request)})
					else:
						if int(quantity) > product.stock:
								quantity = product.stock
						wishlist = Wishlist.objects.create(user=request.user)
						total = product.price*int(quantity)
						item = WishlistItems.objects.create(
							wishlist = Wishlist.objects.get(user=request.user),
							product = product,
							quantity = quantity,
							per_item_cost = product.price,
							total_cost = total
						)
						for x in variants:
							print("rerwe", x)
							WItemVariant.objects.create(wishlist=wishlist, wishlistitem=item, product_variant=ProductVariant.objects.get(id=x))
						Wishlist.objects.filter(user=request.user).update(subtotal=total)
						# calculate_wishlist_tax(request)
						return JsonResponse({'response':'success', 'wishlist_len':get_wishlist_len(request)})
		return JsonResponse({'response':'failed'})
	else:
		return render(request, '403.html')

def user_wishlist(request):
	if check_user_authentication(request, 'User'):
		categories = ProductCategory.objects.all()
		if Wishlist.objects.filter(user=request.user).exists():
			dic = get_wishlist_items(request)
			if len(WishlistItems.objects.filter(wishlist=Wishlist.objects.get(user=request.user))) == 0:
				empty = True
			else:
				empty = False
			stock_out = False
			for x in dic['items']:
				if x['stock_out']:
					stock_out = True
					break
			dic.update({'empty':empty, 'stock_out':stock_out})
			dic.update(get_cart_len(request))
			dic.update({
						'categories':categories,
						'notification':get_notifications(request.user),
						'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
					})
			return render(request, 'usertemplate/wishlist.html', dic)
		else:
			dic = {'empty':True}
			dic.update(get_dic(request))
			dic.update(get_cart_len(request))
			dic.update({
							'categories':categories,
						'notification':get_notifications(request.user),
						'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
					})
			return render(request, 'usertemplate/wishlist.html', dic)
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')



def user_cart(request):
	if check_user_authentication(request, 'User'):
		categories = ProductCategory.objects.all()
		if Cart.objects.filter(user=request.user).exists():
			dic = get_cart_items(request)
			if len(CartItems.objects.filter(cart=Cart.objects.get(user=request.user))) == 0:
				empty = True
			else:
				empty = False
			stock_out = False
			for x in dic['items']:
				if x['stock_out']:
					stock_out = True
					break
			dic.update({'empty':empty, 'stock_out':stock_out})
			dic.update({
				'categories':categories,
				# 'notification':get_notifications(request.user),
				# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
				})
			dic.update(get_wishlist_len(request))
			print(dic)
			return render(request, 'usertemplate/cart.html', dic)
		else:
			dic = {'empty':True}
			dic.update(get_dic(request))
			dic.update({
				'categories':categories,
				'wish_len':get_wishlist_len(request),
				'notification':get_notifications(request.user),
				'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
				})
			return render(request, 'usertemplate/cart.html', dic)
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


def update_cart_item(request):
	cart = Cart.objects.get(user=request.user)
	print("cart=>", cart)
	item = CartItems.objects.get(id=request.GET.get('item'))
	print("item", item)
	new_quantity = int(request.GET.get('quantity'))
	if new_quantity > item.quantity:
		print('1')
		updated_quantity = new_quantity - item.quantity
		total_price = item.total_cost + (item.product.price * updated_quantity)
		price = item.product.price
		CartItems.objects.filter(id=request.GET.get('item')).update(
			quantity = new_quantity,
			per_item_cost = price,
			total_cost = total_price
		)
		subtotal = cart.subtotal + (updated_quantity*price)
		Cart.objects.filter(user=request.user).update(subtotal=subtotal)
		calculate_cart_tax(request)
	else:
		print('2')
		updated_quantity = item.quantity - new_quantity
		total_price = item.total_cost - (item.product.price * updated_quantity)
		price = item.product.price
		CartItems.objects.filter(id=request.GET.get('item')).update(
			quantity = new_quantity,
			per_item_cost = price,
			total_cost = total_price
		)
		subtotal = cart.subtotal - (int(updated_quantity)*item.product.price)
		Cart.objects.filter(user=request.user).update(subtotal=subtotal)
		calculate_cart_tax(request)
	cart = Cart.objects.get(user=request.user)
	dic = {
		'item_total':CartItems.objects.get(id=request.GET.get('item')).total_cost,
		'subtotal':cart.subtotal,
		'tax':cart.tax,
		'delivery':cart.delivery_charges,
		'total':cart.total
	}
	return JsonResponse(dic)

def remove_cart_item(request):
	cart = Cart.objects.get(user=request.user)
	item = CartItems.objects.get(id=request.GET.get('item'))
	subtotal = cart.subtotal - item.total_cost
	CartItemVariant.objects.filter(cartitem=CartItems.objects.get(id=request.GET.get('item'))).delete()
	CartItems.objects.filter(id=request.GET.get('item')).delete()
	Cart.objects.filter(user=request.user).update(subtotal=subtotal)
	calculate_cart_tax(request)
	cart = Cart.objects.get(user=request.user)
	if len(CartItems.objects.filter(cart=cart)) == 0:
		empty = '1'
	else:
		empty = '0'
	dic = {
		'subtotal':cart.subtotal,
		'tax':cart.tax,
		'delivery':cart.delivery_charges,
		'total':cart.total,
		'empty':empty
	}
	return JsonResponse(dic)

def remove_wishlist_item(request):
	wishlist = Wishlist.objects.get(user=request.user)
	item = WishlistItems.objects.get(id=request.GET.get('item'))
	subtotal = wishlist.subtotal - item.total_cost
	WishlistItemVariant.objects.filter(wishlistitem=WishlistItems.objects.get(id=request.GET.get('item'))).delete()
	WishlistItems.objects.filter(id=request.GET.get('item')).delete()
	Wishlist.objects.filter(user=request.user).update(subtotal=subtotal)
	wishlist = Wishlist.objects.get(user=request.user)
	if len(WishlistItems.objects.filter(wishlist=wishlist)) == 0:
		empty = '1'
	else:
		empty = '0'
	dic = {
		'subtotal':wishlist.subtotal,
		'tax':wishlist.tax,
		'delivery':wishlist.delivery_charges,
		'total':wishlist.total,
		'empty':empty
	}
	return JsonResponse(dic)

@csrf_exempt
def my_address(request):
	if check_user_authentication(request, 'User'):
		if request.method == 'POST':
			location = request.POST.get('location')
			name = request.POST.get('name')
			home_no = request.POST.get('home_no')
			landmark = request.POST.get('landmark')
			city = request.POST.get('city')
			pincode = request.POST.get('pincode')
			state = request.POST.get('state')
			contact = request.POST.get('contact')
			if len(Address.objects.filter(user=request.user)) == 0:
				default = True
			else:
				default = False
			gmaps = googlemaps.Client(key='AIzaSyCEjY246d9MYQIe69nPzV_ceogrpglpY0Q')
			if location:
				add_lat_long = gmaps.geocode(location)
				lat = add_lat_long[0]['geometry']['location']['lat']
				lng = add_lat_long[0]['geometry']['location']['lng']
				Address.objects.create(
					user = request.user,
					latitude = lat,
					longitude = lat,
					name = name,
					home_no = home_no,
					landmark = landmark,
					city = city,
					pincode = pincode,
					state = state,
					contact = contact,
					default = default
				)
			code = ''
			for x in Address.objects.filter(user=request.user):
				code = code + '<tr>'
				code = code + '<td>'+x.name+'</td>'
				code = code + '<td>'+x.home_no+'</td>'
				code = code + '<td>'+x.landmark+'</td>'
				code = code + '<td>'+x.city+'</td>'
				code = code + '<td>'+x.pincode+'</td>'
				code = code + '<td>'+x.state+'</td>'
				code = code + '<td>'+x.contact+'</td>'
				code = code + '</tr>'
			dic = {'data':code, 'msg':'Address Added Successfully !!!!'}
			return JsonResponse(dic)
		return render(request, 'user_app/my-address.html', {'user':UserData.objects.get(user=request.user), 'data':Address.objects.filter(user=request.user)})
	else:
		return render(request, '403.html')

def user_set_default_address(request):
	if check_user_authentication(request, 'User'):
		if request.method == 'GET':
			id_ = request.GET.get('id')
			Address.objects.filter(user=request.user).update(default=False)
			Address.objects.filter(id=id_).update(default=True)
			address = Address.objects.get(id=id_)
			code = address.name+'<span id="span" style="background-color:green;color:white;padding-right:5px;padding-left:5px;border-radius:50px;">DEFAULT</span>'
			return HttpResponse(code)
	else:
		return render(request, '403.html')

@csrf_exempt
def add_new_address(request):
	if check_user_authentication(request, 'User'):
		if request.method == 'POST':
			location = request.POST.get('location')
			name = request.POST.get('name')
			home_no = request.POST.get('home_no')
			landmark = request.POST.get('landmark')
			city = request.POST.get('city')
			pincode = request.POST.get('pincode')
			state = request.POST.get('state')
			contact = request.POST.get('contact')
			if len(Address.objects.filter(user=request.user)) == 0:
				default = True
			else:
				default = False
			gmaps = googlemaps.Client(key='AIzaSyCEjY246d9MYQIe69nPzV_ceogrpglpY0Q')
			if location:
				# add_lat_long = gmaps.geocode(location)
				# lat = add_lat_long[0]['geometry']['location']['lat']
				# lng = add_lat_long[0]['geometry']['location']['lng']
				lat= 28.7983
				lng = 79.0220
				Address.objects.create(
					user = request.user,
					latitude = lat,
					longitude = lng,
					name = name,
					home_no = home_no,
					landmark = landmark,
					city = city,
					pincode = pincode,
					state = state,
					contact = contact,
					default = default
				)
			return redirect('/selectaddress/?cart='+request.session['cart_id'])
		return render(request, 'user_app/my-address.html', {'user':UserData.objects.get(user=request.user), 'data':Address.objects.filter(user=request.user)})
	else:
		return render(request, '403.html')

def my_order(request):
	if check_user_authentication(request, 'User'):
		store_id = request.GET.get('store')
		orders = []
		if store_id:
			store = Store.objects.get(id=store_id)
			orders = get_my_orders(request.user, store)
		else:
			orders = get_my_orders(request.user)
		dic = {
			'user':UserData.objects.get(user=request.user),
			'orders':orders,
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'user_app/my_order.html', dic)
	else:
		return render(request, '403.html')

def enable_self_pickup(request):
	check = request.GET.get('self')
	if check == '1':
		Cart.objects.filter(id=request.GET.get('c')).update(self_pickup=True)
	else:
		Cart.objects.filter(id=request.GET.get('c')).update(self_pickup=False)
	return JsonResponse({'response':'success'})

@csrf_exempt
def save_location(request):
	if check_user_authentication(request, 'User'):
		address = request.GET.get('location')
		gmaps = googlemaps.Client(key='AIzaSyBqBF76cMbvE_LREvm1S43LzZGxTsRQ0wA')
		if address:
			add_lat_long = gmaps.geocode(address)
			lat = add_lat_long[0]['geometry']['location']['lat']
			lng = add_lat_long[0]['geometry']['location']['lng']
		UserData.objects.filter(user=request.user).update(
			latitude=lat,
			longitude=lng
		)
		return JsonResponse({'response':'success'})

def user_wallet(request):
	if check_user_authentication(request, 'User'):
		if not Wallet.objects.filter(user=request.user).exists():
			Wallet.objects.create(user=request.user)
		dic = {'user':UserData.objects.get(user=request.user),
			'wallet':Wallet.objects.get(user=request.user),
			'wallet_transactions':WalletTransaction.objects.filter(wallet=Wallet.objects.get(user=request.user)).order_by('-transaction_date'),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'user_app/wallet-dash.html', dic)
	else:
		return render(request, '403.html')

def user_pv_wallet(request):
	if check_user_authentication(request, 'User'):
		print(UserData.objects.get(user=request.user).pv)
		dic = {'user':UserData.objects.get(user=request.user),
			'pv':fetch_pv(request.user),
			'transactions':fetch_pv_transactions(request.user),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'user_app/pv.html', dic)
	else:
		return render(request, '403.html')

def user_tree(request):
	if check_user_authentication(request, 'User'):
		dic = {
			'user':UserData.objects.get(user=request.user),
			'tree':fetch_user_tree(request.user),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'user_app/tree.html', dic)
	else:
		return render(request, '403.html')

@csrf_exempt
def user_save_product_rating(request):
	if check_user_authentication(request, 'User'):
		if request.method == 'POST':
			product = Product.objects.get(id=request.POST.get('product'))
			rating = request.POST.get('rating')
			print(rating)
			review  = request.POST.get('review')
			print(review)
			user = request.user
			# if not ProductRating.objects.create(user=user, product=product).exists():
			ProductRating.objects.create(user=user, product=product, rating=rating, review=review)
			return redirect('/user/myorder')
	else:
		return render(request, '403.html')

@csrf_exempt
def user_withdraw(request):
	if check_user_authentication(request, 'User'):
		if request.method == 'POST':
			amount = float(request.POST.get('amount'))
			if amount < 500:
				messages.success(request, 'Withdrawl amount must be greater than 500.')
				return redirect('/user/withdraw')
			flag = True
			for x in UserWithdrawRequest.objects.filter(user=request.user):
				if x.status == 0 or x.status == 1:
					flag = False
					break
			if flag:
				tds = ((amount/100)*5)
				UserWithdrawRequest.objects.create(
					user = request.user,
					request_date = timezone.now(),
					amount = amount,
					tds = tds
				)
				messages.success(request, 'We have received your payment withdraw request. Your payment wil be credited in your account in 3 working days after approval.')
				return redirect('/user/withdraw')
			else:
				messages.success(request, 'You already have a withdrawl request pending, please wait for it to credit.')
				return redirect('/user/withdraw')
		flag = True
		if PaymentInfo.objects.filter(user=request.user).exists():
			flag = True
		else:
			flag = False
		if not Wallet.objects.filter(user=request.user).exists():
			Wallet.objects.create(user=request.user)
		dic = {
			'user':UserData.objects.get(user=request.user),
			'flag':flag,
			'wallet':Wallet.objects.get(user=request.user),
			'data':UserWithdrawRequest.objects.filter(user=request.user),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'user_app/withdraw.html', dic)
	else:
		return render(request, '403.html')


@csrf_exempt
def user_save_paymentinfo(request):
	if check_user_authentication(request, 'User'):
		if request.method == 'POST':
			pan = request.FILES['pan']
			aadhar = request.FILES['aadhar']
			number = request.POST.get('number')
			name = request.POST.get('name')
			ifsc = request.POST.get('ifsc')
			if not PaymentInfo.objects.filter(user=request.user).exists():
				PaymentInfo.objects.create(
					user = request.user,
					account_no = number,
					bank_name = name,
					ifsc = ifsc,
					pan = pan,
					aadhar = aadhar
				)
			messages.success(request, 'Payment Details Saved Successfully')
			return redirect('/user/withdraw')
	else:
		return render(request, '403.html')

@csrf_exempt
def user_help(request):
	if check_user_authentication(request, 'User'):
		if request.method == 'POST':
			subject = request.POST.get('subject')
			message = request.POST.get('message')
			Query.objects.create(user=request.user, query_date=timezone.now(), subject=subject, message=message)
			messages.success(request, 'Query Received')
			return redirect('/user/help')
		dic = {
			'user':UserData.objects.get(user=request.user),
			'queries':Query.objects.filter(user=request.user),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'user_app/help.html', dic)
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')



def user_product_query(request):
	if check_user_authentication(request, 'User'):
		order = OrderItems.objects.get(id=request.GET.get('order'))
		dic = {
			'order':order,
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'user_app/product-query.html', dic)
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def user_cancel_order(request):
	if check_user_authentication(request, 'User'):
		order = OrderItems.objects.get(id=request.GET.get('order'))
		# reason = OrderItems.objects.get(reason)
		dic = {
			'order':order,
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'user_app/cancel-order.html', dic)
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def cancel_confirm(request):
	if check_user_authentication(request, 'User'):
		if request.method == 'POST':
			order_id = request.POST.get('order_id')
			print(order_id)
			reason = request.POST.get('reason')
			print(reason)
			obj = OrderItems.objects.get(id=order_id, order__user__username=request.user)
			obj.cancelled_on = timezone.now()
			obj.cancellation_reason = reason
			obj.delivery_status = 'Cancelled'
			if obj:
				obj.save()
				print(obj)
				messages.success(request, 'Order Cancelled!')
				dic = {
					'user':UserData.objects.get(user=request.user),
					'notification':get_notifications(request.user),
					'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
					}
				notification(request.user, 'Order Cancelled Successfully!')
				return redirect('/user/myorder', dic)
			else:
				print('hello')
				dic = {
					'user':UserData.objects.get(user=request.user),
					'notification':get_notifications(request.user),
					'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
					}
				messages.error(request, 'Please enter Valid data.')
				return redirect('/user/myorder', dic)
			# except:
			# 	print('hnhjhj')
			# 	return render(request, 'user_app/my_order.html')
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')



def user_generate_invoice(request):
	if check_user_authentication(request, 'User'):
		order = OrderItems.objects.get(id=request.GET.get('i'))
		dic = {
			'order':order
		}
		return render_to_pdf('main_app/invoice.html', dic)
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def create_vendor_link(request):
	if check_user_authentication(request, 'User'):
		if UserVendorRelation.objects.filter(user=request.user).exists():
			dic = {
			'user':UserData.objects.get(user=request.user),
			'vendor_user':UserVendorRelation.objects.filter(user=request.user),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=True))
		}
		else:
			dic = {
			'user':UserData.objects.get(user=request.user),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=True))
		}
		print("printing user")
		print(UserData.objects.get(user=request.user).user.usr.first_name)
		return render(request, 'user_app/create-vendor-link.html',dic)
	else:
		return HttpResponse('404 Not Found')

def user_vendor_generate_link(request):
	if check_user_authentication(request, 'User'):
		data = {'link':generate_link(request.user, 'Vendor')}
		return JsonResponse(data)
	else:
		return JsonResponse({'response':'Error'})

@csrf_exempt
def subscription_amount(request):
	if check_user_authentication(request, 'User'):
		if request.method == 'POST':
			amount = request.POST.get('amount')
			amt = float(amount) / 100
			receipt = Memberip_Receipt.objects.create(user=request.user, amount=amt)
			data = create_razorpay_order2(str(receipt.id), request.user, amount)
			return JsonResponse({'data':data})
		else:
			month = request.GET.get('month')
			sub = SubscriptionCharge.objects.all()
			if len(sub) > 0:
				sub = sub[0]
				if month == '1':
					dic = {'amount':sub.one_month_subscription_charge}
					return JsonResponse(dic)
				elif month == '3':
					dic = {'amount':sub.three_month_subscription_charge}
					return JsonResponse(dic)
				elif month == '6':
					dic = {'amount':sub.six_month_subscription_charge}
					return JsonResponse(dic)
				elif month == '12':
					dic = {'amount':sub.twelve_month_subscription_charge}
					return JsonResponse(dic)
				else:
					return JsonResponse({'amount':'0.0'})
			else:
				return JsonResponse({'amount':'Error'})
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def capture_recharge_payment(request):
	if request.method == 'POST':
		payment_id = request.POST.get('razorpay_payment_id')
		order_id = request.POST.get('razorpay_order_id')
		signature = request.POST.get('razorpay_signature')
		receipt = Memberip_Receipt.objects.get(razorpay_order_id=order_id)
		razorpaytransaction = RazorpayTransaction.objects.create(payment_id=payment_id, order_id=order_id, signature=signature)
		receipt.payment_id = payment_id
		receipt.status = True
		receipt.save()
		#make_business_limit_transaction(request.user.vendor, receipt.amount, 'CREDIT', 'Recharge Receipt ID '+str(receipt.id))
		#below vendor recharge amount credit in admin wallet
		#Transaction goes to Admin wallet
		make_commission_transaction(receipt.amount, 'CREDIT')
		if Membership.objects.filter(user = request.user).exists():
			Membership.objects.filter(user = request.user).delete()
		Membership.objects.create(user = request.user)
		UserData.objects.filter(user = request.user).update(subscribed = True)
		sub = 'AVPL - Subscription '
		msg = '''Hi there!
Your Subscription has been successfully completed with amount Rs '''+str(receipt.amount)+'''.

Thanks!'''
		EmailMessage(sub, msg, to=[request.user.email]).send()
		notification(request.user, 'Subscription Successfully.')
		return render(request, 'user_app/subscription-success.html')
	else:
		return HttpResponse('Failed')

@csrf_exempt
def vendor_list(request):
	if check_user_authentication(request, 'User'):
		if request.method == 'GET':
			vendors = User.objects.all()
			return render(request, 'user_app/vendor-list.html', {'vendors':vendors})
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')
@csrf_exempt
def subscriptionRequest(request):
	if check_user_authentication(request, 'User'):
		if request.method == "POST":
			if not UserSubscriptionRequest.objects.filter(user=request.user, status=False).exists():
				vendor_id = request.POST.get('key')
				amount = request.POST.get('amount')
				month = request.POST.get('month')
				vendor = Vendor.objects.get(id = vendor_id)
				UserSubscriptionRequest.objects.create(
					user = request.user,
					vendor = vendor,
					amount = amount,
					month = month
				)
				return JsonResponse({'success':"success"})
			else:
				msg ="You have already requested for plus membership"
				return HttpResponse(msg)
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def user_billing_request(request):
	if check_user_authentication(request, 'User'):
		if request.method == 'POST':
			store = Store.objects.get(id=request.POST.get('store_id'))
			amount = request.POST.get('amount')
			plan = request.POST.get('plan')
			Billing_Request.objects.create(
				user = request.user,
				store = store,
				amount = amount,
				plan = plan
			)
			messages.success(request, 'Billing Request Created Successfully')
			return redirect('/user/billing/request/')
		dic = {'stores':fetch_vendors(request.session.get('lat'), request.session.get('lng')), 'requests':Billing_Request.objects.filter(user=request.user, status=False)}
		return render(request, 'user_app/billing-request.html', dic)
	return render(request, '403.html')
	# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def user_tds_withdraw(request):
	if check_user_authentication(request, 'User'):
		dic = {
			'tds_log':TDS_Log.objects.filter(user=request.user),
			'users':UserWithdrawRequest.objects.all(), 'vendors':VendorWithdrawRequest.objects.all(), 'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'user_app/tdslog.html', dic)
	else:
		return render(request, '403.html')
		# return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


##########################################################################################################################

from django.contrib.auth.decorators import login_required
from main_app.models import Wallet,WalletTransfer
import random

from django.db import transaction


login_required('/')
def wallet_transfer_vendor(request):	
	bal = Wallet.objects.get(user=request.user).current_balance
	vandordata = Vendor.objects.filter(status = True)
	transectiondata = WalletTransfer.objects.filter(user=request.user).order_by('-transection_time')
	context = {
			'vendordata': vandordata,
			'transectiodetails':transectiondata,
			'bal':bal
		}
	if WalletTransferApproval.objects.get(id =1).customer == 1:
		if request.method == 'POST':
			request.session['recivername'] = request.POST.get('rvname') 
			request.session['amount']  = int(request.POST.get('amt'))
			request.session['senderotp'] = random.randint(100000,999999)
			# request.session['reciverotp'] = random.randint(100000,999999)
			request.session['type012'] = 1
			# request.session['timer'] = str(datetime.datetime.now() + datetime.timedelta(minutes=2))
			# print('-------------------------->',request.session['timer'],type(request.session['timer']),request.session['type012'])
			print(request.session['senderotp'],'\n---------->',request.session['recivername'])

			return render(request,'user_app/otpverify.html')
		

		return render(request,'user_app/vendorwallettransfer.html',context=context)

	else:
		messages.error(request,'Payments Mode off')
		return render(request,'user_app/vendorwallettransfer.html',context=context)


login_required('/')
@transaction.atomic
def transfer_amount(request):
	
	if request.method == 'POST':
		senderotp = int(request.POST.get('otp1') )
	
		# if datetime.datetime.now() < datetime.datetime.strptime(request.session['timer'], '%Y-%m-%d %H:%M:%S.%f') :
		
		if senderotp == request.session['senderotp']:
			
			if Wallet.objects.get(user=request.user).current_balance >= request.session['amount']:

				make_wallet_transaction(user = request.user, amount = request.session['amount'], trans_type = 'DEBIT')
				make_wallet_transaction(user = User.objects.get(username = request.session['recivername']), 
					amount = request.session['amount'], trans_type = 'CREDIT')
				print(request.session['recivername'])
				transfer_into_another_account(usr = request.user, sender = request.user.username,
					reciver = request.session['recivername'],amount = request.session['amount'])
				print('done!')
				messages.success(request,'Successfully Transfered')
				# if int(request.session['type012']) == 0:
				# 	return redirect('transfer_money')
				# else:
				return redirect('vendor-wallet-transfer')


			else :
				messages.error(request,'Not having sufficient balance')
				if int(request.session['type012']) == 0:
					return redirect('transfer_money')
				else:
					return redirect('vendor-wallet-transfer')

		else :
			messages.error(request,'OTP is not Correct')
			if int(request.session['type012']) == 0:
				return redirect('transfer_money')
			else:
				return redirect('transfer_money_vander')
		# else:
		# 	messages.error(request,'Timeout')
		# 	if int(request.session['type012']) == 0:
		# 		return redirect('transfer_money')
		# 	else:
		# 		return redirect('transfer_money_vander')
	if int(request.session['type012']) == 0:
		return redirect('transfer_money')
	else:
		return redirect('transfer_money_vander')
	# return render(request,'user_app/otpverify.html')

