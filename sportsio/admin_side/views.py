import calendar
import datetime
from django.contrib import messages
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from admin_side.models import *
from django.contrib.auth import login,logout
from django.db.models.functions import TruncYear, TruncMonth, TruncDate
from django.http import FileResponse
import json
from django.http import HttpHeaders
from django.views.decorators.http import require_GET
from django.db.models import DateField
import io
from django.db.models import Count, Sum, F
from products.models import Products
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import A4, inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.views.decorators.http import require_http_methods
from datetime import date, datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from category.models import Brand, category
from products.models import Products
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.http import HttpResponse
from io import BytesIO
from userprofile.models import Order,OrderItem

#------------------------------------------------------------Admin Login
 
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CustomUser

def admin_login(request):
    if 'email' in request.session:
        return redirect('dashboard')
    else:
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')

            try:
                # Attempt to fetch the user object based on email
                user_obj = CustomUser.objects.get(email=email)

                # Check if the user is a superuser
                if not user_obj.is_superuser:
                    messages.error(request, "Only Admin can log in.")
                    return redirect('admin_login')

                # Verify the password
                if user_obj.check_password(password):
                    request.session['email'] = email
                    login(request, user_obj)
                    return redirect('dashboard')
                else:
                    messages.error(request, "Wrong credentials")
                    return redirect("admin_login")

            except CustomUser.DoesNotExist:
                messages.error(request, "User not found")
                return redirect('admin_login')

        return render(request, 'admin_side/admin_login.html')



#Dashboard_______________________________


@require_GET
def dashboard(request):
    if "email" not in request.session:
        return redirect("admin_login")

    # Check if it's an AJAX request for filtering sales
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return filter_sales(request)

    # Regular dashboard view logic
    top_products = Products.objects.annotate(
        total_orders=Count("orderitem__order")
    ).order_by("-total_orders")[:10]

    top_brands = Brand.objects.annotate(total_orders=Count("brand_name")).order_by(
        "-total_orders"
    )[:10]

    top_categories = category.objects.annotate(
        total_orders=Count("category_name")
    ).order_by("-total_orders")[:10]

    monthly_revenue = (
        Order.objects.filter(paid=True)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total_revenue=Sum("total_price"))
    )

    yearly_revenue = (
        Order.objects.filter(paid=True)
        .annotate(year=TruncYear("created_at"))
        .values("year")
        .annotate(total_revenue=Sum("total_price"))
    )

    orders = Order.objects.order_by("-id")
    labels = [str(order.id) for order in orders]
    data = [float(order.total_price) for order in orders]

    total_customers = CustomUser.objects.count()

    one_week_ago = timezone.now() - timezone.timedelta(weeks=1)

    new_users_last_week = CustomUser.objects.filter(
        date_joined__gte=one_week_ago
    ).count()
    total_order = OrderItem.objects.count()
    
    total_orders_delivered = Order.objects.filter(status="Delivered").count()

    total_offer_price_amount = Order.objects.aggregate(
        total_offer_price_amount=Sum("total_price")
    )

    total_amount = total_offer_price_amount.get("total_offer_price_amount", 0)
    total_amount //= 1000
    
    total_coupon_price = Order.objects.aggregate(
        total_coupon_price=Sum("discount_price")
    )
    total_coupon_price = total_coupon_price.get("total_coupon_price", 0)
    total_coupon_price //= 1000

    order_details_last_week = Order.objects.filter(
        paid=True, created_at__gte=one_week_ago
    ).count()

    main_categories = category.objects.annotate(num_product_variants=Count("name"))

    category_labels = [category.name for category in main_categories]
    category_data = [category.num_product_variants for category in main_categories]

    total_products = Products.objects.count()

    monthly_sales = (
        Order.objects.filter(paid=True)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total_amount=Sum("total_price"))
        .order_by("month")
    )
    monthly_labels = [entry["month"].strftime("%B %Y") for entry in monthly_sales]
    monthly_data = [float(entry["total_amount"]) for entry in monthly_sales]

    context = {
        "top_products": top_products,
        "monthly_revenue": monthly_revenue,
        "yearly_revenue": yearly_revenue,
        "labels": json.dumps(labels),
        "data": json.dumps(data),
        "total_amount": total_amount,
        "total_customers": total_customers,
        "new_users_last_week": new_users_last_week,
        "total_order": total_order,
        "total_products": total_products,
        "category_labels": json.dumps(category_labels),
        "category_data": json.dumps(category_data),
        "monthly_labels": json.dumps(monthly_labels),
        "monthly_data": json.dumps(monthly_data),
        "top_categories": top_categories,
        "top_brands": top_brands,
        "total_coupon_price": total_coupon_price,
        "total_orders_delivered": total_orders_delivered,
    }

    # Handle date range filtering
    from_date_str = request.GET.get("from_date")
    to_date_str = request.GET.get("to_date")

    if from_date_str and to_date_str:
        from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
        to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()

        filtered_orders = Order.objects.filter(
            created_at__date__range=[from_date, to_date]
        )
        filtered_customers = CustomUser.objects.filter(
            date_joined__date__range=[from_date, to_date]
        )
        if isinstance(filtered_customers, int):
            total_customers = filtered_customers
        else:
            total_customers = filtered_customers.count()

        order_count = filtered_orders.count()
        total_amount_received = filtered_orders.aggregate(
            total_price_sum=Sum("total_price")
        )
        total_amount = total_amount_received.get("total_price_sum", 0)

        if total_amount is not None:
            total_amount //= 1000  # Assuming you're dealing with currency values
        else:
            total_amount = 0

        data = [float(order.total_price) for order in filtered_orders]
        labels = [str(order.id) for order in filtered_orders]

        recent_orders = Order.objects.order_by("-id")[:5]

        context.update({
            "total_orders": order_count,
            "total_amount_received": total_amount,
            "total_customers": total_customers,
            "labels": json.dumps(labels),
            "data": json.dumps(data),
            "recent_orders": recent_orders,
        })

    return render(request, "admin_side/index.html", context)

