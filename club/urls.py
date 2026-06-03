from django.urls import path
from . import views
from . import api_views
from . import auth_api
from . import admin_api

urlpatterns = [
    # Главная
    path('', views.home, name='home'),

    # Авторизация
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),

    # Абонементы
    path('memberships/', views.membership_list, name='membership_list'),
    path('memberships/<int:pk>/', views.membership_detail, name='membership_detail'),
    path('memberships/<int:pk>/buy/', views.buy_membership, name='buy_membership'),
    path('memberships/create/', views.membership_create, name='membership_create'),
    path('memberships/<int:pk>/edit/', views.membership_edit, name='membership_edit'),
    path('memberships/<int:pk>/delete/', views.membership_delete, name='membership_delete'),

    # Тренеры
    path('trainers/', views.trainer_list, name='trainer_list'),
    path('trainers/create/', views.trainer_create, name='trainer_create'),
    path('trainers/<int:pk>/edit/', views.trainer_edit, name='trainer_edit'),
    path('trainers/<int:pk>/delete/', views.trainer_delete, name='trainer_delete'),

    # Акции
    path('promotions/', views.promotion_list, name='promotion_list'),
    path('promotions/create/', views.promotion_create, name='promotion_create'),
    path('promotions/<int:pk>/edit/', views.promotion_edit, name='promotion_edit'),
    path('promotions/<int:pk>/delete/', views.promotion_delete, name='promotion_delete'),

    # Аналитика
    path('analytics/', views.analytics, name='analytics'),

    # API для React
    path('api/trainers/<int:pk>/', api_views.trainer_detail_api, name='api_trainer_detail'),
    path('api/memberships/', api_views.memberships_api, name='api_memberships'),
    path('api/trainers/', api_views.trainers_api, name='api_trainers'),
    path('api/schedule/', api_views.schedule_api, name='api_schedule'),
    path('api/promotions/', api_views.promotions_api, name='api_promotions'),
    path('api/services/', api_views.services_api, name='api_services'),
    path('api/favorites/toggle/', api_views.toggle_favorite_api, name='api_toggle_favorite'),

    # Auth API
    path('api/auth/login/', auth_api.api_login, name='api_login'),
    path('api/auth/register/', auth_api.api_register, name='api_register'),
    path('api/auth/logout/', auth_api.api_logout, name='api_logout'),
    path('api/auth/me/', auth_api.api_me, name='api_me'),
    path('api/auth/profile/', auth_api.api_profile_data, name='api_profile_data'),
    path('api/auth/profile/update/', auth_api.api_profile_update, name='api_profile_update'),
    path('api/memberships/<int:pk>/buy/', auth_api.api_buy_membership, name='api_buy_membership'),
    path('api/memberships/<int:pk>/switch/', auth_api.api_switch_membership, name='api_switch_membership'),
    path('api/auth/trainer/set/', auth_api.api_set_trainer, name='api_set_trainer'),

    # Admin CRUD API
    path('api/admin/dashboard/', admin_api.admin_dashboard),
    path('api/admin/memberships/', admin_api.admin_memberships_list),
    path('api/admin/memberships/create/', admin_api.admin_membership_create),
    path('api/admin/memberships/<int:pk>/update/', admin_api.admin_membership_update),
    path('api/admin/memberships/<int:pk>/delete/', admin_api.admin_membership_delete),
    path('api/admin/trainers/', admin_api.admin_trainers_list),
    path('api/admin/trainers/create/', admin_api.admin_trainer_create),
    path('api/admin/trainers/<int:pk>/update/', admin_api.admin_trainer_update),
    path('api/admin/trainers/<int:pk>/delete/', admin_api.admin_trainer_delete),
    path('api/admin/services/', admin_api.admin_services_list),
    path('api/admin/services/create/', admin_api.admin_service_create),
    path('api/admin/services/<int:pk>/update/', admin_api.admin_service_update),
    path('api/admin/services/<int:pk>/delete/', admin_api.admin_service_delete),
    path('api/admin/promotions/', admin_api.admin_promotions_list),
    path('api/admin/promotions/create/', admin_api.admin_promotion_create),
    path('api/admin/promotions/<int:pk>/update/', admin_api.admin_promotion_update),
    path('api/admin/promotions/<int:pk>/delete/', admin_api.admin_promotion_delete),
    path('api/admin/schedule/', admin_api.admin_schedule_list),
    path('api/admin/schedule/create/', admin_api.admin_schedule_create),
    path('api/admin/schedule/<int:pk>/update/', admin_api.admin_schedule_update),
    path('api/admin/schedule/<int:pk>/delete/', admin_api.admin_schedule_delete),
    path('api/admin/users/', admin_api.admin_users_list),
    path('api/admin/users/<int:pk>/role/', admin_api.admin_user_update_role),
    path('api/admin/analytics/', admin_api.admin_analytics),
]