
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings


def ajax_load_address(request):
    address_id = request.GET.get('address_id')
    address = ShippingAddress.objects.get(id=address_id)
    data = {
        'id': address.id,
        # Include other fields as needed
    }
    return JsonResponse(data)

class Order(models.Model):
    order_id = models.AutoField(db_column='Order_ID', primary_key=True)  # Field name made lowercase.
    user = models.ForeignKey('User', models.DO_NOTHING, db_column='User_ID')  # Field name made lowercase.
    total_price = models.DecimalField(db_column='Total_Price', max_digits=10, decimal_places=2)  # Field name made lowercase.
    order_status = models.CharField(db_column='Order_Status', max_length=9)  # Field name made lowercase.
    payment_info = models.ForeignKey('PaymentInfo', models.DO_NOTHING, db_column='Payment_Info_ID')  # Field name made lowercase.
    payment_status = models.CharField(db_column='Payment_Status', max_length=10)  # Field name made lowercase.
    order_datetime = models.DateTimeField(db_column='Order_Datetime', blank=True, null=True)  # Field name made lowercase.
    shipping_address = models.ForeignKey('ShippingAddress', models.DO_NOTHING, db_column='Shipping_Address_ID')  # Field name made lowercase.
    session_id = models.ForeignKey('Session', models.DO_NOTHING, db_column='session_id', blank=False, null=False)

    class Meta:
        managed = True
        db_table = 'order'


class OrderItem(models.Model):
    order_item_id = models.AutoField(db_column='Order_Item_ID', primary_key=True)  # Field name made lowercase.
    order = models.ForeignKey(Order, models.DO_NOTHING, related_name='order_items', db_column='Order_ID')  # Field name made lowercase.
    product = models.ForeignKey('Product', models.DO_NOTHING, db_column='Product_ID')  # Field name made lowercase.
    quantity = models.IntegerField(db_column='Quantity')  # Field name made lowercase.
    price = models.DecimalField(db_column='Price', max_digits=10, decimal_places=2)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'order_item'


class PaymentInfo(models.Model):
    payment_info_id = models.AutoField(db_column='Payment_Info_ID', primary_key=True)  # Field name made lowercase.
    payment_method = models.CharField(db_column='Payment_Method', max_length=50, blank=True, null=True)  # Field name made lowercase.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Field name made lowercase.
    card_type = models.CharField(db_column='card_type', max_length=50, blank=True, null=True)
    card_number = models.CharField(db_column='card_number', max_length=255, blank=False, null=False)
    cvv = models.CharField(db_column='cvv',max_length=255, blank=False, null=False)
    card_nickname = models.CharField(db_column='nickname',blank=False,null=False, max_length=45)


    class Meta:
        managed = True
        db_table = 'payment_info'


class Product(models.Model):
    product_id = models.AutoField(db_column='Product_ID', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=255)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    price = models.DecimalField(db_column='Price', max_digits=10, decimal_places=2)  # Field name made lowercase.
    in_stock_quantity = models.IntegerField(db_column='In_Stock_Quantity')  # Field name made lowercase.
    image = models.ImageField(upload_to='product_images/', db_column='image')
    is_active = models.BooleanField(default=True, db_column='is_active')

    class Meta:
        managed = True
        db_table = 'product'


class Session(models.Model):
    session_id = models.CharField(db_column='Session_ID', max_length=255, blank=False, null=False, primary_key=True)  # Field name made lowercase.
    user = models.ForeignKey('User', models.DO_NOTHING, db_column='User_ID', blank=True, null=True)  # Field name made lowercase.
    session_datetime = models.DateTimeField(db_column='Session_Datetime', default=timezone.now)  # Field name made lowercase.
    latest_activity = models.DateTimeField(db_column='latest_activity', default=timezone.now)

    def __str__(self):
        return self.session_id

    class Meta:
        managed = True
        db_table = 'session'


class ShippingAddress(models.Model):
    shipping_address_id = models.AutoField(db_column='Shipping_Address_ID', primary_key=True)  # Field name made lowercase.
    user = models.ForeignKey('User', models.DO_NOTHING, db_column='User_ID', blank=False, null=False)  # Field name made lowercase.
    street = models.CharField(db_column='Street', max_length=255, blank=False, null=False,  )  # Field name made lowercase.
    city = models.CharField(db_column='City', max_length=255, blank=False, null=False)  # Field name made lowercase.
    state = models.CharField(db_column='State', max_length=255, blank=False, null=False)  # Field name made lowercase.
    country = models.CharField(db_column='Country', max_length=255, blank=False, null=False)  # Field name made lowercase.
    postal_code = models.CharField(db_column='Postal_Code', max_length=20, blank=False, null=False)  # Field name made lowercase.
    nickname = models.CharField(db_column='nickname',max_length=20)

    class Meta:
        managed = True
        db_table = 'shipping_address'

class CustomUserManager(BaseUserManager):

    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})
class User(AbstractBaseUser):
    user_id = models.AutoField(db_column='User_ID', primary_key=True)
    username = models.CharField(db_column='Username', max_length=255, unique=True)  # Field name made lowercase.
    email_address = models.CharField(db_column='Email_Address', unique=True, max_length=255)  # Field name made lowercase.
    password = models.CharField(db_column='PasswordHash', max_length=256)  # Field name made lowercase.
    role = models.CharField(db_column='Role', max_length=255)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreatedAt', blank=True, null=True,default=timezone.now)  # Field name made lowercase.
    last_login = models.DateTimeField(db_column='LastLogin', blank=True, null=True,default=timezone.now)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email_address']

    objects = CustomUserManager()

    class Meta:
        managed = True
        db_table = 'user'


class Cart(models.Model):
    cart_id = models.AutoField(db_column='Cart_ID', primary_key=True)  # Field name made lowercase.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='User_ID', blank=True, null=True)  # Field name made lowercase.
    session_id = models.ForeignKey(Session, models.DO_NOTHING, db_column='Session_ID', blank=False, null=False)  # Field name made lowercase.
    is_active = models.IntegerField(db_column='is_active',blank=False,null=False)

    class Meta:
        managed = True
        db_table = 'cart'


class CartItem(models.Model):
    cart_item_id = models.AutoField(db_column='Cart_Item_ID', primary_key=True)  # Field name made lowercase.
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, db_column='Cart_ID', blank=True, null=True)  # Field name made lowercase.
    product = models.ForeignKey('Product', on_delete=models.CASCADE, db_column='Product_ID', blank=True, null=True)  # Field name made lowercase.
    quantity = models.IntegerField(db_column='Quantity', default=1)  # Field name made lowercase.
    added_item_datetime = models.DateTimeField(db_column='Added_Item_Datetime',auto_now_add=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'cart_item'





