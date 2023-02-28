from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import status
from .utils import *
from user_app. utils import *
from django.http import HttpResponse
from django.contrib.auth import authenticate,login,logout
from .serializers import *
from django.core.mail import EmailMessage
from .razor import *
import uuid
import datetime
import random
# Models Import 
# from .models import User, OTP,PasswordResetToken,Token
from main_app.models import *
from vendor_app.models import *
from admin_app.models import *
from user_app.models import *
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt   
from math import sin, cos, sqrt, atan2, radians
from geopy.distance import geodesic
import geocoder
import googlemaps
from geopy.geocoders import Nominatim
import geopy.distance

# Serializers Import 
from .serializers import *

# Login API Section  -- -- -

@api_view(['POST'])
@csrf_exempt
def api_login(request, *args):
	email = request.data.get('email')
	password = request.data.get('password')
	
	print(email,password)
	if User.objects.filter(email=email).exists():
		if User.objects.filter(email=email, is_active=True).exists():
			chk_user = User.objects.get(email=email)
			user = authenticate(request, username=chk_user.username , password=password)

			if user is not None:
				# token=Token.objects.get(user=user)
				# print(token)
				# if request.data.get("firebase_token") != "":
				# 	Leads_User_profile.objects.filter(id=user.id).update(firebase_token=request.data.get("firebase_token"))
				return Response(data = {'msg_code':1, 'msg':'Success','response_code':200 ,'data':{'chk_user_name':chk_user.username,'chk_user_first_name':chk_user.first_name,'chk_user_lastname':chk_user.last_name,'chk_user_email':chk_user.email, 'chk_user_id':chk_user.id}}, status=status.HTTP_200_OK)
			else:
				return Response(data = {'msg_code':0, 'msg':'Incorrect Password', 'response_code':201,'data':{}}, status=status.HTTP_201_CREATED)
		else:
			return Response(data = {'msg_code':0, 'msg':'Email Not Verified', 'data':{}}, status=status.HTTP_201_CREATED)
	else:
		return Response(data = {'msg_code':0, 'msg':'Incorrect Email','response_code':201 ,'data':{}}, status=status.HTTP_201_CREATED)


#Main Category API

@api_view(['GET'])
@csrf_exempt
def product_data(request):
	queryset=Product.objects.all()
	serializer=ProductSerializer(queryset,many=True)

	return Response(data={'msg':'Success','data':serializer.data,'response_code':200},status=status.HTTP_200_OK)

#category and sub category
@api_view(['GET'])
@csrf_exempt
def category_detail(request):
	if request.method == 'GET':
		category_id = request.query_params.get('category_id')
		sub_category_id = request.query_params.get('sub_category_id')
		sub_sub_category_id = request.query_params.get('sub_sub_category_id')
		if category_id:
			category_data = ProductSubCategorySerializer(ProductSubCategory.objects.filter(category__id=category_id), many=True)
			if sub_category_id:
				sub_category_data = ProductSubSubCategorySerializer(ProductSubSubCategory.objects.filter(subcategory__id=sub_category_id, subcategory__category__id=category_id), many=True)
				return Response(data={'subsubcategory':sub_category_data.data, 'response_code':200})
			return Response(data={'subcategory':category_data.data, 'response_code':200})
		else:
			category_data = ProductCategorySerializer(ProductCategory.objects.all(), many=True)
			subcategory_data = ProductSubCategorySerializer(ProductSubCategory.objects.all(), many=True)
			subsubcategory_data = ProductSubSubCategorySerializer(ProductSubSubCategory.objects.all(), many=True)
			return Response(data={'category':category_data.data, 'sub_category':subcategory_data.data,'sub_sub_category':subsubcategory_data.data, 'response_code':200})




#product details

