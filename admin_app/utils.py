from django.contrib.auth.models import User
from user_app.utils import *
from user_app.models import *
from admin_app.models import *
from main_app.utils import *
from main_app.models import *
from main_app.mlm_utils import *
import datetime

def get_eligible_users():
	eligible = []
	for x in User.objects.all():
		pv = 0.0
		d = datetime.datetime.now()
		try:
			if x.role.level.level == 'User':
				for order in Orders.objects.filter(user=x):
					if order.order_date.strftime("%m") == d.strftime("%m"):
						pv = pv + order.point_value
				if pv > 50.0:
					eligible.append(x)
		except Exception as e:
			continue
	print(eligible)
	return eligible

def fetch_pv_pair_users():
	pair_value = PVPairValue.objects.all()[0].pair_value
	lt = []
	lt2 = []
	total=0
	for x in get_eligible_users():
		try:
			if x.role.level.level == 'User':
				total_pv1=0.0
				total_pv2=0.0
				total_pv3=0.0
				pv = fetch_pv(x)
				if UserPV.objects.filter(user=x).exists():
					print(pv, '111')
					UserPV.objects.filter(user=x).update(right_pv=pv['right'], left_pv=pv['left'])
				else:
					print(pv,'222')
					UserPV.objects.create(user=x, right_pv=pv['right'], left_pv=pv['left'])
				outstanding_pv = 0.0
				user_pv = UserPV.objects.get(user=x)
				if user_pv.left_pv == user_pv.right_pv:
					total_pv1 = user_pv.left_pv + user_pv.right_pv
					outstanding_pv = user_pv.left_pv + user_pv.level_pv
					PV_data.objects.create(user=x,match_pv=outstanding_pv)
					UserPV.objects.filter(user=x).update(right_pv=0, left_pv=0)
				elif user_pv.left_pv > user_pv.right_pv:
					total_pv2 = user_pv.left_pv + user_pv.right_pv
					# print('total_pv2', total_pv2)
					print(x, user_pv.right_pv)
					outstanding_pv = user_pv.right_pv + user_pv.level_pv
					PV_data.objects.create(user=x,match_pv=outstanding_pv)
					print('ewwwwwwwwwww', outstanding_pv)
					UserPV.objects.filter(user=x).update(right_pv=0, left_pv=(user_pv.left_pv-user_pv.right_pv))
				elif user_pv.left_pv < user_pv.right_pv:
					total_pv3 = user_pv.left_pv + user_pv.right_pv
					print('total_pv3=====>', total_pv3)
					outstanding_pv = user_pv.left_pv + user_pv.level_pv
					print('pvvvvvvv', outstanding_pv)
					PV_data.objects.create(user=x,match_pv=outstanding_pv)
					UserPV.objects.filter(user=x).update(right_pv=(user_pv.right_pv-user_pv.left_pv), left_pv=0.0) 
				outstanding_pair = round(outstanding_pv/pair_value, 0)
				# print('outstanding_pair=========>', outstanding_pair)
				total_pv = total_pv1 + total_pv2 + total_pv3
				total +=total_pv
				# print('total', total)

				UserData.objects.filter(user=x).update(pv=0.0)
				lt.append({'user':x, 'pairs':outstanding_pair, 'total':total})
				print(lt,'<====')
				
				# total = lt[-1]	
			# lt2.append(total)
		except:
			continue
	return lt

