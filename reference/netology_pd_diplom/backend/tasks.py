from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from celery import shared_task
from requests import get
from yaml import load as load_yaml, Loader
from django.db import transaction
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.options import ThumbnailOptions
from django.core.files.storage import default_storage
import logging

from backend.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter

logger = logging.getLogger(__name__)

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

@shared_task
def generate_thumbnail(image_path, alias_name, **options):
    """
    Асинхронная генерация миниатюры
    """
    try:
        if default_storage.exists(image_path):
            thumbnail_options = ThumbnailOptions(options)
            thumbnailer = get_thumbnailer(image_path)
            thumbnail = thumbnailer.get_thumbnail(thumbnail_options)
            logger.info(f'Thumbnail generated for {image_path} with alias {alias_name}')
            return thumbnail.url
    except Exception as e:
        logger.error(f'Error generating thumbnail for {image_path}: {str(e)}')
        return None

@shared_task
def generate_all_thumbnails(image_path, aliases_list):
    """
    Генерация всех миниатюр для изображения
    """
    results = {}
    for alias_name in aliases_list:
        result = generate_thumbnail.delay(image_path, alias_name)
        results[alias_name] = result.id
    return results

@shared_task
def cleanup_thumbnails(image_path):
    """
    Очистка миниатюр при удалении изображения
    """
    try:
        thumbnailer = get_thumbnailer(image_path)
        thumbnailer.delete_thumbnails()
        logger.info(f'Thumbnails cleaned for {image_path}')
    except Exception as e:
        logger.error(f'Error cleaning thumbnails for {image_path}: {str(e)}')