@api_view(['GET'])
@csrf_exempt
def product_details(request):
	category_id = request.query_params.get('category_id')
	sub_category_id = request.query_params.get('sub_category_id')
	sub_sub_category_id = request.query_params.get('sub_sub_category_id')
	vendor_id = request.query_params.get('vendor_id')
	search = request.query_params.get('search')
	print(search)
	brand_id = request.query_params.get('brand_id')
	min_price = request.query_params.get('min_price')
	max_price = request.query_params.get('max_price')
	sort_ascend = request.query_params.get('sort_ascend')
	sort_descend = request.query_params.get('sort_descend')
	if request.method == 'GET':
		if category_id and sub_category_id is None and sub_sub_category_id is None:
			print('11111')
			product_img = Product.objects.filter(category__id = category_id).values()
			# product_img_serializer = ProductImagesSerializer(product_img, many=True)
			for data in product_img:
				product=Product.objects.filter(id=data['id']).first()
				product_image = ProductImages.objects.filter(product__category__id = category_id).values().first()
				data['product_img'] = product_image
				product_data=Product.objects.filter(id=data['id']).values().first()
				data['product'] = product_data
				cat = ProductCategory.objects.filter(id=product.category.id).values().first()
				data['cat']=cat
				sub_cat = ProductSubCategory.objects.filter(id=product.subcategory.id).values().first()
				data['subcat']=sub_cat
				
				sub_sub_cat = ProductSubSubCategory.objects.filter(id=product.subsubcategory.id).values().first()
				data['subsubcat'] = sub_sub_cat

                # data['category_image']=Product.objects.get(id=data['product_id']).subcategory.image
			return Response({'msg':'Success', 'data':data, 'response_code':'200'},status=status.HTTP_200_OK)
		# if sub_category_id and category_id and sub_sub_category_id is None:
		# 	print('22222')
		# 	product_img = ProductImages.objects.filter(product__subcategory__id = sub_category_id).values()
		# 	for data in product_img:
		# 		product=Product.objects.filter(id=data['product_id']).first()
		# 		product_image = ProductImages.objects.filter(product__subcategory__id = sub_category_id).values().first()
		# 		data['product_img'] = product_image
		# 		product_data=Product.objects.filter(id=data['product_id']).values().first()
		# 		data['product'] = product_data
		# 		cat = ProductCategory.objects.filter(id=product.category.id).values().first()
		# 		data['cat']=cat
		# 		sub_cat = ProductSubCategory.objects.filter(id=product.subcategory.id).values().first()
		# 		data['subcat']=sub_cat
		# 		sub_sub_cat = ProductSubSubCategory.objects.filter(id=product.subsubcategory.id).values().first()
		# 		data['subsubcat'] = sub_sub_cat
		# 	return Response({'msg':'Success', 'data':product_img, 'response_code':'200'},status=status.HTTP_200_OK)
		if sub_category_id and category_id and sub_sub_category_id is None:
			print('44444')
			product = Product.objects.filter(subcategory__id = sub_category_id,category__id = category_id).values()
			image = []
			product_data = []
			prod_img = []
			for data in product:
				print(data['id'])
				# product=Product.objects.filter(id=data['id']).values()
				product_image = ProductImages.objects.filter(product__id = data['id']).values()
				# print(product_image)
				# for i in product_image:
				# 	product_img = i['image']
				# 	if i['product_id'] == data['id']:
				# 		image.append({data['id']:product_img})
				# 		data['product_img'] = image
				# for x in image:
				# 	for j,k in x.items():
				# 		if j == data['id']:
				# 			prod_img.append(k)
				# data['image'] = prod_img
				data['product_images'] = product_image
				cat = ProductCategory.objects.filter(id=data['category_id']).values()
				data['cat']=cat
				sub_cat = ProductSubCategory.objects.filter(id=data['subcategory_id']).values()
				data['subcat']=sub_cat
				sub_sub_cat = ProductSubSubCategory.objects.filter(id=data['subsubcategory_id']).values().first()
				data['subsubcat'] = sub_sub_cat
				prod_review = ProductRating.objects.filter(product_id=data['id'])
				data['review'] = prod_review
				total = 0.0
				for x in prod_review:
					total = total + x['rating']
				rating = 0.0
				if len(prod_review) <= 0:
					rating = 0.0
				else:
					rating = (total/len(prod_review))
				data['rating_len'] = len(prod_review)
				data['avg_rating'] = rating
				product_data.append(data)
			# print(data['id'])
			return Response({'msg':'Success', 'data':product_data, 'response_code':'200'},status=status.HTTP_200_OK)
		if sub_sub_category_id and sub_category_id and category_id:
			print('333')
			product_img = ProductImages.objects.filter(product__subcategory__id = sub_category_id,product__category__id = category_id,product__subsubcategory__id = sub_sub_category_id).values()
			for data in product_img:
				product=Product.objects.filter(id=data['product_id']).first()
				product_image = ProductImages.objects.filter(product__subcategory__id = sub_category_id,product__category__id = category_id,product__subsubcategory__id = sub_sub_category_id).values().first()
				data['product_img'] = product_image
				product_data=Product.objects.filter(id=data['product_id']).values().first()
				data['product'] = product_data
				cat = ProductCategory.objects.filter(id=product.category.id).values().first()
				data['cat']=cat
				sub_cat = ProductSubCategory.objects.filter(id=product.subcategory.id).values().first()
				data['subcat']=sub_cat
				sub_sub_cat = ProductSubSubCategory.objects.filter(id=product.subsubcategory.id).values().first()
				data['subsubcat'] = sub_sub_cat
			return Response({'msg':'Success', 'data':product_img, 'response_code':'200'},status=status.HTTP_200_OK)		
		if brand_id:
			print('55555')
			product_data = []
			product = Product.objects.filter(brand_id = brand_id).values()
			for data in product:
				# product=Product.objects.filter(id=data['product_id']).first()
				product_image = ProductImages.objects.filter(product__brand__id = data['brand_id']).values().first()
				data['product_img'] = product_image
				# product_data=Product.objects.filter(id=data['id']).values().first()
				# data['product'] = product_data
				cat = ProductCategory.objects.filter(id=data['category_id']).values().first()
				data['cat']=cat
				sub_cat = ProductSubCategory.objects.filter(id=data['subcategory_id']).values().first()
				data['subcat']=sub_cat
				sub_sub_cat = ProductSubSubCategory.objects.filter(id=data['subsubcategory_id']).values().first()
				data['subsubcat'] = sub_sub_cat
				prod_review = ProductRating.objects.filter(product_id=data['id']).values()
				data['review'] = prod_review
				total = 0.0
				for x in prod_review:
					total = total + x['rating']
				rating = 0.0
				if len(prod_review) <= 0:
					rating = 0.0
				else:
					rating = (total/len(prod_review))
				data['rating_len'] = len(prod_review)
				data['avg_rating'] = rating
				product_data.append(data)
			return Response({'msg':'Success', 'data':product_data, 'response_code':'200'},status=status.HTTP_200_OK)
		if search:
			product_data = []
			product = Product.objects.filter(name__icontains = search).values()
			for data in product:
				product_image =  ProductImages.objects.filter(product_id=data['id']).values()
				data['product_img'] = product_image
				prod_review = ProductRating.objects.filter(product_id=data['id']).values()
				data['review'] = prod_review
				total = 0.0
				for x in prod_review:
					total = total + x['rating']
				rating = 0.0
				if len(prod_review) <= 0:
					rating = 0.0
				else:
					rating = (total/len(prod_review))
				data['rating_len'] = len(prod_review)
				data['avg_rating'] = rating
				product_data.append(data)
			product_img_serializer = ProductImagesSerializer(ProductImages.objects.filter(product__name__icontains = search), many=True)
			return Response(data= {'msg':'Success', 'data':product_data, 'response_code':'200'},status=status.HTTP_200_OK)
			# print('88888')
			# product_img = ProductImages.objects.filter(product__name__icontains = search).values()
			# for data in product_img:
			# 	product=Product.objects.filter(id=data['product_id']).first()
			# 	product_image = ProductImages.objects.filter(product__category__id = category_id).values().first()
			# 	data['product_img'] = product_image
			# 	product_data=Product.objects.filter(id=data['product_id']).values().first()
			# 	data['product'] = product_data
			# 	cat = ProductCategory.objects.filter(id=product.category.id).values().first()
			# 	data['cat']=cat
			# 	sub_cat = ProductSubCategory.objects.filter(id=product.subcategory.id).values().first()
			# 	data['subcat']=sub_cat
			# 	sub_sub_cat = ProductSubSubCategory.objects.filter(id=product.subsubcategory.id).values().first()
			# 	data['subsubcat'] = sub_sub_cat
			# return Response({'msg':'Success', 'data':product_img, 'response_code':'200'},status=status.HTTP_200_OK)
		if min_price and max_price:
			print('77777')
			product_data = []
			product = Product.objects.filter(price__range = [min_price ,max_price ]).values()
			for data in product:
				product_image =  ProductImages.objects.filter(product_id=data['id']).values()
				data['product_img'] = product_image
				prod_review = ProductRating.objects.filter(product_id=data['id']).values()
				data['review'] = prod_review
				total = 0.0
				for x in prod_review:
					total = total + x['rating']
				rating = 0.0
				if len(prod_review) <= 0:
					rating = 0.0
				else:
					rating = (total/len(prod_review))
				data['rating_len'] = len(prod_review)
				data['avg_rating'] = rating
				product_data.append(data)
			# product_img_serializer = ProductImagesSerializer(ProductImages.objects.filter(product__price__range = [min_price ,max_price ]), many=True)
			return Response(data= {'msg':'Success', 'data':product_data, 'response_code':'200'},status=status.HTTP_200_OK)
			# product_img = ProductImages.objects.filter(product__price__range = [min_price ,max_price ]).values()
			# for data in product_img:
			# 	product=Product.objects.filter(id=data['product_id']).first()
			# 	product_image = ProductImages.objects.filter(product__category__id = category_id).values().first()
			# 	data['product_img'] = product_image
			# 	product_data=Product.objects.filter(id=data['product_id']).values().first()
			# 	data['product'] = product_data
			# 	cat = ProductCategory.objects.filter(id=product.category.id).values().first()
			# 	data['cat']=cat
			# 	sub_cat = ProductSubCategory.objects.filter(id=product.subcategory.id).values().first()
			# 	data['subcat']=sub_cat
			# 	sub_sub_cat = ProductSubSubCategory.objects.filter(id=product.subsubcategory.id).values().first()
			# 	data['subsubcat'] = sub_sub_cat
			# return Response({'msg':'Success', 'data':product_img, 'response_code':'200'},status=status.HTTP_200_OK)
		if sort_ascend:
			product_data = []
			product = Product.objects.all().order_by('name').values()
			for data in product:
				product_image =  ProductImages.objects.filter(product_id=data['id']).values()
				data['product_img'] = product_image
				prod_review = ProductRating.objects.filter(product_id=data['id']).values()
				print(prod_review)
				data['review'] = prod_review
				total = 0.0
				for x in prod_review:
					total = total + x['rating']
				rating = 0.0
				if len(prod_review) <= 0:
					rating = 0.0
				else:
					rating = (total/len(prod_review))
				data['rating_len'] = len(prod_review)
				data['avg_rating'] = rating
				product_data.append(data)
			# product_img_serializer = ProductImagesSerializer(ProductImages.objects.all().order_by('product__name'), many=True)
			return Response(data= {'msg':'Success', 'data':product_data, 'response_code':'200'},status=status.HTTP_200_OK)
			# product_img = ProductImages.objects.all().order_by('product__name').values()
			# for data in product_img:
			# 	product=Product.objects.filter(id=data['product_id']).order_by('name').first()
			# 	product_image = ProductImages.objects.filter(product__id = data['product_id']).values().first()
			# 	data['product_img'] = product_image
			# 	product_data=Product.objects.filter(id=data['product_id']).values().first()
			# 	data['product'] = product_data
			# 	cat = ProductCategory.objects.filter(id=product.category.id).values().first()
			# 	data['cat']=cat
			# 	sub_cat = ProductSubCategory.objects.filter(id=product.subcategory.id).values().first()
			# 	data['subcat']=sub_cat
			# 	sub_sub_cat = ProductSubSubCategory.objects.filter(id=product.subsubcategory.id).values().first()
			# 	data['subsubcat'] = sub_sub_cat
			# return Response({'msg':'Success', 'data':product_img, 'response_code':'200'},status=status.HTTP_200_OK)
		if sort_descend:
			product_data = []
			product = Product.objects.all().order_by('-name').values()
			for data in product:
				product_image =  ProductImages.objects.filter(product_id=data['id']).values()
				data['product_img'] = product_image
				prod_review = ProductRating.objects.filter(product_id=data['id']).values()
				data['review'] = prod_review
				total = 0.0
				for x in prod_review:
					total = total + x['rating']
				rating = 0.0
				if len(prod_review) <= 0:
					rating = 0.0
				else:
					rating = (total/len(prod_review))
				data['rating_len'] = len(prod_review)
				data['avg_rating'] = rating
				product_data.append(data)
			# product_img_serializer = ProductImagesSerializer(ProductImages.objects.all().order_by('-product__name'), many=True)
			return Response(data= {'msg':'Success', 'data':product_data, 'response_code':'200'},status=status.HTTP_200_OK)
			# product_img = ProductImages.objects.all().order_by('-product__name').values()
			# for data in product_img:
			# 	product=Product.objects.filter(id=data['product_id']).order_by('name').first()
			# 	product_image = ProductImages.objects.filter(product__id = data['product_id']).values().first()
			# 	data['product_img'] = product_image
			# 	product_data=Product.objects.filter(id=data['product_id']).values().first()
			# 	data['product'] = product_data
			# 	cat = ProductCategory.objects.filter(id=product.category.id).values().first()
			# 	data['cat']=cat
			# 	sub_cat = ProductSubCategory.objects.filter(id=product.subcategory.id).values().first()
			# 	data['subcat']=sub_cat
			# 	sub_sub_cat = ProductSubSubCategory.objects.filter(id=product.subsubcategory.id).values().first()
			# 	data['subsubcat'] = sub_sub_cat
			# return Response({'msg':'Success', 'data':product_img, 'response_code':'200'},status=status.HTTP_200_OK)
		if category_id is None and sub_category_id is None and search is None and min_price is None and max_price is None:
			print('666666')
			product_data = []
			product = Product.objects.all().values()
			# print(len(product))
			# product_img_serializer = ProductImagesSerializer(product_img, many=True)
			for data in product:
				product_image = ProductImages.objects.filter(product_id = data['id']).values()
				data['product_img'] = product_image
				prod_review = ProductRating.objects.filter(product_id=data['id']).values()
				data['review'] = prod_review
				total = 0.0
				for x in prod_review:
					total = total + x['rating']
				rating = 0.0
				if len(prod_review) <= 0:
					rating = 0.0
				else:
					rating = (total/len(prod_review))
				data['rating_len'] = len(prod_review)
				data['avg_rating'] = rating
				product_data.append(data)
			return Response(data= {'msg':'Success', 'data':product_data, 'response_code':'200'},status=status.HTTP_200_OK)
		if search == '':
			print('hjhjhhhjhj')
			product_img = ProductImages.objects.all()
			product_img_serializer = ProductImagesSerializer(product_img, many=True)
			return Response(data= {'msg':'Success', 'data':product_img_serializer.data, 'response_code':'200'},status=status.HTTP_200_OK)
		else:
			print('99999')
			product = Product.objects.all().values()
			# product_img_serializer = ProductImagesSerializer(product_img, many=True)
			for data in product:
				# product=Product.objects.filter(id=data['id'])
				product_image = ProductImages.objects.filter(product__id = data['id']).values()
				data['product_img'] = product_image
				prod_review = ProductRating.objects.filter(product_id=data['id']).values()
				data['review'] = prod_review
				total = 0.0
				for x in prod_review:
					total = total + x['rating']
				rating = 0.0
				if len(prod_review) <= 0:
					rating = 0.0
				else:
					rating = (total/len(prod_review))
				data['rating_len'] = len(prod_review)
				data['avg_rating'] = rating
			return Response(data= {'msg':'Success','data':data,'response_code':'200'},status=status.HTTP_200_OK)


