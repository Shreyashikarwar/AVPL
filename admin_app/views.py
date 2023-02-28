from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators import csrf
from admin_app.models import *
from main_app.models import *
from vendor_app.models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login , logout
from django.http import JsonResponse
import uuid
import datetime
from main_app.utils import *
from main_app.razor import *
from admin_app.utils import *
from django.utils import timezone

def admin_show(request):
#	for x in ProductCategory.objects.all():
#		PointValue.objects.create(category=x)
#	ProductCategory.objects.filter(name='Computers').delete()
#	User.objects.create_user(email='admin@avpl.com',username='adminavpl',password='1234')
#	user = User.objects.get(email='admin@avpl.com')
#	Role(user=user, level=Levels.objects.get(level='Admin')).save()
	return HttpResponse('Done!')

@csrf_exempt
def admin_login(request):
	if request.method == 'POST':
		email = request.POST.get('email')
		password = request.POST.get('password')
		if User.objects.filter(email=email).exists():
			chk_user = User.objects.get(email=email)
			user = authenticate(request, username=chk_user.username , password=password)
			if user is not None:
				login(request,user)
				if check_user_authentication(request, 'Admin'):
					return redirect('/admins/dashboard')
				else:
					messages.info(request, 'You are not allowed to login')
					logout(request)
					return redirect('/admins/')
			else:
				messages.info(request,'Incorrect Admin Password')
				return redirect('/admins/')
		elif User.objects.filter(username=email).exists():
			chk_user = User.objects.get(username=email)
			user = authenticate(request, username=chk_user.username , password=password)
			if user is not None:
				login(request,user)
				if check_user_authentication(request, 'Admin'):
					return redirect('/admins/dashboard')
				else:
					messages.info(request, 'You are not allowed to login')
					logout(request)
					return redirect('/admins/')
			else:
				messages.info(request,'Incorrect Admin Password')
				return redirect('/admins/')
		else:
			messages.info(request,'Incorrect Admin Email/Username')
			return redirect('/admins/')
	else:
		if request.user.is_authenticated and check_user_authentication(request, 'Admin'):
			return redirect('/admins/dashboard')
		else:
			return render(request, 'admin_app/login.html', {})

