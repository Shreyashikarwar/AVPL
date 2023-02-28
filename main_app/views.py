from django.core.paginator import *
from django.shortcuts import render, redirect
from django.http import JsonResponse, response
from django.core.mail import EmailMessage
from django.contrib import messages
from django.http import HttpResponse
from main_app.models import *
from vendor_app.models import *
from admin_app.models import *
from user_app.models import *
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import geocoder
import googlemaps
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import geopy.distance
import uuid
import datetime
from django.contrib.auth import authenticate,login,logout
from main_app.utils import *
from main_app.mlm_utils import *
from user_app.utils import *
from django.utils import timezone
from main_app.razor import *
from admin_app.utils import *
from math import sin, cos, sqrt, atan2, radians

def test(request):
	return render(request, 'test.html', {})

def show(request):
	#User.objects.filter(email='aryankul97@gmail.com').delete()
	User.objects.filter(email='anmolmasih7@gmail.com').delete()
	return HttpResponse('Done')

def show_parent(request):
	node = UserData.objects.get(user = request.user)
	parents = fetch_parent_nodes(node.user,[])
	return HttpResponse(parents)

def contact(request):
	dic = get_dic(request)
	return render(request, 'usertemplate/contectus.html', dic)

def about(request):
	dic = get_dic(request)
	return render(request, 'main_app/about.html', dic)

def faq(request):
	dic = get_dic(request)
	return render(request, 'main_app/faq.html', dic)

@csrf_exempt
def get_location(request):
	lat = request.GET.get('lat')
	lng = request.GET.get('lng')
	request.session['lat'] = lat
	request.session['lng'] = lng
	return HttpResponse('Success')


def search_result(request):
	key = request.GET.get('key')
	page = request.GET.get('page')
	category = request.GET.get('category')
	brand = request.GET.get('brand')
	min_price = request.GET.get('min_price')
	max_price = request.GET.get('max_price')
	in_stock = request.GET.get('in_stock')
	
	results = getresult(key	, category, brand, min_price, max_price)
	dic = {'results':results}
	return render(request, 'main_app/search.html', dic)

def search_result2(request):
	d = datetime.datetime.now()
	latest_product = []
	for latest in ProductImages.objects.all():
		if latest.product.created_at.strftime("%m") == d.strftime("%m"):
			latest_product.append(latest)

	brand_list = Brand.objects.all()
	if request.method == 'POST':
		min_price = request.POST.get('min_price')
		max_price = request.POST.get('max_price')
		in_stock = request.POST.get('in_stock')
		rate = request.POST.get('rate')
		print(rate)
		brand = request.GET.get('brand')
		key = request.GET.get('key')
		category = request.GET.get('category')
		if key == '':
			results = []
			if min_price and max_price and in_stock==True and rate:
				for product in getresult(key, category, brand, min_price, max_price, in_stock, rate):
					results.append(get_product_thumb(product))
			else:
				for product in getresult(key, category,brand, min_price, max_price, in_stock, rate):
					results.append(get_product_thumb(product))
		else:
			results = []
			if min_price and max_price and in_stock==True:
				for product in getresult(key, category, brand, min_price, max_price, in_stock, rate):
					pv_percent = PointValue.objects.get(category=product.category).percentage
					pv = (product.price/100)*pv_percent
					results.append(get_product_thumb(product))
			elif rate:
				for product in getresult(key, category, brand, min_price, max_price, in_stock, rate):
					pv_percent = PointValue.objects.get(category=product.category).percentage
					pv = (product.price/100)*pv_percent
					results.append(get_product_thumb(product))
			else:
				for product in getresult(key, category,brand, min_price, max_price,in_stock, rate):
					pv_percent = PointValue.objects.get(category=product.category).percentage
					pv = (product.price/100)*pv_percent
					results.append(get_product_thumb(product))
		dic = {'len':len(results)}

		dic.update(get_dic(request))
		data=[]
		page = request.GET.get('page')
		paginator = Paginator(results, 20)
		page = request.GET.get('page')
		try:
			data = paginator.page(page)
		except PageNotAnInteger:
			data = paginator.page(1)
		except EmptyPage:
			data = paginator.page(paginator.num_pages)
		dic.update({'data':data, 'results':results, 'key':key, 'category':category,'paginator':paginator, 'brand':brand_list, 'latest':latest_product })
		return render(request, 'usertemplate/collection.html', dic)
	else:
		key = request.GET.get('key')
		category = request.GET.get('category')
		brand = request.GET.get('brand')
		in_stock = request.POST.get('in_stock')
		if key == '':
			results = []
			for product in getresult(key, category, brand, min_price = '', max_price = '',in_stock = '' , rate=None):
				results.append(get_product_thumb(product))
		else:
			results = []
			for product in getresult(key, category, brand, min_price = '', max_price = '',in_stock = '', rate=None):
				pv_percent = PointValue.objects.get(category=product.category).percentage
				pv = (product.price/100)*pv_percent
				results.append(get_product_thumb(product))
		dic = {'len':len(results)}
		dic.update(get_dic(request))
		data=[]
		
		paginator = Paginator(results, 20)
		page = request.GET.get('page')
		try:
			data = paginator.page(page)
		except PageNotAnInteger:
			data = paginator.page(1)
		except EmptyPage:
			data = paginator.page(paginator.num_pages)
		dic.update({'data':data, 'results':results, 'key':key, 'category':category, 'paginator':paginator, 'brand':brand_list, 'latest':latest_product })
		return render(request, 'usertemplate/collection.html', dic)

