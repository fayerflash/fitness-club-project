import io
from django.http import HttpResponse
from django.contrib import admin
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.utils import timezone

# Регистрируем Arial с поддержкой кириллицы
pdfmetrics.registerFont(TTFont('Arial', '/System/Library/Fonts/Supplemental/Arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', '/System/Library/Fonts/Supplemental/Arial Bold.ttf'))

from .models import (
    User, Service, Membership, Trainer, Schedule,
    Order, OrderItem, UserMembership, ConsultationRequest,
    Promotion, PromotionMembership, Favorite
)

# list_display       — колонки в таблице списка объектов
# list_display_links — кликабельные колонки (ведут на страницу объекта)
# list_filter        — фильтры справа: можно использовать поля связных моделей
# search_fields      — поля для строки поиска (__ для связных таблиц)
# date_hierarchy     — навигация по датам над списком
# readonly_fields    — поля только для чтения (нельзя редактировать)
# raw_id_fields      — заменяет select на поле с лупой, если записей много
# inlines            — встроенные таблицы связных объектов
# filter_horizontal  — виджет двух колонок для ManyToMany (без through)
# @admin.display     — декоратор для кастомного поля в list_display
# short_description  — подпись колонки / действия
# actions            — кастомные действия в выпадающем меню


# =============================================================
# PDF ЭКСПОРТ — [Ч3] Генерация PDF 
# [Ч3] short_description задаёт текст в меню "Действия"
# =============================================================

def export_to_pdf(modeladmin, request, queryset):  # noqa: параметры нужны Django
    """Универсальный экспорт любой модели в PDF."""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="{queryset.model._meta.model_name}_export.pdf"'
    )
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont("Arial-Bold", 16)
    p.drawString(50, height - 50, f"Экспорт: {queryset.model._meta.verbose_name_plural}")
    p.setFont("Arial", 10)
    p.drawString(50, height - 70, f"Дата: {timezone.now().strftime('%d.%m.%Y %H:%M')}")

    y = height - 100
    for obj in queryset:
        if y < 50:
            p.showPage()
            y = height - 50
            p.setFont("Arial", 10)
        p.drawString(50, y, str(obj)[:90])
        y -= 20
    p.save()

    response.write(buffer.getvalue())
    buffer.close()
    return response

# [Ч3] short_description — текст пункта в меню "Действия"
export_to_pdf.short_description = "📄 Экспорт в PDF"


def export_memberships_pdf(modeladmin, request, queryset):
    """Детальный PDF-экспорт абонементов с таблицей."""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="memberships.pdf"'
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont("Arial-Bold", 18)
    p.drawString(50, height - 50, "Список абонементов")
    p.setFont("Arial", 10)
    p.drawString(50, height - 70, f"Дата: {timezone.now().strftime('%d.%m.%Y %H:%M')}")

    y = height - 100
    p.setFont("Arial-Bold", 10)
    for label, x in [("ID", 50), ("Название", 100), ("Цена", 300), ("Дней", 400)]:
        p.drawString(x, y, label)
    y -= 20
    p.setFont("Arial", 10)

    for m in queryset:
        if y < 50:
            p.showPage(); y = height - 50
        p.drawString(50, y, str(m.id))
        p.drawString(100, y, m.title[:30])
        p.drawString(300, y, f"{m.price} ₽")
        p.drawString(400, y, str(m.duration_days))
        y -= 20
    p.save()

    response.write(buffer.getvalue())
    buffer.close()
    return response

export_memberships_pdf.short_description = "📊 Экспорт абонементов (детальный)"


