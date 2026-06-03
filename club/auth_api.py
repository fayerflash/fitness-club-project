import json
from datetime import timedelta

from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone  # [Ч1] timezone

from .models import User, UserMembership, Order, Membership, OrderItem, Trainer

# ============================================================
# AUTH API — авторизация через сессии
# [Ч1] timezone — last_login, start_date, end_date
# [Ч3] redirect аналог на фронте — navigate() в React
# [Ч4] update() — массовая деактивация абонементов
# ============================================================


def _user_json(user):
    pt = user.preferred_trainer
    return {
        'id': user.id,
        'full_name': user.full_name,
        'email': user.email,
        'phone': user.phone or '',
        'role': user.role,
        'role_display': user.get_role_display(),
        'created_at': user.created_at.strftime('%Y-%m-%d'),
        'preferred_trainer': {
            'id': pt.id,
            'full_name': pt.full_name,
            'specialization': pt.specialization or '',
            'photo_url': pt.photo_url or '',
            'photo_file_url': pt.photo.url if pt.photo else '',
        } if pt else None,
    }


@csrf_exempt
@require_http_methods(['POST'])
def api_login(request):
    data = json.loads(request.body)
    email = data.get('email', '').strip()
    password = data.get('password', '')

    user = authenticate(request, username=email, password=password)
    if user is None:
        return JsonResponse({'error': 'Неверный email или пароль'}, status=400)

    login(request, user)
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])
    return JsonResponse({'user': _user_json(user)})