@api_view(['GET'])
@csrf_exempt
def offer_and_featured(request):
	if request.method == 'GET':
		product_data1 = []
		product_data2 = []
		product_featured = Product.objects.filter(featured = True).values()
		product_offer = Product.objects.filter(offer = True).values()
		for data in product_featured:
			product_image =  ProductImages.objects.filter(product_id=data['id']).values()
			data['product_img'] = product_image
			product_data1.append(data)
		for data in product_offer:
			product_image =  ProductImages.objects.filter(product_id=data['id']).values()
			data['product_img'] = product_image
			product_data2.append(data)
		# product_img_serializer = ProductImagesSerializer(ProductImages.objects.filter(product__price__range = [min_price ,max_price ]), many=True)
		return Response(data= {'msg':'Success', 'data1':product_data1, 'data2':product_data2, 'response_code':'200'},status=status.HTTP_200_OK)

#add to cart


@api_view(['GET','POST', 'DELETE'])
@csrf_exempt
def add_to_cart(request):
	if request.method == 'GET':
		cart_details = CartItems.objects.filter(cart__user__username=request.user).values()
		for data in cart_details:

			product = Product.objects.values().filter(id=data['product_id']).first()
			product['image'] = ProductImages.objects.values().filter(product__id=data['product_id'])[0]['image']
			data['product']  = product
		return Response({'response':'success', 'data':cart_details,'product_data':"",  'response':'200'},status=status.HTTP_200_OK)


		
	if request.method == 'POST':
		if User.objects.filter(username=request.user).exists():
			variants = request.POST.getlist('variants[]')
			product_id = request.data.get('product_id')
			quantity = request.data.get('quantity')
			product = Product.objects.get(id=product_id)
			try:
				store_id = request.data['store_id']
			except:
				store_id = None
			if product.stock>int(quantity):
				
				if product:
					if Cart.objects.filter(user=request.user).exists():
						print("bjhbjhgjh")
						cart = Cart.objects.get(user=request.user)
						print(cart)
						allow = True
						for x in CartItems.objects.filter(cart=cart):
							print('xxx', x)
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
								print('new_quantity',new_quantity)
								if new_quantity > product.stock:
									new_quantity = product.stock
								price = item.product.price
								total_price = item.product.price * new_quantity
								print('total_price', total_price)
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
						# else:
						# 	return Response({'response':'failed2', 'cart_len':get_cart_len(request)})
					else:
						if int(quantity) > product.stock:
								quantity = product.stock
						cart = Cart.objects.create(user=request.user)
						total = product.price*int(quantity)
						print('total===>', total)
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
						return Response({'response':'success', 'cart_len':get_cart_len(request)})
			return Response({'response':'failed'})
		else:
			return Response(data={'msg':'User not Logged In'}, status= status.HTTP_200_OK)
	
	if request.method == 'DELETE':
		cart_id = request.data.get('cart_id')
		print(cart_id)
		if User.objects.filter(username=request.user):
			print(request.user)
			cart_del = CartItems.objects.filter(cart__user__username=request.user, id = cart_id)
			if cart_del:
				cart_del.delete()
				return Response(data={'msg':'Cart deleted Successfully'},status=status.HTTP_200_OK) 
			else:
				return Response(data={'msg':'Cart not found'},  status=status.HTTP_200_OK)
		else:
			return Response(data={'msg':'User not Logged In'}, status= status.HTTP_200_OK)

	# if request.method == 'POST':
	# 	if User.objects.filter(username=request.user).exists():
	# 		variants = request.POST.getlist('variants[]')
	# 		product_id = request.data.get('product_id')
	# 		quantity = request.data.get('quantity')
	# 		product = Product.objects.get(id=product_id)
	# 		if product_id:
	# 			if Cart.objects.filter(user=request.user).exists():
	# 				cart = Cart.objects.get(user=request.user)
	# 				allow = True
	# 				for x in CartItems.objects.filter(cart=cart):
	# 					if x.product.store == product.store:
	# 						print(x)
	# 						allow = True
	# 						break
	# 					else:
	# 						allow=False
	# 				if allow:
						
	# 					variant_matched = False
	# 					item = ''
	# 					try:
	# 						for items in CartItems.objects.filter(cart=cart, product=product):
	# 							print('hello')
	# 							if int(quantity) > product.stock:
	# 								print(product.stock)
	# 						if variant_matched:
	# 							pass
	# 						# print('yjhjhjhjj')
	# 						# new_quantity = int(quantity) + item.quantity
	# 						# print(new_quantity)
	# 						# print('new_quantity',new_quantity)
	# 						if new_quantity > product.stock:
	# 							new_quantity = product.stock
	# 							price = item.product.price
	# 							total_price = item.product.price * new_quantity
	# 							print('total_price', total_price)
	# 							CartItems.objects.filter(id=item.id).update(
	# 								quantity = new_quantity,
	# 								per_item_cost = price,
	# 								total_cost = total_price
	# 							)
								
	# 							subtotal = cart.subtotal + (int(quantity)*item.product.price)
	# 							Cart.objects.filter(user=request.user).update(subtotal=subtotal)
	# 							calculate_cart_tax(request)
	# 						else:
	# 							if int(quantity) > product.stock:
	# 								quantity = product.stock
	# 							item = CartItems.objects.create(
	# 								cart = cart,
	# 								product = product,
	# 								quantity = quantity,
	# 								per_item_cost = product.price,
	# 								total_cost = product.price*int(quantity)
	# 							)
	# 							for x in variants:
	# 								print("xxxxx",x)
	# 								CartItemVariant.objects.create(cart=cart, cartitem=item, product_variant=ProductVariant.objects.get(id=x))
	# 							subtotal = cart.subtotal + (int(quantity)*product.price)
	# 							Cart.objects.filter(user=request.user).update(subtotal=subtotal)
	# 							print("prining here")
	# 							print(subtotal)
	# 							calculate_cart_tax(request)
	# 							pass
	# 		return Response(data={'msg':'User Logged In', 'response_code':200}, status=status.HTTP_200_OK)
	# 	else:
	# 		return Response(data={'msg':'User not Logged In', 'response_code':200}, status=status.HTTP_200_OK)
	