def export_trainers_pdf(modeladmin, request, queryset):
    """Детальный PDF-экспорт тренеров с таблицей."""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="trainers.pdf"'

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Заголовок
    p.setFont("Arial-Bold", 18)
    p.drawString(50, height - 50, "Список тренеров")
    p.setFont("Arial", 10)
    p.drawString(50, height - 70, f"Дата: {timezone.now().strftime('%d.%m.%Y %H:%M')}")
    p.drawString(50, height - 85, f"Всего тренеров: {queryset.count()}")

    # Шапка таблицы
    y = height - 115
    p.setFont("Arial-Bold", 9)
    p.drawString(40,  y, "ID")
    p.drawString(70,  y, "ФИО")
    p.drawString(230, y, "Специализация")
    p.drawString(360, y, "Опыт (лет)")
    p.drawString(430, y, "Статус")
    p.drawString(490, y, "Нанят")

    # Линия под шапкой
    y -= 5
    p.line(40, y, width - 40, y)
    y -= 15

    # Данные
    p.setFont("Arial", 9)
    for t in queryset:
        if y < 50:
            p.showPage()
            y = height - 50
            p.setFont("Arial", 9)

        p.drawString(40,  y, str(t.id))
        p.drawString(70,  y, (t.full_name or '')[:22])
        p.drawString(230, y, (t.specialization or '-')[:18])
        p.drawString(360, y, str(t.experience_years))
        p.drawString(430, y, 'Активен' if t.is_active else 'Неактивен')
        p.drawString(490, y, t.hired_at.strftime('%d.%m.%Y'))
        y -= 18

    p.save()
    response.write(buffer.getvalue())
    buffer.close()
    return response

export_trainers_pdf.short_description = "📄 Экспорт тренеров в PDF"


# =============================================================
# КАСТОМНЫЕ ДЕЙСТВИЯ
# [Ч3] Действия в Django Admin — появляются в выпадающем меню
# [Ч4] update() — массовое обновление одним SQL-запросом
# =============================================================

def mark_as_active(modeladmin, request, queryset):
    """Отмечает выбранные объекты как активные."""
    # [Ч4] update() — без загрузки каждого объекта в Python
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f"Активировано объектов: {updated}")

mark_as_active.short_description = "✅ Отметить как активные"


def mark_as_inactive(modeladmin, request, queryset):
    """Деактивирует выбранные объекты."""
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f"Деактивировано объектов: {updated}")

mark_as_inactive.short_description = "❌ Отметить как неактивные"


# =============================================================
# INLINE-КЛАССЫ
# inlines — встроенные таблицы связных объектов внутри формы
# raw_id_fields в inline — заменяет select на поле-ссылку
#   (актуально когда в таблице тысячи записей — select тормозит)
# =============================================================

class OrderItemInline(admin.TabularInline):
    """Позиции заказа — встроены в форму заказа."""
    model = OrderItem
    extra = 1                           # 1 пустая строка для добавления
    # raw_id_fields: Membership может иметь много записей — не грузим select
    raw_id_fields = ('membership',)
    readonly_fields = ('price_paid',)   # цена фиксируется при создании


class PromotionMembershipInline(admin.TabularInline):
    """Абонементы по акции — встроены в форму акции."""
    model = PromotionMembership
    extra = 1
    # raw_id_fields: вместо <select> с абонементами — компактное поле с лупой
    raw_id_fields = ('membership',)


class ScheduleInline(admin.TabularInline):
    """Расписание — встроено в форму услуги."""
    model = Schedule
    extra = 1
    # raw_id_fields: тренеров может быть много — используем id-поле
    raw_id_fields = ('trainer',)


class UserMembershipInline(admin.TabularInline):
    """Абонементы пользователя — встроены в форму пользователя."""
    model = UserMembership
    extra = 0                           # не показываем пустые строки
    raw_id_fields = ('membership',)
    readonly_fields = ('purchase_date',)


class FavoriteInline(admin.TabularInline):
    """Избранное пользователя — встроено в форму пользователя."""
    model = Favorite
    extra = 0
    # raw_id_fields: и membership, и service могут иметь много записей
    raw_id_fields = ('membership', 'service')
    readonly_fields = ('created_at',)


