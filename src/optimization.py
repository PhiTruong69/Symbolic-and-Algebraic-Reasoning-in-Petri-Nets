# Task 5: Optimization over reachable markings using BDD + ILP
# Yêu cầu: maximize c^T M, với M ∈ Reach(M0)

# - BDD (Task 3) dùng để sinh tập Reach(M0)
# - ILP (pulp) dùng để chọn marking tối ưu theo vector trọng số c

import functools
import time
import operator
import tracemalloc
import random

from pyeda.inter import bddvars
from pulp import LpProblem, LpVariable, LpBinary, lpSum, LpStatus, LpMaximize, PULP_CBC_CMD

from petri_net import PetriNet
from parser_simple import load_pnml
from task3 import symbolic_reachability, get_place_list, marking_to_string 

# =============================================================================
# HELPER: Chuyển BDD Reach -> danh sách các marking reachable (explicit)
# =============================================================================

def bdd_to_states(Reach_bdd, place_list):
    """
    Chuyển BDD Reach(X) thành list marking, mỗi marking là frozenset(place_id)

    Args:
        Reach_bdd: BDD kết quả từ symbolic_reachability
        place_list: danh sách place IDs (đã sort, cùng thứ tự với Task 3)

    Returns:
        states: list[frozenset[str]]
    """
    n_places = len(place_list)
    X = bddvars('x', n_places)

    states = []
    for solution in Reach_bdd.satisfy_all():
        marking = frozenset(
            place_list[i]
            for i in range(n_places)
            if solution.get(X[i], False)  # X[i] = True => place có token
        )
        states.append(marking)

    return states

# =============================================================================
# ELPER: Generate weight's place 
# ============================================================================

def generate_weights_from_places(place_list):
    """
    Generate random integer weights (1 to 9) for each place.

    Example:
        place_list = ['wait', 'work', 'done']
        => {'wait': 7, 'work': 2, 'done': 9}  (random)
    """
    weight_dict = {}
    for p in place_list:
        weight_dict[p] = random.randint(1, 9)
    return weight_dict


# =============================================================================
# CORE: ILP Optimization
# =============================================================================

def optimize_marking_with_ilp(states, place_list, weight_dict):
    """
    Tối ưu hóa c^T M trên tập reachable markings (đã explicit hóa từ BDD).

    Args:
        states: list[frozenset[str]]
            Mỗi phần tử là một marking (tập các place đang có token)
        place_list: list[str]
            Danh sách id của tất cả places (không bắt buộc, chỉ để in cho đẹp)
        weight_dict: dict[str, int]
            Trọng số c[p] cho mỗi place p (nếu place không có trong dict, mặc định 0)

    Returns:
        chosen_index: int | None
            Index của marking tối ưu trong `states`, hoặc None nếu không tìm được.
        best_value: int | float | None
            Giá trị tối ưu c^T M, hoặc None nếu không có nghiệm.
    """
    if not states:
        return None, None

    # Tính giá trị c^T M cho từng marking trước (offline)
    state_values = []
    for m in states:
        val = sum(weight_dict.get(p, 0) for p in m)
        state_values.append(val)

    # ILP: biến z_i ∈ {0,1} cho mỗi marking i
    prob = LpProblem("PetriNet_Reachability_Optimization", LpMaximize)

    z_vars = [
        LpVariable(f"z_{i}", lowBound=0, upBound=1, cat=LpBinary)
        for i in range(len(states))
    ]

    # Constraint: chọn đúng 1 marking
    prob += lpSum(z_vars) == 1, "SelectExactlyOneMarking"

    # Objective: maximize sum_i z_i * value_i
    prob += lpSum(state_values[i] * z_vars[i] for i in range(len(states))), "TotalWeight"

    # Giải bài toán
    prob.solve(PULP_CBC_CMD(msg=False))

    if LpStatus[prob.status] != "Optimal":
        # Không tìm được nghiệm tối ưu
        return None, None

    # Tìm marking nào được chọn (z_i = 1)
    chosen_index = None
    best_value = None
    for i, z in enumerate(z_vars):
        z_val = z.varValue
        if z_val is not None and round(z_val) == 1:
            chosen_index = i
            best_value = state_values[i]
            break

    return chosen_index, best_value


# =============================================================================
# TASK 5 WRAPPER: Chạy từ PNML + BDD Task 3
# =============================================================================