def home(request):
	if request.user.is_authenticated:
		if request.user.is_superuser:
			return redirect('/admins/dashboard')
		elif request.user.role.level.level == 'Vendor':
			return redirect('/vendor/')
		elif request.user.role.level.level == 'Admin':
			return redirect('/admins/dashboard')
	t = request.GET.get('t')
	request.session['t']=t
	
	if t == 'a':
		user = get_user_from_key(request.GET.get('u'))
		request.session['parent'] = user.id
		request.session['parent_type'] = 'Admin'
		dic = {'name':'Admin'}
		dic.update(get_dic(request))
		return render(request, 'main_app/user-register.html', dic)
	elif t == 'u':
		user = get_user_from_key(request.GET.get('u'))
		request.session['parent'] = user.id
		request.session['parent_type'] = 'User'
		dic = {'name':user.usr.first_name+' '+user.usr.last_name}
		dic.update(get_dic(request))
		return render(request, 'main_app/user-register.html', dic)
	elif t == 'v':
		user = get_user_from_key(request.GET.get('u'))
		request.session['refered_by'] = user.id
		dic = {'name':user.usr.first_name+' '+user.usr.last_name}
		dic.update(get_dic(request))
		return render(request, 'main_app/register.html', dic)
	else:
		request.session['lat'] = None
		request.session['lng'] = None
		request.session['cat'] = None
		l1 = []
		d = datetime.datetime.now()
		latest_product = []
		for latest in ProductImages.objects.all():
			if latest.product.created_at.strftime("%m") == d.strftime("%m"):
				latest_product.append(latest)
		for x in ProductCategory.objects.all():
			l1.append(x)
		for x in l1:
			if Product.objects.filter(category__name=x.name):
				prod1 = Product.objects.filter(category__name=x.name)
		eeprod = ProductImages.objects.filter(product__category__name='Electric & Electronics')
		hcprod = ProductImages.objects.filter(product__category__name="Heath care")
		# for i in ProductCategory.objects.all():
		# 	for j in Product.objects.filter(category__name=i.name).values():
		# 		l1.append({i:j})
		product = Product.objects.all()
		print(product)
		# pv_percent = PointValue.objects.get(category=product.category).percentage
		# pv = (product.price/100)*pv_percent
		bestseller = StoreImages.objects.filter(store__best_seller = True)
		featured = ProductImages.objects.filter(product__featured = True)
		offer = ProductImages.objects.filter(product__offer = True)
		special_offer = ProductImages.objects.filter(product__special_offer = True)
		footer_banner = HomeFooterBanner.objects.all()
		categories = ProductCategory.objects.all()
		if request.session.get('store_ids'):
			store_objs=Store.objects.get(vendor__id__in=request.session.get('store_ids'))
			store_id = store_objs.id
			store_img = StoreImages.objects.get(store__vendor__id__in=request.session.get('store_ids'))
			# del request.session.get('store_ids')
			img_list = []
			dic = get_dic(request)
			for i in product:
				x=ProductImages.objects.filter(product=i)
				img_list.append(x)
			dic.update({'image':img_list})
			dic.update({'banners':HomeBanner.objects.all(), 'footer_banner':footer_banner,  'bestseller':bestseller, 'store':store_objs, 'store_img':store_img,
				'offer':offer,'featured':featured, 'special_offer':special_offer, 'categories':categories, 'l1':l1,'product':product,
				'eeprod':eeprod, 'hcprod':hcprod, 'latest':latest_product,})
			# dic.update({'banners':HomeBanner.objects.all(), 'product':ProductRating.objects.all(), 'bestseller':bestseller, 'img':ProductImages.objects.all() , 'stores':fetch_vendors(request.session['lat'], 
			# 		request.session['lng']),'st':fetch_vendors_catby(request.session['cat'],request.session['lat'], request.session['lng']),
			# 		'store':store_objs, 'store_img':store_img})
			return render(request,'usertemplate/index.html',dic)
		else:
			dic = get_dic(request)
			img_list = []
			for i in product:
				x=ProductImages.objects.filter(product=i)
				img_list.append(x)
			dic.update({'image':img_list})
			dic.update({'banners':HomeBanner.objects.all(), 'footer_banner':footer_banner,'bestseller':bestseller,'offer':offer,'featured':featured, 'special_offer':special_offer
				, 'categories':categories, 'l1':l1, 'eeprod':eeprod, 'hcprod':hcprod , 'product':product,'latest':latest_product,

				})
			print(dic)
			# dic.update({'banners':HomeBanner.objects.all(), 'product':ProductRating.objects.all(),'img':ProductImages.objects.all() ,'bestseller':bestseller, 'stores':fetch_vendors(request.session['lat'], 
			# 		request.session['lng']),'st':fetch_vendors_catby(request.session['cat'],request.session['lat'], request.session['lng'])})
			return render(request,'usertemplate/index.html',dic)
		return render(request,'usertemplate/index.html',dic)



