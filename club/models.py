from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.utils import timezone          # [Ч1] timezone — используется везде ниже
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# ============================================================
# [Ч1] СОБСТВЕННЫЙ МЕНЕДЖЕР — переопределяем get_queryset()
# Менеджер — интерфейс для создания QuerySet.
# objects = стандартный, active = наш кастомный.
# ============================================================

class ActiveMembershipManager(models.Manager):
    """[Ч1] Кастомный менеджер: возвращает только активные абонементы."""
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

    def expensive(self):
        # [Ч1] __ (lookup): price__gte — поле >= значение
        return self.get_queryset().filter(price__gte=2000)

    def with_unlimited_visits(self):
        # [Ч1] __ (lookup): visits_limit__isnull — поле IS NULL
        return self.get_queryset().filter(visits_limit__isnull=True)


class ActivePromotionManager(models.Manager):
    """[Ч1] Кастомный менеджер: возвращает только текущие акции по датам."""
    def get_queryset(self):
        today = timezone.now().date()   # [Ч1] timezone — пример 3: текущая дата
        return super().get_queryset().filter(
            is_active=True,
            start_date__lte=today,      # [Ч1] __ lookup: start_date <= today
            end_date__gte=today         # [Ч1] __ lookup: end_date >= today
        )


class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('role', 'superadmin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, full_name, password, **extra_fields)


# ============================================================
# [Ч1] choices в поле модели
# [Ч1] class Meta: ordering
# [Ч1] timezone — дата регистрации пользователя
# [Ч3] preferred_trainer — ForeignKey (выбор тренера)
# ============================================================

class User(AbstractBaseUser, PermissionsMixin):

    # [Ч1] choices — список допустимых значений поля
    ROLE_CHOICES = [
        ('client', 'Клиент'),
        ('gym_admin', 'Админ тренажерки'),
        ('superadmin', 'Суперадмин сайта'),
    ]

    full_name = models.CharField(max_length=100, verbose_name='ФИО')
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон')

    # [Ч1] choices используется здесь: role принимает только значения из ROLE_CHOICES
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client', verbose_name='Роль')

    # [Ч1] timezone пример 1: сохраняем момент регистрации пользователя
    # Кейс: показываем "С нами с 2024-01-15" в профиле
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Дата регистрации')

    # [Ч1] timezone пример 4: обновляется при каждом входе (views.py, auth_api.py)
    last_login = models.DateTimeField(blank=True, null=True, verbose_name='Последний вход')

    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_staff = models.BooleanField(default=False, verbose_name='Доступ в админку')

    # [Ч1] related_name='preferred_by' — обратная связь к тренеру
    preferred_trainer = models.ForeignKey(
        'Trainer',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='preferred_by',    # trainer.preferred_by.all() — все клиенты этого тренера
        verbose_name='Предпочитаемый тренер'
    )

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']      # [Ч1] Meta ordering: новые пользователи сначала

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    @property
    def is_gym_admin(self):
        return self.role == 'gym_admin'

    @property
    def is_superadmin(self):
        return self.role == 'superadmin'

    @property
    def is_client(self):
        return self.role == 'client'


# ============================================================
# [Ч4] models.URLField — три поля в одной модели
# [Ч3] models.ImageField — icon
# [Ч1] class Meta: ordering
# ============================================================

class Service(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название услуги')
    title_en = models.CharField(max_length=100, blank=True, null=True, verbose_name='Название (англ.)')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')

    # [Ч4] URLField — хранит ссылку на изображение (валидируется как URL)
    image_url = models.URLField(blank=True, null=True, verbose_name='Изображение')

    is_active = models.BooleanField(default=True, verbose_name='Активна')

    # [Ч3] ImageField — загрузка файла-картинки, сохраняется в MEDIA_ROOT/services/icons/
    icon = models.ImageField(
        upload_to='services/icons/',
        blank=True, null=True,
        verbose_name='Иконка услуги'
    )

    # [Ч4] URLField — ещё два примера URLField в одной модели
    website_url = models.URLField(
        blank=True, null=True,
        verbose_name='Сайт услуги',
        help_text='Ссылка на официальный сайт услуги'
    )
    video_url = models.URLField(
        blank=True, null=True,
        verbose_name='Ссылка на видео',
        help_text='Ссылка на видео-презентацию услуги'
    )

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['title']    # [Ч1] Meta ordering: алфавитный порядок

    def __str__(self):
        return self.title

    def get_icon_url(self):
        if self.icon:
            return self.icon.url
        return '/static/images/default_service.png'


# ============================================================
# [Ч1] get_absolute_url + reverse
# [Ч1] Кастомный менеджер (active = ActiveMembershipManager)
# [Ч1] timezone пример 2 — is_new через created_at
# [Ч1] Meta ordering
# [Ч3] Собственный метод модели
# ============================================================

class Membership(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название абонемента')
    title_en = models.CharField(max_length=100, blank=True, null=True, verbose_name='Название (англ.)')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    duration_days = models.PositiveIntegerField(verbose_name='Срок действия (дней)')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Цена')
    visits_limit = models.PositiveIntegerField(blank=True, null=True, verbose_name='Лимит посещений')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    # [Ч1] timezone пример 2: дата создания абонемента
    # Кейс: если абонемент создан <= 30 дней назад — показываем бейдж "Новинка" на фронте
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')

    objects = models.Manager()          # стандартный менеджер
    active = ActiveMembershipManager()  # [Ч1] наш кастомный — только is_active=True

    class Meta:
        verbose_name = 'Абонемент'
        verbose_name_plural = 'Абонементы'
        ordering = ['price']            # [Ч1] Meta ordering: от дешёвых к дорогим

    def __str__(self):
        return f"{self.title} — {self.price} ₽"

    # [Ч1] get_absolute_url + reverse
    # Используется в шаблоне: {{ membership.get_absolute_url }}
    # Django сам вызывает reverse() и строит URL /memberships/5/
    def get_absolute_url(self):
        return reverse('membership_detail', kwargs={'pk': self.pk})

    # [Ч3] Собственный метод модели (property)
    # Кейс: на фронте показывается зелёный тег "Новинка" если абонемент свежий
    @property
    def is_new(self):
        return (timezone.now() - self.created_at).days <= 30  # [Ч1] timezone: сравниваем с now()


# ============================================================
# [Ч3] ImageField — photo
# [Ч3] FileField — cv_file (резюме PDF)
# [Ч4] URLField — photo_url
# [Ч1] timezone — hired_at, work_experience_days
# [Ч3] Собственные методы модели
# [Ч1] related_name в ForeignKey (Schedule → Trainer)
# ============================================================

class Trainer(models.Model):
    full_name = models.CharField(max_length=100, verbose_name='ФИО тренера')
    full_name_en = models.CharField(max_length=100, blank=True, null=True, verbose_name='ФИО (англ.)')
    specialization = models.CharField(max_length=100, blank=True, null=True, verbose_name='Специализация')
    experience_years = models.PositiveIntegerField(default=0, verbose_name='Опыт (лет)')

    # [Ч4] URLField — ссылка на фото как URL (не файл)
    photo_url = models.URLField(blank=True, null=True, verbose_name='Фото')

    bio = models.TextField(blank=True, null=True, verbose_name='Биография')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    # [Ч1] timezone — дата найма, используется в work_experience_days ниже
    hired_at = models.DateField(default=timezone.now, verbose_name='Дата найма')

    # ManyToMany без through — для filter_horizontal в Admin
    # Смысл: тренер может вести несколько видов услуг
    services = models.ManyToManyField(
        'Service',
        blank=True,
        related_name='specialist_trainers',
        verbose_name='Услуги тренера'
    )

    # [Ч3] ImageField — загрузка фото тренера через форму/API
    # Файл сохраняется физически в media/trainers/photos/
    photo = models.ImageField(
        upload_to='trainers/photos/',
        blank=True, null=True,
        verbose_name='Фото тренера'
    )

    # [Ч3] FileField — загрузка PDF-резюме
    # Валидация .pdf — в forms.py (clean_cv_file)
    cv_file = models.FileField(
        upload_to='trainers/cv/',
        blank=True, null=True,
        verbose_name='Резюме (PDF)'
    )

    class Meta:
        verbose_name = 'Тренер'
        verbose_name_plural = 'Тренеры'
        ordering = ['full_name']        # [Ч1] Meta ordering: алфавитный

    def __str__(self):
        return self.full_name

    # [Ч3] Собственный метод модели — property
    # Кейс: считаем сколько дней тренер работает в клубе
    @property
    def work_experience_days(self):
        return (timezone.now().date() - self.hired_at).days  # [Ч1] timezone: разница дат

    # [Ч3] Собственный метод модели — обычный метод
    # Кейс: возвращает читаемую строку об уровне тренера для отображения в карточке
    def get_experience_display(self):
        if self.experience_years >= 10:
            return f"{self.experience_years} лет (эксперт)"
        elif self.experience_years >= 5:
            return f"{self.experience_years} лет (опытный)"
        elif self.experience_years >= 2:
            return f"{self.experience_years} года (средний)"
        else:
            return f"{self.experience_years} лет (начинающий)"

    def get_photo_url(self):
        if self.photo:
            return self.photo.url
        return '/static/images/default_avatar.png'


# ============================================================
# [Ч1] related_name — 'schedules' используется в аннотации Count('schedules')
# [Ч1] Meta ordering по двум полям
# [Ч2] select_related — Service + Trainer в одном запросе (api_views.py)
# ============================================================

class Schedule(models.Model):
    # [Ч1] related_name='schedules' — используется как:
    # service.schedules.all() — все занятия этой услуги
    # Service.objects.annotate(schedules_count=Count('schedules'))
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='Услуга'
    )
    # [Ч1] related_name='schedules' — trainer.schedules.all()
    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='Тренер'
    )
    class_date = models.DateField(verbose_name='Дата занятия')
    start_time = models.TimeField(verbose_name='Время начала')
    end_time = models.TimeField(verbose_name='Время окончания')
    hall = models.CharField(max_length=50, blank=True, null=True, verbose_name='Зал')
    capacity = models.PositiveIntegerField(default=20, verbose_name='Вместимость')

    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписание'
        ordering = ['class_date', 'start_time']  # [Ч1] Meta ordering по двум полям

    def __str__(self):
        return f"{self.service.title} — {self.class_date} {self.start_time}"


# ============================================================
# [Ч1] choices — два набора (PAYMENT_CHOICES, STATUS_CHOICES)
# [Ч1] related_name='orders' — используется: user.orders.all()
# [Ч1] timezone — дата заказа
# [Ч1] Meta ordering
# ============================================================

class Order(models.Model):

    # [Ч1] choices — способ оплаты
    PAYMENT_CHOICES = [
        ('card', 'Банковская карта'),
        ('wallet', 'Электронный кошелёк'),
        ('cash', 'Наличные'),
    ]

    # [Ч1] choices — статус заказа
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('cancelled', 'Отменён'),
        ('refunded', 'Возврат'),
    ]

    # [Ч1] related_name='orders' — используется в profile_view: user.orders.all()[:10]
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Пользователь'
    )

    # [Ч1] timezone — фиксируем момент создания заказа
    order_date = models.DateTimeField(default=timezone.now, verbose_name='Дата заказа')

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Сумма заказа')

    # [Ч1] choices используется
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='card', verbose_name='Способ оплаты')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-order_date']      # [Ч1] Meta ordering: новые заказы сначала

    def __str__(self):
        return f"Заказ №{self.id} — {self.user.full_name}"


