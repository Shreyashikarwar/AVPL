from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

# Models Import 
# from .models import User, OTP,PasswordResetToken,Token

from main_app.models import *
from vendor_app.models import *
from admin_app.models import *
from user_app.models import *


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields ="__all__"




class PrivacyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = privacypolicy
        fields= "__all__"



class TermsandConditionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = termsandcondition
        fields= "__all__"

class OrderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = OrderItems
        fields= "__all__"
    def to_representation(self, instance):
        rep = super(OrderSerializer, self).to_representation(instance)
        rep['product'] = instance.product.name
        rep['quantity'] = instance.quantity
        rep['per_item_cost'] = instance.per_item_cost
        rep['subtotal'] = instance.subtotal
        rep['tax'] = instance.tax
        rep['total'] = instance.total
        rep['delivery_status'] = instance.delivery_status
        rep['delivered_on'] = instance.delivered_on
        rep['user'] = instance.order.user.username
        rep['order_date'] = instance.order.order_date
        rep['address'] = instance.order.address.id
        rep['point_value'] = instance.order.point_value
        rep['paid'] = instance.order.paid
        return rep

class AboutSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUs
        fields = "__all__"

class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = "__all__"


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields ="__all__"


class  HomeBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeBanner
        fields= "__all__"

class  StoreImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreImages
        fields= "__all__"
    def to_representation(self, instance):
        rep = super(StoreImagesSerializer, self).to_representation(instance)
        rep['vendor'] = instance.store.vendor.user.username
        rep['store_name'] = instance.store.name
        rep['description'] = instance.store.description
        rep['registration_number'] = instance.store.registration_number
        rep['closing_day'] = instance.store.closing_day
        rep['opening_time'] = instance.store.opening_time
        rep['closing_time'] = instance.store.closing_time

        return rep

class  ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields= "__all__"

class  ProductSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSubCategory
        fields= "__all__"
class  ProductSubSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSubSubCategory
        fields= "__all__"

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItems
        fields = "__all__"
    def to_representation(self, instance):
        rep= super(CartItemSerializer,self).to_representation(instance)
        rep['user'] = instance.cart.user.username
        rep['cart_id'] = instance.cart.id
        rep['subtotal'] = instance.cart.subtotal
        rep['delivery_charges'] = instance.cart.delivery_charges
        rep['tax'] = instance.cart.tax
        rep['total'] = instance.cart.total
        rep['self_pickup'] = instance.cart.self_pickup
        rep['product'] = instance.product.name
        rep['quantity'] = instance.quantity
        rep['per_item_cost'] = instance.per_item_cost
        rep['total_cost'] = instance.total_cost

        return rep


class QuerySerializer(serializers.ModelSerializer):
    class Meta:
        model= Query
        fields="__all__"




class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model= contact_us
        fields="__all__"


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields ="__all__"
    def to_representation(self, instance):
        rep = super(WalletSerializer, self).to_representation(instance)
        rep['username'] = instance.wallet.user.username
        rep['current_balance'] = instance.wallet.current_balance

        return rep

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"

class WishlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishlistItems
        fields = '__all__'


class ProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = "__all__"
    def to_representation(self, instance):
        rep = super(ProductImagesSerializer, self).to_representation(instance)
        rep['store'] = instance.product.store.name
        rep['store_id'] = instance.product.store.id
        rep['category'] = instance.product.category.name
        # rep['category_img'] = instance.product.category.image
        rep['subcategory'] = instance.product.subcategory.name
        # rep['subcategory_img'] = instance.product.subcategory.image
        rep['subsubcategory'] = instance.product.subsubcategory.name
        # rep['subsubcategory_img'] = instance.product.subsubcategory.image
        rep['brand'] = instance.product.brand.name
        rep['brand_id'] = instance.product.brand.id
        rep['name'] = instance.product.name
        rep['description'] = instance.product.description
        rep['mrp'] = instance.product.mrp
        rep['stock'] = instance.product.stock
        rep['price'] = instance.product.price
        rep['weight'] = instance.product.weight
        rep['product_reject_reason'] = instance.product.product_reject_reason
        rep['product_rejection'] = instance.product.product_rejection
        rep['status'] = instance.product.status
        rep['offer_status'] = instance.product.offer
        rep['discount'] = instance.product.discount
        rep['featured_status'] = instance.product.featured


        return rep

class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = "__all__"

        
class StoreSerializerobj(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = "__all__"


class UserWithdrawRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWithdrawRequest
        fields = "__all__"


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreImages
        fields = "__all__"
    def to_representation(self, instance):
        rep = super(StoreSerializer, self).to_representation(instance)
        rep['vendor'] = instance.store.vendor.user.username
        rep['name'] = instance.store.name
        rep['description'] = instance.store.description
        rep['registration_number'] = instance.store.registration_number
        rep['closing_day'] = instance.store.closing_day
        rep['opening_time'] = instance.store.opening_time
        rep['closing_time'] = instance.store.closing_time

        return rep

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