def store_page(request):
	store = Store.objects.get(id=request.GET.get('22'))
	products = []
	for x in Product.objects.filter(store=store)[0:50]:
		products.append(get_product_thumb(x))
	dic = {
			'store':store,
			'distance':get_store_distance(request.session['lat'], request.session['lng'], store.vendor.latitude, store.vendor.longitude),
			'store_categories':get_store_categories(store, request.session['lat'], request.session['lng']),
			'products':reversed(products)
	}
	
	dic.update(get_dic(request))
	print(dic)
	return render(request, 'main_app/storepage.html', dic)

def store_details(request, id):
	store = Store.objects.get(id=id)
	all_store = StoreImages.objects.all()
	store_img = StoreImages.objects.get(store__id =id)
	product = Product.objects.filter(store__id=id).values()
	product_num = Product.objects.filter(store__id=id).count()
	image_data = []
	for data in product:
		product_img = ProductImages.objects.values().filter(product__id = data['id'])[0]['image']
		image_data.append({data['id']:product_img})
	dic = get_dic(request)
	dic.update({
			'store':store,
			'store_img':store_img,
			'product':product,
			'image_data':image_data,
			'all_store':all_store,
			'product_num':product_num,
			# 'distance':get_store_distance(home_address)

	})
	return render(request, 'usertemplate/store-details.html', dic)

def home_store_categories(request):
	cat_id = request.GET.get('c')
	category = ProductCategory.objects.get(id = cat_id)
	results = fetch_vendors_catby(category, request.session['lat'], request.session['lng'])
	dic = get_dic(request)
	dic.update({
		'category':category,
		'subcategory':ProductSubCategory.objects.filter(category=category),
		'id':request.GET.get('c')
	})
	data=[]
	page = request.GET.get('page')
	paginator = Paginator(list(results), 50)
	try:
		data = paginator.page(page)
	except PageNotAnInteger:
		data = paginator.page(1)
	except EmptyPage:
		data = paginator.page(paginator.num_pages)
	dic.update({'data':data, 'len':len(results)})
	return render(request, 'main_app/storecategories.html', dic)

def home_categories(request):
	sort = request.GET.get('sort')
	category = ProductCategory.objects.get(id=request.GET.get('c'))
	products = getproduct_bylocation(request.session['lat'], request.session['lng'])
	results = []
	
	for product in products:
		if product.category == category:
			results.append(get_product_thumb(product))
	dic = get_dic(request)
	dic.update({
		'category':category,
		'brands':Brand.objects.filter(category=category),
		'variants':get_variants(results),
		'selected_brands':[],
		'selected_variants':[],
		'subcategory':ProductSubCategory.objects.filter(category=category),
		'id':request.GET.get('c')
	})
	
	results = sort_products(results, int(sort))
	
	if request.GET.get('store') != None and request.GET.get('store') != '':
		dic.update({'store':Store.objects.get(id=request.GET.get('store'))})
		filter_product_by_store(Store.objects.get(id=request.GET.get('store')), results)

	try:
		if len(request.session['brands']) != 0:
			selected_brands = []
			for x in request.session['brands']:
				selected_brands.append(int(x))
			dic.update({'selected_brands':selected_brands})
			results = brand_filter(request.session['brands'], results)
	except:
		pass

	try:
		selected_variants = []
		for x in request.session['variants']:
			selected_variants.append(int(x))
		dic.update({'selected_variants':selected_variants})
		results = variant_filter(request.session['variants'], results)
	except:
		pass
	data=[]
	page = request.GET.get('page')
	paginator = Paginator(list(results), 50)
	try:
		data = paginator.page(page)
	except PageNotAnInteger:
		data = paginator.page(1)
	except EmptyPage:
		data = paginator.page(paginator.num_pages)
	dic.update({'data':data, 'sort':sort, 'len':len(results), 'store':Store.objects.get(id=request.GET.get('store'))})
	return render(request, 'main_app/categories.html', dic)

def home_store_subcategories(request):
	subcat_id = request.GET.get('c')
	subcategory = ProductSubCategory.objects.get(id = subcat_id)
	results = fetch_vendors_subcatby(subcategory, request.session['lat'], request.session['lng'])
	dic = get_dic(request)
	dic.update({
		'category':subcategory,
		'subcategory':ProductSubSubCategory.objects.filter(subcategory=subcategory),
	})
	data=[]
	page = request.GET.get('page')
	paginator = Paginator(list(results), 50)
	try:
		data = paginator.page(page)
	except PageNotAnInteger:
		data = paginator.page(1)
	except EmptyPage:
		data = paginator.page(paginator.num_pages)
	dic.update({'data':data, 'len':len(results)})
	return render(request, 'main_app/storesubcategories.html', dic)

