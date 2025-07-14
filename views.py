from django.shortcuts import render, get_object_or_404, redirect
from .forms import QRCodeForm
from .models import Restaurant, Table, MenuItem, Order, OrderItem
import qrcode
import os
from django.conf import settings
from django.utils.text import slugify


def generate_qr_code(request):
    if request.method == 'POST':
        form = QRCodeForm(request.POST)
        if form.is_valid():
            res_name = form.cleaned_data['restaurant_name']
            menu_url = form.cleaned_data['url']

            restaurant, created = Restaurant.objects.get_or_create(
    name=res_name,
    defaults={'menu_url': menu_url, 'slug': slugify(res_name)}

)


            qr_urls = []

            for i in range(1, 5):
                table, _ = Table.objects.get_or_create(number=i, restaurant=restaurant)
                table_url = f"https://500df8b54f8a.ngrok-free.app/menu/{restaurant.slug}/table/{table.number}/"

                qr = qrcode.make(table_url)
                file_name = f"{restaurant.slug}_table_{table.number}.png"
                file_path = os.path.join(settings.MEDIA_ROOT, file_name)
                qr.save(file_path)

                qr_url = f"{settings.MEDIA_URL}{file_name}"
                qr_urls.append({'table': table.number, 'qr_url': qr_url})

            context = {
                'res_name': res_name,
                'qr_urls': qr_urls
            }
            return render(request, 'restaurant/qr_result.html', context)
    else:
        form = QRCodeForm()

    return render(request, 'restaurant/generate_qr_code.html', {'form': form})



def menu_view(request, restaurant_slug, table_number):
    restaurant = get_object_or_404(Restaurant, slug=restaurant_slug)
    table = get_object_or_404(Table, number=table_number, restaurant=restaurant)
    items = MenuItem.objects.filter(restaurant=restaurant)

    if request.method == 'POST':
        order = Order.objects.create(table=table)

        for item in items:
            qty_str = request.POST.get(f'item_{item.id}', '0')
            try:
                quantity = int(qty_str)
            except ValueError:
                quantity = 0

            if quantity > 0:
                OrderItem.objects.create(order=order, menu_item=item, quantity=quantity)

        return redirect('order_bill', order_id=order.id)

    return render(request, 'restaurant/menu.html', {
        'restaurant': restaurant,
        'table': table,
        'items': items
    })



def order_bill(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = OrderItem.objects.filter(order=order)
    total = sum(item.menu_item.price * item.quantity for item in items)

    
    if request.method == 'POST':
        order.is_completed = True
        order.save()
        message = "Order marked as completed!"
    else:
        message = ""

    return render(request, 'restaurant/bill.html', {
        'order': order,
        'items': items,
        'total': total,
        'message': message
    })