# =============================================================
# ПОЛЬЗОВАТЕЛИ
# =============================================================

@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    # list_display — колонки таблицы; последняя ('orders_count') — кастомный метод
    list_display = (
        'id', 'full_name', 'email', 'phone',
        'role', 'is_active', 'created_at', 'orders_count'
    )

    # list_display_links — по каким колонкам можно кликнуть чтобы открыть объект
    list_display_links = ('id', 'full_name', 'email')

    # list_filter — фильтры справа; 'preferred_trainer' — поле связной модели
    list_filter = ('role', 'is_active', 'created_at')

    # search_fields — полнотекстовый поиск; __ = поиск по полю связной модели
    search_fields = ('full_name', 'email', 'phone')

    # readonly_fields — эти поля нельзя изменить в форме (устанавливаются автоматически)
    readonly_fields = ('created_at', 'last_login')

    # date_hierarchy — навигация по датам над списком (год → месяц → день)
    date_hierarchy = 'created_at'

    # inlines — встроенные таблицы связных объектов
    inlines = [UserMembershipInline, FavoriteInline]

    # raw_id_fields — preferred_trainer: тренеров может быть много, не грузим <select>
    raw_id_fields = ('preferred_trainer',)

    # @admin.display — декоратор для кастомной колонки в list_display
    # description — заголовок колонки (аналог short_description)
    @admin.display(description='Заказов')
    def orders_count(self, obj):
        return obj.orders.count()


# =============================================================
# УСЛУГИ
# =============================================================

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):

    # list_display с кастомным методом schedules_count
    list_display = ('id', 'title', 'title_en', 'is_active', 'schedules_count')

    list_display_links = ('id', 'title')

    list_filter = ('is_active',)

    # search_fields — ищем по полям самой модели
    search_fields = ('title', 'title_en', 'description')

    # inlines — расписание встроено в форму услуги
    inlines = [ScheduleInline]

    actions = [mark_as_active, mark_as_inactive, export_to_pdf]

    @admin.display(description='Занятий')
    def schedules_count(self, obj):
        # related_name='schedules' позволяет обращаться так
        return obj.schedules.count()


# =============================================================
# АБОНЕМЕНТЫ
# =============================================================

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):

    list_display = (
        'id', 'title', 'title_en', 'price', 'duration_days',
        'visits_limit', 'is_active', 'is_new_display', 'created_at', 'purchases_count'
    )

    list_display_links = ('id', 'title')

    # list_filter — 'is_active' и дата создания
    list_filter = ('is_active', 'created_at')

    search_fields = ('title', 'title_en', 'description')

    readonly_fields = ('created_at',)

    date_hierarchy = 'created_at'

    actions = [export_to_pdf, export_memberships_pdf, mark_as_active, mark_as_inactive]

    # @admin.display с boolean=True — показывает иконку ✓ или ✗
    @admin.display(description='Новинка', boolean=True)
    def is_new_display(self, obj):
        return obj.is_new

    @admin.display(description='Покупок')
    def purchases_count(self, obj):
        # related_name='order_items' в OrderItem.membership
        return obj.order_items.count()


# =============================================================
# ТРЕНЕРЫ
# =============================================================

@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):

    list_display = (
        'id', 'full_name', 'full_name_en', 'specialization',
        'experience_years', 'is_active', 'hired_at', 'services_list'
    )

    list_display_links = ('id', 'full_name')

    # list_filter — 'is_active', 'hired_at' и поле связной модели 'services'
    list_filter = ('is_active', 'hired_at', 'services')

    search_fields = ('full_name', 'full_name_en', 'specialization', 'bio')

    readonly_fields = ('hired_at', 'work_experience_days_display')

    date_hierarchy = 'hired_at'

    # filter_horizontal — виджет "двух колонок" для ManyToMany
    # Применяется только к прямым M2M (без through)
    # Trainer.services — прямой M2M к Service
    filter_horizontal = ('services',)

    actions = [export_to_pdf, export_trainers_pdf, mark_as_active, mark_as_inactive]

    @admin.display(description='Услуги')
    def services_list(self, obj):
        names = obj.services.values_list('title', flat=True)
        return ', '.join(names) if names else '—'

    @admin.display(description='Дней в клубе')
    def work_experience_days_display(self, obj):
        return obj.work_experience_days