def home_subcategories(request):
	sort = request.GET.get('sort')
	subcategory = ProductSubCategory.objects.get(id=request.GET.get('c'))
	products = getproduct_bylocation(request.session['lat'], request.session['lng'])
	results = []
	for product in products:
		if product.subcategory == subcategory:
			results.append(get_product_thumb(product))
	dic = get_dic(request)
	dic.update({
		'category':subcategory,
		'subcategory':ProductSubSubCategory.objects.filter(subcategory=subcategory),
		'brands':Brand.objects.filter(category=subcategory.category),
		'variants':get_variants(results),
		'selected_brands':[],
		'selected_variants':[]
	})
	
	results = sort_products(results, int(sort))
	
	if request.GET.get('store') != None and request.GET.get('store') != '':
		dic.update({'store':Store.objects.get(id=request.GET.get('store'))})
		filter_product_by_store(Store.objects.get(id=request.GET.get('store')), results)

	try:
		if len(request.session['brands']) != 0:
			selected_brands = []
			for x in request.session['brands']:
				selected_brands.append(int(x))
			dic.update({'selected_brands':selected_brands})
			results = brand_filter(request.session['brands'], results)
	except:
		pass

	try:
		selected_variants = []
		for x in request.session['variants']:
			selected_variants.append(int(x))
		dic.update({'selected_variants':selected_variants})
		results = variant_filter(request.session['variants'], results)
	except:
		pass

	data=[]
	page = request.GET.get('page')
	paginator = Paginator(list(results), 50)
	try:
		data = paginator.page(page)
	except PageNotAnInteger:
		data = paginator.page(1)
	except EmptyPage:
		data = paginator.page(paginator.num_pages)
	dic.update({'data':data, 'sort':sort, 'len':len(results)})
	return render(request, 'main_app/subcategories.html', dic)

def home_store_subsubcategories(request):
	subcat_id = request.GET.get('c')
	subsubcategory = ProductSubSubCategory.objects.get(id = subcat_id)
	results = fetch_vendors_subsubcatby(subsubcategory, request.session['lat'], request.session['lng'])
	dic = get_dic(request)
	dic.update({
		'category':subsubcategory,
		'subcategory':ProductSubSubCategory.objects.filter(subcategory=subsubcategory.subcategory),
	})
	data=[]
	page = request.GET.get('page')
	paginator = Paginator(list(results), 50)
	try:
		data = paginator.page(page)
	except PageNotAnInteger:
		data = paginator.page(1)
	except EmptyPage:
		data = paginator.page(paginator.num_pages)
	dic.update({'data':data, 'len':len(results)})
	return render(request, 'main_app/storesubsubcategories.html', dic)

def home_subsubcategories(request):
	sort = request.GET.get('sort')
	subsubcategory = ProductSubSubCategory.objects.get(id=request.GET.get('c'))
	products = getproduct_bylocation(request.session['lat'], request.session['lng'])
	results = []
	for product in products:
		if product.subsubcategory == subsubcategory:
			results.append(get_product_thumb(product))
	dic = get_dic(request)
	dic.update({
		'category':subsubcategory,
		'subcategory':ProductSubSubCategory.objects.filter(subcategory=subsubcategory.subcategory),
		'brands':Brand.objects.filter(category=subsubcategory.subcategory.category),
		'variants':get_variants(results),
		'selected_brands':[],
		'selected_variants':[]
	})
	
	results = sort_products(results, int(sort))
	
	if request.GET.get('store') != None and request.GET.get('store') != '':
		dic.update({'store':Store.objects.get(id=request.GET.get('store'))})
		filter_product_by_store(Store.objects.get(id=request.GET.get('store')), results)

	try:
		if len(request.session['brands']) != 0:
			selected_brands = []
			for x in request.session['brands']:
				selected_brands.append(int(x))
			dic.update({'selected_brands':selected_brands})
			results = brand_filter(request.session['brands'], results)
	except:
		pass

	try:
		selected_variants = []
		for x in request.session['variants']:
			selected_variants.append(int(x))
		dic.update({'selected_variants':selected_variants})
		results = variant_filter(request.session['variants'], results)
	except:
		pass

	data=[]
	page = request.GET.get('page')
	paginator = Paginator(list(results), 50)
	try:
		data = paginator.page(page)
	except PageNotAnInteger:
		data = paginator.page(1)
	except EmptyPage:
		data = paginator.page(paginator.num_pages)
	dic.update({'data':data, 'sort':sort, 'len':len(results)})
	return render(request, 'main_app/subsubcategories.html', dic)

@csrf_exempt
def apply_filters(request):
	request.session['variants'] = request.POST.getlist('variant_values[]')
	request.session['brands'] = request.POST.getlist('brands[]')
	return JsonResponse({'response':'Success'})

def remove_filters(request):
	del request.session['variants']
	del request.session['brands']
	return JsonResponse({'response':'Success'})

#PV Calculate here
def product_page(request):
	product = Product.objects.get(id=request.GET.get('p'))
	pv_percent = PointValue.objects.get(category=product.category).percentage
	pv = (product.price/100)*pv_percent
	dic = {
		'product':product,
		'images':ProductImages.objects.filter(product=product),
		'variants':get_product_variants(product),
		'pv':pv
	}
	ratings = ProductRating.objects.filter(product=product)
	total = 0.0
	for x in ratings:
		total = total + x.rating
	rating = 0.0
	if len(ratings) <= 0:
		rating = 0.0
	else:
		rating = (total/len(ratings))	
	dic.update({'rating':round(rating, 1), 'rating_len':len(ratings), 'ratings':ratings})
	dic.update(get_cart_len(request))
	print(dic)
	return render(request, 'usertemplate/collection.html', dic)


