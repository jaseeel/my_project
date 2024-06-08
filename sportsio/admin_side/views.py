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
from django.db.models import DateField
import io
from django.db.models import Count, Sum, F
from products.models import Products
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import A4, inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.views.decorators.http import require_http_methods
from datetime import date, datetime
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
 
def admin_login(request):
    if 'email' in request.session:
        return redirect('dashboard')
    else:
        if request.method=='POST':
            email=request.POST.get('email')
            password=request.POST.get('password')

            if CustomUser.objects.filter(email=email).exists():
                user_obj=CustomUser.objects.get(email=email,is_superuser=True)
                if user_obj.check_password(password):
                    request.session['email']=email
                    login(request,user_obj)
                    return redirect('dashboard')
                else:
                    messages.error("wrong credentials")
            else:
                messages.error("User not Found")   

        return render(request,'admin_side/admin_login.html')

#-------------------------------------------------------------Dashboard view
def dashboard(request):
    if "email" in request.session:
        order_count = 0
        total_amount = 0
        filtered_customers = 0
        recent_orders = None
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
            Order.objects.filter(paid=True or status == "Delivered")
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(total_revenue=Sum("total_price"))
        )
        filtered_orders = None
        # Yearly Revenue
        yearly_revenue = (
            Order.objects.filter(paid=True or status == "Delivered")
            .annotate(year=TruncYear("created_at"))
            .values("year")
            .annotate(total_revenue=Sum("total_price"))
        )

        orders = Order.objects.order_by("-id")
        labels = []
        data = []

        for order in orders:
               labels.append(str(order.id))
               data.append(float(order.total_price))

        total_customers = CustomUser.objects.count()

        one_week_ago = timezone.now() - timezone.timedelta(weeks=1)

        new_users_last_week = CustomUser.objects.filter(
            date_joined__gte=one_week_ago
            ).count()
        total_orders = OrderItem.objects.count()
        total_offer_price_amount = Order.objects.aggregate(
                total_offer_price_amount=Sum("total_price")
            )

        total_amount_received = total_offer_price_amount.get("total_price", 0)
        total_amount_received //= 1000
        order_details_last_week = Order.objects.filter(
            paid=True, created_at__gte=one_week_ago
        )

        order_details_last_week = order_details_last_week.count()
        # Calculate the total offer price for order details from last week
        # total_amount_received_last_week_details = order_details_last_week.aggregate(total_offer_price_amount=Sum('total_price'))
        # total_amount_received_last_week = total_amount_received_last_week_details['total_price'] or 0  # Handle None case
        # total_amount_received_last_week //= 1000
        main_categories = category.objects.annotate(num_product_variants=Count("name"))

        category_labels = [category.name for category in main_categories]
        
        category_data = [category.num_product_variants for category in main_categories]
        total_products = Products.objects.count()
        time_interval = request.GET.get(
            "time_interval", "all"
        )  # Default to "all" if we're not provided anything
        if time_interval == "yearly":
                orders = Order.objects.annotate(
                    date_truncated=TruncYear("created_at", output_field=DateField())
                )
                orders = orders.values("date_truncated").annotate(
                    total_amount=Sum("total_price")
                )
        elif time_interval == "monthly":
            orders = Order.objects.annotate(
                date_truncated=TruncMonth("created_at", output_field=DateField())
            )
            orders = orders.values("date_truncated").annotate(
                total_amount=Sum("offer_price")
            )
            monthly_sales = (
                Order.objects.filter(paid=True)  # Add your filter condition here
                .annotate(month=TruncMonth("created_at"))
                .values("month")
                .annotate(total_amount=Sum("total_price"))
                .order_by("month")
            )
            monthly_labels = [entry["month"].strftime("%B %Y") for entry in monthly_sales]
            monthly_data = [float(entry["total_amount"]) for entry in monthly_sales]
            monthly_data = [float(entry["total_amount"]) for entry in monthly_sales]

            headers = HttpHeaders(request.headers)
            is_ajax_request = headers.get("X-Requested-With") == "XMLHttpRequest"

            if is_ajax_request and request.method == "GET":
                time_interval = request.GET.get("time_interval", "all")
                filtered_labels = []
                filtered_data = []

                if time_interval == "yearly":
                    filtered_orders = Order.objects.annotate(
                        date_truncated=TruncYear("created_at", output_field=DateField())
                    )
                elif time_interval == "monthly":
                    filtered_orders = Order.objects.annotate(
                        date_truncated=TruncMonth("created_at", output_field=DateField())
                    )
                else:
                    filtered_orders = Order.objects.annotate(date_truncated=F("created_at"))

                filtered_orders = filtered_orders.values("date_truncated")

                filtered_orders = (
                    filtered_orders.values("date_truncated")
                    .annotate(total_amount=Sum("offer_price"))
                    .order_by("date_truncated")
                )
                filtered_labels = [
                    entry["date_truncated"].strftime("%B %Y") for entry in filtered_orders
                ]
                filtered_data = [float(entry["total_amount"]) for entry in filtered_orders]
                return JsonResponse({"labels": filtered_labels, "data": filtered_data})
        
            context = {
                "top_products": top_products,
                "monthly_revenue": monthly_revenue,
                "yearly_revenue": yearly_revenue,
                "top_products": top_products,
                "labels": json.dumps(labels),
                "data": json.dumps(data),
                "total_customers": total_customers,
                "new_users_last_week": new_users_last_week,
                "total_orders": total_orders,
                "total_amount_received": total_amount_received,
                "total_products": total_products,
                "category_labels": json.dumps(category_labels),
                "category_data": json.dumps(category_data),
                "monthly_labels": json.dumps(monthly_labels),
                "monthly_data": json.dumps(monthly_data),
                "top_categories": top_categories,
                "top_brands": top_brands,
            }

            if request.method == "GET":
                # Get the start and end dates from the request GET parameters
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

                    if (
                        total_amount_received is not None
                        and total_amount_received["total_price_sum"] is not None
                    ):
                        total_amount = (
                            total_amount_received["total_price_sum"] // 1000
                        )  # Assuming you're dealing with currency values
                    else:
                        total_amount = 0

                    data = [float(order.total_price) for order in filtered_orders]
                    labels = [str(order.id) for order in filtered_orders]

                    recent_orders = Order.objects.order_by("-id")[:5]
                # Update the context with filtered data
                context.update(
                    {
                        "total_orders": order_count,
                        "total_amount_received": total_amount,
                        "total_customers": total_customers,
                        "labels": json.dumps(labels),
                        "data": json.dumps(data),
                        "recent_orders": recent_orders,
                    }
                )

    return render(request,'admin_side/index.html')      