@csrf_exempt
@require_http_methods(['POST'])
def api_register(request):
    data = json.loads(request.body)
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    phone = data.get('phone', '').strip()

    if not full_name or not email or not password:
        return JsonResponse({'error': 'Заполните все обязательные поля'}, status=400)

    if len(password) < 6:
        return JsonResponse({'error': 'Пароль должен быть не менее 6 символов'}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({'error': 'Пользователь с таким email уже существует'}, status=400)

    user = User.objects.create_user(
        email=email,
        full_name=full_name,
        password=password,
        phone=phone or None,
        role='client',
    )
    login(request, user)
    return JsonResponse({'user': _user_json(user)}, status=201)


@csrf_exempt
@require_http_methods(['POST'])
def api_logout(request):
    logout(request)
    return JsonResponse({'status': 'ok'})


def api_me(request):
    if not request.user.is_authenticated:
        return JsonResponse({'user': None})
    return JsonResponse({'user': _user_json(request.user)})


@csrf_exempt
@require_http_methods(['POST'])
def api_profile_update(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Не авторизован'}, status=401)

    data = json.loads(request.body)
    user = request.user
    full_name = data.get('full_name', '').strip()
    phone = data.get('phone', '').strip()

    if not full_name:
        return JsonResponse({'error': 'ФИО не может быть пустым'}, status=400)

    user.full_name = full_name
    user.phone = phone or None
    user.save(update_fields=['full_name', 'phone'])
    return JsonResponse({'user': _user_json(user)})


def api_profile_data(request):
    """
    [Ч2] select_related() — UserMembership + Membership одним запросом
    [Ч1] filter() + order_by()
    [Ч1] related_name='memberships', 'orders' — обращение через объект user
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Не авторизован'}, status=401)

    user = request.user

    # [Ч2] select_related() — подгружаем Membership JOIN'ом (без N+1 запросов)
    # [Ч1] filter() по статусу + order_by()
    user_memberships = UserMembership.objects.filter(
        user=user, status='active'
    ).select_related('membership').order_by('-purchase_date')[:5]

    # [Ч1] filter() + order_by()
    orders = Order.objects.filter(user=user).order_by('-order_date')[:10]

    return JsonResponse({
        'user': _user_json(user),
        'memberships': [
            {
                'id': um.id,
                'membership_title': um.membership.title,
                'membership_title_en': um.membership.title_en or '',
                'start_date': um.start_date.strftime('%d.%m.%Y'),
                'end_date': um.end_date.strftime('%d.%m.%Y'),
                'status': um.status,
                'status_display': um.get_status_display(),
                'visits_used': um.visits_used,
                'visits_limit': um.membership.visits_limit,
            }
            for um in user_memberships
        ],
        'orders': [
            {
                'id': o.id,
                'total_amount': str(o.total_amount),
                'payment_method': o.get_payment_method_display(),
                'status': o.status,
                'status_display': o.get_status_display(),
                'order_date': o.order_date.strftime('%d.%m.%Y %H:%M'),
            }
            for o in orders
        ],
    })


@csrf_exempt
@require_http_methods(['POST'])
def api_set_trainer(request):
    """Клиент выбирает предпочитаемого тренера."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Не авторизован'}, status=401)

    data = json.loads(request.body)
    trainer_id = data.get('trainer_id')

    if trainer_id is None:
        request.user.preferred_trainer = None
        request.user.save(update_fields=['preferred_trainer'])
        return JsonResponse({'status': 'cleared'})

    try:
        trainer = Trainer.objects.get(pk=trainer_id, is_active=True)
    except Trainer.DoesNotExist:
        return JsonResponse({'error': 'Тренер не найден'}, status=404)

    request.user.preferred_trainer = trainer
    request.user.save(update_fields=['preferred_trainer'])
    return JsonResponse({
        'status': 'ok',
        'trainer': {
            'id': trainer.id,
            'full_name': trainer.full_name,
            'specialization': trainer.specialization or '',
            'photo_url': trainer.photo_url or '',
        },
    })


@csrf_exempt
@require_http_methods(['POST'])
def api_switch_membership(request, pk):
    """
    Смена абонемента клиентом.
    [Ч4] update() — массовое обновление статуса без загрузки объектов
    [Ч1] timezone — даты начала и конца нового абонемента
    [Ч4] Http404 — если абонемент не найден
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Не авторизован'}, status=401)
    if request.user.role != 'client':
        return JsonResponse({'error': 'Только для клиентов'}, status=403)

    try:
        # [Ч1] get() — один объект
        new_membership = Membership.objects.get(pk=pk, is_active=True)
    except Membership.DoesNotExist:
        # [Ч4] Http404 аналог через JSON-ответ для API
        return JsonResponse({'error': 'Абонемент не найден'}, status=404)

    # [Ч4] update() — один SQL UPDATE, без загрузки каждого объекта в Python
    UserMembership.objects.filter(
        user=request.user, status='active'
    ).update(status='expired')

    order = Order.objects.create(
        user=request.user, total_amount=new_membership.price,
        payment_method='card', status='paid',
    )
    OrderItem.objects.create(order=order, membership=new_membership, price_paid=new_membership.price)
    UserMembership.objects.create(
        user=request.user, membership=new_membership,
        # [Ч1] timezone: вычисляем даты в момент покупки
        start_date=timezone.now().date(),
        end_date=timezone.now().date() + timedelta(days=new_membership.duration_days),
        status='active',
    )

    return JsonResponse({
        'status': 'ok',
        'message': f'Абонемент изменён на «{new_membership.title}»!',
        'order_id': order.id,
    })


@csrf_exempt
@require_http_methods(['POST'])
def api_buy_membership(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Необходимо войти в систему'}, status=401)

    if request.user.role != 'client':
        return JsonResponse({'error': 'Только клиенты могут покупать абонементы'}, status=403)

    try:
        membership = Membership.objects.get(pk=pk, is_active=True)
    except Membership.DoesNotExist:
        return JsonResponse({'error': 'Абонемент не найден'}, status=404)

    order = Order.objects.create(
        user=request.user,
        total_amount=membership.price,
        payment_method='card',
        status='paid',
    )
    OrderItem.objects.create(order=order, membership=membership, price_paid=membership.price)
    UserMembership.objects.create(
        user=request.user,
        membership=membership,
        start_date=timezone.now().date(),
        end_date=timezone.now().date() + timedelta(days=membership.duration_days),
        status='active',
    )

    return JsonResponse({
        'status': 'ok',
        'message': f'Абонемент "{membership.title}" успешно куплен!',
        'order_id': order.id,
    })