def product_detail(request):
	product = Product.objects.get(id=request.GET.get('p'))
	pv_percent = PointValue.objects.get(category=product.category).percentage
	pv = (product.price/100)*pv_percent
	sub_cat_data = Product.objects.values().filter(subcategory_id = product.subcategory)
	for i in sub_cat_data:
		for x in ProductImages.objects.filter(product__id=i['id']).values():
			i['image'] = x['image']
	dic = {
		'product':product,
		'sub_cat_data':sub_cat_data,
		# 'sub_cat_data_images':ProductImages.objects.filter(product=sub_cat_data)[0],
		'images':ProductImages.objects.filter(product=product),
		'categories':ProductCategory.objects.all(),
		'variants':get_product_variants(product),
		'pv':pv
	}
	ratings = ProductRating.objects.filter(product=product)
	total = 0.0
	rating5 = []
	rating4 = []
	rating3 = []
	rating2 = []
	rating1 = []
	norating = []
	for x in ratings:
		print(x.rating)
		total = total + x.rating
		if x.rating == 5.0:
			rating5.append(x.rating)
			dic.update({'rating5':len(rating5) })
		elif x.rating == 4.0:
			rating4.append(x.rating)
			dic.update({'rating4':len(rating4) })
		elif x.rating == 3.0:
			rating4.append(x.rating)
			print(len(rating4))
			dic.update({'rating3':len(rating3)})
		elif x.rating == 2.0:
			rating2.append(x.rating)
			dic.update({'rating2':len(rating2)})
		elif x.rating == 1.0:
			rating1.append(x.rating)
			dic.update({'rating1':len(rating1)})
		else:
			norating.append('0')
			dic.update({'norating':len(rating1)})
	print(dic)
	
	rating = 0.0
	if len(ratings) <= 0:
		rating = 0.0
	else:
		rating = (total/len(ratings))	
	dic.update({'rating':round(rating, 1), 'rating_len':len(ratings), 'ratings':ratings})
	dic.update(get_cart_len(request))
	dic.update(get_wishlist_len(request))
	return render(request, 'usertemplate/product-detail.html', dic)


def product_filter_range(request):
	if request.method == 'POST':
		min_price = request.POST.get('min_price')
		max_price = request.POST.get('max_price')
		prod =  Product.objects.filter(price__range=[min_price ,max_price ])
		print(prod)
		return render(request, 'usertemplate/collection.html', {'prod':prod})

def send_otp(request, utype, user):
	if utype == 'Vendor':
		otp = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(datetime.datetime.today())+user.email+user.vendor.phone+user.vendor.first_name+user.vendor.last_name).int)
		otp = otp[0:6]
		request.session['otp'] = otp
		request.session['utype'] = 'Vendor'
		request.session['vendor'] = Vendor.objects.get(user=user).id
		sub = 'Welcome to AVPL'
		msg = '''Hi there!
You have successfully registered as vendor at AVPL. Please confirm your account with below OTP,
'''+str(otp)
		EmailMessage(sub,msg,to=[user.email]).send()
		messages.success(request,'Please Verify Your Account.')
		return redirect('/otp')
	elif utype == 'User':
		otp = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(datetime.datetime.today())+user.email+user.usr.phone+user.usr.first_name+user.usr.last_name).int)
		otp = otp[0:6]
		request.session['otp'] = otp
		request.session['utype'] = 'User'
		request.session['user'] = user.id
		sub = 'Welcome to AVPL'
		#print(user)
		msg = "Hi "+str(user.usr.first_name)+ '''
You have successfully registered as user at AVPL. Please confirm your account with below OTP,
'''+str(otp)
		EmailMessage(sub,msg,to=[user.email]).send()
		messages.success(request,'Please verify your account.')
		return redirect('/otp')


def resend_otp(request):
	utype = request.session['utype']
	if utype == 'Vendor':
		return send_otp(request, utype, Vendor.objects.get(id=request.session['vendor']).user)
	elif utype == 'User':
		print(request.session['user'])
		return send_otp(request, utype, User.objects.get(id=request.session['user']))


@csrf_exempt
def login_view(request):
	if request.method == 'POST':
		email = request.POST.get('email')
		password = request.POST.get('password')
		if User.objects.filter(email=email).exists():
			chk_user = User.objects.get(email=email)
			user = authenticate(request, username=chk_user.username , password=password)
			if user is not None:
				login(request,user)
				if request.user.role.level.level == 'Vendor':
					if Vendor.objects.filter(user = chk_user, verified = False).exists():
						logout(request)
						return send_otp(request, 'Vendor', chk_user)
					return redirect('/vendor/')
				elif check_user_authentication(request, 'User'):
					return redirect('/')
				else:
					logout(request)
					return response(data={'msg':'Unauthorized User','response_code':201},status=status.HTTP_201_CREATED)
			else:
				messages.info(request,'Incorrect Password')
				return redirect('/login/')
		else:
			messages.info(request,'Incorrect Email')
			return redirect('/login/')
	else:
		if request.user.is_authenticated:
			if request.user.role.level.level == 'Vendor':
				return redirect('/vendor/')
			elif check_user_authentication(request, 'User'):
				return redirect('/')
			elif request.user.role.level.level == 'Admin':
				return redirect('/admins/')
		else:
			return render(request,'main_app/login.html',{})

def register(request):
	return render(request,'main_app/register.html',{})

def otp(request):
	return render(request, 'main_app/otp.html', {})