def run_task5_optimization(pnml_file, weight_dict=None, verbose=False):
    """
    Chạy Task 5 cho 1 model PNML:
        - Load Petri Net
        - Chạy symbolic_reachability (Task 3) để lấy Reach_bdd
        - Dùng BDD -> states explicit
        - Dùng ILP để tìm marking tối ưu

    Args:
        pnml_file: đường dẫn file .pnml
        weight_dict: dict[str, int], trọng số c[p] cho mỗi place
        verbose: bool, in chi tiết

    Returns:
        success: bool
    """
    print("\n" + "=" * 70)
    print(f"TASK 5: OPTIMIZATION OVER REACHABLE MARKINGS")
    print(f"Model: {pnml_file}")
    print("=" * 70)

    # Load Petri Net từ PNML
    try:
        net = load_pnml(pnml_file)
    except Exception as e:
        print(f"Error: Lỗi load PNML: {e}")
        import traceback
        traceback.print_exc()
        return False

    place_list = get_place_list(net)
    print(f"\n[Thông tin Petri Net]")
    print(f"  Places: {len(place_list)} - {place_list}")
    print(f"  Transitions: {len(net.transitions)} - {[t.id for t in net.transitions]}")
    print(f"  Arcs: {len(net.arcs)}")

    # Nếu không truyền weight_dict từ ngoài vào -> tự tạo theo place_list
    if weight_dict is None:
        weight_dict = generate_weights_from_places(place_list)

    # -------------------------------------------------------------------------
    # Task 3: Symbolic reachability để lấy Reach_bdd
    # -------------------------------------------------------------------------
    # print("\n" + "-" * 70)
    # print("TASK 3 (Reuse): SYMBOLIC REACHABILITY (BDD)")
    # print("-" * 70)
    print("\n[TASK 3 (Reuse): SYMBOLIC REACHABILITY (BDD)]")
    

    tracemalloc.start()
    start_bdd = time.perf_counter()

    try:
        Reach_bdd, count, iterations, stats = symbolic_reachability(net, verbose=False)
    except Exception as e:
        print(f"Error: Lỗi trong symbolic_reachability: {e}")
        import traceback
        traceback.print_exc()
        tracemalloc.stop()
        return False

    end_bdd = time.perf_counter()
    _, peak_bdd = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    time_bdd_ms = (end_bdd - start_bdd) * 1000

    print(f"  Số trạng thái reachable (BDD): {count}")
    print(f"  Số vòng lặp fixed-point: {iterations}")
    print(f"  Thời gian BDD: {time_bdd_ms:.3f} ms")
    print(f"  Bộ nhớ peak BDD: {peak_bdd / 1024:.2f} KB")

    # -------------------------------------------------------------------------
    # Bước phụ: BDD -> danh sách các marking reachable (explicit)
    # -------------------------------------------------------------------------
    # print("\n" + "-" * 70)
    # print("CHUYỂN BDD -> TẬP TRẠNG THÁI EXPLICIT")
    # print("-" * 70)
    print("\n[TẬP TRẠNG THÁI DẠNG EXPLICIT]")

    states = bdd_to_states(Reach_bdd, place_list)
    print(f"  Tổng số trạng thái (từ BDD): {len(states)}")

    if verbose:
        print("\n  Một vài trạng thái đầu:")
        for i, m in enumerate(states[:10]):
            print(f"    State {i}: {marking_to_string(m, place_list)}")

    # -------------------------------------------------------------------------
    # Task 5: ILP Optimization
    # -------------------------------------------------------------------------
    # print("\n" + "-" * 70)
    # print("TASK 5: ILP OPTIMIZATION (maximize c^T M)")
    # print("-" * 70)

    print("\n[ILP OPTIMIZATION (maximize c^T M)]")

    print(f"  Vector trọng số c:")
    for p in place_list:
        w = weight_dict.get(p, 0)
        print(f"    c[{p}] = {w}")

    tracemalloc.start()
    start_ilp = time.perf_counter()

    chosen_index, best_value = optimize_marking_with_ilp(states, place_list, weight_dict)

    end_ilp = time.perf_counter()
    _, peak_ilp = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    time_ilp_ms = (end_ilp - start_ilp) * 1000

    if chosen_index is None:
        print("Not Found: Không tìm được nghiệm ILP (không có marking nào được chọn).")
        return False

    best_marking = states[chosen_index]

    print("\n[MARKING TỐI ƯU]")
    print(f"  Chọn marking state = {chosen_index}")
    print(f"  M* = {marking_to_string(best_marking, place_list)}")
    print(f"  Giá trị tối ưu c^T M* = {best_value}")
    print(f"  Thời gian ILP: {time_ilp_ms:.3f} ms")
    print(f"  Bộ nhớ peak ILP: {peak_ilp / 1024:.2f} KB")
    return True


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    pnml_path = "../data/test1_workflow.pnml" 

    # Ví dụ vector trọng số c cho từng place
    # weight_dict = {
    #     "wait": 1,
    #     "work": 3,
    #     "done": 5,
    #     "free": 1,
    #     "docu": 2,
    # }

    run_task5_optimization(pnml_path,  weight_dict=None, verbose=True)
 