def send_profit_to_users():
	share = 0.0
	try:
		share = PVConversionValue.objects.all()[0].conversion_value
	except:
		share = 0.0
	pv_pairs = fetch_pv_pair_users()
	cal_pv = 0.0
	d = datetime.datetime.now()
	for pv_trn in PVTransactions.objects.all():
		if pv_trn.transaction_date.strftime("%m") == d.strftime("%m"):
			cal_pv += pv_trn.total_pv

	profit  = ((round(cal_pv,0))/100)*share
	print('profit===>', profit)
	total_pairs = 0
	per_pair_value = 0
	for x in pv_pairs:
		print('xxx',x, x['pairs'])
		print(total_pairs)
		total_pairs = total_pairs + x['pairs']
	if total_pairs == 0:
		per_pair_value = 0
	else:
		print("total_pairs", total_pairs)
		per_pair_value = profit/total_pairs
		print("per_pair_value", per_pair_value  )
	current_balance = Commission.objects.all()[0].current_balance
	print(current_balance)
	print(total_pairs*per_pair_value)
	if current_balance > total_pairs*per_pair_value and total_pairs !=0:
		for x in pv_pairs:
			print("llll",x)
			if x['pairs'] != 0:
				Commission.objects.all().update(current_balance = current_balance - x['pairs']*per_pair_value)
				make_wallet_transaction(x['user'], round((x['pairs']*per_pair_value), 2), 'CREDIT')
		make_commission_transaction(profit, 'DEBIT')
		Yearly_PV.objects.all().update(pv = pv + cal_pv)
		if cal_pv:
			Monthly_PV.objects.create(pv = cal_pv)
		if len(Savings.objects.all()) <= 0:
			Savings.objects.create()
		savings_balance = Savings.objects.all()[0].savings
		current_balance = Commission.objects.all()[0].current_balance
		print('lllllll',current_balance)
		# Savings.objects.all().update(savings = savings_balance + current_balance)
		# Commission.objects.all().update(current_balance=0.0)
	# elif current_balance > total_pairs*per_pair_value and total_pairs ==0:
	# 	if len(Savings.objects.all()) <= 0:
	# 		Savings.objects.create()
	# 	savings_balance = Savings.objects.all()[0].savings
	# 	current_balance = Commission.objects.all()[0].current_balance
	# 	print('hffg',current_balance)
		# Savings.objects.all().update(savings = savings_balance + current_balance)
		# Commission.objects.all().update(current_balance=0.0)
	elif current_balance<total_pairs*per_pair_value and total_pairs !=0:
		print('HJHHHHHHHHHHHHH')
		message.error('Do not have sufficient Amount!')


def get_leadership_eligible_users(request):
	eligible = []
	pv = 0.0
	for x in User.objects.all():
		
		d = datetime.datetime.now()
		try:
			if x.role.level.level == 'User':
				for pv_trn in PVTransactions.objects.filter(user=x):
					if pv_trn.transaction_date.strftime("%m") == d.strftime("%m"):
						pv += pv_trn.total_pv
				for user_pv in UserPV.objects.filter(user=x):
					if user_pv.right_pv > user_pv.left_pv and user_pv.left_pv>=int(UserLeadershipBonusCommission.objects.all()[0].target):
						eligible.append(x)
					elif user_pv.right_pv < user_pv.left_pv and user_pv.right_pv>=int(UserLeadershipBonusCommission.objects.all()[0].target):
						eligible.append(x)
					elif user_pv.right_pv == user_pv.left_pv and user_pv.left_pv>=int(UserLeadershipBonusCommission.objects.all()[0].target):
						eligible.append(x)
				
		except Exception as e:
			continue
	if len(eligible) != 0:
		bonus = int(UserLeadershipBonusCommission.objects.all()[0].percentage)*pv/(len(eligible)*100)
		return [{'user':eligible, 'bonus':bonus, 'month':d.strftime("%m")}]
	else:
		return None


def get_travel_fund_eligible_users(request):
	eligible = []
	pv = 0.0
	for x in User.objects.all():
		
		d = datetime.datetime.now()
		try:
			if x.role.level.level == 'User':
				for pv_trn in PVTransactions.objects.filter(user=x):
					if pv_trn.transaction_date.strftime("%m") == d.strftime("%m"):
						pv += pv_trn.total_pv
					
				for user_pv in UserPV.objects.filter(user=x):
					if user_pv.right_pv > user_pv.left_pv and user_pv.left_pv>=TravelFund.objects.all()[0].target:
						eligible.append(x)
					elif user_pv.right_pv < user_pv.left_pv and user_pv.right_pv>=TravelFund.objects.all()[0].target:
						eligible.append(x)
					elif user_pv.right_pv == user_pv.left_pv and user_pv.left_pv>=TravelFund.objects.all()[0].target:
						eligible.append(x)
		except Exception as e:
			continue
	if len(eligible) !=0:
		bonus = int(TravelFund.objects.all()[0].percentage)*pv/(len(eligible)*100)
		return [{'user':eligible, 'bonus':bonus, 'month':d.strftime("%m")}]
	else:
		return None

