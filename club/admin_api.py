import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count

from django.db.models import Avg, Sum, Min, Max, Count, F, FloatField, ExpressionWrapper
from .models import (
    Membership, Trainer, Schedule, Promotion, Service, User, Order, OrderItem
)


def _is_admin(user):
    return user.is_authenticated and user.role in ('gym_admin', 'superadmin')


def _require_admin(request):
    if not _is_admin(request.user):
        return JsonResponse({'error': 'Доступ запрещён'}, status=403)
    return None


# ─── DASHBOARD ────────────────────────────────────────────────

def admin_dashboard(request):
    err = _require_admin(request)
    if err:
        return err

    today = timezone.now().date()

    data = {
        'memberships': Membership.objects.count(),
        'trainers': Trainer.objects.count(),
        'services': Service.objects.count(),
        'schedule_upcoming': Schedule.objects.filter(class_date__gte=today).count(),
        'promotions_active': Promotion.active.count(),
        'users': User.objects.filter(role='client').count(),
        'orders_total': Order.objects.count(),
        'orders_paid': Order.objects.filter(status='paid').count(),
        'role': request.user.role,
    }
    return JsonResponse(data)


# ─── MEMBERSHIPS ──────────────────────────────────────────────

def admin_memberships_list(request):
    err = _require_admin(request)
    if err:
        return err

    qs = Membership.objects.all().order_by('price')
    return JsonResponse({'results': [
        {
            'id': m.id, 'title': m.title, 'title_en': m.title_en or '',
            'description': m.description or '', 'price': str(m.price),
            'duration_days': m.duration_days, 'visits_limit': m.visits_limit,
            'is_active': m.is_active,
            'created_at': m.created_at.strftime('%d.%m.%Y'),
        }
        for m in qs
    ]})


@csrf_exempt
@require_http_methods(['POST'])
def admin_membership_create(request):
    err = _require_admin(request)
    if err:
        return err

    data = request.POST
    required = ['title', 'price', 'duration_days']
    for f in required:
        if not data.get(f):
            return JsonResponse({'error': f'Поле {f} обязательно'}, status=400)

    m = Membership.objects.create(
        title=data['title'],
        title_en=data.get('title_en', ''),
        description=data.get('description', ''),
        price=data['price'],
        duration_days=int(data['duration_days']),
        visits_limit=data.get('visits_limit') or None,
        is_active=data.get('is_active', 'true').lower() == 'true',
    )
    return JsonResponse({'id': m.id, 'title': m.title}, status=201)


@csrf_exempt
@require_http_methods(['POST'])
def admin_membership_update(request, pk):
    err = _require_admin(request)
    if err:
        return err

    try:
        m = Membership.objects.get(pk=pk)
    except Membership.DoesNotExist:
        return JsonResponse({'error': 'Не найден'}, status=404)

    data = request.POST
    m.title = data.get('title', m.title)
    m.title_en = data.get('title_en', m.title_en or '')
    m.description = data.get('description', m.description)
    m.price = data.get('price', m.price)
    m.duration_days = int(data.get('duration_days', m.duration_days))
    m.visits_limit = data.get('visits_limit') or None
    m.is_active = data.get('is_active', 'true').lower() == 'true'
    m.save()
    return JsonResponse({'id': m.id, 'title': m.title})


@csrf_exempt
@require_http_methods(['POST'])
def admin_membership_delete(request, pk):
    err = _require_admin(request)
    if err:
        return err

    try:
        m = Membership.objects.get(pk=pk)
        m.delete()
        return JsonResponse({'status': 'deleted'})
    except Membership.DoesNotExist:
        return JsonResponse({'error': 'Не найден'}, status=404)


# ─── TRAINERS ─────────────────────────────────────────────────

def admin_trainers_list(request):
    err = _require_admin(request)
    if err:
        return err

    qs = Trainer.objects.all().order_by('full_name')
    return JsonResponse({'results': [
        {
            'id': t.id, 'full_name': t.full_name, 'full_name_en': t.full_name_en or '',
            'specialization': t.specialization or '', 'experience_years': t.experience_years,
            'bio': t.bio or '', 'photo_url': t.photo_url or '',
            'photo_file_url': t.photo.url if t.photo else '',
            'cv_url': t.cv_file.url if t.cv_file else '',
            'is_active': t.is_active,
            'hired_at': t.hired_at.strftime('%Y-%m-%d'),
        }
        for t in qs
    ]})


