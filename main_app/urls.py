#Main App URL Config

from django.urls import path, include
from main_app.views import *
from main_app.apiviews import *


urlpatterns = [


	path('test/', test),
	path('', home),
	path('login/', login_view),
	path('logout/', logout_view),
	path('register/', register),
	path('show/', show),
	path('otp/', otp),
	path('create/', create_vendor),
	path('verify/', verify_account),
	path('categories/', home_categories),
	path('storecategories/', home_store_categories),
	path('getlocation/', get_location),
	path('productpage/', product_page),
	path('productdetail/', product_detail),
	path('product_filter_range/', product_filter_range),
	path('term-and-condition/', termsancondition),
	path('contect-us/', contactus),
	path('privacy-policy/', privacy_policy),
	path('about-us/', about),
	path('subcategories/', home_subcategories),
	path('storesubcategories/', home_store_subcategories),
	path('subsubcategories/', home_subsubcategories),
	path('storesubsubcategories/', home_store_subsubcategories),
	path('contact/', contact),
	path('about/', about),
	path('blog/', blog),
	path('gallery/', gallery_data),

	path('faq/', faq),
	path('selectaddress/', checkout_1),
	path('ordersummary/', checkout_2),
	path('placeorder/', place_order),
	path('forgot/', forgotpassword),
	path('check/', check_email),
	path('forgot-otp/', forgot_otp),
	path('verifyforgot/', verify_forgot),
	path('change-password/', change_password),
	path('captureonlinepayment/', capture_online_payment, ),
	path('search/', search_result),
	path('search2/', search_result2),
	path('applyfilters/', apply_filters),
	path('removefilters/', remove_filters),
	path('marknotificationread/', mark_notification_read),
	path('resendotp/', resend_otp),
	path('store/', store_page),
	path('contact/save/', contact_us_save),
	path('categorywise/store/', category_wise_store),
	path('admins/', include('admin_app.urls')),
	path('vendor/', include('vendor_app.urls')),
	path('user/', include('user_app.urls')),
	path('userpv/',userpv),
	path('parents/',show_parent),#testing
	path('assign_store/',assign_store),

	path('store_details/<int:id>/', store_details),



	# AVPL API Section Urls
	
	# AUTH Section 
	path('api/login/',api_login),


    # DASHBOARD Section 
	path('api/product_data/',product_data),
	path('api/product_details/',product_details),

	path('api/privacy_and_policy/',privacy_and_policy),
	path('api/terms_condition/',terms_condition),
	path('api/add_to_cart/',add_to_cart),
	path('api/add_to_wishlist/',add_to_wishlist),
	path('api/my_order/',my_order),
	path('api/banner/',bnanner_api_section),
	path('api/query/',user_query_data),

	path('api/contact_data/',contact_data),
	path('api/wallet/',wallet_details),
	path('api/user_address/',user_address),
	path('api/order_place/',order_place),
	path('api/send_otp/',send_otp),
	path('api/otp_check/',otp_check),
	path('api/password_changed/',password_changed),
	path('api/userprofile/',userprofile),
	path('api/storedata/',storedata),
	path('api/storeproductdata/',storeproductdata),
	path('api/notification/',notification),
	path('api/category_detail/',category_detail),
	path('api/nearby_store/',nearby_store),
	path('api/offer_and_featured/',offer_and_featured),
	path('api/user_downline/',user_downline),
	path('api/latest_product/',latest_product),
	path('api/product_rating/',product_rating),
	










]