# ============================================================
# [Ч1] related_name='items' — используется: order.items.all()
# [Ч1] __ (связанная таблица): items__membership в filter()
# ============================================================

class OrderItem(models.Model):
    # [Ч1] related_name='items' — используется как:
    # order.items.all() — все позиции заказа
    # Order.objects.filter(items__membership=membership) — JOIN через __
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ'
    )
    # [Ч1] related_name='order_items' — используется в аннотации:
    # Membership.objects.annotate(purchases_count=Count('order_items'))
    membership = models.ForeignKey(
        Membership,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name='Абонемент'
    )
    price_paid = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Оплаченная цена')

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

    def __str__(self):
        return f"{self.membership.title} в заказе №{self.order.id}"


# ============================================================
# [Ч1] choices — статус абонемента пользователя
# [Ч1] related_name='memberships' — user.memberships.all()
# [Ч4] update() — используется в auth_api.py для смены абонемента
# ============================================================

class UserMembership(models.Model):
    # [Ч1] choices — статус
    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('expired', 'Истёк'),
        ('frozen', 'Заморожен'),
    ]

    # [Ч1] related_name='memberships' — user.memberships.filter(status='active')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name='Пользователь'
    )
    # [Ч1] related_name='user_memberships' — membership.user_memberships.all()
    membership = models.ForeignKey(
        Membership,
        on_delete=models.CASCADE,
        related_name='user_memberships',
        verbose_name='Абонемент'
    )

    # [Ч1] timezone — дата покупки
    purchase_date = models.DateTimeField(default=timezone.now, verbose_name='Дата покупки')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата окончания')

    # [Ч1] choices
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Статус')
    visits_used = models.PositiveIntegerField(default=0, verbose_name='Использовано посещений')

    class Meta:
        verbose_name = 'Абонемент пользователя'
        verbose_name_plural = 'Абонементы пользователей'
        unique_together = ('user', 'membership', 'start_date')
        ordering = ['-purchase_date']   # [Ч1] Meta ordering

    def __str__(self):
        return f"{self.user.full_name} — {self.membership.title}"