@csrf_exempt
@require_http_methods(['POST'])
def admin_trainer_create(request):
    err = _require_admin(request)
    if err:
        return err

    data = request.POST
    if not data.get('full_name'):
        return JsonResponse({'error': 'ФИО обязательно'}, status=400)

    cv = request.FILES.get('cv_file')
    if cv and not cv.name.endswith('.pdf'):
        return JsonResponse({'error': 'Резюме должно быть в формате PDF'}, status=400)

    t = Trainer.objects.create(
        full_name=data['full_name'],
        full_name_en=data.get('full_name_en', ''),
        specialization=data.get('specialization', ''),
        experience_years=int(data.get('experience_years', 0)),
        bio=data.get('bio', ''),
        photo_url=data.get('photo_url', ''),
        is_active=data.get('is_active', 'true').lower() == 'true',
    )
    if request.FILES.get('photo'):
        t.photo = request.FILES['photo']
        t.save()
    if cv:
        t.cv_file = cv
        t.save()
    return JsonResponse({'id': t.id, 'full_name': t.full_name}, status=201)


@csrf_exempt
@require_http_methods(['POST'])
def admin_trainer_update(request, pk):
    err = _require_admin(request)
    if err:
        return err

    try:
        t = Trainer.objects.get(pk=pk)
    except Trainer.DoesNotExist:
        return JsonResponse({'error': 'Не найден'}, status=404)

    cv = request.FILES.get('cv_file')
    if cv and not cv.name.endswith('.pdf'):
        return JsonResponse({'error': 'Резюме должно быть в формате PDF'}, status=400)

    data = request.POST
    t.full_name = data.get('full_name', t.full_name)
    t.full_name_en = data.get('full_name_en', t.full_name_en or '')
    t.specialization = data.get('specialization', t.specialization)
    t.experience_years = int(data.get('experience_years', t.experience_years))
    t.bio = data.get('bio', t.bio)
    t.photo_url = data.get('photo_url', t.photo_url)
    t.is_active = data.get('is_active', 'true').lower() == 'true'
    if request.FILES.get('photo'):
        t.photo = request.FILES['photo']
    if cv:
        t.cv_file = cv
    t.save()
    return JsonResponse({
        'id': t.id, 'full_name': t.full_name,
        'cv_url': t.cv_file.url if t.cv_file else '',
        'photo_url_file': t.photo.url if t.photo else '',
    })


@csrf_exempt
@require_http_methods(['POST'])
def admin_trainer_delete(request, pk):
    err = _require_admin(request)
    if err:
        return err

    try:
        Trainer.objects.get(pk=pk).delete()
        return JsonResponse({'status': 'deleted'})
    except Trainer.DoesNotExist:
        return JsonResponse({'error': 'Не найден'}, status=404)


# ─── SERVICES ─────────────────────────────────────────────────

def admin_services_list(request):
    err = _require_admin(request)
    if err:
        return err

    qs = Service.objects.annotate(schedules_count=Count('schedules')).order_by('title')
    return JsonResponse({'results': [
        {
            'id': s.id, 'title': s.title, 'title_en': s.title_en or '',
            'description': s.description or '', 'image_url': s.image_url or '',
            'is_active': s.is_active, 'schedules_count': s.schedules_count,
        }
        for s in qs
    ]})


@csrf_exempt
@require_http_methods(['POST'])
def admin_service_create(request):
    err = _require_admin(request)
    if err:
        return err

    data = request.POST
    if not data.get('title'):
        return JsonResponse({'error': 'Название обязательно'}, status=400)

    s = Service.objects.create(
        title=data['title'],
        title_en=data.get('title_en', ''),
        description=data.get('description', ''),
        image_url=data.get('image_url', ''),
        is_active=data.get('is_active', 'true').lower() == 'true',
    )
    return JsonResponse({'id': s.id, 'title': s.title}, status=201)


@csrf_exempt
@require_http_methods(['POST'])
def admin_service_update(request, pk):
    err = _require_admin(request)
    if err:
        return err

    try:
        s = Service.objects.get(pk=pk)
    except Service.DoesNotExist:
        return JsonResponse({'error': 'Не найден'}, status=404)

    data = request.POST
    s.title = data.get('title', s.title)
    s.title_en = data.get('title_en', s.title_en or '')
    s.description = data.get('description', s.description)
    s.image_url = data.get('image_url', s.image_url)
    s.is_active = data.get('is_active', 'true').lower() == 'true'
    s.save()
    return JsonResponse({'id': s.id, 'title': s.title})


@csrf_exempt
@require_http_methods(['POST'])
def admin_service_delete(request, pk):
    err = _require_admin(request)
    if err:
        return err

    try:
        Service.objects.get(pk=pk).delete()
        return JsonResponse({'status': 'deleted'})
    except Service.DoesNotExist:
        return JsonResponse({'error': 'Не найден'}, status=404)


