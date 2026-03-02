from typing import Type

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver, Signal
from django_rest_passwordreset.signals import reset_password_token_created

from backend.models import ConfirmEmailToken, User, User, Product, ProductImage
from backend.tasks import generate_all_thumbnails, cleanup_thumbnails

new_user_registered = Signal()

new_order = Signal()


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, **kwargs):
    """
    Отправляем письмо с токеном для сброса пароля
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param kwargs:
    :return:
    """
    # send an e-mail to the user

    msg = EmailMultiAlternatives(
        # title:
        f"Password Reset Token for {reset_password_token.user}",
        # message:
        reset_password_token.key,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [reset_password_token.user.email]
    )
    msg.send()


@receiver(post_save, sender=User)
def new_user_registered_signal(sender: Type[User], instance: User, created: bool, **kwargs):
    """
     отправляем письмо с подтрердждением почты
    """
    if created and not instance.is_active:
        # send an e-mail to the user
        token, _ = ConfirmEmailToken.objects.get_or_create(user_id=instance.pk)

        msg = EmailMultiAlternatives(
            # title:
            f"Password Reset Token for {instance.email}",
            # message:
            token.key,
            # from:
            settings.EMAIL_HOST_USER,
            # to:
            [instance.email]
        )
        msg.send()


@receiver(new_order)
def new_order_signal(user_id, **kwargs):
    """
    отправяем письмо при изменении статуса заказа
    """
    # send an e-mail to the user
    user = User.objects.get(id=user_id)

    msg = EmailMultiAlternatives(
        # title:
        f"Обновление статуса заказа",
        # message:
        'Заказ сформирован',
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [user.email]
    )
    msg.send()


@receiver(post_save, sender=User)
def handle_user_avatar(sender, instance, created, **kwargs):
    """
    Генерация миниатюр аватара пользователя
    """
    if instance.avatar:
        generate_all_thumbnails.delay(
            instance.avatar.name,
            ['avatar_small', 'avatar_medium']
        )

@receiver(post_save, sender=Product)
def handle_product_image(sender, instance, created, **kwargs):
    """
    Генерация миниатюр изображения товара
    """
    if instance.image:
        generate_all_thumbnails.delay(
            instance.image.name,
            ['product_small', 'product_medium', 'product_large']
        )

@receiver(post_save, sender=ProductImage)
def handle_additional_image(sender, instance, created, **kwargs):
    """
    Генерация миниатюр для дополнительных изображений
    """
    if instance.image:
        generate_all_thumbnails.delay(
            instance.image.name,
            ['product_small', 'product_medium']
        )

@receiver(pre_delete, sender=User)
@receiver(pre_delete, sender=Product)
@receiver(pre_delete, sender=ProductImage)
def cleanup_image_thumbnails(sender, instance, **kwargs):
    """
    Очистка миниатюр при удалении объекта
    """
    if hasattr(instance, 'avatar') and instance.avatar:
        cleanup_thumbnails.delay(instance.avatar.name)
    if hasattr(instance, 'image') and instance.image:
        cleanup_thumbnails.delay(instance.image.name)