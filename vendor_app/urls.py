from django.contrib import admin
from django.urls import path
from vendor_app.views import *

urlpatterns = [
    path('', vendor_dashboard),
    path('storeinfo', store_info),
    path('verification', vendor_doc),
    path('addproduct', add_product),
    path('addproductimages', add_product_images),
    path('addproductvariant', add_product_variant),
    path('fetchsubcategory', fetch_sub_category),
    path('fetchsubsubcategory', fetch_sub_sub_category),
    path('productlist', vendor_product_list),
    path('profile', vendor_profile),
    path('edit-profile', edit_vendor_profile),
    path('product', vendor_product),
    path('productbasicedit', vendor_product_basic_edit),
    path('fetchvariantvalue', fetch_variant_value),
    path('orders', vendor_orders),
    path('orderdetail', vendor_order_detail),
    path('changeorderstatus', vendor_change_order_status),
    path('completeorders', vendor_complete_orders),
    path('brand', vendor_brand),
    path('fetchbrands', fetch_brands),
    path('deleteproductimage', vendor_delete_product_image),
    path('deleteproductvariant', vendor_delete_product_variant),
    path('outofstock', vendor_product_out_of_stock),
    path('paymenttransactions', vendor_payment_transactions),
    path('wallet', vendor_wallet_dash),
    path('withdraw', vendor_withdraw),
    path('help', vendor_help),
    #recharge
    path('businesslimit', vendor_Business_limit_dash),
    path('businesslimittransaction', vendor_recharge),
    path('capturerecharge', capture_recharge_payment),
    path('userSubscriptionRequest',userSubscriptionRequest),
    path('activateusersubscription',vendor_activate_subscription),
    path('billing/requests/',vendor_billing_requests),
    path('billing/requests/confirm/', vendor_confirm_billing_requests),

    path('balanacetransfer', vendorbalanacetransfer, name='balanacetransfer'),
    path('otpvalidation', transfer_amount_vendor, name='otpvalidation'),


]