class ConsultationRequest(models.Model):
    # [Ч1] choices
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('processed', 'В обработке'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    ]

    # [Ч1] related_name='consultation_requests'
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='consultation_requests',
        verbose_name='Пользователь'
    )
    full_name = models.CharField(max_length=100, verbose_name='ФИО')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    preferred_time = models.CharField(max_length=100, blank=True, null=True, verbose_name='Удобное время')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус')  # [Ч1] choices

    # [Ч1] timezone — дата заявки
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Заявка на консультацию'
        verbose_name_plural = 'Заявки на консультацию'
        ordering = ['-created_at']      # [Ч1] Meta ordering

    def __str__(self):
        return f"Заявка: {self.full_name} ({self.phone})"


# ============================================================
# [Ч2] ManyToManyField с through — связь через промежуточную таблицу
# [Ч3] ImageField — image
# [Ч4] URLField — image_url
# [Ч1] Кастомный менеджер — active = ActivePromotionManager
# [Ч1] timezone — несколько примеров
# [Ч3] Собственные методы модели
# ============================================================

class Promotion(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название акции')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Скидка (%)')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата окончания')

    # [Ч4] URLField — ссылка на картинку
    image_url = models.URLField(blank=True, null=True, verbose_name='Изображение')

    is_active = models.BooleanField(default=True, verbose_name='Активна')

    # [Ч1] timezone — дата создания акции
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')

    # [Ч2] ManyToManyField с through — вместо прямой связи используем промежуточную модель
    # Это позволяет добавить дополнительные поля к связи в будущем
    # Использование: promo.memberships.all() — все абонементы по акции
    #                membership.promotions.all() — все акции этого абонемента
    memberships = models.ManyToManyField(
        Membership,
        through='PromotionMembership',  # [Ч2] through — промежуточная таблица
        related_name='promotions',
        verbose_name='Абонементы'
    )

    # [Ч3] ImageField — загружаемое изображение акции (файл, не URL)
    image = models.ImageField(
        upload_to='promotions/',
        blank=True, null=True,
        verbose_name='Изображение акции'
    )

    objects = models.Manager()          # стандартный менеджер
    active = ActivePromotionManager()   # [Ч1] кастомный — только текущие акции

    class Meta:
        verbose_name = 'Акция'
        verbose_name_plural = 'Акции'
        ordering = ['-start_date']      # [Ч1] Meta ordering: новые акции сначала

    def __str__(self):
        return f"{self.title} ({self.discount_percent}%)"

    # [Ч3] Собственный метод-свойство
    # Кейс: проверяем активна ли акция прямо сейчас (дата попадает в диапазон)
    @property
    def is_current(self):
        today = timezone.now().date()   # [Ч1] timezone пример 3
        return self.start_date <= today <= self.end_date

    # [Ч3] Собственный метод модели
    # Кейс: на фронте показываем "осталось N дней" рядом с акцией
    def get_days_left(self):
        today = timezone.now().date()   # [Ч1] timezone: арифметика с датами
        if self.end_date >= today:
            return (self.end_date - today).days
        return 0

    # [Ч3] Собственный метод — возвращает статус для отображения
    def is_active_display(self):
        today = timezone.now().date()
        if self.is_current:
            return "Активна"
        elif self.start_date > today:
            return "Скоро начнется"
        else:
            return "Завершена"


