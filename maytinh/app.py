from flask import Flask, render_template, request

app = Flask(__name__)


def parse_number(val_str):
    """Chuyển đổi chuỗi sang số thực, chấp nhận dấu phẩy thập phân."""
    if val_str is None or val_str.strip() == "":
        return None, "Vui lòng nhập một số."
    # Chấp nhận dấu phẩy thập phân (ví dụ: 2,5 -> 2.5)
    clean_val = val_str.strip().replace(",", ".")
    try:
        num = float(clean_val)
        return num, None
    except ValueError:
        return None, "Vui lòng nhập một số."


def format_num(val):
    """Định dạng số hiển thị: nếu là số nguyên thì bỏ phần .0, làm tròn tránh sai số thực."""
    val = round(val, 10)
    if val == 0:
        return "0"
    if val == int(val):
        return str(int(val))
    return str(val)


@app.route("/", methods=["GET", "POST"])
def index():
    a = ""
    b = ""
    op = "+"
    result = None
    errors = {}

    if request.method == "POST":
        a = request.form.get("a", "")
        b = request.form.get("b", "")
        op = request.form.get("op", "+")

        # 1. Kiểm tra số thứ nhất a
        num_a, err_a = parse_number(a)
        if err_a:
            errors["a"] = err_a

        # 2. Kiểm tra phép toán op
        valid_ops = ["+", "-", "*", "/"]
        if op not in valid_ops:
            errors["op"] = "Phép toán không hợp lệ."

        # 3. Kiểm tra số thứ hai b
        num_b, err_b = parse_number(b)
        if err_b:
            errors["b"] = err_b

        # 4. Kiểm tra phép chia cho 0
        if "b" not in errors and "op" not in errors and op == "/" and num_b == 0:
            errors["b"] = "Không thể chia cho 0."

        # 5. Nếu không có lỗi, thực hiện tính toán
        if not errors:
            if op == "+":
                res = num_a + num_b
            elif op == "-":
                res = num_a - num_b
            elif op == "*":
                res = num_a * num_b
            elif op == "/":
                res = num_a / num_b

            result = f"{format_num(num_a)} {op} {format_num(num_b)} = {format_num(res)}"

    return render_template(
        "index.html",
        a=a,
        b=b,
        op=op,
        result=result,
        errors=errors
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