# =============================================================
# РАСПИСАНИЕ
# =============================================================

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):

    list_display = (
        'id', 'service', 'trainer', 'class_date',
        'start_time', 'end_time', 'hall', 'capacity'
    )

    list_display_links = ('id', 'service')

    # list_filter — используем поля связных моделей: service и trainer
    list_filter = ('class_date', 'service', 'trainer', 'hall')

    # search_fields с __ — поиск по полям связных таблиц
    # service__title — поле title из таблицы Service
    # trainer__full_name — поле full_name из таблицы Trainer
    search_fields = ('service__title', 'trainer__full_name', 'hall')

    date_hierarchy = 'class_date'

    # raw_id_fields: Service и Trainer могут иметь много записей
    # Без raw_id_fields — Django загрузит все записи в <select>, что медленно
    raw_id_fields = ('service', 'trainer')

    actions = [export_to_pdf]


# =============================================================
# ЗАКАЗЫ
# =============================================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id', 'user', 'total_amount', 'payment_method',
        'status', 'order_date', 'items_count', 'user_role'
    )

    list_display_links = ('id', 'user')

    # list_filter с полем связной модели: user__role — роль из таблицы User
    list_filter = ('status', 'payment_method', 'order_date', 'user__role')

    # search_fields: __ — ищем по полям связной таблицы User
    search_fields = ('user__full_name', 'user__email', 'user__phone')

    readonly_fields = ('order_date',)

    date_hierarchy = 'order_date'

    # raw_id_fields: пользователей может быть много — не грузим <select>
    raw_id_fields = ('user',)

    inlines = [OrderItemInline]

    actions = [export_to_pdf]

    @admin.display(description='Позиций')
    def items_count(self, obj):
        return obj.items.count()

    # Пример использования поля связной модели в @admin.display
    @admin.display(description='Роль клиента')
    def user_role(self, obj):
        return obj.user.get_role_display()


# =============================================================
# ПОЗИЦИИ ЗАКАЗА
# =============================================================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = ('id', 'order', 'membership', 'price_paid', 'buyer_name', 'order_status')

    list_display_links = ('id', 'order')

    # list_filter с полями связных моделей через __
    list_filter = ('order__status', 'order__payment_method', 'membership')

    # search_fields: трёхуровневый __ — из OrderItem → Order → User
    search_fields = (
        'membership__title',
        'order__user__full_name',
        'order__user__email'
    )

    # raw_id_fields: Order и Membership — не грузим их в <select>
    raw_id_fields = ('order', 'membership')

    actions = [export_to_pdf]

    @admin.display(description='Покупатель')
    def buyer_name(self, obj):
        return obj.order.user.full_name

    @admin.display(description='Статус заказа')
    def order_status(self, obj):
        return obj.order.get_status_display()


# =============================================================
# АБОНЕМЕНТЫ ПОЛЬЗОВАТЕЛЕЙ
# =============================================================

@admin.register(UserMembership)
class UserMembershipAdmin(admin.ModelAdmin):

    list_display = (
        'id', 'user', 'membership', 'start_date',
        'end_date', 'status', 'visits_used', 'visits_left_display'
    )

    list_display_links = ('id', 'user')

    # list_filter с полями связных моделей
    list_filter = ('status', 'start_date', 'membership__is_active')

    # search_fields по полям связных таблиц
    search_fields = (
        'user__full_name', 'user__email',
        'membership__title'
    )

    # raw_id_fields: User и Membership — много записей
    raw_id_fields = ('user', 'membership')

    readonly_fields = ('purchase_date',)

    date_hierarchy = 'start_date'

    actions = [export_to_pdf]

    @admin.display(description='Осталось визитов')
    def visits_left_display(self, obj):
        if obj.membership.visits_limit is None:
            return '∞ (безлимит)'
        left = obj.membership.visits_limit - obj.visits_used
        return max(left, 0)


