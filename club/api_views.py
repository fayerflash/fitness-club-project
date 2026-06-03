import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Avg, Count, Min, Max, Sum
from django.utils import timezone

from .models import Membership, Trainer, Service, Schedule, Promotion, Favorite, User


# ============================================================
# JSON API для React-фронтенда
# ============================================================

def memberships_api(request):
    """
    [Ч1] filter() — только активные
    [Ч4] __icontains — поиск
    [Ч1] order_by() — сортировка
    [Ч1] Аннотация Count
    [Ч1] Агрегация: AVG, MIN, MAX, COUNT
    """
    search = request.GET.get('q', '').strip()
    limit = int(request.GET.get('limit', 10))
    ordering = request.GET.get('ordering', 'price')

    # [Ч1] filter() в view
    qs = Membership.objects.filter(is_active=True)

    if search:
        # [Ч4] __icontains — поиск без учёта регистра
        qs = qs.filter(title__icontains=search)

    # [Ч1] order_by() + аннотация Count (кол-во добавлений в избранное)
    qs = qs.order_by(ordering).annotate(favorites_count=Count('favorites'))[:limit]

    # [Ч1] Агрегация: три функции за один запрос к БД
    stats = Membership.objects.filter(is_active=True).aggregate(
        avg_price=Avg('price'),     # [Ч1] AVG
        min_price=Min('price'),     # [Ч1] MIN
        max_price=Max('price'),     # [Ч1] MAX
        total=Count('id'),          # [Ч1] COUNT
    )

    data = {
        'results': [
            {
                'id': m.id,
                'title': m.title,
                'title_en': m.title_en or '',
                'description': m.description or '',
                'price': str(m.price),
                'duration_days': m.duration_days,
                'visits_limit': m.visits_limit,
                'created_at': m.created_at.strftime('%Y-%m-%d'),
                'is_new': m.is_new,
                'favorites_count': m.favorites_count,
            }
            for m in qs
        ],
        'stats': {
            'avg_price': round(float(stats['avg_price'] or 0), 2),
            'min_price': str(stats['min_price'] or 0),
            'max_price': str(stats['max_price'] or 0),
            'total': stats['total'],
        },
    }
    return JsonResponse(data)


def trainer_detail_api(request, pk):
    """
    [Ч1] get() — получаем одного тренера по pk
    [Ч4] Http404 — возвращаем 404 если не найден
    [Ч2] select_related() — JOIN с Service
    [Ч1] order_by()
    [Ч1] timezone — фильтрация по текущей дате
    """
    try:
        # [Ч1] get() — один объект по pk
        t = Trainer.objects.get(pk=pk, is_active=True)
    except Trainer.DoesNotExist:
        # [Ч4] Http404 — аналог raise Http404, но через JSON для API
        return JsonResponse({'error': 'Тренер не найден'}, status=404)

    today = timezone.now().date()   # [Ч1] timezone
    schedule = (
        Schedule.objects.filter(trainer=t, class_date__gte=today)  # [Ч1] filter() + __gte
        .select_related('service')  # [Ч2] select_related — Service подгружается JOIN'ом
        .order_by('class_date', 'start_time')[:20]  # [Ч1] order_by()
    )

    return JsonResponse({
        'trainer': {
            'id': t.id,
            'full_name': t.full_name,
            'full_name_en': t.full_name_en or '',
            'specialization': t.specialization or '',
            'experience_years': t.experience_years,
            'experience_label': t.get_experience_display(),
            'bio': t.bio or '',
            'photo_url': t.photo_url or '',
            'photo_file_url': t.photo.url if t.photo else '',
            'cv_url': t.cv_file.url if t.cv_file else '',
            'hired_at': t.hired_at.strftime('%Y-%m-%d'),
        },
        'schedule': [
            {
                'id': s.id,
                'class_date': s.class_date.strftime('%Y-%m-%d'),
                'start_time': s.start_time.strftime('%H:%M'),
                'end_time': s.end_time.strftime('%H:%M'),
                'hall': s.hall or '',
                'capacity': s.capacity,
                'service_title': s.service.title,
                'service_title_en': s.service.title_en or '',
            }
            for s in schedule
        ],
    })


