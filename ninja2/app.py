from flask import Flask, render_template, request, abort
from datetime import datetime
import math

app = Flask(__name__)

# Thông tin quán
SHOP = {
    "name": "Cà phê Sông Hương",
    "address": "12 Lê Lợi, Huế",
    "phone": "0234 3888 999"
}

# Dữ liệu 7 món thực đơn theo đúng thứ tự phân trang bài 4
MENU = [
    {"id": 1, "name": "Cà phê đen", "price": 20000, "image": "ca-phe-den.jpg", "available": True},
    {"id": 2, "name": "Cà phê sữa", "price": 25000, "image": "ca-phe-sua.jpg", "available": True},
    {"id": 3, "name": "Bạc xỉu", "price": 30000, "image": "bac-xiu.jpg", "available": False},
    {"id": 4, "name": "Trà đào", "price": 35000, "image": "tra-dao.jpg", "available": True},
    {"id": 5, "name": "Trà sữa", "price": 35000, "image": "tra-sua.jpg", "available": True},
    {"id": 6, "name": "Nước cam", "price": 40000, "image": "nuoc-cam.jpg", "available": True},
    {"id": 7, "name": "Sinh tố bơ", "price": 45000, "image": "sinh-to-bo.jpg", "available": True},
]

PER_PAGE = 3

# Tự động truyền biến shop vào tất cả các template
@app.context_processor
def inject_shop():
    return dict(shop=SHOP)

# Custom filter định dạng VND: 25000 -> 25.000 đ
@app.template_filter("vnd")
def vnd_filter(value):
    try:
        val = int(round(float(value)))
        return f"{val:,}".replace(",", ".") + " đ"
    except (ValueError, TypeError):
        return f"{value} đ"

@app.route("/")
def index():
    if "gio" in request.args:
        gio = request.args.get("gio", type=int)
        if gio is None or not 0 <= gio <= 23:
            return "Giờ không hợp lệ!", 400
    else:
        gio = datetime.now().hour

    dang_mo = 6 <= gio < 22

    return render_template(
        "index.html",
        gio=gio,
        dang_mo=dang_mo
    )

@app.route("/menu")
def menu():
    # Hỗ trợ tham số ?empty=1 để kiểm tra trường hợp MENU = []
    items_all = [] if "empty" in request.args else MENU

    total_items = len(items_all)
    pages = max(1, math.ceil(total_items / PER_PAGE))

    # /menu?page=abc : Như trang 1
    page_param = request.args.get("page", 1)
    try:
        page = int(page_param)
    except (ValueError, TypeError):
        page = 1

    # /menu?page=4, /menu?page=0 : Báo lỗi 404
    if total_items > 0 and (page < 1 or page > pages):
        abort(404)

    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    items_on_page = items_all[start:end]

    return render_template(
        "menu.html",
        items=items_on_page,
        page=page,
        pages=pages,
        total_items=total_items,
    )

@app.route("/contact")
def contact():
    return render_template("contact.html")

# Xử lý trang lỗi 404 (kế thừa base.html)
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)
