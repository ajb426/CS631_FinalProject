# Generated by Django 5.0.3 on 2024-04-16 21:59

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.AutoField(db_column='User_ID', primary_key=True, serialize=False)),
                ('username', models.CharField(db_column='Username', max_length=255, unique=True)),
                ('email_address', models.CharField(db_column='Email_Address', max_length=255, unique=True)),
                ('password', models.CharField(db_column='PasswordHash', max_length=256)),
                ('role', models.CharField(db_column='Role', max_length=255)),
                ('createdate', models.DateTimeField(blank=True, db_column='CreatedAt', default=django.utils.timezone.now, null=True)),
                ('last_login', models.DateTimeField(blank=True, db_column='LastLogin', default=django.utils.timezone.now, null=True)),
            ],
            options={
                'db_table': 'user',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('product_id', models.AutoField(db_column='Product_ID', primary_key=True, serialize=False)),
                ('name', models.CharField(db_column='Name', max_length=255)),
                ('description', models.TextField(blank=True, db_column='Description', null=True)),
                ('price', models.DecimalField(db_column='Price', decimal_places=2, max_digits=10)),
                ('in_stock_quantity', models.IntegerField(db_column='In_Stock_Quantity')),
                ('image', models.ImageField(db_column='image', upload_to='product_images/')),
                ('is_active', models.BooleanField(db_column='is_active', default=True)),
            ],
            options={
                'db_table': 'product',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('cart_id', models.AutoField(db_column='Cart_ID', primary_key=True, serialize=False)),
                ('is_active', models.IntegerField(db_column='is_active')),
                ('user', models.ForeignKey(blank=True, db_column='User_ID', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'cart',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='PaymentInfo',
            fields=[
                ('payment_info_id', models.AutoField(db_column='Payment_Info_ID', primary_key=True, serialize=False)),
                ('payment_method', models.CharField(blank=True, db_column='Payment_Method', max_length=50, null=True)),
                ('card_type', models.CharField(blank=True, db_column='card_type', max_length=50, null=True)),
                ('card_number', models.CharField(db_column='card_number', max_length=255)),
                ('cvv', models.CharField(db_column='cvv', max_length=255)),
                ('card_nickname', models.CharField(db_column='nickname', max_length=45)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'payment_info',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.AutoField(db_column='Order_ID', primary_key=True, serialize=False)),
                ('total_price', models.DecimalField(db_column='Total_Price', decimal_places=2, max_digits=10)),
                ('order_status', models.CharField(db_column='Order_Status', max_length=9)),
                ('payment_status', models.CharField(db_column='Payment_Status', max_length=10)),
                ('order_datetime', models.DateTimeField(blank=True, db_column='Order_Datetime', null=True)),
                ('user', models.ForeignKey(db_column='User_ID', on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('payment_info', models.ForeignKey(db_column='Payment_Info_ID', on_delete=django.db.models.deletion.DO_NOTHING, to='myapp.paymentinfo')),
            ],
            options={
                'db_table': 'order',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('order_item_id', models.AutoField(db_column='Order_Item_ID', primary_key=True, serialize=False)),
                ('quantity', models.IntegerField(db_column='Quantity')),
                ('price', models.DecimalField(db_column='Price', decimal_places=2, max_digits=10)),
                ('order', models.ForeignKey(db_column='Order_ID', on_delete=django.db.models.deletion.DO_NOTHING, related_name='order_items', to='myapp.order')),
                ('product', models.ForeignKey(db_column='Product_ID', on_delete=django.db.models.deletion.DO_NOTHING, to='myapp.product')),
            ],
            options={
                'db_table': 'order_item',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('cart_item_id', models.AutoField(db_column='Cart_Item_ID', primary_key=True, serialize=False)),
                ('quantity', models.IntegerField(db_column='Quantity', default=1)),
                ('added_item_datetime', models.DateTimeField(auto_now_add=True, db_column='Added_Item_Datetime')),
                ('cart', models.ForeignKey(blank=True, db_column='Cart_ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.cart')),
                ('product', models.ForeignKey(blank=True, db_column='Product_ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.product')),
            ],
            options={
                'db_table': 'cart_item',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('session_id', models.CharField(db_column='Session_ID', max_length=255, primary_key=True, serialize=False)),
                ('session_datetime', models.DateTimeField(db_column='Session_Datetime', default=django.utils.timezone.now)),
                ('latest_activity', models.DateTimeField(db_column='latest_activity', default=django.utils.timezone.now)),
                ('user', models.ForeignKey(blank=True, db_column='User_ID', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'session',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='order',
            name='session_id',
            field=models.ForeignKey(db_column='session_id', on_delete=django.db.models.deletion.DO_NOTHING, to='myapp.session'),
        ),
        migrations.AddField(
            model_name='cart',
            name='session_id',
            field=models.ForeignKey(db_column='Session_ID', on_delete=django.db.models.deletion.DO_NOTHING, to='myapp.session'),
        ),
        migrations.CreateModel(
            name='ShippingAddress',
            fields=[
                ('shipping_address_id', models.AutoField(db_column='Shipping_Address_ID', primary_key=True, serialize=False)),
                ('street', models.CharField(db_column='Street', max_length=255)),
                ('city', models.CharField(db_column='City', max_length=255)),
                ('state', models.CharField(db_column='State', max_length=255)),
                ('country', models.CharField(db_column='Country', max_length=255)),
                ('postal_code', models.CharField(db_column='Postal_Code', max_length=20)),
                ('nickname', models.CharField(db_column='nickname', max_length=20)),
                ('user', models.ForeignKey(db_column='User_ID', on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'shipping_address',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_address',
            field=models.ForeignKey(db_column='Shipping_Address_ID', on_delete=django.db.models.deletion.DO_NOTHING, to='myapp.shippingaddress'),
        ),
    ]