# ─── PROMOTIONS ───────────────────────────────────────────────

def admin_promotions_list(request):
    err = _require_admin(request)
    if err:
        return err

    qs = Promotion.objects.prefetch_related('memberships').all().order_by('-start_date')
    return JsonResponse({'results': [
        {
            'id': p.id, 'title': p.title, 'description': p.description or '',
            'discount_percent': str(p.discount_percent),
            'start_date': p.start_date.strftime('%Y-%m-%d'),
            'end_date': p.end_date.strftime('%Y-%m-%d'),
            'is_active': p.is_active,
            'status_display': p.is_active_display(),
            'image_url': p.image.url if p.image else (p.image_url or ''),
            'membership_ids': list(p.memberships.values_list('id', flat=True)),
        }
        for p in qs
    ]})


@csrf_exempt
@require_http_methods(['POST'])
def admin_promotion_create(request):
    err = _require_admin(request)
    if err:
        return err

    data = request.POST
    required = ['title', 'discount_percent', 'start_date', 'end_date']
    for f in required:
        if not data.get(f):
            return JsonResponse({'error': f'Поле {f} обязательно'}, status=400)

    p = Promotion.objects.create(
        title=data['title'],
        description=data.get('description', ''),
        discount_percent=data['discount_percent'],
        start_date=data['start_date'],
        end_date=data['end_date'],
        is_active=data.get('is_active', 'true').lower() == 'true',
    )
    if request.FILES.get('image'):
        p.image = request.FILES['image']
        p.save()
    membership_ids = data.getlist('membership_ids')
    if membership_ids:
        p.memberships.set(Membership.objects.filter(id__in=membership_ids))
    return JsonResponse({'id': p.id, 'title': p.title}, status=201)


@csrf_exempt
@require_http_methods(['POST'])
def admin_promotion_update(request, pk):
    err = _require_admin(request)
    if err:
        return err

    try:
        p = Promotion.objects.get(pk=pk)
    except Promotion.DoesNotExist:
        return JsonResponse({'error': 'Не найден'}, status=404)

    data = request.POST
    p.title = data.get('title', p.title)
    p.description = data.get('description', p.description)
    p.discount_percent = data.get('discount_percent', p.discount_percent)
    p.start_date = data.get('start_date', p.start_date)
    p.end_date = data.get('end_date', p.end_date)
    p.is_active = data.get('is_active', 'true').lower() == 'true'
    if request.FILES.get('image'):
        p.image = request.FILES['image']
    p.save()
    membership_ids = data.getlist('membership_ids')
    p.memberships.set(Membership.objects.filter(id__in=membership_ids))
    return JsonResponse({'id': p.id, 'title': p.title})


@csrf_exempt
@require_http_methods(['POST'])
def admin_promotion_delete(request, pk):
    err = _require_admin(request)
    if err:
        return err

    try:
        Promotion.objects.get(pk=pk).delete()
        return JsonResponse({'status': 'deleted'})
    except Promotion.DoesNotExist:
        return JsonResponse({'error': 'Не найден'}, status=404)


# ─── SCHEDULE ─────────────────────────────────────────────────

def admin_schedule_list(request):
    err = _require_admin(request)
    if err:
        return err

    qs = Schedule.objects.select_related('service', 'trainer').order_by('class_date', 'start_time')
    return JsonResponse({'results': [
        {
            'id': s.id,
            'class_date': s.class_date.strftime('%Y-%m-%d'),
            'start_time': s.start_time.strftime('%H:%M'),
            'end_time': s.end_time.strftime('%H:%M'),
            'hall': s.hall or '',
            'capacity': s.capacity,
            'service_id': s.service_id,
            'service_title': s.service.title,
            'trainer_id': s.trainer_id,
            'trainer_name': s.trainer.full_name,
        }
        for s in qs
    ]})


@csrf_exempt
@require_http_methods(['POST'])
def admin_schedule_create(request):
    err = _require_admin(request)
    if err:
        return err

    data = request.POST
    required = ['service_id', 'trainer_id', 'class_date', 'start_time', 'end_time']
    for f in required:
        if not data.get(f):
            return JsonResponse({'error': f'Поле {f} обязательно'}, status=400)

    try:
        service = Service.objects.get(pk=data['service_id'])
        trainer = Trainer.objects.get(pk=data['trainer_id'])
    except (Service.DoesNotExist, Trainer.DoesNotExist):
        return JsonResponse({'error': 'Услуга или тренер не найдены'}, status=400)

    s = Schedule.objects.create(
        service=service, trainer=trainer,
        class_date=data['class_date'],
        start_time=data['start_time'],
        end_time=data['end_time'],
        hall=data.get('hall', ''),
        capacity=int(data.get('capacity', 20)),
    )
    return JsonResponse({'id': s.id}, status=201)


