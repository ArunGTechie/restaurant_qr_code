from django.contrib import admin
from django.urls import path
from restaurant import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.generate_qr_code, name='generate_qr_code'),
    path('menu/<slug:restaurant_slug>/table/<int:table_number>/', views.menu_view, name='menu_view'),
    path('bill/<int:order_id>/', views.order_bill, name='order_bill'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
