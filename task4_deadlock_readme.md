# TASK 4 -- Deadlock Detection bằng BDD + ILP cho Petri Net

## 0. Cách sử dụng
    pip install pulp
------------------------------------------------------------------------

## 1. BDD Reachability: Liệt kê tất cả các marking có thể đạt được

### Mục đích

Dùng **Binary Decision Diagram (BDD)** để khám phá không gian trạng thái một cách symbolic, tránh bùng nổ trạng thái khi số place lớn.

### Quy trình

1.  **Load PNML**
    -   File PNML được đọc bằng `load_pnml`.
    -   Lấy danh sách place (`get_place_list`).
    -   Xây dựng thông tin transition: pre-places & post-places
        (`build_transition_info`).
2.  **Xác định marking ban đầu**
    -   Được lấy bằng `get_initial_marking_set`.
3.  **Symbolic reachability**
    -   Hàm `symbolic_reachability(net)` trả về:
        -   `Reach_bdd`: BDD biểu diễn tập marking có thể đạt.
        -   `count`: số trạng thái.
        -   `iters`: số vòng fixpoint.
        -   `stats`: các thống kê khác.
4.  **Convert từ BDD thành danh sách explicit markings**\
    BDD sử dụng biến `x_i` ứng với mỗi place.\
    Với mỗi assignment trong `Reach_bdd.satisfy_all()`:
    -   Tạo từ điển `{place_id: 0/1}`
    -   Sau đó chuyển thành `frozenset` chứa các place đang có token.

Ví dụ:

    Marking 2: {"p1": 1, "p3": 1, "p4": 0} → {p1, p3}

Kết quả cuối:

    Total reachable markings: N

------------------------------------------------------------------------

## 2. ILP Deadlock Checking: Xác định marking nào là deadlock

### Ý tưởng

Một marking là deadlock khi:

> **Không có transition nào khả thi (enabled)**.

Thay vì kiểm tra thủ công, đoạn mã sinh một **ILP model** mô phỏng điều kiện enable của từng transition và yêu cầu ILP solver chứng minh rằng toàn bộ transition đều disabled.

------------------------------------------------------------------------

## 3. ILP model -- Cách mã hóa điều kiện enable/disable

### Biến ILP

-   `x_p ∈ {0,1}`: token trên place `p`
-   `z_t ∈ {0,1}`: transition `t` có enabled hay không

Tất cả `x_p` đều **được fix** theo marking đang kiểm tra.

### Điều kiện enabling của mỗi transition

Với transition `t`:

-   `pre`: tập các input places
-   `post`: tập output places
-   `post_only = post - pre`

**Điều kiện để transition được enable:**

1.  Tất cả `pre-places` phải có token

        z_t ≤ x_p    (với mọi p ∈ pre)

2.  Các `post-only places` phải rỗng

        z_t ≤ 1 - x_p    (với mọi p ∈ post_only)

3.  Ràng buộc "nếu thỏa hết thì must enable" (điều kiện ép solver thực thi z_t = 1 nếu z_t ≤ 1):

        z_t ≥ (sum(x_p for pre) + sum(1-x_p for post_only)) - (k - 1)

    -   `k = |pre| + |post_only|`
    -   Nếu tất cả điều kiện thỏa → RHS = 1 → buộc `z_t = 1`.

4.  Nếu transition **không có pre-place** → luôn enable

        z_t = 1

### Điều kiện deadlock

Deadlock được mô hình hóa bằng constraint:

    sum(z_t over all transitions) = 0

Nếu ILP solver tìm được nghiệm ⇒ marking **là deadlock**.

ILP không có hàm mục tiêu: solver chỉ tìm nghiệm khả thi cho constraint (pulp ưu tiên return Optimal dù thực tế đang không tìm nghiệm tối ưu).

    pulp.LpStatus[status] in ["Optimal", "Feasible"]

------------------------------------------------------------------------

## 4. Chế độ Debug

Hàm `explain_transition_enable()` hiển thị lý do enable/disable của từng
transition:

Ví dụ:

    - pre-place p1 has token.
    - post-only place p3 empty.
    => Transition ENABLED

------------------------------------------------------------------------

## 5. Nhận diện Final Markings (không xem là deadlock)

Final places được xác định tự động:

    places không có arc ra → final place

Các marking chứa final place được xem là kết thúc tự nhiên, không phải
deadlock.

------------------------------------------------------------------------

## 6. Toàn bộ pipeline hoạt động trong `run_task4()`

Luồng xử lý:

1.  Load PNML
2.  In thông tin Place & Transition
3.  BDD reachability → tất cả reachable markings
4.  ILP checking cho từng feasible marking
5.  In danh sách deadlock
6.  Báo cáo thời gian chạy

Ví dụ output:

    ILP DEADLOCK DETECTION
    Checking marking ['p1', 'p3']:
    => ILP solver result: Optimal
    => DEADLOCK

------------------------------------------------------------------------

## 7. Kết quả trả về

Hàm `run_task4()` trả về:

    list of deadlock markings (danh sách các frozenset)

------------------------------------------------------------------------

(End of README content)