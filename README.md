# Hướng dẫn cài đặt và chạy chương trình

## 1. Cài môi trường

Sử dụng **Anaconda Prompt**, chạy lần lượt các lệnh sau:

```bash
conda create -n mhh_env python=3.11
conda activate mhh_env
conda install -c conda-forge pyeda
```
---

## 2. Chạy code

1. Mở **Anaconda Prompt**

4. Chạy các task:

   * **Task 1:**

     ```bash
     python .\src\parser_simple.py
     ```
   * **Task 2:**

     ```bash
     python .\src\dfs.py 
     ```
   * **Task 3:**

     ```bash
     python .\src\task3.py  
     ```
   * **Task 4:**

     ```bash
     python .\src\task4.py  
     ```
   * **Task 5:**

     ```bash
     python .\src\optimization.py  
     ```

---

## 3. Tạo testcase mới và test

* Cài **Tapaal** tại:
  [https://www.tapaal.net/download/](https://www.tapaal.net/download/)
* Lưu ý: Tapaal chỉ mở được file **.tapn**
* Nếu muốn mở file → chọn file `.tapn` trong thư mục **Tapaal**
* Nếu muốn vẽ mô hình → bây cứ vẽ rồi export ra **.pnml**
* Add file `.pnml` vào project.

---
# TASK 1 -- ĐỌC FILE PNML 
# TASK 2 -- TÍNH TOÁN CÁC MARKINGSMARKINGS CÓ THỂ CÓ
# TASK 3 -- SYMBOLIC REACHABILITY (BDD)
## Giải thích Task TEST 1 - WORKFLOW

### **Places** (5 places):
- `wait` (có token ban đầu - ●)
- `free` (có token ban đầu - ●)
- `work` (không có token)
- `done` (không có token)
- `docu` (không có token)

### **Transitions** (3 transitions):
- `start`: {wait, free} → {work}
- `change`: {work} → {done, docu}
- `end`: {docu} → {free}

### **Initial Marking**:
```
M0 = {wait: 1, free: 1}
```

---

## BƯỚC 1: SETUP

```python
place_list = ['docu', 'done', 'free', 'wait', 'work']  # sorted
place_map = {
    'docu': 0,
    'done': 1, 
    'free': 2,
    'wait': 3,
    'work': 4
} # Sắp xếp theo alphabet thôi
n_places = 5

trans_info = {
    'start': {
        'pre': {'wait', 'free'},
        'post': {'work'}
    },
    'change': {
        'pre': {'work'},
        'post': {'done', 'docu'}
    },
    'end': {
        'pre': {'docu'},
        'post': {'free'}
    }
}
```

---

## BƯỚC 2: KHAI BÁO BIẾN BDD

```python
X = [x[0], x[1], x[2], x[3], x[4]]  # Trạng thái hiện tại
Y = [y[0], y[1], y[2], y[3], y[4]]  # Trạng thái tiếp theo

# Mapping:
# x[0]/y[0] = docu
# x[1]/y[1] = done
# x[2]/y[2] = free
# x[3]/y[3] = wait
# x[4]/y[4] = work
```

---

## BƯỚC 3: MÃ HÓA TRẠNG THÁI BAN ĐẦU R0

Initial marking = {wait, free}

```python
r0_literals = [
    ~x[0],  # docu = 0
    ~x[1],  # done = 0
     x[2],  # free = 1  ✓
     x[3],  # wait = 1  ✓
    ~x[4]   # work = 0
]

R0 = ~x[0] ∧ ~x[1] ∧ x[2] ∧ x[3] ∧ ~x[4]
```

**Nghĩa**: Trạng thái ban đầu có token ở `free` và `wait`, không có ở các place khác.

---

## BƯỚC 4: MÃ HÓA TRANSITION RELATIONS

### **4.1. Transition "start": {wait, free} → {work}**

#### Enable Condition:
```python
pre_set = {'wait', 'free'}
post_set = {'work'}

# Pre-places phải có token
pre_conditions = [x[3], x[2]]  # wait=1, free=1

# Post-only places phải trống (work chưa có token)
post_only = {'work'} - {'wait', 'free'} = {'work'}
post_empty = [~x[4]]  # work=0

Pre_start = x[3] ∧ x[2] ∧ ~x[4]
```

#### Next State Logic:
```python
for i in [0,1,2,3,4]:
    pid = place_list[i]
    
    # i=0 (docu): không thuộc pre hay post → giữ nguyên
    y[0] ↔ x[0]
    
    # i=1 (done): không thuộc pre hay post → giữ nguyên
    y[1] ↔ x[1]
    
    # i=2 (free): thuộc pre, không thuộc post → mất token
    y[2] ↔ False  →  ~y[2]
    
    # i=3 (wait): thuộc pre, không thuộc post → mất token
    y[3] ↔ False  →  ~y[3]
    
    # i=4 (work): thuộc post → có token
    y[4] ↔ True  →  y[4]

Next_start = (y[0]↔x[0]) ∧ (y[1]↔x[1]) ∧ ~y[2] ∧ ~y[3] ∧ y[4]
```

#### Kết hợp:
```python
T_start = Pre_start ∧ Next_start
        = (x[3] ∧ x[2] ∧ ~x[4]) ∧ 
          ((y[0]↔x[0]) ∧ (y[1]↔x[1]) ∧ ~y[2] ∧ ~y[3] ∧ y[4])
```

**Ý nghĩa**: 
- Nếu có token ở `wait` và `free`, không có ở `work`
- Thì sau khi fire: mất token ở `wait`, `free`, được token ở `work`

---

### **4.2. Transition "change": {work} → {done, docu}**

#### Enable Condition:
```python
pre_set = {'work'}
post_set = {'done', 'docu'}

pre_conditions = [x[4]]  # work=1
post_only = {'done', 'docu'} - {'work'} = {'done', 'docu'}
post_empty = [~x[1], ~x[0]]  # done=0, docu=0

Pre_change = x[4] ∧ ~x[1] ∧ ~x[0]
```

#### Next State Logic:
```python
# i=0 (docu): thuộc post → có token
y[0] ↔ True  →  y[0]

# i=1 (done): thuộc post → có token  
y[1] ↔ True  →  y[1]

# i=2 (free): không thuộc pre hay post → giữ nguyên
y[2] ↔ x[2]

# i=3 (wait): không thuộc pre hay post → giữ nguyên
y[3] ↔ x[3]

# i=4 (work): thuộc pre, không thuộc post → mất token
y[4] ↔ False  →  ~y[4]

Next_change = y[0] ∧ y[1] ∧ (y[2]↔x[2]) ∧ (y[3]↔x[3]) ∧ ~y[4]
```

#### Kết hợp:
```python
T_change = Pre_change ∧ Next_change
         = (x[4] ∧ ~x[1] ∧ ~x[0]) ∧
           (y[0] ∧ y[1] ∧ (y[2]↔x[2]) ∧ (y[3]↔x[3]) ∧ ~y[4])
```

---

### **4.3. Transition "end": {docu} → {free}**

#### Enable Condition:
```python
pre_set = {'docu'}
post_set = {'free'}

pre_conditions = [x[0]]  # docu=1
post_only = {'free'} - {'docu'} = {'free'}
post_empty = [~x[2]]  # free=0

Pre_end = x[0] ∧ ~x[2]
```

#### Next State Logic:
```python
# i=0 (docu): thuộc pre, không thuộc post → mất token
y[0] ↔ False  →  ~y[0]

# i=1 (done): không thuộc pre hay post → giữ nguyên
y[1] ↔ x[1]

# i=2 (free): thuộc post → có token
y[2] ↔ True  →  y[2]

# i=3 (wait): không thuộc pre hay post → giữ nguyên
y[3] ↔ x[3]

# i=4 (work): không thuộc pre hay post → giữ nguyên
y[4] ↔ x[4]

Next_end = ~y[0] ∧ (y[1]↔x[1]) ∧ y[2] ∧ (y[3]↔x[3]) ∧ (y[4]↔x[4])
```

#### Kết hợp:
```python
T_end = Pre_end ∧ Next_end
      = (x[0] ∧ ~x[2]) ∧
        (~y[0] ∧ (y[1]↔x[1]) ∧ y[2] ∧ (y[3]↔x[3]) ∧ (y[4]↔x[4]))
```

---

### **4.4. Tổng hợp Transition Relation**

```python
T = T_start ∨ T_change ∨ T_end
```

**Ý nghĩa**: Từ trạng thái X, có thể chuyển sang Y nếu tồn tại ít nhất 1 transition có thể fire.

---

## BƯỚC 5: FIXED-POINT ITERATION

### **Iteration 1**:

```python
Reach = R0 = {(0,0,1,1,0)}  # {free, wait}

# Tìm các trạng thái mới
Img = Reach ∧ T
    = R0 ∧ (T_start ∨ T_change ∨ T_end)
```

**Kiểm tra từng transition**:
- `T_start`: R0 thỏa mãn Pre_start (có wait=1, free=1, work=0) ✓
  - Kết quả: Y = (0,0,0,0,1) = {work}
  
- `T_change`: R0 không thỏa mãn Pre_change (cần work=1) ✗

- `T_end`: R0 không thỏa mãn Pre_end (cần docu=1) ✗

```python
Img_Abstracted = Img.smoothing(X)  # Loại bỏ biến X, chỉ giữ Y
NewStates = Img_Abstracted.compose({y[i]: x[i]})  # Đổi Y→X

NewStates = {(0,0,0,0,1)}  # {work}

Reach = R0 ∪ NewStates 
      = {(0,0,1,1,0), (0,0,0,0,1)}
      = {{free,wait}, {work}}
```

---

### **Iteration 2**:

```python
OldReach = {{free,wait}, {work}}
```

**Kiểm tra với trạng thái {work} = (0,0,0,0,1)**:

- `T_start`: không thỏa mãn (cần wait, free) ✗

- `T_change`: thỏa mãn Pre_change (có work=1, done=0, docu=0) ✓
  - Kết quả: Y = (1,1,0,0,0) = {docu, done}

- `T_end`: không thỏa mãn (cần docu=1) ✗

```python
NewStates = {(1,1,0,0,0)}  # {docu, done}

Reach = OldReach ∪ NewStates
      = {{free,wait}, {work}, {docu,done}}
```

---

### **Iteration 3**:

**Kiểm tra với trạng thái {docu, done} = (1,1,0,0,0)**:

- `T_start`: không thỏa mãn ✗

- `T_change`: không thỏa mãn (cần work=1) ✗

- `T_end`: thỏa mãn Pre_end (có docu=1, free=0) ✓
  - Kết quả: Y = (0,1,1,0,0) = {done, free}

```python
NewStates = {(0,1,1,0,0)}  # {done, free}

Reach = OldReach ∪ NewStates
      = {{free,wait}, {work}, {docu,done}, {done,free}}
```

---

### **Iteration 4**:

**Kiểm tra với trạng thái {done, free} = (0,1,1,0,0)**:

- `T_start`: không thỏa mãn (cần wait=1) ✗
- `T_change`: không thỏa mãn ✗
- `T_end`: không thỏa mãn (cần docu=1) ✗

```python
NewStates = ∅  # Không có trạng thái mới

Reach == OldReach  → CONVERGED! ✓
```

---

## KẾT QUẢ CUỐI CÙNG

### **Reachable States (4 trạng thái)**:

```python
State 1: {free, wait}     = (0,0,1,1,0)  # Initial
State 2: {work}           = (0,0,0,0,1)  # After "start"
State 3: {docu, done}     = (1,1,0,0,0)  # After "change"
State 4: {done, free}     = (0,1,1,0,0)  # After "end"
```

### **Reachability Graph**:

```
{wait,free} --[start]--> {work} --[change]--> {docu,done} --[end]--> {done,free}
```
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
# TASK 5 -- Optimization over reachable markings using BDD + ILP
(End of README content)

=======

# Hướng dẫn cài đặt và chạy chương trình

## 1. Cài môi trường

Sử dụng **Anaconda Prompt**, chạy lần lượt các lệnh sau:

```bash
conda create -n mhh_env python=3.11
conda activate mhh_env
conda install -c conda-forge pyeda
```
---

## 2. Chạy code

1. Mở **Anaconda Prompt**

4. Chạy các task:

   * **Task 1:**

     ```bash
     python .\src\parser_simple.py
     ```
   * **Task 2:**

     ```bash
     python .\src\dfs.py 
     ```
   * **Task 3:**

     ```bash
     python .\src\task3.py  
     ```
   * **Task 4:**

     ```bash
     python .\src\task4.py  
     ```
   * **Task 5:**

     ```bash
     python .\src\optimization.py  
     ```

---

## 3. Tạo testcase mới và test

* Cài **Tapaal** tại:
  [https://www.tapaal.net/download/](https://www.tapaal.net/download/)
* Lưu ý: Tapaal chỉ mở được file **.tapn**
* Nếu muốn mở file → chọn file `.tapn` trong thư mục **Tapaal**
* Nếu muốn vẽ mô hình → bây cứ vẽ rồi export ra **.pnml**
* Add file `.pnml` vào project.

---
# TASK 1 -- ĐỌC FILE PNML 
# TASK 2 -- TÍNH TOÁN CÁC MARKINGSMARKINGS CÓ THỂ CÓ
# TASK 3 -- SYMBOLIC REACHABILITY (BDD)
## Giải thích Task TEST 1 - WORKFLOW

### **Places** (5 places):
- `wait` (có token ban đầu - ●)
- `free` (có token ban đầu - ●)
- `work` (không có token)
- `done` (không có token)
- `docu` (không có token)

### **Transitions** (3 transitions):
- `start`: {wait, free} → {work}
- `change`: {work} → {done, docu}
- `end`: {docu} → {free}

### **Initial Marking**:
```
M0 = {wait: 1, free: 1}
```

---

## BƯỚC 1: SETUP

```python
place_list = ['docu', 'done', 'free', 'wait', 'work']  # sorted
place_map = {
    'docu': 0,
    'done': 1, 
    'free': 2,
    'wait': 3,
    'work': 4
} # Sắp xếp theo alphabet thôi
n_places = 5

trans_info = {
    'start': {
        'pre': {'wait', 'free'},
        'post': {'work'}
    },
    'change': {
        'pre': {'work'},
        'post': {'done', 'docu'}
    },
    'end': {
        'pre': {'docu'},
        'post': {'free'}
    }
}
```

---

## BƯỚC 2: KHAI BÁO BIẾN BDD

```python
X = [x[0], x[1], x[2], x[3], x[4]]  # Trạng thái hiện tại
Y = [y[0], y[1], y[2], y[3], y[4]]  # Trạng thái tiếp theo

# Mapping:
# x[0]/y[0] = docu
# x[1]/y[1] = done
# x[2]/y[2] = free
# x[3]/y[3] = wait
# x[4]/y[4] = work
```

---

## BƯỚC 3: MÃ HÓA TRẠNG THÁI BAN ĐẦU R0

Initial marking = {wait, free}

```python
r0_literals = [
    ~x[0],  # docu = 0
    ~x[1],  # done = 0
     x[2],  # free = 1  ✓
     x[3],  # wait = 1  ✓
    ~x[4]   # work = 0
]

R0 = ~x[0] ∧ ~x[1] ∧ x[2] ∧ x[3] ∧ ~x[4]
```

**Nghĩa**: Trạng thái ban đầu có token ở `free` và `wait`, không có ở các place khác.

---

## BƯỚC 4: MÃ HÓA TRANSITION RELATIONS

### **4.1. Transition "start": {wait, free} → {work}**

#### Enable Condition:
```python
pre_set = {'wait', 'free'}
post_set = {'work'}

# Pre-places phải có token
pre_conditions = [x[3], x[2]]  # wait=1, free=1

# Post-only places phải trống (work chưa có token)
post_only = {'work'} - {'wait', 'free'} = {'work'}
post_empty = [~x[4]]  # work=0

Pre_start = x[3] ∧ x[2] ∧ ~x[4]
```

#### Next State Logic:
```python
for i in [0,1,2,3,4]:
    pid = place_list[i]
    
    # i=0 (docu): không thuộc pre hay post → giữ nguyên
    y[0] ↔ x[0]
    
    # i=1 (done): không thuộc pre hay post → giữ nguyên
    y[1] ↔ x[1]
    
    # i=2 (free): thuộc pre, không thuộc post → mất token
    y[2] ↔ False  →  ~y[2]
    
    # i=3 (wait): thuộc pre, không thuộc post → mất token
    y[3] ↔ False  →  ~y[3]
    
    # i=4 (work): thuộc post → có token
    y[4] ↔ True  →  y[4]

Next_start = (y[0]↔x[0]) ∧ (y[1]↔x[1]) ∧ ~y[2] ∧ ~y[3] ∧ y[4]
```

#### Kết hợp:
```python
T_start = Pre_start ∧ Next_start
        = (x[3] ∧ x[2] ∧ ~x[4]) ∧ 
          ((y[0]↔x[0]) ∧ (y[1]↔x[1]) ∧ ~y[2] ∧ ~y[3] ∧ y[4])
```

**Ý nghĩa**: 
- Nếu có token ở `wait` và `free`, không có ở `work`
- Thì sau khi fire: mất token ở `wait`, `free`, được token ở `work`

---

### **4.2. Transition "change": {work} → {done, docu}**

#### Enable Condition:
```python
pre_set = {'work'}
post_set = {'done', 'docu'}

pre_conditions = [x[4]]  # work=1
post_only = {'done', 'docu'} - {'work'} = {'done', 'docu'}
post_empty = [~x[1], ~x[0]]  # done=0, docu=0

Pre_change = x[4] ∧ ~x[1] ∧ ~x[0]
```

#### Next State Logic:
```python
# i=0 (docu): thuộc post → có token
y[0] ↔ True  →  y[0]

# i=1 (done): thuộc post → có token  
y[1] ↔ True  →  y[1]

# i=2 (free): không thuộc pre hay post → giữ nguyên
y[2] ↔ x[2]

# i=3 (wait): không thuộc pre hay post → giữ nguyên
y[3] ↔ x[3]

# i=4 (work): thuộc pre, không thuộc post → mất token
y[4] ↔ False  →  ~y[4]

Next_change = y[0] ∧ y[1] ∧ (y[2]↔x[2]) ∧ (y[3]↔x[3]) ∧ ~y[4]
```

#### Kết hợp:
```python
T_change = Pre_change ∧ Next_change
         = (x[4] ∧ ~x[1] ∧ ~x[0]) ∧
           (y[0] ∧ y[1] ∧ (y[2]↔x[2]) ∧ (y[3]↔x[3]) ∧ ~y[4])
```

---

### **4.3. Transition "end": {docu} → {free}**

#### Enable Condition:
```python
pre_set = {'docu'}
post_set = {'free'}

pre_conditions = [x[0]]  # docu=1
post_only = {'free'} - {'docu'} = {'free'}
post_empty = [~x[2]]  # free=0

Pre_end = x[0] ∧ ~x[2]
```

#### Next State Logic:
```python
# i=0 (docu): thuộc pre, không thuộc post → mất token
y[0] ↔ False  →  ~y[0]

# i=1 (done): không thuộc pre hay post → giữ nguyên
y[1] ↔ x[1]

# i=2 (free): thuộc post → có token
y[2] ↔ True  →  y[2]

# i=3 (wait): không thuộc pre hay post → giữ nguyên
y[3] ↔ x[3]

# i=4 (work): không thuộc pre hay post → giữ nguyên
y[4] ↔ x[4]

Next_end = ~y[0] ∧ (y[1]↔x[1]) ∧ y[2] ∧ (y[3]↔x[3]) ∧ (y[4]↔x[4])
```

#### Kết hợp:
```python
T_end = Pre_end ∧ Next_end
      = (x[0] ∧ ~x[2]) ∧
        (~y[0] ∧ (y[1]↔x[1]) ∧ y[2] ∧ (y[3]↔x[3]) ∧ (y[4]↔x[4]))
```

---

### **4.4. Tổng hợp Transition Relation**

```python
T = T_start ∨ T_change ∨ T_end
```

**Ý nghĩa**: Từ trạng thái X, có thể chuyển sang Y nếu tồn tại ít nhất 1 transition có thể fire.

---

## BƯỚC 5: FIXED-POINT ITERATION

### **Iteration 1**:

```python
Reach = R0 = {(0,0,1,1,0)}  # {free, wait}

# Tìm các trạng thái mới
Img = Reach ∧ T
    = R0 ∧ (T_start ∨ T_change ∨ T_end)
```

**Kiểm tra từng transition**:
- `T_start`: R0 thỏa mãn Pre_start (có wait=1, free=1, work=0) ✓
  - Kết quả: Y = (0,0,0,0,1) = {work}
  
- `T_change`: R0 không thỏa mãn Pre_change (cần work=1) ✗

- `T_end`: R0 không thỏa mãn Pre_end (cần docu=1) ✗

```python
Img_Abstracted = Img.smoothing(X)  # Loại bỏ biến X, chỉ giữ Y
NewStates = Img_Abstracted.compose({y[i]: x[i]})  # Đổi Y→X

NewStates = {(0,0,0,0,1)}  # {work}

Reach = R0 ∪ NewStates 
      = {(0,0,1,1,0), (0,0,0,0,1)}
      = {{free,wait}, {work}}
```

---

### **Iteration 2**:

```python
OldReach = {{free,wait}, {work}}
```

**Kiểm tra với trạng thái {work} = (0,0,0,0,1)**:

- `T_start`: không thỏa mãn (cần wait, free) ✗

- `T_change`: thỏa mãn Pre_change (có work=1, done=0, docu=0) ✓
  - Kết quả: Y = (1,1,0,0,0) = {docu, done}

- `T_end`: không thỏa mãn (cần docu=1) ✗

```python
NewStates = {(1,1,0,0,0)}  # {docu, done}

Reach = OldReach ∪ NewStates
      = {{free,wait}, {work}, {docu,done}}
```

---

### **Iteration 3**:

**Kiểm tra với trạng thái {docu, done} = (1,1,0,0,0)**:

- `T_start`: không thỏa mãn ✗

- `T_change`: không thỏa mãn (cần work=1) ✗

- `T_end`: thỏa mãn Pre_end (có docu=1, free=0) ✓
  - Kết quả: Y = (0,1,1,0,0) = {done, free}

```python
NewStates = {(0,1,1,0,0)}  # {done, free}

Reach = OldReach ∪ NewStates
      = {{free,wait}, {work}, {docu,done}, {done,free}}
```

---

### **Iteration 4**:

**Kiểm tra với trạng thái {done, free} = (0,1,1,0,0)**:

- `T_start`: không thỏa mãn (cần wait=1) ✗
- `T_change`: không thỏa mãn ✗
- `T_end`: không thỏa mãn (cần docu=1) ✗

```python
NewStates = ∅  # Không có trạng thái mới

Reach == OldReach  → CONVERGED! ✓
```

---

## KẾT QUẢ CUỐI CÙNG

### **Reachable States (4 trạng thái)**:

```python
State 1: {free, wait}     = (0,0,1,1,0)  # Initial
State 2: {work}           = (0,0,0,0,1)  # After "start"
State 3: {docu, done}     = (1,1,0,0,0)  # After "change"
State 4: {done, free}     = (0,1,1,0,0)  # After "end"
```

### **Reachability Graph**:

```
{wait,free} --[start]--> {work} --[change]--> {docu,done} --[end]--> {done,free}
```
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
# TASK 5 -- Optimization over reachable markings using BDD + ILP
(End of README content)
>>>>>>> 9c6965e (Remove old README files)