@api_view(['POST'])
@csrf_exempt
def product_rating(request):
	if check_user_authentication(request, 'User'):
		if request.method == 'POST':
			product_id = request.query_params.get('product_id')
			if product_id:
				product_data = []
				product = Product.objects.get(id = product_id)
				rating = request.data.get('rating')
				review = request.data.get('review')
				rated = ProductRating.objects.create(product = product, user =request.user , rating=rating, review=review)
				data = ProductRating.objects.filter(id = rated.id).values()
				for i in data:
					print(i)
					product_data.append({'data':i})
				return Response(data={'msg':'success', 'data':data},status=status.HTTP_200_OK) 
			else:
				return Response(data={'msg':'Select Correct Product'},status=status.HTTP_200_OK)
	else:
		return Response(data={'msg':'User not Logged In.'},status=status.HTTP_200_OK)





@api_view(['GET','POST', 'DELETE'])
@csrf_exempt
def add_to_wishlist(request):
	if request.method == 'GET':
		wishlist_details = WishlistItems.objects.filter(wishlist__user=request.user).values()

		for data in wishlist_details:

			product = Product.objects.values().filter(id=data['product_id']).first()
			product['image'] = ProductImages.objects.values().filter(product__id=data['product_id'])[0]['image']
			data['product']  = product

			# data['image']   = ProductImages.objects.filter(product__id=data['product_id']).values()
		# wishlist_details_ids = WishlistItems.objects.filter(wishlist__user=request.user).values_list('product__id',flat=True)

		# print("ids===>",wishlist_details_ids)

        # product = 
		# product_images=

		# print(wishlist_details_ids)
		# img_serializer = ProductImagesSerializer(ProductImages.objects.filter(product__id__in = wishlist_details_ids), many=True)
		# wishlist_serializer = WishlistItemSerializer(wishlist_details, many=True)

		return Response({'response':'success', 'data':wishlist_details,'product_data':"",  'response':'200'},status=status.HTTP_200_OK)


	if request.method == 'POST':
		variants = request.POST.getlist('variants[]')
		quantity = request.POST.get('quantity')
		product_id = request.data.get('product_id')
		product = Product.objects.get(id=product_id)
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
						return Response({'response':'success', 'wishlist_len':get_wishlist_len(request)})
						# else:
						# 	return Response({'response':'failed2', 'wishlist_len':get_wishlist_len(request)})
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
						return Response({'response':'success', 'wishlist_len':get_wishlist_len(request)})
		return Response({'response':'failed'})


	if request.method == 'DELETE':
		wishlist_id = request.data.get('wishlist_id')
		print(wishlist_id)
		if User.objects.filter(username=request.user):
			print(request.user)
			wishlist_del = WishlistItems.objects.filter(wishlist__user__username=request.user, id = wishlist_id)
			if wishlist_del:
				wishlist_del.delete()
				return Response(data={'msg':'Wishlist deleted Successfully'},status=status.HTTP_200_OK) 
			else:
				return Response(data={'msg':'Wishlist not found'},  status=status.HTTP_200_OK)
		else:
			return Response(data={'msg':'User not Logged In'}, status= status.HTTP_200_OK)

