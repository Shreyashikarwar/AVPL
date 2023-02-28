import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
import geocoder
import googlemaps
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from django.http import HttpResponse
from vendor_app.models import *
from main_app.models import *
from admin_app.models import *
from django.http import JsonResponse
from vendor_app.utils import *
from main_app.utils import *
from django.utils import timezone

def vendor_dashboard(request):
	if check_user_authentication(request, 'Vendor'):
		vendor = Vendor.objects.get(id=request.user.vendor.id)
		if vendor.store_created and vendor.verified and vendor.status:
			dic = {'vendor':vendor, 'orders':OrderItems.objects.filter(store=request.user.vendor.store)}
			return render(request, 'vendor_app/dashboard.html', dic)
		elif vendor.doc_submitted == False:
			return redirect('/vendor/verification')
		elif vendor.store_created == False:
			return redirect('/vendor/storeinfo')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def store_info(request):
	if check_user_authentication(request, 'Vendor'):
		if request.method == 'POST':
			vendor = Vendor.objects.get(user=request.user)
			name = request.POST.get('name')
			description = request.POST.get('description')
			reg_no = request.POST.get('reg_no')
			logo = request.FILES['logo']
			image = request.FILES['image']
			closing_day = request.POST.get('closing_day')
			closing_time = request.POST.get('closing_time')
			opening_time = request.POST.get('opening_time')
			banner = request.FILES['banner']
			if Store.objects.filter(name=name, registration_number=reg_no).exists():
				messages.info(request, 'Store Already Exists')
				return redirect('/vendor/storeinfo')
			else:
				Store.objects.create(
					vendor = vendor,
					name = name,
					description = description,
					registration_number = reg_no,
					closing_day = closing_day,
					opening_time = opening_time,
					closing_time = closing_time
				)
				store = Store.objects.get(vendor=vendor)
				StoreImages.objects.create(
					store = store,
					logo = logo,
					banner = banner,
					image = image
				)
				Vendor.objects.filter(id=vendor.id).update(store_created=True)
				BusinessLimit.objects.create(vendor=vendor)
				messages.info(request, 'Store Created Successfully !!!!')
				return redirect('/vendor/')
		return render(request, 'vendor_app/store-register.html', {})
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def vendor_doc(request):
	if check_user_authentication(request, 'Vendor'):
		if request.method == 'POST':
			vendor = Vendor.objects.get(id=request.user.vendor.id)
			aadhar = None
			aadharfront = None
			aadharback = None
			#making Adhar optional
			try:
				aadhar = request.POST.get('aadhar')
				aadharfront = request.FILES['aadharfront']
				aadharback = request.FILES['aadharback']
			except:
				pass
			gst = request.POST.get('gst')
			msme = request.POST.get('msme')
			pan = request.POST.get('pan')
			bank_no = request.POST.get('bank_no')
			bank_name = request.POST.get('bank')
			panimage = request.FILES['panimage']
			shippingpolicy = request.FILES['shippingpolicy']
			returnpolicy = request.FILES['returnpolicy']
			ifsc = request.POST.get('ifsc')
			bank_passbook = request.FILES['bank_passbook']
			razorpay_id = request.POST.get('razor')
			VendorDocs.objects.create(
				vendor = vendor,
				vendor_idproof = aadhar,
				front_idproof = aadharfront,
				back_idproof = aadharback,
				store_gst = gst,
				store_msme = msme,
				pancard = pan,
				pancard_image = panimage,
				shiping_policy = shippingpolicy,
				return_policy = returnpolicy,
				bank_account_number = bank_no,
				bank_name = bank_name,
				bank_ifsc = ifsc,
				bank_passbook = bank_passbook,
				razorpay_id = razorpay_id
			)
			Vendor.objects.filter(id=vendor.id).update(doc_submitted=True)
			sub = 'AVPL - Thank You For Submitting KYC Documents'
			msg = '''Hi there!
We got your documents for KYC, we will verify them soon and let you know,

Thanks!'''
			EmailMessage(sub,msg,to=[request.user.email]).send()
			return redirect('/vendor/verification')
		else:
			vendor = Vendor.objects.get(id=request.user.vendor.id)
			dic = {'vendor':vendor, 'flag':vendor.doc_submitted}
			return render(request, 'vendor_app/vendor-doc.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def add_product(request):
	if check_user_authentication(request, 'Vendor'):
		if request.method == 'POST':

			vendor = Vendor.objects.get(id=request.user.vendor.id)
			print(vendor)
			store = request.user.vendor.store
			category = ProductCategory.objects.get(id=request.POST.get('cate'))
			subcategory = ProductSubCategory.objects.get(id=request.POST.get('subcate'))
			subsubcategory = ProductSubSubCategory.objects.get(id=request.POST.get('subsubcate'))
			brand = Brand.objects.get(id=request.POST.get('brand'))
			name = request.POST.get('name')
			# des = request.POST.get('des')
			# print(des)
			mrp_price = request.POST.get('mrp_price')
			price = request.POST.get('price')
			stock = request.POST.get('stock')
			weight = request.POST.get('weight')
			offer = request.POST.get('offer')
			discount = request.POST.get('discount')
			if Product.objects.filter(store=store, name=name).exists():
				messages.info(request, 'Product Already Exists')
				return redirect('/vendor/addproduct')
			else:
				product = Product.objects.create(
					store = store,
					category = category,
					subcategory = subcategory,
					subsubcategory = subsubcategory,
					brand = brand,
					name = name,
					description = "hello",
					mrp = mrp_price,
					price = price,
					stock = stock,
					weight = weight,
					offer=offer,
					discount = discount
				)
				messages.success(request, 'Product Added Successfully')
				dic = {
					'vendor':vendor,
					'categories':ProductCategory.objects.all(),
					'subcategories':ProductSubCategory.objects.all(),
					'subsubcategories':ProductSubSubCategory.objects.all(),
					'brands':Brand.objects.all(),
					'images':True,
					'product':product,
					'notification':get_notifications(request.user),
					'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
				}
				request.session['product'] = Product.objects.get(store=store, name=name).id
				return render(request,'vendor_app/add-product.html', dic)
		else:
			#Product.objects.all().delete()
			vendor = Vendor.objects.get(id=request.user.vendor.id)
			dic = {
				'vendor':vendor,
				'categories':ProductCategory.objects.all(),
				'categories':ProductCategory.objects.all(),
				'subcategories':ProductSubCategory.objects.all(),
				'brands':Brand.objects.all(),
				'subsubcategories':ProductSubSubCategory.objects.all(),
				'info':True,
				'notification':get_notifications(request.user),
				'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
			}
			return render(request,'vendor_app/add-product.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def add_product_images(request):
	if check_user_authentication(request, 'Vendor'):
		if request.method == 'POST':
			vendor = Vendor.objects.get(id=request.user.vendor.id)
			images = request.FILES.getlist('images')
			product = Product.objects.get(id=request.session['product'])
			for image in images:
				ProductImages.objects.create(product=product,image=image)
			messages.success(request, 'Product Images Added Successfully')
			dic = {
				'vendor':vendor,
				'categories':ProductCategory.objects.all(),
				'variants':Variant.objects.all(),
				'variant':True,
				'product':product,
				'notification':get_notifications(request.user),
				'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
			}
			return render(request,'vendor_app/add-product.html', dic)
		else:
			vendor = Vendor.objects.get(id=request.user.vendor.id)
			dic = {
				'vendor':vendor,
				'categories':ProductCategory.objects.all(),
				'info':True,
				'notification':get_notifications(request.user),
				'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
			}
			return render(request,'vendor_app/add-product.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def add_product_variant(request):
	if check_user_authentication(request, 'Vendor'):
		if request.method == 'POST':
			variant = Variant.objects.get(id=request.POST.get('variant'))
			variant_value = VariantValue.objects.get(id=request.POST.get('variantvalue'))
			variant_stock = request.POST.get('variantstock')
			product = Product.objects.get(id=request.session['product'])
			if ProductVariant.objects.filter(product=product, variant=variant, variant_value=variant_value).exists():
				return JsonResponse({'response':'failed'})
			ProductVariant.objects.create(product=product, variant=variant, variant_value=variant_value, variant_stock=variant_stock)
			data = ''
			for x in ProductVariant.objects.filter(product=product):
				data = data + '<tr><td>'+x.variant.name+'</td><td>'+x.variant_value.value+'</td><td>'+str(x.variant_stock)+'</td></tr>'
			return HttpResponse(data)
		else:
			vendor = Vendor.objects.get(id=request.user.vendor.id)
			dic = {
				'vendor':vendor,
				'categories':ProductCategory.objects.all(),
				'info':True,
				'notification':get_notifications(request.user),
				'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
			}
			messages.success(request, 'Product has been added and added successfully. Now waiting for admin approval.')
			return render(request,'vendor_app/add-product.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def fetch_sub_category(request):
	category = ProductCategory.objects.get(id=request.GET.get('cate'))
	subcategory = ProductSubCategory.objects.filter(category = category)
	data = '<option selected disabled>----select product sub category----</option>'
	for x in subcategory:
		data = data + '<option value="'+str(x.id)+'">'+x.name+'</option>'
	return HttpResponse(data)

def fetch_variant_value(request):
	variant = Variant.objects.get(id=request.GET.get('variant'))
	data = ''
	for x in VariantValue.objects.filter(variant=variant):
		data = data + '<option value="'+str(x.id)+'">'+x.value+'</option>'
	return HttpResponse(data)

def fetch_sub_sub_category(request):
	subcategory = ProductSubCategory.objects.get(id=request.GET.get('subcate'))
	subsubcategory = ProductSubSubCategory.objects.filter(subcategory = subcategory)
	data = '<option selected disabled>----select product sub sub category----</option>'
	for x in subsubcategory:
		data = data + '<option value="'+str(x.id)+'">'+x.name+'</option>'
	return HttpResponse(data)

def fetch_brands(request):
	category = ProductCategory.objects.get(id = request.GET.get('cate'))
	brands = Brand.objects.filter(category=category)
	data = '<option selected disabled>----select product brand----</option>'
	for x in brands:
		data = data + '<option value="'+str(x.id)+'">'+x.name+'</option>'
	return HttpResponse(data)

def vendor_product_list(request):
	if check_user_authentication(request, 'Vendor'):
		vendor = Vendor.objects.get(id=request.user.vendor.id)
		dic = {
			'vendor':vendor,
			'products':Product.objects.filter(store=vendor.store),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/product-list.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def vendor_profile(request):
	if check_user_authentication(request, 'Vendor'):
		vendor = Vendor.objects.get(id=request.user.vendor.id)
		vendoc = VendorDocs.objects.get(vendor__user=request.user)
		store = Store.objects.get(vendor__user=request.user)
		images = StoreImages.objects.get(store=store)
		vanadd = Vendor.objects.get(user=request.user)
		dic = {
			'vendoc':vendoc,
			'store':store,
			'info':vanadd,
			'vendor':vendor,
			'images':images,
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}			
		return render(request,'vendor_app/vendor-profile.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def edit_vendor_profile(request):
	if check_user_authentication(request, 'Vendor'):
		store = Store.objects.get(vendor__user=request.user)
		images = StoreImages.objects.get(store=store)
		vanadd = Vendor.objects.get(user=request.user)
		if request.method == 'POST':
			banner = request.FILES.get('banner_update')
			logo =  request.FILES.get('logo_update')
			store_name =  request.POST.get('store_name')
			description =  request.POST.get('description')
			address =  request.POST.get('address')
			closing_day =  request.POST.get('closing_day')
			closing_time =  request.POST.get('closing_time')
			opening_time =  request.POST.get('opening_time')
			print(store_name, logo)
			if banner and logo is None:
				images.banner = banner
				images.save()
			elif logo and banner is None:
				images.logo = logo
				images.save()
			elif logo and banner:
				images.banner = banner
				images.logo = logo
				images.save()
			else:
				store.name = store_name
				store.description = description
				store.closing_day = closing_day
				store.closing_time = closing_time
				store.opening_time = opening_time
				store.save()
				vanadd.address = address
				vanadd.save()
		dic = {
			'store':store,
			'info':vanadd,
			'images':images,
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
			
		return render(request,'vendor_app/edit-vendor.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def vendor_product(request):
	if check_user_authentication(request, 'Vendor'):
		vendor = Vendor.objects.get(id=request.user.vendor.id)
		product = Product.objects.get(id=request.GET.get('id'))
		dic = {
			'vendor':vendor,
			'product':product,
			'images':ProductImages.objects.filter(product=product),
			'variants':ProductVariant.objects.filter(product=product),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request,'vendor_app/product.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def vendor_product_basic_edit(request):
	if check_user_authentication(request, 'Vendor'):
		if request.method == 'POST':
			vendor = Vendor.objects.get(id=request.user.vendor.id)
			store = request.user.vendor.store
			name = request.POST.get('name')
			des = request.POST.get('des')
			price = request.POST.get('price')
			mrp = request.POST.get('mrp')
			stock = request.POST.get('stock')
			weight = request.POST.get('weight')
			offer = request.POST.get('offer')
			discount = request.POST.get('discount')

			Product.objects.filter(id=request.POST.get('id')).update(
				name = name,
				description = des,
				price = price,
				mrp = mrp,
				stock = stock,
				weight = weight,
				offer = offer,
				discount= discount,
			)
			messages.success(request, 'Product Updated Successfully')
			return redirect('/vendor/product?id='+request.POST.get('id'))
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def vendor_delete_product_image(request):
	if check_user_authentication(request, 'Vendor'):
		if request.method == 'GET':
			ProductImages.objects.filter(id=request.GET.get('i')).delete()
			return JsonResponse({'response':'Success'})
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def vendor_delete_product_variant(request):
	if check_user_authentication(request, 'Vendor'):
		if request.method == 'GET':
			ProductVariant.objects.filter(id=request.GET.get('i')).delete()
			return JsonResponse({'response':'Success'})
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def vendor_product_out_of_stock(request):
	if check_user_authentication(request, 'Vendor'):
		if request.method == 'GET':
			Product.objects.filter(id=request.GET.get('i')).update(stock=0)
			return JsonResponse({'response':'Success'})
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def vendor_orders(request):
	if check_user_authentication(request, 'Vendor'):
		vendor = Vendor.objects.get(id=request.user.vendor.id)
		dic = {
			'orders':OrderItems.objects.filter(store=request.user.vendor.store),
			'vendor':vendor,
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/orders.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def vendor_complete_orders(request):
	if check_user_authentication(request, 'Vendor'):
		vendor = Vendor.objects.get(id=request.user.vendor.id)
		dic = {
			'orders':OrderItems.objects.filter(store=request.user.vendor.store),
			'vendor':vendor,
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/complete-orders.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def vendor_order_detail(request):	
	if check_user_authentication(request, 'Vendor'):
		vendor = Vendor.objects.get(id=request.user.vendor.id)
		order_id = request.GET.get('i')
		dic = {
			'vendor':vendor,
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		dic.update(get_order_details(order_id))
		return render(request, 'vendor_app/order-detail.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

#changes for COD 
def vendor_change_order_status(request):
	if check_user_authentication(request, 'Vendor'):
		vendor = Vendor.objects.get(id=request.user.vendor.id)
		admin = User.objects.get(is_superuser = True)
		print('admin',admin)
		print(admin.id)
		order_id = request.GET.get('i')
		status = request.GET.get('s')
		if status == 'Delivered':
			OrderItems.objects.filter(id=order_id).update(delivery_status=status, delivered_on=timezone.now())
			user = OrderItems.objects.get(id=order_id).order.user
			order = OrderItems.objects.get(id=order_id).order
			if not order.paid:
				orderitems = OrderItems.objects.get(id=order_id)
				admin_commission = (orderitems.total/100)*orderitems.product.category.commission
				print("admin commission percentage")
				print(orderitems.product.category.commission)
				print(admin_commission,'KKKKKKKKKKKKKK')
				gst = (admin_commission/100)*18   #GST of 18 per on admin charge deduct from businesslimit
				print(gst)
				admin_commission_plus_gst = admin_commission + gst
				print("printing total_detection_amt")
				print(admin_commission_plus_gst)
				GST_Log.objects.create(orders = orderitems, gst_amt=gst)
				trans_name = 'Transaction for ORD'+str(order.id)+str(orderitems.id)
				#make_business_limit_transaction(vendor, admin_commission, 'DEBIT', trans_name)
				make_business_limit_transaction(vendor, admin_commission_plus_gst, 'DEBIT', trans_name)
				make_commission_transaction(admin_commission_plus_gst, 'CREDIT')
				user_c = 0.0
				if UserVendorRelation.objects.filter(vendor=vendor).exists():
					print('hhhhhhhhhhhhhhhh')
					user = UserVendorRelation.objects.get(vendor=vendor)
					percentage = float(str(UserVendorCommission.objects.get()))
					user_c = (orderitems.total/100) * percentage
					make_commission_transaction(admin_commission_plus_gst, 'CREDIT')
					make_wallet_transaction(vendor.user, user_c, 'DEBIT')
		else:
			OrderItems.objects.filter(id=order_id).update(delivery_status=status)
			notification(vendor.user, 'Order '+status)
		return redirect('/vendor/orderdetail?i='+order_id)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def vendor_brand(request):
	if check_user_authentication(request, 'Vendor'):
		if request.method == 'POST':
			category = ProductCategory.objects.get(id=request.POST.get('category'))
			name = request.POST.get('name')
			if Brand.objects.filter(category=category, name=name).exists():
				messages.info(request, 'Brand Already Exists')
				return redirect('/vendor/brand')
			else:
				Brand.objects.create(category=category, name=name)
				messages.success(request, 'Brand Added Successfully !!!!')
				return redirect('/vendor/brand')
		else:
			vendor = Vendor.objects.get(id=request.user.vendor.id)
			dic = {'vendor':vendor, 'categories':ProductCategory.objects.all(),
				'brands':Brand.objects.all(),
				'notification':get_notifications(request.user),
				'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
			}
			return render(request, 'vendor_app/brand.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def vendor_payment_transactions(request):
	if check_user_authentication(request, 'Vendor'):
		vendor = Vendor.objects.get(id=request.user.vendor.id)
		dic = {
			'vendor':vendor,
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/payment-transactions.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def vendor_wallet_dash(request):
	if check_user_authentication(request, 'Vendor'):
		if not Wallet.objects.filter(user=request.user).exists():
			Wallet.objects.create(user=request.user)
		vendor = Vendor.objects.get(id=request.user.vendor.id)
		wallet = Wallet.objects.get(user=request.user)
		transactions = WalletTransaction.objects.filter(wallet=wallet)
		dic = {
			'vendor':vendor,
			'wallet':wallet,
			'transactions':transactions,
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/wallet-dash.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

#method for Business Limit 
def vendor_Business_limit_dash(request):
	if check_user_authentication(request, 'Vendor'):
		if not BusinessLimit.objects.filter(vendor=request.user.vendor).exists():
			BusinessLimit.objects.create(vendor=request.user.vendor)
		vendor = Vendor.objects.get(id=request.user.vendor.id)
		business_limit = BusinessLimit.objects.get(vendor=request.user.vendor)
		business_limit_transactions = BusinessLimitTransaction.objects.filter(business_limit=business_limit)
		dic = {
			'vendor':vendor,
			'business_limit':business_limit,
			'business_limit_transactions':business_limit_transactions,
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/Business-limit-dash.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def vendor_withdraw(request):
	if check_user_authentication(request, 'Vendor'):
		if request.method == 'POST':
			amount = request.POST.get('amount')
			if float(amount) < 500:
				messages.success(request, 'Withdrawl amount must be greater than 500.')
				return redirect('/vendor/withdraw')
			flag = True
			for x in VendorWithdrawRequest.objects.filter(user=request.user):
				if x.status == 0 or x.status == 1:
					flag = False
					break
			if flag:
				VendorWithdrawRequest.objects.create(
					user = request.user,
					request_date = timezone.now(),
					amount = amount
				)
				messages.success(request, 'We have received your payment withdraw request. Your payment wil be credited in your account in 3 working days after approval.')
				return redirect('/vendor/withdraw')
			else:
				messages.success(request, 'You already have a withdrawl request pending, please wait for it to credit.')
				return redirect('/vendor/withdraw')
		vendor = Vendor.objects.get(id=request.user.vendor.id)
		if not Wallet.objects.filter(user=request.user).exists():
			Wallet.objects.create(user=request.user)
		dic = {
			'vendor':vendor,
			'wallet':Wallet.objects.get(user=request.user),
			'data':VendorWithdrawRequest.objects.filter(user=request.user),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/withdraw.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def vendor_help(request):
	if check_user_authentication(request, 'Vendor'):
		if request.method == 'POST':
			subject = request.POST.get('subject')
			message = request.POST.get('message')
			Query.objects.create(user=request.user, query_date=timezone.now(), subject=subject, message=message)
			messages.success(request, 'Query Received')
			return redirect('/vendor/help')
		vendor = Vendor.objects.get(id=request.user.vendor.id)
		dic = {
			'vendor':vendor,
			'queries':Query.objects.filter(user=request.user),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'vendor_app/help.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

#vender recharge below code not in working
from main_app.razor import *
@csrf_exempt
def vendor_recharge(request):
	if check_user_authentication(request, 'Vendor'):
		if request.method == 'POST':
			amount = request.POST.get('amount')
			amt = float(amount) / 100
			receipt = Recharge_Receipt.objects.create(vendor=request.user.vendor, amount=amt)
			data = create_razorpay_order(str(receipt.id), request.user.vendor, amount)
			return JsonResponse({'data':data})
		else:
			dic = {'business_limit':BusinessLimit.objects.get(vendor=request.user.vendor)}
			return render(request, 'vendor_app/businesslimittransaction.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def capture_recharge_payment(request):
	if request.method == 'POST':
		payment_id = request.POST.get('razorpay_payment_id')
		order_id = request.POST.get('razorpay_order_id')
		signature = request.POST.get('razorpay_signature')
		receipt = Recharge_Receipt.objects.get(razorpay_order_id=order_id)
		razorpaytransaction = RazorpayTransaction.objects.create(payment_id=payment_id, order_id=order_id, signature=signature)
		receipt.payment_id = payment_id
		receipt.status = True
		receipt.save()
		make_business_limit_transaction(request.user.vendor, receipt.amount, 'CREDIT', 'Recharge Receipt ID '+str(receipt.id))
		#below vendor recharge amount credit in admin wallet
		make_commission_transaction(receipt.amount, 'CREDIT')
		sub = 'AVPL - Business Limit Recharged'
		msg = '''Hi there!
Your business limit has been successfully recharge with amount Rs '''+str(receipt.amount)+'''.

Thanks!'''
		EmailMessage(sub, msg, to=[request.user.email]).send()
		notification(request.user, 'Recharged Successfully.')
		return render(request, 'vendor_app/recharge-success.html')
	else:
		return HttpResponse('Failed')

def userSubscriptionRequest(request):
	if request.user.role.level.level=='Vendor':
		if request.method == 'GET':
			data = UserSubscriptionRequest.objects.filter(vendor = request.user.vendor)
			dic={'data':data}
			return render(request, 'vendor_app/subscription-request.html', dic)

from datetime import tzinfo, timedelta, datetime

#function for activate User Subscription
def vendor_activate_subscription(request):
	if check_user_authentication(request, 'Vendor'):
		id_=request.GET.get('id')
		obj = UserSubscriptionRequest.objects.get(id=id_)
		
		UserSubscriptionRequest.objects.filter(id=id_).update(status=True)
		UserData.objects.filter(user=obj.user).update(subscribed=True)
		
		UserSubscription.objects.filter(user = obj.user).delete()
		UserSubscription.objects.create(user = obj.user, months=obj.month)
		
		business_limit=BusinessLimit.objects.get(vendor=request.user.vendor)
		subs_charges = SubscriptionCharge.objects.get()
		amount = obj.amount
		Gst = (amount/100)*18
		amt = amount -Gst
		vendor_percentage = subs_charges.vendor_percentage
		comiission_vendor = (amt/100)*float(vendor_percentage)
		admin_amt = float(amt) - float(comiission_vendor)
		admin_amt = float(admin_amt) + float(Gst)
		make_business_limit_transaction(request.user.vendor, admin_amt, 'DEBIT', 'payment sucessfull')
		make_commission_transaction(admin_amt, 'CREDIT')
		node = MLM.objects.get(node = obj.user)
		if not node.parent.role.level.level == 'Admin':
			save_pv_transaction2(node.parent, float(amount), 'Level')
		sub = 'Online Apni Dukaan - Subscription Activated Successfully'
		msg = '''Hi '''+obj.user.usr.first_name+'''!

You have successfully subscribed to Plus Membership of Online Apni Dukaan. Now you will get free delivery for 1 year. Enjoy shopping on onlineapnidukaan.com

Thanks & Regards,
Team Online Apni Dukaan'''
		EmailMessage(sub,msg,to=[obj.user.email]).send()
		messages.success(request, 'User Subscription Activated Successfully !!!!')
		notification(request.user, 'Vendor '+obj.vendor.first_name+' '+obj.vendor.last_name)
		notification(obj.user, 'Subscription Activated Successfully.')
		return redirect('/vendor/userSubscriptionRequest')
	else:
		return HttpResponse('404 Not Found')

def vendor_billing_requests(request):
	if check_user_authentication(request, 'Vendor'):
		dic = {'requests':Billing_Request.objects.filter(store=request.user.vendor.store, status=False)}
		return render(request, 'vendor_app/billing-requests.html', dic)
	return HttpResponse('404 Not Found')

def vendor_confirm_billing_requests(request):
	if check_user_authentication(request, 'Vendor'):
		config = None
		if len(Billing_Config.objects.all()) > 0:
			config = Billing_Config.objects.get()
		else:
			messages.success(request, 'Billing request not configured by admin yet')
			return redirect('/vendor/billing/requests/')
		billing = Billing_Request.objects.get(id=request.GET.get('i'))
		check_user_subscription(billing.user)
		admin_commission = save_vendor_commission(request.user, billing.amount, config.admin_commission)
		make_business_limit_transaction(billing.store.vendor, admin_commission, 'DEBIT', 'Billing Request Approval')
		user_c = 0.0
		if UserVendorRelation.objects.filter(vendor=billing.store.vendor).exists():
			user = UserVendorRelation.objects.get(vendor=billing.store.vendor)
			percentage = float(str(UserVendorCommission.objects.get()))
			user_c = (billing.amount/100) * percentage
			make_wallet_transaction(billing.user, user_c, 'CREDIT')
			make_business_limit_transaction(billing.store.vendor, user_c, 'DEBIT', 'User Commission')
			#make_wallet_transaction(billing.store.vendor.user, user_c, 'DEBIT')
		pv_percent = config.pv_percent
		pv = (billing.amount/100)*pv_percent
		total_pv = billing.user.usr.pv + pv
		PVTransactions.objects.create(
			user = billing.user,
			transaction_date = timezone.now(),
			previous_pv = billing.user.usr.pv,
			pv = pv,
			total_pv = billing.user.usr.pv + pv,
			plan = billing.plan
		)
		update_user_pv(billing.user, pv, billing.plan)
		billing.status = True
		billing.save()
		msg = ''' Hi there!
Your billing request has been approved by the vendor successfully. We have also transacted the resulted PV in your wallet.

Thanks!'''
		EmailMessage('AVPL - Billing Requests Approved', msg, to=[billing.user.email]).send()
		messages.success(request, 'Billing Request Approved Successfully')
		return redirect('/vendor/billing/requests/')
	return HttpResponse('404 Not Found')




####################################################################################################################################





from django.contrib.auth.decorators import login_required
# from main_app.models import Wallet,WalletTransfer
import random
from django.db import transaction
import datetime


login_required('/')
def vendorbalanacetransfer(request):
	bal = Wallet.objects.get(user=request.user).current_balance
	userdata = UserData.objects.filter(status = True)
	transectiondata = WalletTransfer.objects.filter(user=request.user).order_by('-id')
	context = {
			'userdata':userdata,
			'transectiodetails':transectiondata,
			'bal':bal
		}
	if WalletTransferApproval.objects.get(id =1).vendor == 1:

		if request.method == 'POST':
			print(request.user)
			request.session['recivername'] = request.POST.get('rvname') 
			request.session['amount']  = int(request.POST.get('amt'))
			request.session['senderotp'] = random.randint(100000,999999)
			request.session['timer'] = str(datetime.datetime.now() + datetime.timedelta(minutes=2))
			print(request.session['timer'])

			# print('-------------------------->',request.session['recivername'],request.session['senderotp'],type(request.session['timer']))
			print(request.session['senderotp'],'\n---------->',request.session['recivername'])
			msg = ''' Hi there!
Your OTP for wallet transfer for sending ₹''' + str(request.session['amount']) +''' to ''' + request.session['recivername']+ '''is ''' + str(request.session['senderotp'])+'''.

Thanks!'''
			EmailMessage('AVPL - OTP for Wallet transfer', msg, to=[request.user.email]).send()
			print(request.user.email)
			messages.success(request, 'OTP sent successfully.')
			return render(request,'vendor_app/otpverify.html')
		return render(request,'vendor_app/customerwallettransfer.html',context=context)
	else :
		messages.error(request,'Payments Mode off')
		return render(request,'vendor_app/customerwallettransfer.html',context=context)




login_required('/')
@transaction.atomic
def transfer_amount_vendor(request):
	if request.method == 'POST':
		senderotp = int(request.POST.get('otp1') )
		print(senderotp)
		# reciverotp = int(request.POST.get('otp2') )
		# print(datetime.datetime.strptime(request.session['timer'], '%Y-%m-%d %H:%M:%S.%f'))

		# if datetime.datetime.now() < datetime.datetime.strptime(request.session['timer'], '%Y-%m-%d %H:%M:%S.%f') :
		
			# if senderotp == request.session['senderotp'] and reciverotp == request.session['reciverotp']:
		if senderotp == request.session['senderotp']:
			print('hjhjjjjjjjjjjjj')
			if Wallet.objects.get(user=request.user).current_balance >= request.session['amount']:
				print('LLLLLLLLLLLLLLLLLLL')
				make_wallet_transaction(user = request.user, amount = request.session['amount'], trans_type = 'DEBIT')
				make_wallet_transaction(user = User.objects.get(username = request.session['recivername']), 
					amount = request.session['amount'], trans_type = 'CREDIT')
				print(request.session['recivername'])
				transfer_into_another_account(usr = request.user, sender = request.user.username,
					reciver = request.session['recivername'],amount = request.session['amount'])
				print('done')
				messages.success(request,'Successfully Transfered')
				return redirect('balanacetransfer')


			else :
				messages.error(request,'Not having sufficient balance')
				return redirect('balanacetransfer')

		else :
			messages.error(request,'OTP is not Correct')
			return redirect('balanacetransfer')
		# else:
		# 	messages.error(request,'Timeout')
		# 	return redirect('balanacetransfer')
	return redirect('balanacetransfer')
	# return render(request,'user_app/otpverify.html')