def get_car_fund_eligible_users(request):
	eligible = []
	pv = 0.0
	for x in User.objects.all():
		
		d = datetime.datetime.now()
		try:
			if x.role.level.level == 'User':
				for pv_trn in PVTransactions.objects.filter(user=x):
					if pv_trn.transaction_date.strftime("%m") == d.strftime("%m"):
						pv += pv_trn.total_pv
					
				for user_pv in UserPV.objects.filter(user=x):
					if user_pv.right_pv > user_pv.left_pv and user_pv.left_pv>=CarFund.objects.all()[0].target:
						eligible.append(x)
					elif user_pv.right_pv < user_pv.left_pv and user_pv.right_pv>=CarFund.objects.all()[0].target:
						eligible.append(x)
					elif user_pv.right_pv == user_pv.left_pv and user_pv.left_pv>=CarFund.objects.all()[0].target:
						eligible.append(x)
		except Exception as e:
			continue
	if len(eligible) !=0:
		bonus = int(CarFund.objects.all()[0].percentage)*pv/(len(eligible)*100)
		print(bonus)
		return [{'user':eligible, 'bonus':bonus, 'month':d.strftime("%m")}]
	else:
		return None

def get_house_fund_eligible_users(request):
	eligible = []
	pv = 0.0
	for x in User.objects.all():
		
		d = datetime.datetime.now()
		try:
			if x.role.level.level == 'User':
				for pv_trn in PVTransactions.objects.filter(user=x):
					if pv_trn.transaction_date.strftime("%m") == d.strftime("%m"):
						pv += pv_trn.total_pv
					
				for user_pv in UserPV.objects.filter(user=x):
					if user_pv.right_pv > user_pv.left_pv and user_pv.left_pv>=CarFund.objects.all()[0].target:
						eligible.append(x)
					elif user_pv.right_pv < user_pv.left_pv and user_pv.right_pv>=CarFund.objects.all()[0].target:
						eligible.append(x)
					elif user_pv.right_pv == user_pv.left_pv and user_pv.left_pv>=CarFund.objects.all()[0].target:
						eligible.append(x)
		except Exception as e:
			continue
	if len(eligible) !=0:
		bonus = int(HouseFund.objects.all()[0].percentage)*pv/(len(eligible)*100)
		print(bonus)
		return [{'user':eligible, 'bonus':bonus, 'month':d.strftime("%m")}]
	else:
		return None

def get_directorship_fund_eligible_users(request):
	eligible = []
	pv = 0.0
	for x in User.objects.all():
		
		d = datetime.datetime.now()
		try:
			if x.role.level.level == 'User':
				for pv_trn in PVTransactions.objects.filter(user=x):
					if pv_trn.transaction_date.strftime("%m") == d.strftime("%m"):
						pv += pv_trn.total_pv
					
				for user_pv in UserPV.objects.filter(user=x):
					if user_pv.right_pv > user_pv.left_pv and user_pv.left_pv>=DirectorshipFund.objects.all()[0].target:
						eligible.append(x)
					elif user_pv.right_pv < user_pv.left_pv and user_pv.right_pv>=DirectorshipFund.objects.all()[0].target:
						eligible.append(x)
					elif user_pv.right_pv == user_pv.left_pv and user_pv.left_pv>=DirectorshipFund.objects.all()[0].target:
						eligible.append(x)
		except Exception as e:
			continue
	if len(eligible) !=0:
		bonus = int(DirectorshipFund.objects.all()[0].percentage)*pv/(len(eligible)*100)
		print(bonus)
		return [{'user':eligible, 'bonus':bonus, 'month':d.strftime("%m")}]
	else:
		return None