# privacy policy

@api_view(['GET'])
@csrf_exempt
def privacy_and_policy(request):
	queryset=privacypolicy.objects.all().order_by("-id")[:1]
	serializer=PrivacyPolicySerializer(queryset, many=True)
	return Response(data={'msg':'Success','data':serializer.data,'response_code':200},status=status.HTTP_200_OK)
	




# Terms & Conditions

@api_view(['GET'])
@csrf_exempt
def terms_condition(request):
	terms_queryset=termsandcondition.objects.all().order_by("-id")[:1]
	terms_serializer=TermsandConditionSerializer(terms_queryset,many=True)
	about_serializer= AboutSerializer(AboutUs.objects.all(), many=True)
	gallery_serializer = GallerySerializer(Gallery.objects.all(), many=True)
	blog_serializer = BlogSerializer(Blog.objects.all(), many=True)
	return Response(data={'msg':'Success','terms_data':terms_serializer.data, 'about_data':about_serializer.data, 'gallery_data':gallery_serializer.data, 'blog_data':blog_serializer.data,'response_code':200},status=status.HTTP_200_OK)





# Order History Data  Section 

@api_view(['GET', 'POST'])
@csrf_exempt
def my_order(request):
	if check_user_authentication(request, 'User'):
		if request.method == 'GET':
			data=[]
			store = request.data.get('store')
			for order in Orders.objects.filter(user=request.user).order_by('-order_date'):
				if store:
					for item in OrderItems.objects.filter(order=order, store=store).values():
						for x in OrderItemVariant.objects.filter(orderitem=item['id']):
							variants.append(x)
						for x in Product.objects.filter(id=item['product_id']).values():
							item['product_name'] = x['name']
						for x in Orders.objects.filter(id=order.id).values():
							print(x['address'])
							item['order_date'] = x['order_date']
							item['address'] = x['address']
						for x in ProductImages.objects.filter(product=item['product_id']).values():
							item['image'] = x['image']
						data.append(item)
				else:
					for item in OrderItems.objects.filter(order=order).values():
						for x in OrderItemVariant.objects.filter(orderitem=item['id']):
							variants.append(x)
						for x in Product.objects.filter(id=item['product_id']).values():
							item['product_name'] = x['name']
						for x in Orders.objects.filter(id=order.id).values():
							item['order_date'] = x['order_date']
							for y in Address.objects.filter(id = x['address_id']).values():
								item['address'] = y['home_no'] + ' ' + y['landmark'] + ' ' + y['city'] + ' ' + y['state'] + ' ' + (y['pincode'])	
						for x in ProductImages.objects.filter(product=item['product_id']).values():
							item['image'] = x['image']
						data.append(item)
			return Response(data={'msg':'success','response_code':200,'data':data},status=status.HTTP_200_OK)

							
						# if ProductRating.objects.filter(product=item['product_id'], user=request.user).exists().values():
						# else:
						# 	dic.update({'rating_flag':False})
						# dic.update({'date':order.order_date})
						# items.append(dic)



			# if OrderItems.objects.filter(order__user__username = request.user):
			# 	orderdata = OrderItems.objects.all().filter(order__user__username = request.user)
			# 	order_serializer = OrderSerializer(orderdata, many=True)
			# 	orders = get_my_orders(request.user)

			# 	# return JsonResponse({'data':orderdata})
		# else:
		# 	return Response(data={'msg':'failure','response_code':200},status=status.HTTP_200_OK)
		if request.method == 'POST':
			if OrderItems.objects.filter(order__user = request.user):
				order_id = request.query_params.get('order_id')
				delivery_status =  request.data.get('delivery_status')
				cancellation_reason = request.data.get('cancellation_reason')
				print(order_id, delivery_status, cancellation_reason)
				data = []
				try:
					order_data = Orders.objects.get(id= order_id)
					print(order_data)
				except:
					return Response(data = { 'error' : 'item not found' }, status = status.HTTP_404_NOT_FOUND )
				order = OrderItems.objects.filter(order = order_data)
				for i in order:
					i.delivery_status = delivery_status
					i.cancellation_reason = cancellation_reason
					i.save()
				order_status = OrderItems.objects.filter(order = order_data).values()
				for i in order_status:
					data.append(i)

				# print(request.data)
				# order_serializer = OrderSerializer(order_data, data= request.data, partial=True)
				# print(order_serializer)
				# if order_serializer.is_valid():
					# print('KKKKKKKKKKKKKKKKK')
					# order_serializer.save()
					return Response(data= {'msg':'Success', 'data':data}, status=status.HTTP_200_OK)
				else:
					return Response(data= {'msg':'Failure', 'errors':order_serializer.errors}, status=status.HTTP_200_OK)
			return Response(data= {'msg':'User not Logged in.'}, status=status.HTTP_200_OK)