# ============================================================
# [Ч2] Промежуточная модель для ManyToManyField.through
# Именно эту таблицу Django создаёт в БД для связи Promotion ↔ Membership
# ============================================================

class PromotionMembership(models.Model):
    """[Ч2] through-модель: явная промежуточная таблица для M2M связи."""
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, verbose_name='Акция')
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, verbose_name='Абонемент')

    class Meta:
        verbose_name = 'Связь акции и абонемента'
        verbose_name_plural = 'Связи акций и абонементов'
        unique_together = ('promotion', 'membership')   # одна связь не может дублироваться

    def __str__(self):
        return f"{self.promotion.title} → {self.membership.title}"


# ============================================================
# [Ч1] related_name — три ForeignKey с разными related_name
# ============================================================

class Favorite(models.Model):
    # [Ч1] related_name='favorites' — user.favorites.all()
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    # [Ч1] related_name='favorites' — membership.favorites.all() (Count в аннотации)
    membership = models.ForeignKey(
        Membership,
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='favorites',
        verbose_name='Абонемент'
    )
    # [Ч1] related_name='favorites' — service.favorites.all()
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='favorites',
        verbose_name='Услуга'
    )

    # [Ч1] timezone — дата добавления в избранное
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ['-created_at']      # [Ч1] Meta ordering

    def __str__(self):
        target = self.membership.title if self.membership else self.service.title if self.service else "Объект"
        return f"{self.user.full_name} → {target}"
