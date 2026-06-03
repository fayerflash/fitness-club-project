from django.db.models import Avg, Sum, Min, Max, Count, F, FloatField, ExpressionWrapper
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone      # [Ч1] timezone
from datetime import timedelta
from django.http import Http404        # [Ч4] Http404 — для явного вызова

from .models import (
    Membership, Trainer, Promotion,
    Order, OrderItem, Service, User, UserMembership,
)
from .forms import MembershipForm, TrainerForm, PromotionForm, LoginForm, RegistrationForm


def superadmin_required(view_func):
    return login_required(user_passes_test(lambda u: u.role == 'superadmin')(view_func))


def gym_admin_required(view_func):
    return login_required(user_passes_test(lambda u: u.role in ['gym_admin', 'superadmin'])(view_func))


# ============================================================
# АВТОРИЗАЦИЯ
# [Ч3] return redirect — при успешном входе/регистрации
# [Ч1] timezone — обновление last_login
# ============================================================

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')         # [Ч3] redirect: уже вошли — на главную

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.full_name}!')
            return redirect('home')     # [Ч3] redirect после регистрации
    else:
        form = RegistrationForm()

    return render(request, 'club/auth/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # [Ч1] timezone: фиксируем момент входа пользователя
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])

            messages.success(request, f'С возвращением, {user.full_name}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)   # [Ч3] redirect на страницу откуда пришли
    else:
        form = LoginForm()

    return render(request, 'club/auth/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'Вы вышли из системы')
    return redirect('home')             # [Ч3] redirect после выхода


@login_required
def profile_view(request):
    user = request.user
    context = {
        'user': user,
        # [Ч1] related_name='orders' — обращение к связанной таблице через объект
        'orders': user.orders.all()[:10],
        # [Ч1] related_name='memberships' + filter() по статусу
        'user_memberships': user.memberships.filter(status='active'),
    }
    return render(request, 'club/auth/profile.html', context)


@login_required
def profile_edit_view(request):
    user = request.user

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '')
        phone = request.POST.get('phone', '')
        user.full_name = full_name
        user.phone = phone or None
        user.save()
        messages.success(request, 'Профиль обновлён!')
        return redirect('profile')      # [Ч3] redirect после редактирования

    return render(request, 'club/auth/profile_edit.html', {'user': user})


# ============================================================
# ГЛАВНАЯ СТРАНИЦА
# [Ч1] filter() в view
# [Ч1] Кастомный менеджер: Promotion.active
# ============================================================

def home(request):
    # [Ч1] filter() — только активные абонементы
    memberships = Membership.objects.filter(is_active=True)[:3]

    # [Ч1] filter() — только активные тренеры
    trainers = Trainer.objects.filter(is_active=True)[:3]

    # [Ч1] Кастомный менеджер — возвращает только текущие акции (по датам)
    promotions = Promotion.active.all()[:3]

    return render(request, 'club/home.html', {
        'memberships': memberships,
        'trainers': trainers,
        'promotions': promotions,
    })


# ============================================================
# СПИСОК АБОНЕМЕНТОВ
# [Ч4] __icontains — поиск
# [Ч4] values(), values_list()
# [Ч4] count(), exists()
# [Ч4] F expressions
# [Ч1] filter() в view
# ============================================================

def membership_list(request):
    memberships = Membership.objects.all()

    # [Ч1] filter() + [Ч4] __icontains — поиск без учёта регистра
    search_query = request.GET.get('q', '')
    memberships_icontains = []
    if search_query:
        memberships_icontains = Membership.objects.filter(
            title__icontains=search_query  # [Ч4] __icontains
        )

    # [Ч4] values() — возвращает список словарей (не объектов модели)
    memberships_values = Membership.objects.values('id', 'title', 'price')

    # [Ч4] values_list() — возвращает список кортежей
    memberships_list = Membership.objects.values_list('title', 'price')

    # [Ч4] count() — количество записей в таблице
    total_count = Membership.objects.count()

    # [Ч4] exists() — есть ли хоть одна запись (True/False)
    active_exists = Membership.objects.filter(is_active=True).exists()

    # [Ч4] count() + filter()
    expensive_count = Membership.objects.filter(price__gte=2000).count()

    # [Ч4] F expressions — вычисление прямо в SQL без загрузки в Python
    # Кейс: показываем цену +5% как предполагаемое повышение
    increased_prices = Membership.objects.annotate(
        increased_price=ExpressionWrapper(
            F('price') * 1.05,          # [Ч4] F('price') — поле в SQL
            output_field=FloatField()
        )
    )

    context = {
        'memberships': memberships,
        'search_query': search_query,
        'memberships_icontains': memberships_icontains,
        'memberships_values': memberships_values,
        'memberships_list': memberships_list,
        'total_count': total_count,
        'active_exists': active_exists,
        'expensive_count': expensive_count,
        'increased_prices': increased_prices,
    }
    return render(request, 'club/membership_list.html', context)


# ============================================================
# ДЕТАЛЬНАЯ СТРАНИЦА АБОНЕМЕНТА
# [Ч1] exclude()
# [Ч1] __ (два варианта): lookup и связанная таблица
# [Ч2] select_related()
# [Ч4] exists(), count()
# [Ч4] Http404 (через get_object_or_404)
# [Ч4] F expressions
# ============================================================

def membership_detail(request, pk):
    # [Ч4] Http404 — если абонемент не найден, Django вернёт 404-страницу
    # get_object_or_404 внутри вызывает raise Http404
    membership = get_object_or_404(Membership, pk=pk)

    # [Ч1] filter() + exclude()
    # exclude() исключает текущий абонемент из похожих
    similar_memberships = Membership.objects.filter(
        is_active=True
    ).exclude(pk=membership.pk)[:5]     # [Ч1] exclude()

    # ─────────────────────────────────────────────────────────
    # ДЕМОНСТРАЦИЯ select_related()
    # Чтобы увидеть разницу в Debug Toolbar (вкладка SQL):
    
    # БЕЗ select_related — раскомментируй строку ниже и закомментируй С select_related
    orders_with_users = Order.objects.filter(
        items__membership=membership,
        status='paid'
    ).distinct()
    # → в Debug Toolbar увидишь НЕСКОЛЬКО запросов (отдельный на каждого User)
    
    # С select_related — сейчас активна эта версия
    # orders_with_users = Order.objects.select_related(
    #     'user'
    # ).filter(
    #     items__membership=membership,
    #     status='paid'
    # ).distinct()
    # → в Debug Toolbar увидишь ОДИН запрос с INNER JOIN club_user
    # ─────────────────────────────────────────────────────────

    # [Ч4] exists() — есть ли заказы вообще
    has_orders = Order.objects.filter(
        items__membership=membership    # [Ч1] __ по связанной таблице
    ).exists()

    # [Ч4] count() — количество заказов
    orders_count = Order.objects.filter(
        items__membership=membership
    ).count()

    # [Ч4] F expressions — скидка 10% в SQL
    membership_with_discount = Membership.objects.annotate(
        price_with_discount=ExpressionWrapper(
            F('price') * 0.9,           # [Ч4] F expression
            output_field=FloatField()
        )
    ).filter(pk=membership.pk).first()

    context = {
        'membership': membership,
        'similar_memberships': similar_memberships,
        'orders_with_users': orders_with_users,
        'has_orders': has_orders,
        'orders_count': orders_count,
        'membership_with_discount': membership_with_discount,
    }
    return render(request, 'club/membership_detail.html', context)


# ============================================================
# ПОКУПКА АБОНЕМЕНТА
# [Ч1] timezone — start_date, end_date
# [Ч3] redirect после действия
# ============================================================

@login_required
def buy_membership(request, pk):
    membership = get_object_or_404(Membership, pk=pk, is_active=True)

    order = Order.objects.create(
        user=request.user,
        total_amount=membership.price,
        payment_method='card',
        status='paid'
    )
    OrderItem.objects.create(
        order=order, membership=membership, price_paid=membership.price
    )
    UserMembership.objects.create(
        user=request.user,
        membership=membership,
        # [Ч1] timezone: вычисляем даты начала и окончания абонемента
        start_date=timezone.now().date(),
        end_date=timezone.now().date() + timedelta(days=membership.duration_days),
        status='active'
    )

    messages.success(request, f'✅ Вы купили абонемент "{membership.title}" за {membership.price} ₽!')
    return redirect('profile')          # [Ч3] redirect после покупки


# ============================================================
# CRUD АБОНЕМЕНТОВ (Создание / Редактирование / Удаление)
# [Ч2] Демонстрация CRUD на сайте
# [Ч3] redirect после каждого действия
# [Ч4] Http404 в get_object_or_404
# ============================================================

@gym_admin_required
def membership_create(request):
    if request.method == 'POST':
        form = MembershipForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Абонемент создан!')
            return redirect('membership_list')  # [Ч3] redirect после создания
    else:
        form = MembershipForm()

    return render(request, 'club/membership_form.html', {
        'form': form, 'title': 'Создание абонемента',
    })


@gym_admin_required
def membership_edit(request, pk):
    # [Ч4] Http404 если pk не существует
    membership = get_object_or_404(Membership, pk=pk)

    if request.method == 'POST':
        form = MembershipForm(request.POST, instance=membership)
        if form.is_valid():
            form.save()
            messages.success(request, 'Абонемент обновлён!')
            # [Ч3] redirect после редактирования — используем get_absolute_url через reverse
            return redirect('membership_detail', pk=membership.pk)
    else:
        form = MembershipForm(instance=membership)

    return render(request, 'club/membership_form.html', {
        'form': form, 'membership': membership, 'title': 'Редактирование абонемента',
    })


@gym_admin_required
def membership_delete(request, pk):
    membership = get_object_or_404(Membership, pk=pk)

    if request.method == 'POST':
        membership.delete()             # [Ч4] delete() на объекте
        messages.success(request, 'Абонемент удалён!')
        return redirect('membership_list')  # [Ч3] redirect после удаления

    return render(request, 'club/membership_confirm_delete.html', {'membership': membership})


# ============================================================
# ТРЕНЕРЫ
# [Ч1] filter() + __ __icontains
# [Ч4] values_list(), count(), exists()
# [Ч3] request.FILES — загрузка файлов (фото + PDF)
# ============================================================

def trainer_list(request):
    search_query = request.GET.get('search', '')
    trainers = Trainer.objects.all()

    if search_query:
        # [Ч1] filter() + [Ч4] __icontains — поиск по двум полям
        trainers = trainers.filter(
            full_name__icontains=search_query  # [Ч4] __icontains
        ) | trainers.filter(
            specialization__icontains=search_query  # [Ч4] __icontains
        )

    # [Ч4] values_list() с flat=True — просто список имён
    trainer_names = Trainer.objects.values_list('full_name', flat=True)

    # [Ч4] count() — всего тренеров
    total_trainers = Trainer.objects.count()

    # [Ч4] exists() — есть ли активные
    active_trainers_exists = Trainer.objects.filter(is_active=True).exists()

    context = {
        'trainers': trainers,
        'search_query': search_query,
        'trainer_names': trainer_names,
        'total_trainers': total_trainers,
        'active_trainers_exists': active_trainers_exists,
    }
    return render(request, 'club/trainer_list.html', context)


@gym_admin_required
def trainer_create(request):
    if request.method == 'POST':
        # [Ч3] request.FILES — получаем загруженные файлы (photo, cv_file)
        form = TrainerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Тренер добавлен!')
            return redirect('trainer_list')  # [Ч3] redirect
    else:
        form = TrainerForm()

    return render(request, 'club/trainer_form.html', {
        'form': form, 'title': 'Добавление тренера',
    })


@gym_admin_required
def trainer_edit(request, pk):
    trainer = get_object_or_404(Trainer, pk=pk)  # [Ч4] Http404

    if request.method == 'POST':
        # [Ч3] request.FILES — обновляем фото/PDF при редактировании
        form = TrainerForm(request.POST, request.FILES, instance=trainer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные тренера обновлены!')
            return redirect('trainer_list')  # [Ч3] redirect
    else:
        form = TrainerForm(instance=trainer)

    return render(request, 'club/trainer_form.html', {
        'form': form, 'trainer': trainer, 'title': 'Редактирование тренера',
    })


@gym_admin_required
def trainer_delete(request, pk):
    trainer = get_object_or_404(Trainer, pk=pk)

    if request.method == 'POST':
        trainer.delete()                # [Ч4] delete()
        messages.success(request, 'Тренер удалён!')
        return redirect('trainer_list') # [Ч3] redirect после удаления

    return render(request, 'club/trainer_confirm_delete.html', {'trainer': trainer})


# ============================================================
# АКЦИИ
# [Ч1] Кастомный менеджер Promotion.active
# [Ч4] __icontains, values(), count(), exists()
# [Ч4] F expressions — bonus_discount
# ============================================================

def promotion_list(request):
    search_query = request.GET.get('q', '')

    # [Ч1] Кастомный менеджер — только текущие акции
    promotions = Promotion.active.all()

    if search_query:
        # [Ч1] filter() + [Ч4] __icontains
        promotions = promotions.filter(title__icontains=search_query)

    # [Ч4] values() — список словарей
    promotions_values = promotions.values('title', 'discount_percent', 'start_date', 'end_date')

    # [Ч4] count() и exists()
    promotions_count = promotions.count()
    has_promotions = promotions.exists()

    # [Ч4] F expressions — бонусная скидка +5% для отображения
    promotions_with_bonus = promotions.annotate(
        bonus_discount=ExpressionWrapper(
            F('discount_percent') + 5,  # [Ч4] F expression
            output_field=FloatField()
        )
    )

    context = {
        'promotions': promotions,
        'search_query': search_query,
        'promotions_values': promotions_values,
        'promotions_count': promotions_count,
        'has_promotions': has_promotions,
        'promotions_with_bonus': promotions_with_bonus,
    }
    return render(request, 'club/promotion_list.html', context)


@gym_admin_required
def promotion_create(request):
    if request.method == 'POST':
        # [Ч3] request.FILES — загрузка изображения акции
        form = PromotionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Акция создана!')
            return redirect('promotion_list')   # [Ч3] redirect
    else:
        form = PromotionForm()

    return render(request, 'club/promotion_form.html', {
        'form': form, 'title': 'Создание акции',
    })


@gym_admin_required
def promotion_edit(request, pk):
    promotion = get_object_or_404(Promotion, pk=pk)  # [Ч4] Http404

    if request.method == 'POST':
        form = PromotionForm(request.POST, request.FILES, instance=promotion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Акция обновлена!')
            return redirect('promotion_list')   # [Ч3] redirect
    else:
        form = PromotionForm(instance=promotion)

    return render(request, 'club/promotion_form.html', {
        'form': form, 'promotion': promotion, 'title': 'Редактирование акции',
    })


@gym_admin_required
def promotion_delete(request, pk):
    promotion = get_object_or_404(Promotion, pk=pk)

    if request.method == 'POST':
        promotion.delete()              # [Ч4] delete()
        messages.success(request, 'Акция удалена!')
        return redirect('promotion_list')   # [Ч3] redirect после удаления

    return render(request, 'club/promotion_confirm_delete.html', {'promotion': promotion})


# ============================================================
# АНАЛИТИКА
# [Ч1] Агрегация и аннотация — три+ примера
# [Ч4] values(), values_list(), count(), exists(), F expressions
# [Ч1] __ (связанная таблица): user__full_name
# ============================================================

@login_required
def analytics(request):

    # [Ч1] Агрегация пример 1: AVG — средняя цена абонемента
    avg_price = Membership.objects.aggregate(avg_price=Avg('price'))

    # [Ч1] Агрегация пример 2: SUM — общая сумма оплаченных заказов
    total_paid = Order.objects.filter(status='paid').aggregate(total=Sum('total_amount'))

    # [Ч1] Агрегация пример 3: MIN + MAX в одном вызове
    min_max_price = Membership.objects.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )

    # [Ч1] Аннотация: добавляем поле-счётчик к каждой услуге
    # related_name='schedules' позволяет писать Count('schedules')
    services_stats = Service.objects.annotate(
        schedules_count=Count('schedules')  # [Ч1] related_name в аннотации
    )

    # [Ч1] Аннотация: сколько раз покупали каждый абонемент
    memberships_stats = Membership.objects.annotate(
        purchases_count=Count('order_items')  # [Ч1] related_name='order_items'
    )

    # [Ч1] __ (связанная таблица): user__full_name — группировка по полю из User
    # [Ч4] values() + annotate() — группировка как GROUP BY в SQL
    users_orders_stats = Order.objects.values(
        'user__full_name'               # [Ч1] __ по связанной таблице
    ).annotate(
        orders_count=Count('id'),       # [Ч1] аннотация COUNT
        total_spent=Sum('total_amount') # [Ч1] аннотация SUM
    )

    # [Ч4] values_list() — список кортежей (title, price)
    membership_prices = Membership.objects.values_list('title', 'price')

    # [Ч4] count() — разные варианты
    total_orders = Order.objects.count()
    paid_orders_count = Order.objects.filter(status='paid').count()
    cancelled_orders_count = Order.objects.filter(status='cancelled').count()

    # [Ч4] exists()
    has_paid_orders = Order.objects.filter(status='paid').exists()

    # [Ч4] F expressions — цена + 500 вычисляется в SQL
    all_memberships = Membership.objects.annotate(
        new_price=ExpressionWrapper(
            F('price') + 500,           # [Ч4] F expression
            output_field=FloatField()
        )
    )

    context = {
        'avg_price': avg_price,
        'total_paid': total_paid,
        'min_max_price': min_max_price,
        'services_stats': services_stats,
        'memberships_stats': memberships_stats,
        'users_orders_stats': users_orders_stats,
        'membership_prices': membership_prices,
        'total_orders': total_orders,
        'paid_orders_count': paid_orders_count,
        'cancelled_orders_count': cancelled_orders_count,
        'has_paid_orders': has_paid_orders,
        'all_memberships': all_memberships,
    }
    return render(request, 'club/analytics.html', context)


# ============================================================
# [Ч4] Http404 — кастомный обработчик 404
# ============================================================

def custom_404(request, exception):
    """[Ч4] Http404 — показываем свою страницу вместо стандартной."""
    return render(request, 'club/404.html', status=404)
