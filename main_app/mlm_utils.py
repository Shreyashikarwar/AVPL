from django.contrib.auth.models import User
from django.contrib import messages
from main_app.models import *
from user_app.models import *

def add_to_mlm(request):
	parent = User.objects.get(id=request.session['parent'])
	parent_type = request.session['parent_type']
	child = User.objects.get(id=request.session['child'])
	if parent_type == 'Admin':
		MLMAdmin.objects.create(child=child)
		MLM.objects.create(parent=parent, node=child)
		messages.success(request, 'You have been add under Admin')
	if parent_type == 'User':
		if MLM.objects.get(node=parent).left == None:
			print('hello')
			MLM.objects.filter(node=parent).update(left=child)
			MLM.objects.create(parent=parent, node=child)
			messages.success(request, 'You have been add under '+parent.usr.first_name)
		elif MLM.objects.get(node=parent).right == None:
			MLM.objects.filter(node=parent).update(right=child)
			MLM.objects.create(parent=parent, node=child)
			messages.success(request, 'You have been add under '+parent.usr.first_name)

def fetch_empty_nodes(node):
	mlm = MLM.objects.get(node=node)
	right = fetch_one_side_empty_nodes(mlm.right, [])
	left = fetch_one_side_empty_nodes(mlm.left, [])
	return {'left':left, 'right':right}

def fetch_one_side_empty_nodes(node, members):
	if node is not None:
		mlm = MLM.objects.get(node=node)
		if mlm.left == None and mlm.right != None:
			members.append(node)
			fetch_one_side_empty_nodes(mlm.right, members)
		elif mlm.right == None and mlm.left != None:
			members.append(node)
			fetch_one_side_empty_nodes(mlm.left, members)
		elif mlm.left != None and mlm.right != None:
			fetch_one_side_empty_nodes(mlm.left, members)
			fetch_one_side_empty_nodes(mlm.right, members)
		elif mlm.left == None and mlm.right == None:
			members.append(mlm.node)
		return members
	else:
		return members

def calculate_point_value_on_order(cart):
	cartitems = CartItems.objects.filter(cart=cart)
	total_pv = 0.0
	for x in cartitems:
		pv_percent = PointValue.objects.get(category=x.product.category)
		pv = (x.total_cost/100)*pv_percent.percentage
		total_pv = total_pv + pv
	return total_pv

def fetch_nodes(node):
	mlm = MLM.objects.get(node=node)
	right = fetch_one_side_nodes(mlm.right, [])
	left = fetch_one_side_nodes(mlm.left, [])
	return {'left':left, 'right':right}

def fetch_one_side_nodes(node, members):
	if node is not None:
		mlm = MLM.objects.get(node=node)
		if mlm.left == None and mlm.right != None:
			members.append(node)
			fetch_one_side_nodes(mlm.right, members)
		elif mlm.right == None and mlm.left != None:
			members.append(node)
			fetch_one_side_nodes(mlm.left, members)
		elif mlm.left != None and mlm.right != None:
			members.append(node)
			fetch_one_side_nodes(mlm.left, members)
			fetch_one_side_nodes(mlm.right, members)
		elif mlm.left == None and mlm.right == None:
			members.append(mlm.node)
		return members
	else:
		return members

# feching Parents of particular Node
def fetch_parent_nodes(node, parents):
	if node is not None:
		mlm = MLM.objects.get(node = node)
		if not mlm.parent.role.level.level == 'Admin':
			parents.append(mlm.parent)
			fetch_parent_nodes(mlm.parent, parents)
		return parents
	else:
		return parents

