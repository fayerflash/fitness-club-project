from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, time, timedelta
from club.models import (
    User, Service, Membership, Trainer, Schedule,
    Promotion, PromotionMembership, Order, OrderItem, UserMembership
)


class Command(BaseCommand):
    help = 'Заполнить БД тестовыми данными'

    def handle(self, *args, **kwargs):
        self.stdout.write('Очищаю старые данные...')
        Schedule.objects.all().delete()
        PromotionMembership.objects.all().delete()
        OrderItem.objects.all().delete()
        UserMembership.objects.all().delete()
        Order.objects.all().delete()
        Promotion.objects.all().delete()
        Membership.objects.all().delete()
        Service.objects.all().delete()
        Trainer.objects.all().delete()
        User.objects.filter(role__in=['client', 'gym_admin']).delete()

        self.stdout.write('Создаю услуги...')
        services_data = [
            ('Йога', 'Yoga', 'Занятия йогой для всех уровней', 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400'),
            ('Пилатес', 'Pilates', 'Укрепление мышц кора и улучшение осанки', 'https://images.unsplash.com/photo-1518611012118-696072aa579a?w=400'),
            ('Бокс', 'Boxing', 'Бокс и ударные единоборства', 'https://images.unsplash.com/photo-1549719386-74dfcbf7dbed?w=400'),
            ('Кроссфит', 'CrossFit', 'Интенсивные функциональные тренировки', 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=400'),
            ('Аквааэробика', 'Aqua Aerobics', 'Аэробика в бассейне', 'https://images.unsplash.com/photo-1600965962361-9035dbfd1c50?w=400'),
            ('Зумба', 'Zumba', 'Танцевальная фитнес-программа', 'https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=400'),
            ('Стретчинг', 'Stretching', 'Растяжка и гибкость', 'https://images.unsplash.com/photo-1566241440091-ec10de8db2e1?w=400'),
            ('TRX', 'TRX Training', 'Тренировки с подвесными петлями', 'https://images.unsplash.com/photo-1601422407692-ec4eeec1d9b3?w=400'),
            ('Единоборства', 'Martial Arts', 'Смешанные единоборства MMA', 'https://images.unsplash.com/photo-1555597673-b21d5c935865?w=400'),
            ('Силовые тренировки', 'Strength Training', 'Работа с тяжёлыми весами', 'https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=400'),
            ('Кардио', 'Cardio', 'Кардиотренировки для похудения', 'https://images.unsplash.com/photo-1538805060514-97d9cc17730c?w=400'),
        ]
        services = []
        for title, title_en, desc, img in services_data:
            s = Service.objects.create(title=title, title_en=title_en, description=desc, image_url=img, is_active=True)
            services.append(s)

        self.stdout.write('Создаю абонементы...')
        memberships_data = [
            ('Стандарт', 'Standard', 'Базовый абонемент на месяц', 30, 1500, 12),
            ('Премиум', 'Premium', 'Расширенный доступ ко всем залам', 30, 2800, None),
            ('Студенческий', 'Student', 'Специальная цена для студентов', 30, 900, 8),
            ('Годовой', 'Annual', 'Годовой абонемент с выгодой 30%', 365, 9900, None),
            ('Пробный', 'Trial', '7 дней для знакомства с клубом', 7, 500, 5),
            ('Семейный', 'Family', 'Для двух человек из одной семьи', 30, 3500, None),
            ('VIP', 'VIP', 'Персональный тренер + все услуги', 30, 5500, None),
            ('Утренний', 'Morning', 'Посещение только до 12:00', 30, 1100, None),
            ('Безлимит', 'Unlimited', 'Безлимитное посещение любых групп', 30, 3200, None),
            ('Детский', 'Kids', 'Для детей от 6 до 14 лет', 30, 1200, 8),
            ('Онлайн', 'Online', 'Тренировки в прямом эфире', 30, 700, None),
        ]
        memberships = []
        for title, title_en, desc, days, price, visits in memberships_data:
            m = Membership.objects.create(
                title=title, title_en=title_en, description=desc,
                duration_days=days, price=price, visits_limit=visits, is_active=True
            )
            memberships.append(m)

        self.stdout.write('Создаю тренеров...')
        trainers_data = [
            ('Алексей Петров', 'Alexey Petrov', 'Йога, Пилатес', 8,
             'https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=200',
             'Сертифицированный инструктор по йоге и пилатесу.'),
            ('Марина Соколова', 'Marina Sokolova', 'Зумба, Стретчинг', 5,
             'https://images.unsplash.com/photo-1609899464726-209b52e64e29?w=200',
             'Танцевальный тренер с международными сертификатами.'),
            ('Дмитрий Коваль', 'Dmitry Koval', 'Бокс, Единоборства', 12,
             'https://images.unsplash.com/photo-1583454155184-870a1f63aebc?w=200',
             'Мастер спорта по боксу, тренер сборной.'),
            ('Ольга Нечаева', 'Olga Nechaeva', 'Кардио, Кроссфит', 6,
             'https://images.unsplash.com/photo-1548690312-e3b507d8c110?w=200',
             'Специалист по функциональным тренировкам.'),
            ('Сергей Ломов', 'Sergey Lomov', 'Силовые тренировки, TRX', 10,
             'https://images.unsplash.com/photo-1567013127542-490d757e51fc?w=200',
             'Опыт работы с атлетами высшего уровня.'),
            ('Анна Белова', 'Anna Belova', 'Аквааэробика', 4,
             'https://images.unsplash.com/photo-1520880867055-1e30d1cb001c?w=200',
             'Инструктор по плаванию и водным видам фитнеса.'),
            ('Иван Громов', 'Ivan Gromov', 'Кроссфит, Бокс', 7,
             'https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=200',
             'Кроссфит-тренер уровня CF-L2.'),
            ('Екатерина Зайцева', 'Ekaterina Zaitseva', 'Йога', 9,
             'https://images.unsplash.com/photo-1545912452-8aea7e25a3d3?w=200',
             'Преподаватель хатха-йоги и медитации.'),
            ('Павел Морозов', 'Pavel Morozov', 'Силовые тренировки', 15,
             'https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?w=200',
             'Пауэрлифтер, призёр чемпионата страны.'),
            ('Наталья Власова', 'Natalia Vlasova', 'Зумба, Стретчинг', 3,
             'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=200',
             'Энергичный тренер по танцевальному фитнесу.'),
        ]
        trainers = []
        for full_name, full_name_en, spec, exp, photo, bio in trainers_data:
            t = Trainer.objects.create(
                full_name=full_name, full_name_en=full_name_en,
                specialization=spec, experience_years=exp,
                photo_url=photo, bio=bio, is_active=True,
                hired_at=date.today() - timedelta(days=exp * 365)
            )
            trainers.append(t)

        self.stdout.write('Создаю расписание...')
        today = date.today()
        schedule_slots = [
            (0, services[0], trainers[0], time(8, 0), time(9, 0), 'Зал 1'),
            (0, services[5], trainers[1], time(10, 0), time(11, 0), 'Зал 2'),
            (0, services[2], trainers[2], time(18, 0), time(19, 0), 'Зал 3'),
            (1, services[1], trainers[0], time(9, 0), time(10, 0), 'Зал 1'),
            (1, services[3], trainers[3], time(19, 0), time(20, 0), 'Зал 4'),
            (2, services[9], trainers[4], time(7, 30), time(9, 0), 'Зал 5'),
            (2, services[7], trainers[4], time(17, 0), time(18, 0), 'Зал 5'),
            (3, services[0], trainers[7], time(8, 0), time(9, 0), 'Зал 1'),
            (3, services[4], trainers[5], time(11, 0), time(12, 0), 'Бассейн'),
            (4, services[8], trainers[2], time(18, 30), time(20, 0), 'Зал 3'),
            (5, services[1], trainers[7], time(10, 0), time(11, 0), 'Зал 1'),
            (5, services[6], trainers[9], time(12, 0), time(13, 0), 'Зал 2'),
            (6, services[3], trainers[6], time(9, 0), time(10, 30), 'Зал 4'),
            (7, services[10], trainers[3], time(7, 0), time(8, 0), 'Зал 6'),
            (7, services[5], trainers[1], time(20, 0), time(21, 0), 'Зал 2'),
        ]
        for day_offset, svc, trainer, start, end, hall in schedule_slots:
            Schedule.objects.create(
                service=svc, trainer=trainer,
                class_date=today + timedelta(days=day_offset),
                start_time=start, end_time=end, hall=hall, capacity=20
            )

        self.stdout.write('Создаю акции...')
        promotions_data = [
            ('Летний старт', 25, today - timedelta(days=5), today + timedelta(days=25)),
            ('Приведи друга', 15, today - timedelta(days=10), today + timedelta(days=20)),
            ('Первый месяц', 30, today, today + timedelta(days=30)),
            ('Утренний бонус', 20, today - timedelta(days=2), today + timedelta(days=28)),
            ('Студентам', 35, today - timedelta(days=1), today + timedelta(days=14)),
            ('VIP-скидка', 10, today, today + timedelta(days=60)),
            ('День рождения клуба', 50, today, today + timedelta(days=3)),
            ('Семейная цена', 20, today - timedelta(days=7), today + timedelta(days=23)),
            ('Осенний абонемент', 15, today, today + timedelta(days=45)),
            ('Чёрная пятница', 40, today, today + timedelta(days=1)),
        ]
        promotions = []
        for title, discount, start, end in promotions_data:
            p = Promotion.objects.create(
                title=title, discount_percent=discount,
                start_date=start, end_date=end, is_active=True,
                description=f'Скидка {discount}% на абонементы'
            )
            promotions.append(p)

        PromotionMembership.objects.create(promotion=promotions[0], membership=memberships[0])
        PromotionMembership.objects.create(promotion=promotions[0], membership=memberships[1])
        PromotionMembership.objects.create(promotion=promotions[4], membership=memberships[2])
        PromotionMembership.objects.create(promotion=promotions[2], membership=memberships[4])

        self.stdout.write('Создаю администратора тренажерки...')
        if not User.objects.filter(email='manager@fitclub.ru').exists():
            User.objects.create_user(
                email='manager@fitclub.ru',
                full_name='Менеджер Клуба',
                password='manager1234',
                phone='+77001112233',
                role='gym_admin',
                is_staff=True,
            )

        self.stdout.write('Создаю пользователей и заказы...')
        users_data = [
            ('Иван Иванов', 'ivan@example.com', '79001234567'),
            ('Мария Сидорова', 'maria@example.com', '79009876543'),
            ('Пётр Краснов', 'petr@example.com', '79005551234'),
            ('Светлана Миронова', 'sveta@example.com', '79003334455'),
            ('Андрей Кузнецов', 'andrey@example.com', '79007778899'),
            ('Елена Новикова', 'elena@example.com', '79002223344'),
            ('Артём Волков', 'artem@example.com', '79004445566'),
            ('Юлия Смирнова', 'yulia@example.com', '79006667788'),
            ('Николай Попов', 'nikolay@example.com', '79008889900'),
            ('Татьяна Орлова', 'tatyana@example.com', '79001112233'),
        ]
        users = []
        for full_name, email, phone in users_data:
            u = User.objects.create_user(
                email=email, full_name=full_name, password='test1234',
                phone=phone, role='client'
            )
            users.append(u)

        for i, user in enumerate(users[:5]):
            m = memberships[i % len(memberships)]
            order = Order.objects.create(
                user=user, total_amount=m.price,
                payment_method='card', status='paid'
            )
            OrderItem.objects.create(order=order, membership=m, price_paid=m.price)
            UserMembership.objects.create(
                user=user, membership=m,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=m.duration_days),
                status='active'
            )

        self.stdout.write(self.style.SUCCESS('БД успешно заполнена!'))
        self.stdout.write(f'  Услуги: {Service.objects.count()}')
        self.stdout.write(f'  Абонементы: {Membership.objects.count()}')
        self.stdout.write(f'  Тренеры: {Trainer.objects.count()}')
        self.stdout.write(f'  Расписание: {Schedule.objects.count()}')
        self.stdout.write(f'  Акции: {Promotion.objects.count()}')
        self.stdout.write(f'  Пользователи: {User.objects.count()}')