@csrf_exempt
def create_vendor(request):
	# t = request.GET('t')
	# print(t)
	# u =request.GET.get('u')
	# print(u)
	# #usr = get_user_from_key('e2780c6f-7faf-59be-8dc1-473100595c12')
	# print("printing usr")
	# print(u)
	if request.method == 'POST':
		type_ = request.POST.get('type')
		if type_ == 'Vendor':
			email = request.POST.get('email')
			password = request.POST.get('password')
			if User.objects.filter(email=email).exists():
				messages.info(request,'User Already Exists')
				return redirect('/register')
			else:
				User.objects.create_user(email,email,password)
				user = User.objects.get(email=email)
				Role(user=user, level=Levels.objects.get(level='Vendor')).save()
				first_name = request.POST.get('first_name')
				last_name = request.POST.get('last_name')
				gender = request.POST.get('gender')
				phone = request.POST.get('phone')
				zipcode = request.POST.get('zipcode')
				address = request.POST.get('adrs')
				gmaps = googlemaps.Client(key='AIzaSyBqBF76cMbvE_LREvm1S43LzZGxTsRQ0wA')				
				if address:
					add_lat_long = gmaps.geocode(address)
					lat = add_lat_long[0]['geometry']['location']['lat']
					lng = add_lat_long[0]['geometry']['location']['lng']
					# lat = 28.7983
					# lng = 79.0220
					Vendor.objects.create(
						user = user,
						first_name = first_name,
						last_name = last_name,
						phone = phone,
						address = address,
						zipcode = zipcode,
						latitude = lat,
						longitude = lng,
						gender = gender
					)
				t = request.session['t']
				print("printing t here")
				print(t)
				if t == "v":
					print("printing user from key")
					usr=User.objects.get(id= request.session['refered_by'])
					print(usr)
					UserVendorRelation.objects.create(user =usr, vendor=Vendor.objects.get(user=user))
				return send_otp(request, 'Vendor', user)

@csrf_exempt
def verify_account(request):
	if request.method == 'POST':
		otp = request.POST.get('otp')
		otp_2 = request.session['otp']
		try:
			if request.session['utype'] == 'Vendor':
				vendor = request.session['vendor']
				if otp == otp_2:
					Vendor.objects.filter(id=vendor).update(verified=True)
					#something here
					return redirect('/login')
				else:
					messages.info(request, 'Incorrect OTP Entered')
					return redirect('/otp')
			elif request.session['utype'] == 'User':
				user = request.session['user']
				if otp == otp_2:
					UserData.objects.filter(user=User.objects.get(id=user)).update(status=True)
					request.session['child'] = user
					add_to_mlm(request)
					return redirect('/login')
				else:
					messages.info(request, 'Incorrect OTP Entered')
					return redirect('/otp')
		except KeyError:
			return HttpResponse('Error')

def logout_view(request):
	logout(request)
	request.session['lat'] = None
	request.session['lng'] = None
	return redirect('/')

@csrf_exempt
def checkout_1(request):
	if check_user_authentication(request, 'User'):
		if request.method == 'GET':
			request.session['cart_id'] = request.GET.get('cart')
			dic = {'addresses':Address.objects.filter(user=request.user), 'address_len':len(Address.objects.filter(user=request.user))}
			dic.update(get_cart_items(request))
			dic.update(get_dic(request))
			return render(request, 'usertemplate/select-address.html', dic)
		else:
			return HttpResponse('  500 : Request Method Not Allowed')
	else:
		return HttpResponse('Error 500 : Unauthorized User')

@csrf_exempt
def checkout_2(request):
	if check_user_authentication(request, 'User'):
		if request.method == 'POST':
			request.session['address_id'] = request.POST.get('address_id')
			request.session['plan_type'] = request.POST.get('plan_type')
			print(request.session['plan_type'])
			dic = {'address':Address.objects.get(id=request.POST.get('address_id'))}
			dic.update(get_cart_items(request))
			dic.update(get_dic(request))
			return render(request, 'usertemplate/payment.html', dic)
		else:
			return HttpResponse('Error 500 : Request Method Not Allowed')
	else:
		return HttpResponse('Error 500 : Unauthorized User')

@csrf_exempt
def place_order(request):
	if check_user_authentication(request, 'User'):
		Orders.objects.all()
		address = Address.objects.get(id=request.session['address_id'])
		cart = Cart.objects.get(id=request.session['cart_id'])
		payment_type = request.POST.get('payment_type')
		dic = {}
		# request.session['plan_type'] = request.POST.get('plan')
		plan_type = request.session.get('plan_type')
		print(plan_type, cart, address, request.user, 'LLLLLLLLLLLLLLLL')
		if payment_type == 'cod':
			create_cod_order(cart, address, request.user, plan_type)
			print(create_cod_order,'KKKKKKKKKKKKKKKKKK')
			sub = 'AVPL - Order Placed'
			msg = ''' Hi there!
Your order has been placed successfully, Kindly check the My Order section in your dashboard.

Thanks!'''
			EmailMessage(sub, msg, to=[request.user.email]).send()
			notification(request.user, 'Order Placed Successfully.')
		elif payment_type == 'online':
			dic = create_online_order(cart, address, request.user)
			# dic = create_online_order(cart, address, request.user, plan_type)
			print('hhhhhhhhhhhhhhhhhhh',dic)
			# razorpaytransacti   on = dic['id']
			# dic = save_order(cart, address, request.user, razorpaytransaction)
		return JsonResponse({'response':'Success', 'pay_type':payment_type, 'data':dic})
	else:
		return HttpResponse('Error 500 : Unauthorized User')