@csrf_exempt
@require_http_methods(['POST'])
def admin_schedule_update(request, pk):
    err = _require_admin(request)
    if err:
        return err

    try:
        s = Schedule.objects.get(pk=pk)
    except Schedule.DoesNotExist:
        return JsonResponse({'error': 'Не найден'}, status=404)

    data = request.POST
    if data.get('service_id'):
        s.service = Service.objects.get(pk=data['service_id'])
    if data.get('trainer_id'):
        s.trainer = Trainer.objects.get(pk=data['trainer_id'])
    s.class_date = data.get('class_date', s.class_date)
    s.start_time = data.get('start_time', s.start_time)
    s.end_time = data.get('end_time', s.end_time)
    s.hall = data.get('hall', s.hall)
    s.capacity = int(data.get('capacity', s.capacity))
    s.save()
    return JsonResponse({'id': s.id})


@csrf_exempt
@require_http_methods(['POST'])
def admin_schedule_delete(request, pk):
    err = _require_admin(request)
    if err:
        return err

    try:
        Schedule.objects.get(pk=pk).delete()
        return JsonResponse({'status': 'deleted'})
    except Schedule.DoesNotExist:
        return JsonResponse({'error': 'Не найден'}, status=404)


# ─── ANALYTICS ───────────────────────────────────────────────

def admin_analytics(request):
    err = _require_admin(request)
    if err:
        return err

    agg = Membership.objects.aggregate(
        avg_price=Avg('price'), min_price=Min('price'), max_price=Max('price')
    )
    total_paid = Order.objects.filter(status='paid').aggregate(total=Sum('total_amount'))

    services_stats = list(
        Service.objects.annotate(schedules_count=Count('schedules'))
        .values('id', 'title', 'schedules_count').order_by('-schedules_count')
    )
    memberships_stats = list(
        Membership.objects.annotate(purchases_count=Count('order_items'))
        .values('id', 'title', 'price', 'purchases_count').order_by('-purchases_count')
    )
    users_stats = list(
        Order.objects.values('user__full_name', 'user__email')
        .annotate(orders_count=Count('id'), total_spent=Sum('total_amount'))
        .order_by('-total_spent')[:10]
    )

    return JsonResponse({
        'avg_price': round(float(agg['avg_price'] or 0), 2),
        'min_price': str(agg['min_price'] or 0),
        'max_price': str(agg['max_price'] or 0),
        'total_paid': str(total_paid['total'] or 0),
        'total_orders': Order.objects.count(),
        'paid_orders': Order.objects.filter(status='paid').count(),
        'cancelled_orders': Order.objects.filter(status='cancelled').count(),
        'services_stats': services_stats,
        'memberships_stats': [
            {**m, 'price': str(m['price'])} for m in memberships_stats
        ],
        'users_stats': [
            {**u, 'total_spent': str(u['total_spent'] or 0)} for u in users_stats
        ],
    })


# ─── USERS (только для superadmin) ───────────────────────────

def admin_users_list(request):
    if not request.user.is_authenticated or request.user.role != 'superadmin':
        return JsonResponse({'error': 'Доступ запрещён'}, status=403)

    qs = User.objects.all().order_by('-created_at')
    return JsonResponse({'results': [
        {
            'id': u.id, 'full_name': u.full_name, 'email': u.email,
            'phone': u.phone or '', 'role': u.role,
            'role_display': u.get_role_display(),
            'is_active': u.is_active,
            'created_at': u.created_at.strftime('%d.%m.%Y'),
        }
        for u in qs
    ]})


@csrf_exempt
@require_http_methods(['POST'])
def admin_user_update_role(request, pk):
    if not request.user.is_authenticated or request.user.role != 'superadmin':
        return JsonResponse({'error': 'Доступ запрещён'}, status=403)

    try:
        u = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Не найден'}, status=404)

    data = json.loads(request.body)
    new_role = data.get('role')
    if new_role not in ('client', 'gym_admin', 'superadmin'):
        return JsonResponse({'error': 'Недопустимая роль'}, status=400)

    if new_role in ('gym_admin', 'superadmin'):
        u.is_staff = True
    else:
        u.is_staff = False
    if new_role == 'superadmin':
        u.is_superuser = True
    else:
        u.is_superuser = False

    u.role = new_role
    u.save()
    return JsonResponse({'id': u.id, 'role': u.role})