def filter_sales(request):
    time_interval = request.GET.get("interval", "all")
    filtered_labels = []
    filtered_data = []

    if time_interval == "yearly":
        filtered_orders = Order.objects.filter(paid=True).annotate(
            date_truncated=TruncYear("created_at")
        )
    elif time_interval == "monthly":
        filtered_orders = Order.objects.filter(paid=True).annotate(
            date_truncated=TruncMonth("created_at")
        )
    else:  # 'all' or any other value
        filtered_orders = Order.objects.filter(paid=True).annotate(
            date_truncated=TruncDate("created_at")
        )

    filtered_orders = (
        filtered_orders.values("date_truncated")
        .annotate(total_amount=Sum("total_price"))
        .order_by("date_truncated")
    )
    
    for entry in filtered_orders:
        if time_interval == "yearly":
            filtered_labels.append(entry["date_truncated"].strftime("%Y"))
        elif time_interval == "monthly":
            filtered_labels.append(entry["date_truncated"].strftime("%B %Y"))
        else:
            filtered_labels.append(entry["date_truncated"].strftime("%Y-%m-%d"))
        filtered_data.append(float(entry["total_amount"]))

    return JsonResponse({"labels": filtered_labels, "data": filtered_data})

     

#-------------------------------------------------------------User management

from django.db.models import Q


def User_management(request):
    if 'email' in request.session:
        search_query = request.GET.get('search', '')

        # Initially, get all non-superuser users
        users = CustomUser.objects.filter(is_superuser=False)

        # If there's a search query, filter the users
        if search_query:
            users = users.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query)
            )

        context = {
            'users': users,
            'search_query': search_query,
        }
        return render(request, 'admin_side/user_management.html', context)
    else:
        return redirect('admin_login')
    


# -----------------------------------------Block-user

def block(request,user_id):
    user=CustomUser.objects.get(id=user_id)
    user.is_active=False
    user.save()
    return redirect('user_management')

#-------------------------------------------Unblock-user

def unblock(request,user_id):
    user=CustomUser.objects.get(id=user_id)
    user.is_active=True
    user.save()
    return redirect('user_management')

#---------------------------------Delete User

def delete_user(request,user_id):
    user=CustomUser.objects.get(id=user_id)
    user.delete()
    return redirect('user_management')

#-----------------------------------User View

def userviewdetails(request,user_id):
    if 'email' in request.session:
        user=CustomUser.objects.get(id=user_id)
        context={
        'user':user,
        }
        return render(request, 'admin_side/userviewdetails.html',context)
    
#----------------------------------------Admin logout    

def admin_logout(request):
    if 'email' in request.session:
        logout(request)
        request.session.flush()
    return redirect('admin_login')
    
    
    