#-------------------------------------------------------------User management

def User_management(request):
    if 'email' in request.session:

        user = CustomUser.objects.filter(is_superuser=False)
        context={
            'user':user,
        } 
        return render(request,'admin_side/user_management.html',context )
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
def report_generator(request, orders):
    from_date_str = request.POST.get("from_date")
    to_date_str = request.POST.get("to_date")

    from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
    to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()

    if from_date > date.today() or to_date > date.today():
        # Return an error response or show a message
        return HttpResponse("Please enter a valid date.")

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18
    )
    story = []

    data = [["Order ID", "Total Quantity", "Product IDs", "Product Names", "Amount"]]

    total_sales_amount = 0  # Initialize total sales amount sum

    for order in orders:
        order_items = OrderItem.objects.filter(order=order)
        total_quantity = sum(item.quantity for item in order_items)
        product_ids = ", ".join(str(item.product.id) for item in order_items)
        product_names = ", ".join(
            f"{item.product.brand.brand_name} {item.product.title}"
            for item in order_items
        )
        order_amount = sum(item.price for item in order_items)

        total_sales_amount += order_amount  # Accumulate total sales amount

        data.append(
            [order.id, total_quantity, product_ids, product_names[:15], order_amount]
        )

    # Add a row for the total sales amount at the end of the table
    data.append(["Total Sales", "", "", "", total_sales_amount])

    # Create a table with the data
    table = Table(data, colWidths=[1 * inch, 1.5 * inch, 2 * inch, 3 * inch, 1 * inch])

    # Style the table
    table_style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 14),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -2), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, -1), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]
    )
    table.setStyle(table_style)

    # Add the table to the story and build the document
    story.append(table)
    doc.build(story)

    buf.seek(0)
    return FileResponse(buf, content_type="application/pdf")


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
