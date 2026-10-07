from flask import Flask, request, jsonify, redirect, url_for, abort, make_response
from markupsafe import escape
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

STUDENTS = {
    "23T1020001": {"name": "Nguyễn Văn An", "lop": "K47A", "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.0}},
    "23T1020002": {"name": "Trần Thị Bình", "lop": "K47A", "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0}},
    "23T1020003": {"name": "Lê Hoàng Cường", "lop": "K47B", "scores": {"PMMNM": 9.5, "CSDL": 9.0}},
    "23T1020004": {"name": "Phạm Minh Dũng", "lop": "K47B", "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0}},
    "23T1020005": {"name": "Hoàng Thu Hà", "lop": "K47A", "scores": {}},
    "23T1020006": {"name": "Võ Quốc Khánh", "lop": "K47C", "scores": {"PMMNM": 7.5, "MMT": 8.0}},
}

def average(scores):
    if not scores:
        return None
    return round(sum(scores.values()) / len(scores), 2)

def rank(avg):
    if avg is None:
        return "Chưa có điểm"
    if avg >= 8.5: return "Giỏi"
    if avg >= 7.0: return "Khá"
    if avg >= 5.0: return "Trung bình"
    return "Yếu"

def student_summary(mssv):
    if mssv not in STUDENTS:
        return None
    student = STUDENTS[mssv]
    avg = average(student["scores"])
    return {
        "mssv": mssv,
        "name": student["name"],
        "lop": student["lop"],
        "scores": student["scores"],
        "average": avg,
        "rank": rank(avg)
    }

def layout(title, body):
    safe_title = escape(title)
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{safe_title} - Sổ điểm</title>
</head>
<body>
    <nav>
        <a href="{url_for('index')}">Trang chủ</a> &middot;
        <a href="{url_for('student_list')}">Sinh viên</a> &middot;
        <a href="{url_for('search_page')}">Tìm kiếm</a>
    </nav>
    <hr>
    {body}
</body>
</html>"""
    return html

@app.route("/")
def index():
    num_students = len(STUDENTS)
    lops = set(s["lop"] for s in STUDENTS.values())
    num_lops = len(lops)
    body = f"""
    <h1>Tổng quan</h1>
    <p>Tổng số sinh viên: {num_students}</p>
    <p>Tổng số lớp: {num_lops}</p>
    <ul>
        <li><a href="{url_for('student_list')}">Danh sách sinh viên</a></li>
        <li><a href="{url_for('api_students')}">API Danh sách sinh viên</a></li>
    </ul>
    """
    return layout("Tổng quan", body)

@app.route("/students")
def student_list():
    lop_filter = request.args.get("lop", "").strip().upper()
    
    filtered_students = []
    for mssv in STUDENTS:
        s_sum = student_summary(mssv)
        if lop_filter:
            if s_sum["lop"].upper() == lop_filter:
                filtered_students.append(s_sum)
        else:
            filtered_students.append(s_sum)
            
    all_lops = sorted(list(set(s["lop"] for s in STUDENTS.values())))
    
    filter_html = f'<a href="{url_for("student_list")}">Tất cả</a>'
    for l in all_lops:
        filter_html += f' | <a href="{url_for("student_list", lop=l)}">{escape(l)}</a>'
        
    body = f"<h1>Danh sách sinh viên</h1><p>Lọc: {filter_html}</p>"
    
    if not filtered_students:
        body += "<p>Không có sinh viên phù hợp.</p>"
    else:
        body += "<table border='1'><tr><th>MSSV</th><th>Họ tên</th><th>Lớp</th><th>Điểm TB</th><th>Xếp loại</th></tr>"
        for s in filtered_students:
            avg_str = "-" if s["average"] is None else str(s["average"])
            body += f"""<tr>
                <td><a href="{url_for('student_detail', mssv=s['mssv'])}">{escape(s['mssv'])}</a></td>
                <td>{escape(s['name'])}</td>
                <td>{escape(s['lop'])}</td>
                <td>{avg_str}</td>
                <td>{escape(s['rank'])}</td>
            </tr>"""
        body += "</table>"
        
    return layout("Danh sách", body)

@app.route("/students/<mssv>")
def student_detail(mssv):
    s = student_summary(mssv)
    if not s:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
        
    avg_str = "-" if s["average"] is None else str(s["average"])
    body = f"""<h1>Chi tiết sinh viên</h1>
    <p><strong>MSSV:</strong> {escape(s['mssv'])}</p>
    <p><strong>Họ tên:</strong> {escape(s['name'])}</p>
    <p><strong>Lớp:</strong> <a href="{url_for('student_list', lop=s['lop'])}">{escape(s['lop'])}</a></p>
    <p><strong>Điểm TB:</strong> {avg_str}</p>
    <p><strong>Xếp loại:</strong> {escape(s['rank'])}</p>
    """
    
    if s["scores"]:
        body += "<h2>Bảng điểm</h2><table border='1'><tr><th>Học phần</th><th>Điểm</th></tr>"
        for hp, diem in s["scores"].items():
            body += f"<tr><td>{escape(hp)}</td><td>{diem}</td></tr>"
        body += "</table>"
    
    short_link = url_for('short_link', mssv=mssv)
    body += f'<p><a href="{url_for("export_csv", mssv=mssv)}">Tải bảng điểm (CSV)</a></p>'
    body += f'<p>Link rút gọn: <a href="{short_link}">{short_link}</a></p>'
    
    return layout(f"Chi tiết {mssv}", body)

@app.route("/sv/<mssv>")
def short_link(mssv):
    return redirect(url_for('student_detail', mssv=mssv), code=301)

@app.route("/students/<mssv>/export")
def export_csv(mssv):
    s = student_summary(mssv)
    if not s:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
    
    csv_content = "hoc_phan,diem\n"
    for hp, diem in s["scores"].items():
        csv_content += f"{hp},{diem}\n"
        
    response = make_response(csv_content)
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=diem_{mssv}.csv"
    return response

@app.route("/search")
def search_page():
    q = request.args.get("q", "")
    safe_q = escape(q)
    
    body = f"""<h1>Tìm kiếm</h1>
    <form method="GET" action="{url_for('search_page')}">
        <input type="text" name="q" value="{safe_q}">
        <button type="submit">Tìm</button>
    </form>
    """
    
    if q:
        q_lower = q.lower()
        results = []
        for mssv, info in STUDENTS.items():
            if q_lower in mssv.lower() or q_lower in info["name"].lower():
                results.append(student_summary(mssv))
                
        body += f'<p>Tìm thấy {len(results)} kết quả cho "{safe_q}"</p>'
        if results:
            body += "<ul>"
            for s in results:
                body += f'<li><a href="{url_for("student_detail", mssv=s["mssv"])}">{escape(s["mssv"])} - {escape(s["name"])}</a></li>'
            body += "</ul>"
            
    return layout("Tìm kiếm", body)

@app.route("/api/students")
def api_students():
    lop_filter = request.args.get("lop")
    min_avg_str = request.args.get("min_avg")
    
    min_avg = None
    if min_avg_str is not None:
        try:
            min_avg = float(min_avg_str)
        except ValueError:
            abort(400, description="min_avg sai kiểu")
            
    results = []
    for mssv in STUDENTS:
        s = student_summary(mssv)
        
        if lop_filter and s["lop"].upper() != lop_filter.upper():
            continue
            
        if min_avg_str is not None:
            if s["average"] is None or s["average"] < min_avg:
                continue
                
        results.append(s)
        
    return jsonify(results)

@app.route("/api/students/<mssv>")
def api_student_detail(mssv):
    s = student_summary(mssv)
    if not s:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
    return jsonify(s)

@app.route("/api/students/<mssv>/scores/<course>", methods=["GET", "PUT", "DELETE"])
def api_student_score(mssv, course):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
        
    course = course.upper()
    student = STUDENTS[mssv]
    
    if request.method == "GET":
        if course not in student["scores"]:
            abort(404, description=f"Chưa có điểm môn {course}.")
        return jsonify({
            "mssv": mssv,
            "course": course,
            "score": student["scores"][course]
        })
        
    elif request.method == "PUT":
        score_str = request.args.get("score")
        if score_str is None:
            abort(400, description="Thiếu tham số score.")
        try:
            score = float(score_str)
        except ValueError:
            abort(400, description="score sai kiểu.")
            
        if not (0 <= score <= 10):
            abort(400, description="score ngoài khoảng [0, 10].")
            
        is_new = course not in student["scores"]
        student["scores"][course] = score
        
        avg = average(student["scores"])
        
        resp = jsonify({"average": avg})
        resp.status_code = 201 if is_new else 200
        resp.headers["Location"] = url_for("api_student_score", mssv=mssv, course=course)
        return resp
        
    elif request.method == "DELETE":
        if course not in student["scores"]:
            abort(404, description=f"Chưa có điểm môn {course}.")
        del student["scores"][course]
        return "", 204

@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
def handle_error(error):
    if request.path.startswith("/api/"):
        return jsonify({
            "error": error.name,
            "detail": error.description
        }), error.code
    
    body = f"""<h1>Lỗi {error.code}: {error.name}</h1>
    <p>{error.description}</p>
    """
    return layout(f"Lỗi {error.code}", body), error.code

if __name__ == "__main__":
    app.run(debug=True, port=8000)