def trainers_api(request):
    """
    [Ч1] filter() + exclude()
    [Ч1] order_by()
    [Ч4] __icontains
    [Ч1] Агрегация: COUNT, AVG, MAX
    [Ч3] get_experience_display() — собственный метод модели
    """
    search = request.GET.get('q', '').strip()

    # [Ч1] filter() + exclude() + order_by() в цепочке
    qs = (
        Trainer.objects
        .filter(is_active=True)                         # [Ч1] filter()
        .exclude(specialization__isnull=True)           # [Ч1] exclude() + __ lookup
        .order_by('-experience_years')                  # [Ч1] order_by()
    )

    if search:
        # [Ч4] __icontains по двум полям
        qs = qs.filter(full_name__icontains=search) | Trainer.objects.filter(
            is_active=True, specialization__icontains=search
        )

    # [Ч1] Агрегация: COUNT + AVG + MAX
    stats = Trainer.objects.filter(is_active=True).aggregate(
        total=Count('id'),
        avg_experience=Avg('experience_years'),
        max_experience=Max('experience_years'),
    )

    data = {
        'results': [
            {
                'id': t.id,
                'full_name': t.full_name,
                'full_name_en': t.full_name_en or '',
                'specialization': t.specialization or '',
                'experience_years': t.experience_years,
                'experience_label': t.get_experience_display(),
                'bio': t.bio or '',
                'photo_url': t.photo_url or '',
                'photo_file_url': t.photo.url if t.photo else '',
                'cv_url': t.cv_file.url if t.cv_file else '',
                'hired_at': t.hired_at.strftime('%Y-%m-%d'),
            }
            for t in qs
        ],
        'stats': {
            'total': stats['total'],
            'avg_experience': round(float(stats['avg_experience'] or 0), 1),
            'max_experience': stats['max_experience'] or 0,
        },
    }
    return JsonResponse(data)


def schedule_api(request):
    """
    [Ч2] select_related() — загружаем Service и Trainer одним JOIN-запросом
    [Ч1] timezone — только будущие занятия
    [Ч1] __ lookup: class_date__gte
    На странице выводятся данные из 3 таблиц: Schedule + Service + Trainer
    """
    today = timezone.now().date()   # [Ч1] timezone

    qs = (
        Schedule.objects
        .filter(class_date__gte=today)          # [Ч1] filter() + __ lookup __gte
        .select_related('service', 'trainer')   # [Ч2] select_related: 1 запрос вместо N
        .order_by('class_date', 'start_time')   # [Ч1] order_by() по двум полям
        .distinct()[:50]
    )

    data = {
        'results': [
            {
                'id': s.id,
                'class_date': s.class_date.strftime('%Y-%m-%d'),
                'start_time': s.start_time.strftime('%H:%M'),
                'end_time': s.end_time.strftime('%H:%M'),
                'hall': s.hall or '',
                'capacity': s.capacity,
                'service': {
                    'id': s.service.id,
                    'title': s.service.title,
                    'title_en': s.service.title_en or '',
                    'image_url': s.service.image_url or '',
                },
                'trainer': {
                    'id': s.trainer.id,
                    'full_name': s.trainer.full_name,
                    'specialization': s.trainer.specialization or '',
                    'photo_url': s.trainer.photo_url or '',
                    'photo_file_url': s.trainer.photo.url if s.trainer.photo else '',
                },
            }
            for s in qs
        ]
    }
    return JsonResponse(data)


def promotions_api(request):
    """
    [Ч1] Кастомный менеджер Promotion.active — all() возвращает только текущие
    [Ч1] order_by()
    [Ч3] get_days_left() — собственный метод модели
    """
    # [Ч1] Кастомный менеджер: .active автоматически фильтрует по датам
    qs = Promotion.active.all().order_by('-discount_percent')   # [Ч1] order_by()

    data = {
        'results': [
            {
                'id': p.id,
                'title': p.title,
                'description': p.description or '',
                'discount_percent': str(p.discount_percent),
                'start_date': p.start_date.strftime('%Y-%m-%d'),
                'end_date': p.end_date.strftime('%Y-%m-%d'),
                'days_left': p.get_days_left(),     # [Ч3] собственный метод модели
                'image_url': p.image_url or '',
            }
            for p in qs
        ]
    }
    return JsonResponse(data)


def services_api(request):
    """
    [Ч1] Аннотация Count — добавляем поле schedules_count каждой услуге
    [Ч1] related_name='schedules' используется в Count('schedules')
    """
    # [Ч1] annotate() + Count — аналог SQL: SELECT *, COUNT(schedule.id) FROM service
    qs = Service.objects.filter(is_active=True).annotate(
        schedules_count=Count('schedules')  # [Ч1] 'schedules' = related_name в Schedule
    ).order_by('title')

    data = {
        'results': [
            {
                'id': s.id,
                'title': s.title,
                'title_en': s.title_en or '',
                'description': s.description or '',
                'image_url': s.image_url or '',
                'schedules_count': s.schedules_count,
            }
            for s in qs
        ]
    }
    return JsonResponse(data)


@require_http_methods(['POST'])
def toggle_favorite_api(request):
    """Заглушка кнопки 'В избранное' — возвращает новое состояние."""
    try:
        body = json.loads(request.body)
        membership_id = body.get('membership_id')
        return JsonResponse({'status': 'ok', 'favorited': True, 'membership_id': membership_id})
    except Exception:
        return JsonResponse({'error': 'bad request'}, status=400)