def admin_dashboard(request):
	if check_user_authentication(request, 'Admin'):
		pv = 0.0
		pv_year = 0.0
		d = datetime.datetime.now()
		if len(Yearly_PV.objects.all()) == 0:
			Yearly_PV.objects.create()
		for pv_trn in PVTransactions.objects.all():
			if pv_trn.transaction_date.strftime("%m") == d.strftime("%m"):
				pv += pv_trn.total_pv
		for pv_trn in PVTransactions.objects.all():
			if pv_trn.transaction_date.strftime("%Y") == d.strftime("%Y"):
				pv_year += pv_trn.total_pv
		Yearly_PV.objects.update(pv = pv_year)
		print(pv_year<pv)
		pv = round(pv,2)
		
			
		
		dic = {
			'categories':ProductCategory.objects.all(),
			'commission':Commission.objects.all(),
			'savings':Savings.objects.all(),
			'wallet':Wallet.objects.all(),
			'transactions':CommissionTransaction.objects.all().order_by('-id'),
			'total_pv':pv,
			'year_pv':pv_year,
			'wallettransactions':WalletTransaction.objects.all().order_by('-id'),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/dashboard.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def admin_send_money(request):
	if check_user_authentication(request, 'Admin'):
		send_profit_to_users()
		return redirect('/admins/dashboard')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_product_categories(request):
	if check_user_authentication(request, 'Admin'):
		if request.method == 'POST':
			name = request.POST.get('name')
			tax = request.POST.get('tax')
			commission = request.POST.get('commission')
			image = request.FILES['image']
			if ProductCategory.objects.filter(name=name).exists():
				messages.info(request, 'Product Category Already Exists')
				return redirect('/admins/productcategories')
			else:
				ProductCategory.objects.create(name=name, tax=tax, image=image, commission=commission)
				PointValue.objects.create(category=ProductCategory.objects.get(name=name))
				messages.info(request, 'Product Category Added Successfully !!!!')
				return redirect('/admins/productcategories')
		else:
			dic = {
				'data':ProductCategory.objects.all(),
				'categories':ProductCategory.objects.all(),
				'notification':get_notifications(request.user),
				'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
			}
			return render(request, 'admin_app/product-category.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def admin_delete_product_category(request):
	if check_user_authentication(request, 'Admin'):
		if request.method == 'GET':
			id_ = request.GET.get('id_')
			ProductCategory.objects.filter(id=id_).delete()
			messages.info(request, 'Product Category Deleted Successfully !!!!')
			return redirect('/admins/productcategories')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_product_sub_categories(request):
	if check_user_authentication(request, 'Admin'):
		if request.method == 'POST':
			name = request.POST.get('name')
			image = request.FILES['image']
			category = request.POST.get('category')
			if ProductSubCategory.objects.filter(name=name).exists():
				messages.info(request, 'Product Sub Category Already Exists')
				return redirect('/admins/productsubcategories')
			else:
				ProductSubCategory.objects.create(category=ProductCategory.objects.get(id=category),name=name, image=image)
				messages.info(request, 'Product Sub Category Added Successfully !!!!')
				return redirect('/admins/productsubcategories')
		else:
			dic = {
				'categories':ProductCategory.objects.all(),
				'data':ProductSubCategory.objects.all(),
				'notification':get_notifications(request.user),
				'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
			}
			return render(request, 'admin_app/product-sub-category.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def admin_delete_product_sub_category(request):
	if check_user_authentication(request, 'Admin'):
		if request.method == 'GET':
			id_ = request.GET.get('id_')
			ProductSubCategory.objects.filter(id=id_).delete()
			messages.info(request, 'Product Sub Category Deleted Successfully !!!!')
			return redirect('/admins/productsubcategories')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_product_sub_sub_categories(request):
	if check_user_authentication(request, 'Admin'):
		if request.method == 'POST':
			name = request.POST.get('name')
			image = request.FILES['image']
			subcategory = request.POST.get('subcategory')
			if ProductSubSubCategory.objects.filter(name=name).exists():
				messages.info(request, 'Product Sub Sub Category Already Exists')
				return redirect('/admins/productsubsubcategories')
			else:
				ProductSubSubCategory.objects.create(subcategory=ProductSubCategory.objects.get(id=subcategory),name=name, image=image)
				messages.info(request, 'Product Sub Sub Category Added Successfully !!!!')
				return redirect('/admins/productsubsubcategories')
		else:
			dic = {
				'categories':ProductCategory.objects.all(),
				'subcategories':ProductSubCategory.objects.all(),
				'data':ProductSubSubCategory.objects.all(),
				'notification':get_notifications(request.user),
				'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
			}
			return render(request, 'admin_app/product-sub-sub-category.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def admin_delete_product_sub_sub_category(request):
	if check_user_authentication(request, 'Admin'):
		if request.method == 'GET':
			id_ = request.GET.get('id_')
			ProductSubSubCategory.objects.filter(id=id_).delete()
			messages.info(request, 'Product Sub Sub Category Deleted Successfully !!!!')
			return redirect('/admins/productsubsubcategories')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def admin_kyc_requests(request):
	if check_user_authentication(request, 'Admin'):
		dic = {
			'categories':ProductCategory.objects.all(),
			'data':Vendor.objects.filter(doc_submitted=True, status=False),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/kyc-requests.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def admin_kyc_vendors(request):
	if check_user_authentication(request, 'Admin'):
		dic = {
			'categories':ProductCategory.objects.all(),
			'data':Vendor.objects.filter(doc_submitted=True, status=True),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/kyc-vendors.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def admin_vendor_profile(request):
	if check_user_authentication(request, 'Admin'):
		vendor = Vendor.objects.get(id=request.GET.get('i'))
		vendoc = VendorDocs.objects.get(vendor__user=vendor.user)
		store = Store.objects.get(vendor=vendor)
		images = StoreImages.objects.get(store=store)
		vanadd = Vendor.objects.get(user=vendor.user)
		dic = {
			'vendoc':vendoc,
			'store':store,
			'info':vanadd,
			'vendor':vendor,
			'images':images
		}
		return render(request,'admin_app/vendor-profile.html', dic)
	else:
		return HttpResponse('Error 500 : Unauthorized User')

def admin_activate_vendor(request):
	if check_user_authentication(request, 'Admin'):
		id_=request.GET.get('id')
		print("printing id_ here")
		print(id_)
		vendor = Vendor.objects.get(id=id_)
		Vendor.objects.filter(id=id_).update(status=True)
		sub = 'AVPL - Vendor Account Activated Successfully'
		msg = '''Hi there!
YYour AVPL Vendor Account has been activated successfully, you can login and create your store.

Thanks!'''
		EmailMessage(sub,msg,to=[vendor.user.email]).send()
		messages.success(request, 'Vendor Activated Successfully !!!!')
		notification(request.user, 'Vendor '+vendor.first_name+' '+vendor.last_name)
		notification(vendor.user, 'Profile Activated Successfully.')
		return redirect('/admins/kycrequests')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def admin_pv_wallet(request):
	if check_user_authentication(request, 'Admin'):
		print(request.user)
		dic = {'user':UserData.objects.get(user=request.user),
			'pv':fetch_pv(request.user),
			'transactions':fetch_pv_transactions(request.user),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/pv.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')



@csrf_exempt
def admin_point_value(request):
	if check_user_authentication(request, 'Admin'):
		if request.method == 'GET':
			category = ProductCategory.objects.get(id = request.GET.get('c'))
			dic = {'categories':ProductCategory.objects.all(), 'point':PointValue.objects.get(category=category)}
			return render(request,'admin_app/point-value.html', dic)
		elif request.method == 'POST':
			new = request.POST.get('new')
			id_ = request.POST.get('category')
			category = ProductCategory.objects.get(id = id_)
			PointValue.objects.filter(category=category).update(percentage=new)
			messages.success(request, 'Point Value Percentage Updated Successfully !!!!')
			notification(request.user, 'PV of '+category.name+' set to '+str(PointValue.objects.get(category=category).percentage))
			return redirect('/admins/point/?c='+id_)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def admin_create_link(request):
	if check_user_authentication(request, 'Admin'):
		dic = {
			'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/create-link.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def wallet_details(request):
	if check_user_authentication(request, 'Admin'):
		dic = {
			'wallet':Wallet.objects.filter(user__is_superuser=True),
			'wallettransactions':WalletTransaction.objects.filter(wallet__user__is_superuser=True),
			# 'wallettransactions':WalletTransaction.objects.all(),
		}
		return render(request, 'admin_app/wallet.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def admin_generate_link(request):
	if check_user_authentication(request, 'Admin'):
		data = {'link':generate_link(request.user, 'Admin')}
		return JsonResponse(data)
	else:
		return JsonResponse({'response':'Error'})

def admin_under_trees(request):
	if check_user_authentication(request, 'Admin'):
		dic = {'data':MLMAdmin.objects.all(), 'categories':ProductCategory.objects.all(),}
		return render(request, 'admin_app/under-trees.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_delivery_charges(request):
	if check_user_authentication(request, 'Admin'):
		if request.method == 'POST':
			charge = request.POST.get('charge')
			DeliveryCharge.objects.all().delete()
			DeliveryCharge.objects.create(amount=charge)
			messages.success(request, 'Charges Updated Successfully')
			notification(request.user, 'Delivery Charges Changed.')
			return redirect('/admins/deliverycharges')
		dic = {'charge':DeliveryCharge.objects.all(),'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/delivery-charges.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_payment_info(request):
	if check_user_authentication(request, 'Admin'):
		dic = {
			'orders':Orders.objects.all(),
			'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/payment-info.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def admin_orders(request):
	if check_user_authentication(request, 'Admin'):
		dic = {
			'orders':OrderItems.objects.all(),
			'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/orders.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_pvpairvalue(request):
	if check_user_authentication(request, 'Admin'):
		if request.method == 'POST':
			new = request.POST.get('new')
			PVPairValue.objects.all().delete()
			PVPairValue.objects.create(pair_value=new)
			notification(request.user, 'PV Pair Value Changed')
			return redirect('/admins/setpvpair')
		dic = {'data':PVPairValue.objects.all(), 'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/set-pv-pair.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def admin_withdraw(request):
	if check_user_authentication(request, 'Admin'):
		dic = {'users':UserWithdrawRequest.objects.all(), 'vendors':VendorWithdrawRequest.objects.all(), 'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/withdraw.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def admin_change_withdraw_status(request):
	if check_user_authentication(request, 'Admin'):
		type_ = request.GET.get('t')
		id_ = request.GET.get('i')
		status = request.GET.get('s')
		if type_ == 'u':
			UserWithdrawRequest.objects.filter(id=id_).update(status=status)
			withdraw = UserWithdrawRequest.objects.get(id=id_)
			if status == '2':
				TDS_Log.objects.create(user=withdraw.user,amount=withdraw.amount, tds_amt=withdraw.tds)
				make_wallet_transaction(withdraw.user, (withdraw.amount+withdraw.tds), 'DEBIT')
				notification(withdraw.user, 'Rs'+str(withdraw.amount)+' debited from your wallet.')
			notification(withdraw.user, 'Withdraw Request Status Changed.')
		elif type_ == 'v':
			VendorWithdrawRequest.objects.filter(id=id_).update(status=status)
			withdraw = VendorWithdrawRequest.objects.get(id=id_)
			if status == '2':
				make_wallet_transaction(withdraw.user, withdraw.amount, 'DEBIT')
				notification(withdraw.user, 'Rs'+str(withdraw.amount)+' debited from your wallet.')
			notification(withdraw.user, 'Withdraw Request Status Changed.')
		messages.success(request, 'Status Changed Successfully')
		return redirect('/admins/withdraw')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def admin_query(request):
	if check_user_authentication(request, 'Admin'):
		dic = {'queries':Query.objects.all().order_by('-id'),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/query.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def admin_query_result(request):
	if check_user_authentication(request, 'Admin'):
		dic = {'query':Query.objects.get(id=request.GET.get('query_id')),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/query-result.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def admin_change_query_status(request):
	if check_user_authentication(request, 'Admin'):
		Query.objects.filter(id=request.GET.get('query')).update(status=request.GET.get('status'))
		user = Query.objects.get(id=request.GET.get('query')).user
		notification(user, 'Query Status Changed.')
		return JsonResponse({'response`	':'Success'})
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def admin_query_send_reply(request):
	if check_user_authentication(request, 'Admin'):
		Query.objects.filter(id=request.GET.get('query')).update(
			reply=request.GET.get('reply')
		)
		query = Query.objects.get(id=request.GET.get('query'))
		if query.anonymous:
			msg = '''Hi '''+query.name+''',

'''+query.reply+'''

Thanks & Regards,
Team AVPL'''
			EmailMessage('AVPL - Query Reply',msg,to=[query.email]).send()
			return JsonResponse({'response`	':'Success'})
		user = Query.objects.get(id=request.GET.get('query')).user
		notification(user, 'Admin Replied to Your Query')
		return JsonResponse({'response`	':'Success'})
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_set_pv_conversion(request):
	if check_user_authentication(request, 'Admin'):
		if request.method == 'POST':
			value = request.POST.get('new')
			PVConversionValue.objects.all().delete()
			PVConversionValue.objects.create(
				conversion_value = value
			)
			notification(request.user, 'User Share Percent Changed.')
			return redirect('/admins/setpvconversion')
		dic = {'data':PVConversionValue.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/set-pv-conversion.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_direct_referal(request):
	if check_user_authentication(request,'Admin'):
		if request.method == 'POST':
			value = request.POST.get('value')
			DirectReferalCommission.objects.all().delete()
			DirectReferalCommission.objects.create(
				percentage=value,
			)
			notification(request.user,'Direct Referal Commission Precent Changed.')
			return redirect('/admins/direct-referal')
		dic = {'data':DirectReferalCommission.objects.all(),
		'notification':get_notifications(request.user),
		'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/direct-referal.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_leadership_bonus_set(request):
	if check_user_authentication(request,'Admin'):
		if request.method == 'POST':
			value = request.POST.get('leader')
			target = request.POST.get('target')
			UserLeadershipBonusCommission.objects.all().delete()
			UserLeadershipBonusCommission.objects.create(
				percentage=value,
				target=target
			)
			notification(request.user,'Leadership Bonus Precent Changed.')
			return redirect('/admins/leadershipbonus')
		dic = {'data':UserLeadershipBonusCommission.objects.all(),
		'notification':get_notifications(request.user),
		'leadership_bonus':get_leadership_eligible_users(request),
		'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/leadership-bonus.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_travel_fund_set(request):
	if check_user_authentication(request,'Admin'):
		if request.method == 'POST':
			value = request.POST.get('value')
			target = request.POST.get('target')
			TravelFund.objects.all().delete()
			TravelFund.objects.create(
				percentage=value,
				target=target
			)
			notification(request.user,'Leadership Bonus Precent Changed.')
			return redirect('/admin/travelfund')
		dic = {'data':TravelFund.objects.all(),
		'notification':get_notifications(request.user),
		'travel_fund':get_travel_fund_eligible_users(request),
		'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/travel-fund.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_car_fund_set(request):
	if check_user_authentication(request,'Admin'):
		if request.method == 'POST':
			value = request.POST.get('value')
			target = request.POST.get('target')
			CarFund.objects.all().delete()
			CarFund.objects.create(
				percentage=value,
				target=target
			)
			notification(request.user,'Leadership Bonus Precent Changed.')
			return redirect('/admins/carfund')
		dic = {'data':CarFund.objects.all(),
		'notification':get_notifications(request.user),
		'car_fund':get_car_fund_eligible_users(request),
		'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/car-fund.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_house_fund_set(request):
	if check_user_authentication(request,'Admin'):
		if request.method == 'POST':
			value = request.POST.get('value')
			target = request.POST.get('target')
			HouseFund.objects.all().delete()
			HouseFund.objects.create(
				percentage=value,
				target=target
			)
			notification(request.user,'Leadership Bonus Precent Changed.')
			return redirect('/admins/housefund')
		dic = {'data':HouseFund.objects.all(),
		'notification':get_notifications(request.user),
		'house_fund':get_house_fund_eligible_users(request),
		'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/house-fund.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_directorship_fund_set(request):
	if check_user_authentication(request,'Admin'):
		if request.method == 'POST':
			value = request.POST.get('value')
			target = request.POST.get('target')
			DirectorshipFund.objects.all().delete()
			DirectorshipFund.objects.create(
				percentage=value,
				target=target
			)
			notification(request.user,'Leadership Bonus Precent Changed.')
			return redirect('/admins/directorshipfund')
		dic = {'data':DirectorshipFund.objects.all(),
		'notification':get_notifications(request.user),
		'directorship_fund':get_directorship_fund_eligible_users(request),
		'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/directorship-fund.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def admin_product_approval(request):
	if check_user_authentication(request, 'Admin'):
		dic = {'data':Product.objects.filter(status=False, product_rejection=False),
			'rejected_product':Product.objects.filter(status=False, product_rejection=True),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/product-approval.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def admin_activate_product(request):
	if check_user_authentication(request, 'Admin'):
		Product.objects.filter(id=request.GET.get('p')).update(status=True)
		user = Product.objects.get(id=request.GET.get('p')).store.vendor.user
		notification(user, 'Product Activated Successfully.')
		return redirect('/admins/productapproval')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_taxation(request):
	if check_user_authentication(request, 'Admin'):
		if request.method == 'POST':
			pay = request.POST.get('pay')
			TaxPay.objects.create(
				transaction_date = timezone.now(),
				tax_current = Tax.objects.all()[0].current_tax,
				tax_paid = pay,
				tax_remaining = (Tax.objects.all()[0].current_tax - float(pay))
			)
			Tax.objects.all().update(current_tax = (Tax.objects.all()[0].current_tax - float(pay)))
			return redirect('/admins/tax')
		dic = {'tax':Tax.objects.all(), 'transactions':TaxPay.objects.all()}
		return render(request, 'admin_app/tax.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

# def admin_users(request):
# 	if check_user_authentication(request, 'Admin'):
# 		print("printing here Users PV")
# 		pv=UserPV.objects.all()
# 		print(pv)
# 		dic = {'users':User.objects.all(),'pv':pv}
# 		return render(request, 'admin_app/users.html', dic)
# 	else:
# 		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def admin_users(request):
	if check_user_authentication(request, 'Admin'):
		users = User.objects.all()
		lt = []
		for x in users :
			if x.role.level.level == 'User':
				dic = {'user':x}
				dic.update(get_user_indecater(x))
				lt.append(dic)
			elif x.role.level.level == 'Vendor':
				lt.append({'user':x})
		print(lt)
		return render(request, 'admin_app/users.html',{'users':lt})
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def admin_users_delete(request):
	if check_user_authentication(request, 'Admin'):
		User.objects.filter(id=request.GET.get('i')).delete()
		messages.success(request, 'User Deleted Successfully')
		return redirect('/admins/users')
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def user_vendor_commission(request):
	if check_user_authentication(request, 'Admin'):
		if request.method == 'POST':
			new = request.POST.get('new')
			UserVendorCommission.objects.all().delete()
			UserVendorCommission.objects.create(percentage=new)
			notification(request.user, 'User Vendor Commission Changed')
			return redirect('/admins/uservendorcommission')
		dic = {'data':UserVendorCommission.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/set-user-vendor-commission.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_level_settings(request):
	if check_user_authentication(request, 'Admin'):
		if request.method == 'POST':
			levels = int(request.POST.get('levels'))
			groups = int(request.POST.get('groups'))
			if not len(Level_Settings.objects.all()) == 0:
				Level_Settings.objects.all().delete()
			level = Level_Settings.objects.create(
				levels = levels,
				groups = groups
			)
			for x in range(0, level.groups):
				Level_Group.objects.create(level = level)
			messages.success(request, 'Step 1 Configuration Completed Successfully, Please Configure the Level Groups to Complete Configuration')
			return redirect('/admins/level/settings/')
		levels = Level_Settings.objects.all()
		dic = {}
		if len(levels) > 0:
			count = 1
			lt = []
			for x in Level_Group.objects.filter(level=levels[0]):
				for y in range(0, x.no_of_levels):
					dic = {'level':count, 'percent':x.percent_per_level}
					lt.append(dic)
					count = count + 1
			dic = {'level':levels[0], 'groups':Level_Group.objects.filter(level=levels[0]), 'data':lt, 'data_len': len(lt)}
		return render(request, 'admin_app/level.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def admin_fetch_groups(request):
	if check_user_authentication(request, 'Admin'):
		levels = Level_Settings.objects.all()
		dic = {}
		if len(levels) > 0:
			dic = {'level':levels[0], 'groups':Level_Group.objects.filter(level=levels[0])}
		return render(request, 'admin_app/level-table.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_edit_group(request):
	if check_user_authentication(request, 'Admin'):
		if request.method == 'POST':
			levels = request.POST.get('levels')
			percent = request.POST.get('percent')
			group = Level_Group.objects.get(id=request.POST.get('group_id'))
			
			total_levels = int(levels)
			total_percent = float(levels)*float(percent)
			for x in Level_Group.objects.filter(level=group.level):
				total_levels = total_levels + x.no_of_levels
				total_percent = total_percent + (x.percent_per_level*x.no_of_levels)
			
			if total_levels > group.level.levels and total_percent > 100.0:
				return JsonResponse({'response':'Failed'})
			else:
				group.no_of_levels = levels
				group.percent_per_level = percent
				group.save()
				return JsonResponse({'response':'Success'})
	return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_min_cart_value(request):
	if check_user_authentication(request, 'Admin'):
		if request.method == 'POST':
			amount = request.POST.get('amount')
			Min_Amount_For_Free_Delivery.objects.all().delete()
			Min_Amount_For_Free_Delivery.objects.create(amount=amount)
			return redirect('/admins/minmumcartvalue/')
		dic = {'cart':Min_Amount_For_Free_Delivery.objects.get()}
		return render(request, 'admin_app/set-min-cart-value.html', dic)
	return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_billing_config(request):
	if check_user_authentication(request, 'Admin'):
		if request.method == 'POST':
			admin = request.POST.get('admin')
			pv = request.POST.get('pv')
			Billing_Config.objects.all().delete()
			Billing_Config.objects.create(
				admin_commission = admin,
				pv_percent = pv
			)
			messages.success(request, 'Billing Config Saved Successfully')
			return redirect('/admins/billing/config/')
		dic = {}
		if len(Billing_Config.objects.all()) > 0:
			dic = {'data':Billing_Config.objects.get()}
		return render(request, 'admin_app/billing-config.html', dic)
	return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_reject_product(request):
	if check_user_authentication(request, 'Admin'):
		reason = request.POST.get('reason')
		Product.objects.filter(id=request.POST.get('i')).update(product_reject_reason=reason,product_rejection=True,status=False)
		user = Product.objects.get(id=request.POST.get('i')).store.vendor.user
		notification(user, str('Product Rejected Beacause '+reason))
		return JsonResponse({'response':'Success'})
		#return redirect('/admins/productapproval')
	else:
		return redirect('/401/')

@csrf_exempt
def admin_update_product(request):
	if check_user_authentication(request, 'Admin'):
		product_name = request.GET.get('product_name')
		description = request.GET.get('description')
		Product.objects.filter(id=request.GET.get('i')).update(name=product_name,description=description)
		user = Product.objects.get(id=request.GET.get('i')).store.vendor.user
		notification(user,'Product Update by admin')
		return JsonResponse({'response':'Success'})
	else:
		return redirect('/401/')

def admin_gst_log(request):
	if check_user_authentication(request, 'Admin'):
		dic = {
			'order':GST_Log.objects.all().order_by('-id'),
			'orders':OrderItems.objects.all(),
			'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/gstlogs.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

def admin_tds_withdraw(request):
	if check_user_authentication(request, 'Admin'):
		dic = {
			'tds_log':TDS_Log.objects.all(),
			'users':UserWithdrawRequest.objects.all(), 'vendors':VendorWithdrawRequest.objects.all(), 'categories':ProductCategory.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/tdslogs.html', dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def terms(request):
	if check_user_authentication(request,'Admin'):
		if request.method == 'POST':
			title = request.POST.get('title')
			print(title, 'jkkkkkk')
			content = request.POST.get('content')
			print('content',content)
			termsandcondition.objects.all().delete()
			termsandcondition.objects.create(
				title=title,
				content=content
			)
		dic = {
			'data':termsandcondition.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/terms-condition.html',dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def privacy(request):
	if check_user_authentication(request,'Admin'):
		if request.method == 'POST':
			title = request.POST.get('title')
			content = request.POST.get('content')
			privacypolicy.objects.all().delete()
			privacypolicy.objects.create(
				title=title,
				content=content
			)
		dic = {
			'data':privacypolicy.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/privacy.html',dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def contact(request):
	if check_user_authentication(request,'Admin'):
		if request.method == 'POST':
			address= request.POST.get('address')
			contact_no= request.POST.get('phone')
			gmail_id= request.POST.get('gmail')
			facbook_id= request.POST.get('fb')
			instagram_id= request.POST.get('insta')
			twitter_id= request.POST.get('twitter')
			contact_us.objects.all().delete()
			contact_us.objects.create(
				address=address,
				contact_no=contact_no,
				gmail_id=gmail_id,
				facbook_id=facbook_id,
				instagram_id=instagram_id,
				twitter_id=twitter_id,
			)
			print(contact_us)
		dic = {
			'data':contact_us.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		dic.update(get_cart_len(request))
		dic.update(get_wishlist_len(request))
		return render(request, 'admin_app/contact.html',dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_about_us(request):
	if check_user_authentication(request,'Admin'):
		if request.method == 'POST':
			form = AboutForm(request.POST)
			# title = request.POST.get('title')
			# # content = request.POST.get('content')
			# image = request.FILES.get('file')
			# AboutUs.objects.all().delete()
			AboutUs.objects.create(
				title=title,
				content=content,
				image=image,

			)
		dic = {
			'data':AboutUs.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/about-us.html',dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_gallery(request):
	if check_user_authentication(request,'Admin'):
		if request.method == 'POST':
			title = request.POST.get('title')
			image = request.FILES.getlist('pict')
			content = request.POST.get('description')
			print(content)
			for i in image:
				Gallery.objects.create(
					title=title,
					image=i,
					content=content
					)
				
		dic = {
			'data':Gallery.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/gallery.html',dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

@csrf_exempt
def admin_blog(request):
	if check_user_authentication(request,'Admin'):
		if request.method == 'POST':
			title = request.POST.get('title')
			content = request.POST.get('content')
			image = request.FILES.get('file')
			Blog.objects.all().delete()
			Blog.objects.create(
				title=title,
				content=content,
				image=image,

			)
		dic = {
			'data':Blog.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/blog.html',dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')


@csrf_exempt
def admin_banner(request):
	if check_user_authentication(request,'Admin'):
		if request.method == 'POST':
			title = request.POST.get('title')
			print(title)
			sub_title = request.POST.get('sub_title')
			desc = request.POST.get('desc')
			link = request.POST.get('link')
			image = request.FILES.get('file')
			print(image, type(image))
			# HomeBanner.objects.all().delete()
			HomeBanner.objects.create(
				title=title,
				sub_title=sub_title,
				description=desc,
				link=link,
				image=image,

			)
		dic = {
			'data':HomeBanner.objects.all(),
			'notification':get_notifications(request.user),
			'notification_len':len(Notification.objects.filter(user=request.user, read=False)),
		}
		return render(request, 'admin_app/banner.html',dic)
	else:
		return HttpResponse('<h1>Error 403 : Unauthorized User <user not allowed to browse this url></h1>')