#banner section

@api_view(['GET'])
@csrf_exempt
def bnanner_api_section(request):
	if request.method == 'GET':
		queryset = HomeBanner.objects.all()[:4]
		serializer = HomeBannerSerializer(queryset,many=True)
		return Response(data={'msg':'Success','data':serializer.data,'response_code':200},status=status.HTTP_200_OK)
	else:
		return Response(data={'msg':'Banner not Found','response_code':201},status=status.HTTP_201_CREATED)


# Query  Post Section 

@api_view(['GET','POST'])
@csrf_exempt
def user_query_data(request):
	user =  request.user
	print(user)
	if request.method == 'GET':
		if User.objects.filter(username=user):
			query_data = Query.objects.filter(user__username=user)
			query_serializer=QuerySerializer(query_data, many=True)
			return Response(data= {'msg':"Success",'response_code':200, 'data':query_serializer.data}, status=status.HTTP_200_OK)
		else:
			return Response(data={'msg':'User not Logged In'}, status= status.HTTP_200_OK)

	if request.method =='POST':
		if User.objects.filter(username=user):
			query_serializer=QuerySerializer(data=request.data)
			if query_serializer.is_valid():
				query_serializer.save()
				# notification(user, 'Query sent Successfully.')
				return Response(data= {'msg':"Success",'data':query_serializer.data,'response_code':200}, status=status.HTTP_200_OK)
			else:
				return Response(data= {'msg':"Data Not Sent Successfully",'error':query_serializer.errors}, status=status.HTTP_201_CREATED)
		else:
			return Response(data={'msg':'User not Logged In'}, status= status.HTTP_200_OK)
	else:
		return Response(data= {'msg':"You Don't have access",'response_code':'201'}, status=status.HTTP_201_CREATED)





# Query  Post Section 

@api_view(['GET'])
@csrf_exempt
def contact_data(request):
	if request.method == 'GET':
		query_data = contact_us.objects.all().order_by('-id')[:1]
		query_serializer=ContactSerializer(query_data, many=True)
		return Response(data= {'msg':"Success",'response_code':200, 'data':query_serializer.data}, status=status.HTTP_200_OK)


#wallet details

@api_view(['GET','POST'])
@csrf_exempt
def wallet_details(request):
	user = request.user
	if request.method == 'GET':
		if User.objects.filter(username=user):
			data = []
			wallet_data = Wallet.objects.filter(user=user).values()
			for x in wallet_data:
				x['current_balance'] = round(x['current_balance'], 2)
				idd = WalletTransaction.objects.filter(wallet_id = x['id']).order_by('-transaction_date').values()
				x['wallet_transaction'] = idd
				for i in idd:
					i['previous_amount'] = round(i['previous_amount'], 2)
					i['remaining_amount'] = round(i['remaining_amount'], 2)
					i['transaction_amount'] = round(i['transaction_amount'], 2)
				
			data.append(x)

			withdraw_data = UserWithdrawRequest.objects.filter(user__username=user).order_by('-id')
			wallet_serializer = WalletSerializer(idd, many=True)
			withdraw_serializer = UserWithdrawRequestSerializer(withdraw_data, many=True)
			return Response(data={'msg':'Success','data':data,  'withdraw_data':withdraw_serializer.data , 'response_code':200}, status=status.HTTP_200_OK)
		else:
			return Response(data={'msg':'User not Logged In', 'response_code':200}, status=status.HTTP_200_OK)
	if request.method == 'POST':
		amount = request.data.get('amount')
		amount = float(amount)
		if amount > 500:
			flag = True
			for x in UserWithdrawRequest.objects.filter(user=request.user):
				if x.status == 0 or x.status == 1:
					flag = False
					break
			if flag:
				tds = ((amount/100)*5)
				withdraw_data = UserWithdrawRequest.objects.create(
					user = request.user,
					request_date = timezone.now(),
					amount = amount,
					tds = tds
				)
				withdraw_serializer = UserWithdrawRequestSerializer(UserWithdrawRequest.objects.all().order_by('-id')[0])
				# if withdraw_serializer.is_valid():
				# 	withdraw_serializer.save()
				return Response(data={'msg':'Success', 'data':withdraw_serializer.data, 'response_code':200}, status=status.HTTP_200_OK)
				# else:
				# 	return Response(data={'msg':'Enter correct Data', 'response_code':200}, status=status.HTTP_200_OK)
			else:
				return Response(data={'msg':'Already requested', 'response_code':200}, status=status.HTTP_200_OK)
		else:
			return Response(data={'msg':'Withdraw amount must be greater than 500', 'response_code':200}, status=status.HTTP_200_OK)

	flag = True
	if PaymentInfo.objects.filter(user=request.user).exists():
		flag = True
	else:
		flag = False
	if not Wallet.objects.filter(user=request.user).exists():
		Wallet.objects.create(user=request.user)
		pass

