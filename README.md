
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
2. `cd` tới thư mục `src/`
   *Ví dụ:*

   ```bash
   cd C:\MyBachKhoa\MHH\BTL\Git\Code\src
   ```
3. Kích hoạt môi trường:

   ```bash
   conda activate mhh_env
   ```
4. Chạy các task:

   * **Task 1:**

     ```bash
     python parser_simple.py
     ```
   * **Task 2:**

     ```bash
     python dfs.py
     ```
   * **Task 3:**

     ```bash
     python task3.py
     ```
   * **Task 4:**
   
     ```bash
     python --.py
     ```
   * **Task 5:**
   
     ```bash
     python optimization.py
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

--

## Giải thích Task 5 – Optimization over reachable markings (ILP + BDD)