@csrf_exempt
def capture_online_payment(request):
	if request.method == 'POST':
		payment_id = request.POST.get('razorpay_payment_id')
		print(payment_id)
		order_id = request.POST.get('razorpay_order_id')
		signature = request.POST.get('razorpay_signature')
		order = RazorpayOrder.objects.get(razorpay_order_id=order_id)
		print(payment_id,signature,order_id)
		razorpaytransaction = RazorpayTransaction.objects.create(payment_id=payment_id, order_id=order_id, signature=signature)
		save_order(order.cart, order.address, order.user, razorpaytransaction)
		sub = 'AVPL - Order Placed'
		msg = '''Hi there!
We have received your payment and your order has been placed successfully, Kindly check the My Order section in your dashboard.

Thanks!'''
		EmailMessage(sub, msg, to=[request.user.email]).send()
		notification(request.user, 'Order Placed Successfully.')
		return render(request, 'main_app/order-success.html')
	else:
		return HttpResponse('Failed')

@csrf_exempt
def forgotpassword(request):
	return render(request,'main_app/forgot-password.html')

def forgot_otp(request):
	return render(request,'main_app/forgot-otp.html')

@csrf_exempt
def check_email(request):
	if request.method == 'POST':
		email = request.POST.get('myemail')
		if not User.objects.filter(email=email).exists():
			messages.success(request, 'email does not exist with this email id')
			return redirect('/forgot')

		else:
			user = User.objects.get(email=email)
			otp = str(uuid.uuid5(uuid.NAMESPACE_DNS,str(datetime.datetime.today()) + email ).int)
			otp = otp[0:6]
			request.session['otp1'] = otp
			request.session['emailid'] = User.objects.get(email=email).id
			sub = 'AVPL - Password Change Request'
			msg = ''' Hi there!
We received a password change request, please verify your email with below OTP.
'''+str(otp)
			EmailMessage(sub, msg, to=[email]).send()
			messages.success(request, 'An OTP has been sent to your email.')
			return redirect('/forgot-otp')
	return HttpResponse('bossss')

@csrf_exempt
def verify_forgot(request):
	if request.method == 'POST':
		otp = request.POST.get('otp1')
		otp_2 = request.session['otp1']
		try:
			if otp == otp_2:
				return redirect('/change-password/')
			else:
				messages.info(request, 'Incorrect OTP Entered')
				return redirect('/forgot-otp')
		except KeyError:
			return HttpResponse('Error')

@csrf_exempt
def change_password(request):
	if request.method == 'POST':
		setpwd = request.POST.get('set1')
		userid = request.session['emailid']
		user = User.objects.get(id=userid)
		user.set_password(setpwd)
		user.save()
		notification(user, 'Password Changed Successfully.')
		messages.success(request, 'Password Changed Successfully !!!!')
		return redirect('/login/')
	else:
		return render(request, 'main_app/change-password.html')

def mark_notification_read(request):
	Notification.objects.filter(user=request.user).update(read=True)
	return JsonResponse({'response':'Success'})

def userpv(request):
	dic = get_user_indecater(request.user)
	return JsonResponse(dic)

def category_wise_store(request):
	#Notification.objects.filter(user=request.user).update(read=True)
	cat_id = request.GET.get('cat_id')
	category = ProductCategory.objects.get(id = cat_id)
	print(fetch_vendors_catby(cat_id,request.session['lat'], request.session['lng']))
	dic ={
		'store_cat_wise' : fetch_vendors_catby(cat_id,request.session['lat'], request.session['lng'])
	}
	return render(request, 'main_app/category_wise_store.html',dic)

@csrf_exempt
def contact_us_save(request):
	if request.method == 'POST':
		name = request.POST.get('name')
		email = request.POST.get('email')
		mobile = request.POST.get('mobile')
		message = request.POST.get('message')
		Query.objects.create(
			anonymous = True,
			name = name,
			email = email,
			mobile = mobile,
			subject = 'Contact Us Form Submission',
			message = message
		)
		messages.success(request, 'We got your query, we will contact you soon!')
		return redirect('/contact/')
	return redirect('/')