#user address

@api_view(['GET','POST', 'DELETE'])
@csrf_exempt
def user_address(request):
	user = request.user
	if request.method == 'GET':
		if User.objects.filter(username=user):
			address_data = Address.objects.filter(user__username = user)
			address_serializer = AddressSerializer(address_data, many=True)
			return Response(data={'msg':'Success', 'data':address_serializer.data}, status=status.HTTP_200_OK)
		else:
			return Response(data={'msg':'User not Logged In'}, status= status.HTTP_200_OK)
	
	if request.method =='POST':
		if User.objects.filter(username=user):
			address_serializer = AddressSerializer(data = request.data)
			if address_serializer.is_valid():
				address_serializer.save()
				return Response(data={'msg':'Success', 'data':address_serializer.data}, status=status.HTTP_200_OK)
			else:
				return Response(data={'msg':'Address not addedd', 'error':address_serializer.errors},  status=status.HTTP_200_OK)
		else:
			return Response(data={'msg':'User not Logged In'}, status= status.HTTP_200_OK)
	if request.method == 'DELETE':
		address_id = request.data.get('address_id')
		print(address_id)
		if User.objects.filter(username=user):
			print(request.user)
			address_del = Address.objects.filter(user__username=user, id = address_id)
			print(address_del)
			if address_del:
				address_del.delete()
				return Response(data={'msg':'Address deleted Successfully'},status=status.HTTP_200_OK) 
			else:
				return Response(data={'msg':'Address not found'},  status=status.HTTP_200_OK)
		else:
			return Response(data={'msg':'User not Logged In'}, status= status.HTTP_200_OK)


# place order

@api_view(['GET','POST', 'DELETE'])
@csrf_exempt
def order_place(request):
	if check_user_authentication(request, 'User'):

		if request.method =='POST':
			# Orders.objects.all()
			address = Address.objects.get(id=request.query_params.get('address_id'))
			cart_id = request.query_params.get('cart_id')
			cart = Cart.objects.get(id=cart_id)
			plan_type = request.query_params.get('plan_type')
			payment_type = request.query_params.get('payment_type')
			dic = {}
			request.session['plan_type'] = request.POST.get('plan')
		if payment_type == 'cod':
			create_cod_order(cart, address, request.user, plan_type)
			sub = 'AVPL - Order Placed'
			msg = ''' Hi there!
				Your order has been placed successfully, Kindly check the My Order section in your dashboard.
				Thanks!'''
			EmailMessage(sub, msg, to=[request.user.email]).send()
			# notification(request.user, 'Order Placed Successfully.')
		elif payment_type == 'online':
			create_online_order(cart, address, request.user)
			order = RazorpayOrder.objects.all().order_by('-id')[:1]
			razorpaytransaction = RazorpayTransaction.objects.create(payment_id=payment_id, order_id=order_id, signature=signature)
			save_order(order.cart, order.address, order.user, razorpaytransaction)
			dic = save_order(cart, address, request.user)
			dic = create_online_order(cart, address, request.user, request.session.get('plan_type'))
		return Response({'response':'Success', 'pay_type':payment_type, 'data':dic})
	else:
		return Response('Error 500 : Unauthorized User')


# otp send

@api_view(['GET','POST'])
@csrf_exempt
def send_otp(request):
	if request.method =='GET':
		email = request.query_params.get('email')
		if User.objects.filter(username=email):
			return Response(data={'msg':'Email verified'}, status=status.HTTP_200_OK)
		else:
			return Response(data={'msg':'User does not exists'}, status=status.HTTP_200_OK)
	

	if request.method == 'POST':
		email = request.query_params.get('email')
		if User.objects.filter(username=email).exists:
			otp = random.randint(100000,999999)
			request.session['otp1'] = otp
			request.session['emailid'] = User.objects.get(email=email).id
			sub = 'AVPL - Password Change Request'
			msg = ''' Hi there!
			We received a password change request, please verify your email with below OTP.
			'''+str(otp)
			EmailMessage(sub, msg, to=[email]).send()
			notification(request.user, 'OTP sent Successfully.')
			return Response(data ={'msg':'OTP sent successfully'}, status=status.HTTP_200_OK)
			


#otp verify

@api_view(['GET','POST'])
@csrf_exempt
def otp_check(request):
	if request.method == 'POST':
		otp = request.query_params.get('otp2')
		otp_2 = request.session['otp1']
		if otp:
			try:
				otp == otp_2
				return Response(data ={'msg':'OTP Verified', 'status':'200'}, status=status.HTTP_200_OK)
			except:
				return Response(data ={'msg':'OTP does not matched'}, status=status.HTTP_200_OK)
		else:
			return Response(data ={'msg':'No OTP exist'}, status=status.HTTP_200_OK)


#password changed

@api_view(['POST'])
@csrf_exempt
def password_changed(request):
	if request.method == 'POST':
		setpwd = request.query_params.get('set1')
		userid = request.session['emailid']
		if setpwd:
			user = User.objects.get(id=userid)
			user.set_password(setpwd)
			user.save()
			notification(user, 'Password Changed Successfully.')
			return Response(data ={'msg':'Password Changed Successfully', 'status':'200'}, status=status.HTTP_200_OK)
		else:
			return Response(data ={'msg':'Password does not matched', 'status':'200'}, status=status.HTTP_200_OK)


