# Kết quả bài tập tổng hợp chương 3

## 1. Kết quả `flask --app sodiem routes`
```
Endpoint            Methods           Rule                                
------------------  ----------------  ------------------------------------
api_student_detail  GET               /api/students/<mssv>                
api_student_score   DELETE, GET, PUT  /api/students/<mssv>/scores/<course>
api_students        GET               /api/students                       
export_csv          GET               /students/<mssv>/export             
index               GET               /                                   
search_page         GET               /search                             
short_link          GET               /sv/<mssv>                          
static              GET               /static/<path:filename>             
student_detail      GET               /students/<mssv>                    
student_list        GET               /students                           
```

## 2. Kiểm thử bằng curl

1. `curl -i $B/sv/23T1020001`
   - Dòng trạng thái: `HTTP/1.1 301 MOVED PERMANENTLY`
   - Header quan trọng: `Location: /students/23T1020001`
   
2. `curl -i $B/students/23T1020001/export`
   - Dòng trạng thái: `HTTP/1.1 200 OK`
   - Header quan trọng: `Content-Disposition: attachment; filename=diem_23T1020001.csv`
   - Body: 
     ```
     hoc_phan,diem
     PMMNM,8.5
     CSDL,7.0
     MMT,9.0
     ```

3. `curl "$B/api/students?lop=k47a&min_avg=7"`
   - Dòng trạng thái: `HTTP/1.1 200 OK`
   - Body: `[{"average": 8.17, "lop": "K47A", "mssv": "23T1020001", "name": "Nguyễn Văn An", "rank": "Khá", "scores": {"CSDL": 7.0, "MMT": 9.0, "PMMNM": 8.5}}]`

4. `curl -i "$B/api/students?min_avg=abc"`
   - Dòng trạng thái: `HTTP/1.1 400 BAD REQUEST`
   - Body: `{"detail":"min_avg sai kiểu","error":"Bad Request"}`

5. `curl -i $B/api/students/999`
   - Dòng trạng thái: `HTTP/1.1 404 NOT FOUND`
   - Body: `{"detail":"Không có sinh viên với MSSV = 999.","error":"Not Found"}`

6. `curl -i -X PUT "$S/web?score=9"` (Giả sử S=$B/api/students/23T1020005/scores)
   - Dòng trạng thái: `HTTP/1.1 201 CREATED`
   - Header quan trọng: `Location: /api/students/23T1020005/scores/WEB`
   - Body: `{"average": 9.0}`

7. `curl -X PUT "$S/WEB?score=7.5"`
   - Dòng trạng thái: `HTTP/1.1 200 OK`
   - Body: `{"average": 7.5}`

8. `curl -i -X PUT "$S/WEB?score=11"`
   - Dòng trạng thái: `HTTP/1.1 400 BAD REQUEST`
   - Body: `{"detail":"score ngoài khoảng [0, 10].","error":"Bad Request"}`

9. `curl -i -X DELETE $S/WEB`
   - Dòng trạng thái: `HTTP/1.1 204 NO CONTENT`
   - Body: rỗng

10. `curl -i -X POST $S/WEB`
    - Dòng trạng thái: `HTTP/1.1 405 METHOD NOT ALLOWED`
    - Body: JSON thông báo lỗi (vì path bắt đầu bằng /api/).

11. `curl -i -X POST $B/students`
    - Dòng trạng thái: `HTTP/1.1 405 METHOD NOT ALLOWED`
    - Body: Trang HTML báo lỗi 405 (vì path không bắt đầu bằng /api/).

## 3. Trả lời ngắn

- **Vì sao Câu 4 dùng 301 còn Câu 8 trả 201 kèm Location?**
  - **Câu 4 (301):** Là mã trạng thái "Moved Permanently", dùng để chuyển hướng trình duyệt từ link rút gọn sang URL đích thực. Trình duyệt tự động request tới URL mới trong header `Location`.
  - **Câu 8 (201):** Là mã trạng thái "Created", báo hiệu một tài nguyên mới (điểm môn học mới) đã được tạo thành công trên server thông qua phương thức PUT. Header `Location` cung cấp URL của tài nguyên vừa được tạo, nhưng trình duyệt sẽ không tự động chuyển hướng đi đâu cả.

- **Thêm điểm cho 23T1020005 rồi khởi động lại server, điểm đó còn không? Vì sao?**
  - **Không còn**. Vì dữ liệu của ứng dụng (biến `STUDENTS`) đang được lưu trữ dưới dạng biến trên bộ nhớ RAM (memory). Khi tắt và khởi động lại server, tiến trình cũ bị hủy bỏ và biến `STUDENTS` sẽ được khởi tạo lại từ đầu theo giá trị mặc định được hardcode trong file mã nguồn.
