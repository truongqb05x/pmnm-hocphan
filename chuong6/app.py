from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):         
    pass

db = SQLAlchemy(model_class=Base)     

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-chi-dung-khi-phat-trien"
app.config["SQLALCHEMY_DATABASE_URI"] = \
    "sqlite:///qlsv.db"              
db.init_app(app) 
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class Student(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    mssv: Mapped[str] = mapped_column(String(10), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    gpa: Mapped[float] = mapped_column(default=0.0)

    def __repr__(self):
        return f"<Student {self.mssv} {self.name}>"
with app.app_context():
    db.create_all()


from sqlalchemy import func


@app.get("/them-mau")
def add_sample():
    total = db.session.scalar(
        db.select(func.count(Student.id)))
    if total > 0:
        return f"Đã có {total} sinh viên, không thêm nữa."
    an = Student(mssv="23T1020001",
                 name="Nguyễn Văn An", gpa=8.5)
    before = an.id         # chưa ghi xuống CSDL
    db.session.add(an)     # đưa vào "giỏ" chờ ghi
    db.session.add_all([
        Student(mssv="23T1020002", name="Trần Thị Bình", gpa=6.8),
        Student(mssv="23T1020003", name="Lê Hoàng Cường", gpa=9.1),
        Student(mssv="23T1020004", name="Phạm Minh Dũng", gpa=4.5),
        Student(mssv="23T1020005", name="Hoàng Thu Hà", gpa=7.4),
    ])
    db.session.commit()    # ghi thật sự
    return (f"Đã thêm 5 sinh viên. id của An: "
            f"trước commit = {before}, "
            f"sau commit = {an.id}")


if __name__ == "__main__":
    app.run(debug=True)