#user profile

@api_view(['GET'])
@csrf_exempt
def userprofile(request):
	check_user_authentication(request, 'User')
	if request.method == 'GET':
		if User.objects.get(username=request.user):
			profile_data = UserData.objects.filter(user__username = request.user)
			profile_serializer = UserDataSerializer(profile_data, many=True)
			return Response(data={'msg':'Success', 'data':profile_serializer.data}, status=status.HTTP_200_OK)
		else:
			return Response(data ={'msg':'User not Logged in.', 'status':'200'}, status=status.HTTP_200_OK)

#store data 

@api_view(['GET'])
@csrf_exempt
def storedata(request):
	check_user_authentication(request, 'User')
	if request.method == 'GET':
		store_data = StoreImages.objects.all()
		store_serializer = StoreSerializer(store_data, many=True)
		return Response(data={'msg':'Success', 'data':store_serializer.data}, status=status.HTTP_200_OK)

# store product

@api_view(['GET'])
@csrf_exempt
def storeproductdata(request):
	check_user_authentication(request, 'User')
	if request.method == 'GET':
		store_id = request.query_params.get('store_id')
		if store_id:
			product_data = []
			product = Product.objects.filter(store_id = store_id).values()
			for data in product:
				product_image =  ProductImages.objects.filter(product_id=data['id']).values()
				data['product_img'] = product_image
				product_data.append(data)
			# product_img_serializer = ProductImagesSerializer(ProductImages.objects.filter(product__name__icontains = search), many=True)
			return Response(data= {'msg':'Success', 'data':product_data, 'response_code':'200'},status=status.HTTP_200_OK)
			# product_data = Product.objects.filter(store__id=store_id)
			# product_serializer = ProductSerializer(product_data, many=True)
			# product_img = ProductImages.objects.filter(product__store__id = store_id)
			# product_img_serializer = ProductImagesSerializer(product_img, many=True)
			# return Response(data={'msg':'Success', 'product_data':product_img_serializer.data}, status=status.HTTP_200_OK)
		else:
			# product_data = Product.objects.all()
			# product_serializer = ProductSerializer(product_data, many=True)
			product_img = ProductImages.objects.all()
			product_img_serializer = ProductImagesSerializer(product_img, many=True)
			return Response(data={'msg':'Success', 'product_data':product_img_serializer.data}, status=status.HTTP_200_OK)


# notification

@api_view(['GET'])
@csrf_exempt
def notification(request):
	check_user_authentication(request, 'User')
	if request.method == 'GET':
			notification_data = Notification.objects.filter(user__username =request.user).order_by('-id')
			notification_serializer = NotificationSerializer(notification_data, many=True)
			return Response(data={'msg':'Success', 'product_data':notification_serializer.data, }, status=status.HTTP_200_OK)






def find_lat_long(t1,t2):
	R = 6373.0
	lat1 = radians(t1[0])
	lon1 = radians(t1[1])

	lat2 = radians(t2[0])
	lon2 = radians(t2[1])
	x = geopy.distance.geodesic(t1, t2).km
	return x


@api_view(['GET'])
@csrf_exempt
def nearby_store(request):
	if request.method == 'GET':
		home_address=request.query_params.get('home_address')
		lat=request.query_params.get('lat',True)
		lng=request.query_params.get('lng',True)
		if home_address or (lat and lng):
			try:
				gmaps = googlemaps.Client(key='AIzaSyBlEb2wyEYcwIj2HjR0ALpVXhj9Oo8zpVc')
				if home_address:
					add_lat_long=gmaps.geocode(home_address)
					user_lat=add_lat_long[0]['geometry']['location']['lat']
					user_lng=add_lat_long[0]['geometry']['location']['lng']
				else:
					user_lat=float(lat)
					user_lng=float(lng)

				store_address_obj=Vendor.objects.all()
				request.session['usr_address']=home_address
				l={}
				for i in store_address_obj:
					store_addr=gmaps.geocode(str(i.address) +","+str(i.zipcode))
					store_lat=store_addr[0]['geometry']['location']['lat']
					store_lng=store_addr[0]['geometry']['location']['lng']
					l[i.id]=(store_lat, store_lng)
				small=None
				user_store_id=None
				store_distance = []
				for i,j in l.items():
					x=find_lat_long((user_lat,user_lng),j)
					store_distance.append({"store_id":i,"store_distance":x})
				store_ids = []	
				for d in store_distance:
					if d['store_distance']<=300:
						store_ids.append(d['store_id'])
				store_ids = store_ids
				store_list=[]
				
				for i in store_ids:
					store_details = StoreImages.objects.get(store__vendor__id=i)
					store_list.append(store_details)
				store_serializer = StoreImagesSerializer(store_list, many=True)
				return Response(data={'msg':'Success', 'data':store_serializer.data})
			except:
				return Response(data={'msg':'Select Address Properly'})
		return Response(data={'msg':'Success','data':'Enter valid data.'})

@api_view(['GET', 'POST'])
@csrf_exempt
def user_downline(request):
	check_user_authentication(request, 'User')
	if request.method == 'GET':
		
		user = UserData.objects.get(user=request.user)
		downline = fetch_user_tree(request.user)
		print(downline)
		list_data = []
		for i, j in downline.items():
			for k in j:
				k['branch'] =i
				
				list_data.append(k)
		return Response(data ={'msg':'success', 'data':list_data})
	if request.method == 'POST':
		user_id = request.data.get('user_id')
		print(user_id)
		if user_id:
			user = User.objects.get(id=user_id)
			print(user)
			link = generate_link(user, 'User')
			return Response(data ={'msg':'success', 'link':link})
		





@api_view(['GET'])
@csrf_exempt
def latest_product(request):
	check_user_authentication(request, 'User')
	d = datetime.datetime.now()
	latest_product = []
	for latest in Product.objects.all().values():
		idd = latest['id']
		if latest['created_at'].strftime("%m") == d.strftime("%m"):
			for img in ProductImages.objects.all().values():
				if img['product_id'] == idd:
					latest['images'] = img['image']
					latest_product.append(latest)
	return Response(data ={'msg':'success',"data": latest_product})