# =============================================================
# ЗАЯВКИ НА КОНСУЛЬТАЦИЮ
# =============================================================

@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):

    list_display = (
        'id', 'full_name', 'phone', 'email',
        'status', 'created_at', 'linked_user_name'
    )

    list_display_links = ('id', 'full_name')

    list_filter = ('status', 'created_at')

    search_fields = (
        'full_name', 'phone', 'email',
        # __ — ищем по полям связной модели User
        'user__full_name', 'user__email'
    )

    readonly_fields = ('created_at',)

    date_hierarchy = 'created_at'

    # raw_id_fields: User — не грузим весь список пользователей в <select>
    raw_id_fields = ('user',)

    actions = [export_to_pdf]

    @admin.display(description='Пользователь в системе')
    def linked_user_name(self, obj):
        return obj.user.full_name if obj.user else '—'


# =============================================================
# АКЦИИ
# =============================================================

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):

    list_display = (
        'id', 'title', 'discount_percent', 'start_date',
        'end_date', 'is_active', 'status_display', 'memberships_count'
    )

    list_display_links = ('id', 'title')

    list_filter = ('is_active', 'start_date', 'end_date')

    search_fields = ('title', 'description')

    date_hierarchy = 'start_date'

    readonly_fields = ('created_at',)

    # inlines — привязка абонементов через промежуточную таблицу
    # (filter_horizontal здесь нельзя — поле использует through='PromotionMembership')
    inlines = [PromotionMembershipInline]

    actions = [export_to_pdf, mark_as_active, mark_as_inactive]

    @admin.display(description='Статус')
    def status_display(self, obj):
        return obj.is_active_display()

    @admin.display(description='Абонементов')
    def memberships_count(self, obj):
        return obj.memberships.count()


# =============================================================
# СВЯЗЬ АКЦИЯ ↔ АБОНЕМЕНТ (промежуточная таблица)
# =============================================================

@admin.register(PromotionMembership)
class PromotionMembershipAdmin(admin.ModelAdmin):

    list_display = ('id', 'promotion', 'membership', 'promotion_discount', 'membership_price')

    list_display_links = ('id', 'promotion')

    # list_filter с полями связных моделей
    list_filter = ('promotion', 'membership')

    search_fields = ('promotion__title', 'membership__title')

    # raw_id_fields: оба поля — не грузим списки в <select>
    raw_id_fields = ('promotion', 'membership')

    actions = [export_to_pdf]

    @admin.display(description='Скидка (%)')
    def promotion_discount(self, obj):
        return f"{obj.promotion.discount_percent}%"

    @admin.display(description='Цена абонемента')
    def membership_price(self, obj):
        return f"{obj.membership.price} ₽"


# =============================================================
# ИЗБРАННОЕ
# =============================================================

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):

    list_display = (
        'id', 'user', 'favorite_type',
        'membership', 'service', 'created_at'
    )

    list_display_links = ('id', 'user')

    list_filter = ('created_at',)

    # search_fields с __ по связным таблицам
    search_fields = (
        'user__full_name', 'user__email',
        'membership__title',
        'service__title'
    )

    readonly_fields = ('created_at',)

    date_hierarchy = 'created_at'

    # raw_id_fields: User, Membership, Service — много записей, не грузим <select>
    raw_id_fields = ('user', 'membership', 'service')

    actions = [export_to_pdf]

    @admin.display(description='Тип')
    def favorite_type(self, obj):
        if obj.membership:
            return '🎫 Абонемент'
        if obj.service:
            return '🏋️ Услуга'
        return '—'