def termsancondition(request):
	dic = {
			'categories':ProductCategory.objects.all(),
			'data':termsandcondition.objects.all(),
			'cart_len':get_cart_len(request),
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
	dic.update(get_cart_len(request))
	dic.update(get_wishlist_len(request))
	return render(request, 'usertemplate/term_an_condition.html', dic)

def contactus(request):
	dic = {
			'data':termsandcondition.objects.all(),
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
	dic.update(get_cart_len(request))
	dic.update(get_wishlist_len(request))
	print(dic)
	return render(request, 'usertemplate/contectus.html')

def privacy_policy(request):
	dic = {
			'data':privacypolicy.objects.all(),
			'categories':ProductCategory.objects.all(),
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
	dic.update(get_cart_len(request))
	dic.update(get_wishlist_len(request))
	return render(request, 'usertemplate/privacy_policy.html',dic)

def about(request):
	dic = {

			'data':AboutUs.objects.all(),
			'categories':ProductCategory.objects.all(),
			# 'notification':get_notifications(request.user),
			# 'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
	dic.update(get_cart_len(request))
	dic.update(get_wishlist_len(request))
	data = AboutUs.objects.all()
	return render(request, 'usertemplate/about_us.html',dic)


def blog(request):
	dic = {
			'data':Blog.objects.all(),
			'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
	dic.update(get_cart_len(request))
	dic.update(get_wishlist_len(request))
	return render(request, 'usertemplate/blog.html',dic)

def gallery_data(request):
	print('JKKKKKK')
	dic = {
			'data':Gallery.objects.all(),
			'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
	dic.update(get_cart_len(request))
	dic.update(get_wishlist_len(request))
	return render(request, 'usertemplate/gallery.html',dic)


def find_lat_long(t1,t2):
	R = 6373.0
	lat1 = radians(t1[0])
	lon1 = radians(t1[1])

	lat2 = radians(t2[0])
	lon2 = radians(t2[1])
	x = geopy.distance.geodesic(t1, t2).km
	print(x, 'distance')
	return x

def assign_store(request):
	if request.method=='POST':        
		home_address=request.POST.get('home_address')
		print(home_address)
		lat=request.POST.get('lat',True)
		lng=request.POST.get('lng',True)
		print(lat,lng)
		if home_address or (lat and lng):
			try:
				gmaps = googlemaps.Client(key='AIzaSyBlEb2wyEYcwIj2HjR0ALpVXhj9Oo8zpVc')
				print(gmaps)
				if home_address:
					add_lat_long=gmaps.geocode(home_address)
					user_lat=add_lat_long[0]['geometry']['location']['lat']
					print(user_lat, 'jjjjjjjjjj')
					user_lng=add_lat_long[0]['geometry']['location']['lng']
				else:
					user_lat=float(lat)
					user_lng=float(lng)

				store_address_obj=Vendor.objects.all()
				print(store_address_obj)
				request.session['usr_address']=home_address
				print(home_address)
				l={}
				for i in store_address_obj:
					store_addr=gmaps.geocode(str(i.address) +","+str(i.zipcode))
					store_lat=store_addr[0]['geometry']['location']['lat']
					store_lng=store_addr[0]['geometry']['location']['lng']
					l[i.id]=(store_lat, store_lng)
				small=None
				user_store_id=None
				print('litem==>',l.items())
				store_distance = []
				for i,j in l.items():
					x=find_lat_long((user_lat,user_lng),j)
					store_distance.append({"store_id":i,"store_distance":x})

				print(store_distance,'distance')	
				store_ids = []	
				for d in store_distance:
					if d['store_distance']<=30:
						store_ids.append(d['store_id'])
				request.session['store_ids'] = store_ids
				print(request.session['store_ids'], 'store')
   				# if small<=30:
					
				# 	store_name=Store.objects.get(vendor__id=user_store_id)
				# 	# store_ids.append(user_store_id)
				# 	# request.session['name'] = store_name.name
				# 	# request.session['description'] = store_name.description
				# 	# request.session['closing_day'] = store_name.closing_day
				# 	# request.session['opening_time'] = store_name.opening_time
				# 	# request.session['closing_time'] = store_name.closing_time
				# 	# request.session['distance'] = small
				# 	store_img = StoreImages.objects.get(store__id = store_name.id)
				# 	# logo = str(store_img.logo)
				# 	# request.session['logo'] = logo
				# 	# dic = {
				# 	# 	'store':store_name,
				# 	# 	'store_img':store_img,
				# 	# 	'distance':small
				# 	# }
				messages.warning(request,f'The store near you are...')
				return redirect('/')
					# return render(request, 'main_app/index.html', dic)
				# else:
				# 	try:
				# 		del request.session['store_id']
				# 	except:
				# 		pass
				# 	messages.warning(request,f'There are not any store near you')
				# 	return redirect('/')
			except:
				messages.warning(request,f'please enter valid address.')
				return redirect('/')

		else:
			messages.warning(request,f'please enter valid address ')
			return redirect('/')


def get_store_distance():
	if request.method=='POST':        
		home_address=request.POST.get('home_address')
		print(home_address)
		lat=request.POST.get('lat',True)
		lng=request.POST.get('lng',True)
		print(lat,lng)
		if home_address or (lat and lng):
			try:
				gmaps = googlemaps.Client(key='AIzaSyBlEb2wyEYcwIj2HjR0ALpVXhj9Oo8zpVc')
				print(gmaps)
				if home_address:
					add_lat_long=gmaps.geocode(home_address)
					user_lat=add_lat_long[0]['geometry']['location']['lat']
					print(user_lat, 'jjjjjjjjjj')
					user_lng=add_lat_long[0]['geometry']['location']['lng']
				else:
					user_lat=float(lat)
					user_lng=float(lng)

				store_address_obj=Vendor.objects.all()
				print(store_address_obj)
				request.session['usr_address']=home_address
				print(home_address)
				l={}
				for i in store_address_obj:
					store_addr=gmaps.geocode(str(i.address) +","+str(i.zipcode))
					store_lat=store_addr[0]['geometry']['location']['lat']
					store_lng=store_addr[0]['geometry']['location']['lng']
					l[i.id]=(store_lat, store_lng)
				small=None
				user_store_id=None
				print('litem==>',l.items())
				store_distance = []
				for i,j in l.items():
					x=find_lat_long((user_lat,user_lng),j)
					store_distance.append({"store_id":i,"store_distance":x})
				return store_distance
			except:
				pass