# ----------------------------------------------------------------sales filtering based on month and year --------------------------------
def filter_sales(request):
    time_interval = request.GET.get("time_interval", "all")

    if time_interval == "yearly":
        # Filter data for yearly sales
        filtered_data = (
            Order.objects.annotate(date_truncated=TruncYear("created_at"))
            .values("date_truncated")
            .annotate(total_amount=Sum("amount"))
            .order_by("date_truncated")
        )

    elif time_interval == "monthly":
        # Filter data for monthly sales
        filtered_data = (
            Order.objects.annotate(date_truncated=TruncMonth("created_at"))
            .values("date_truncated")
            .annotate(total_amount=Sum("amount"))
            .order_by("date_truncated")
        )

    else:
        # Default to 'all' or handle other time intervals as needed
        # Here, we are using DateTrunc to truncate the date to a day
        filtered_data = (
            Order.objects.annotate(date_truncated=TruncDate("day", "date"))
            .values("date_truncated")
            .annotate(total_amount=Sum("amount"))
            .order_by("date_truncated")
        )

    # Extract data for the filtered chart
    filtered_labels = [
        entry["date_truncated"].strftime("%B %Y") for entry in filtered_data
    ]
    filtered_data = [float(entry["total_amount"]) for entry in filtered_data]

    return JsonResponse({"labels": filtered_labels, "data": filtered_data})


# ----------------------------------------------------------------pdf report generator docs specification----------------------------------------------------------------

import io
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4

from datetime import datetime, date
import openpyxl

def report_generator(request,orders):
    if request.method == 'POST':
        report_type = request.POST.get("report_type")
        format_choice = request.POST.get("format")

        if report_type == 'custom':
            from_date_str = request.POST.get("from_date")
            to_date_str = request.POST.get("to_date")
            from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
            to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
        elif report_type == 'monthly':
            month_str = request.POST.get("month")
            year, month = map(int, month_str.split('-'))
            from_date = date(year, month, 1)
            to_date = date(year, month, calendar.monthrange(year, month)[1])
        elif report_type == 'yearly':
            year = int(request.POST.get("year"))
            from_date = date(year, 1, 1)
            to_date = date(year, 12, 31)


        # Prepare data for the report
        orders = Order.objects.filter(created_at__range=(from_date, to_date))
        data = [["Order ID", "Total Quantity", "Product IDs", "Product Names", "Amount",  "Coupon"]]
        total_sales_amount = 0
        total_coupon_discount=0

        for order in orders:
            order_items = OrderItem.objects.filter(order=order)
            total_quantity = sum(item.quantity for item in order_items)
            product_ids = ", ".join(str(item.product.id) for item in order_items)
            product_names = ", ".join(f"{item.product.brand.brand_name} {item.product.title}" for item in order_items)
            order_amount = sum(item.price for item in order_items)

            discount_amount= order.discount_price

            total_sales_amount += order_amount
            if discount_amount:
                total_coupon_discount += discount_amount

            data.append([order.id, total_quantity, product_ids, product_names[:15], order_amount , discount_amount])

        # Add a row for the total sales amount at the end of the table
        data.append(["Total Sales", "", "", "", total_sales_amount])
        data.append(["Total Discount","","","","",total_coupon_discount])
        

        # Generate PDF report
        if format_choice == 'pdf':
            pdf_buf = io.BytesIO()
            doc = SimpleDocTemplate(pdf_buf, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=19)
            story = []
            table = Table(data, colWidths=[1 * inch, 1 * inch, 1 * inch, 3 * inch, 1 * inch, 1 * inch])
            
            # Apply the style to the table
            table_style = TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -2), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, -1), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ])
            table.setStyle(table_style)
            story.append(table)
            doc.build(story)
            pdf_buf.seek(0)
            return FileResponse(pdf_buf, content_type="application/pdf")

        # Generate Excel report
        elif format_choice == 'excel':
            excel_buf = io.BytesIO()
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Sales Report"

            for i, row in enumerate(data, start=1):
                for j, cell_value in enumerate(row, start=1):
                    ws.cell(row=i, column=j, value=cell_value)

            wb.save(excel_buf)
            excel_buf.seek(0)
            return FileResponse(excel_buf, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    current_year = datetime.now().year
    year_range = range(current_year - 4, current_year + 1)  # Last 5 years
    return render(request, 'your_template_name.html', {'year_range': year_range})# Replace 'your_template_name.html' with your actual template name




# ----------------------------------------------------------------pdf generator based on the dates----------------------------------------------------------------
def report_pdf_order(request):
    if request.method == "POST":
        from_date_str = request.POST.get("from_date")
        to_date_str = request.POST.get("to_date")

        try:
            from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
            to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
        except ValueError:
            return HttpResponse("Invalid date format.")

        orders = Order.objects.filter(
            created_at__date__range=[from_date, to_date]
        ).order_by("-id")
        return report_generator(request, orders)
