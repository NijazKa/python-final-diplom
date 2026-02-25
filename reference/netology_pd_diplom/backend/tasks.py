from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from celery import shared_task
from requests import get
from yaml import load as load_yaml, Loader
from django.db import transaction

from backend.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter



@shared_task
def test_task():
    print("тестовая задача выполнена")

User = get_user_model()

# задача в celery для отправки письма подтверждения регистрации
@shared_task
def send_confirmation_email(email):
    try:

        send_mail(
            'Подтверждение регистрации',
            'Спасибо за регистрацию!',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return "Email sent"

    except User.DoesNotExist:
        return "User not found"

@shared_task(bind=True)
def process_partner_yaml(self, url, user_id):
    try:
        stream = get(url).content
        data = load_yaml(stream, Loader=Loader)

        with transaction.atomic():

            shop, _ = Shop.objects.get_or_create(
                name=data['shop'],
                user_id=user_id
            )

            for category in data['categories']:
                category_object, _ = Category.objects.get_or_create(
                    id=category['id'],
                    name=category['name']
                )
                category_object.shops.add(shop.id)
                category_object.save()

            ProductInfo.objects.filter(shop_id=shop.id).delete()

            for item in data['goods']:
                product, _ = Product.objects.get_or_create(
                    name=item['name'],
                    category_id=item['category']
                )

                product_info = ProductInfo.objects.create(
                    product_id=product.id,
                    external_id=item['id'],
                    model=item['model'],
                    price=item['price'],
                    price_rrc=item['price_rrc'],
                    quantity=item['quantity'],
                    shop_id=shop.id
                )

                for name, value in item['parameters'].items():
                    parameter_object, _ = Parameter.objects.get_or_create(name=name)

                    ProductParameter.objects.create(
                        product_info_id=product_info.id,
                        parameter_id=parameter_object.id,
                        value=value
                    )

        return "YAML processed successfully"

    except Exception as e:
        self.retry(exc=e, countdown=5, max_retries=3)