import functools
import operator
import time
import tracemalloc
from pyeda.inter import bddvars
from petri_net import PetriNet
from parser_simple import load_pnml

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def build_transition_info(net):  # Tìm tập trước và sau của transition ()
    trans_info = {} # Đầu tiên khỏi tạo rỗng trước
    
    for t in net.transitions: 
        trans_info[t.id] = {
            'pre': set(),
            'post': set(),
            'obj': t
        }
    
    for arc in net.arcs:
        from petri_net import Place, Transition
        src = arc.source
        tgt = arc.target
        
        if isinstance(src, Place) and isinstance(tgt, Transition): #tìm tập pre
            trans_info[tgt.id]['pre'].add(src.id)
        elif isinstance(src, Transition) and isinstance(tgt, Place): # tìm tập post
            trans_info[src.id]['post'].add(tgt.id)
    # in ra kết quả để debug
    # for t_id, info in trans_info.items():
    #     print(f"Transition {t_id}: Pre = {info['pre']}, Post = {info['post']}")
    
    return trans_info

def get_place_list(net):
    """Lấy danh sách place IDs đã sắp xếp"""
    return sorted([p.id for p in net.places])

def get_initial_marking_set(net):
    """Chuyển initial_marking từ dict {pid: tokens} sang frozenset {pid} (in ra place có token)"""
    return frozenset(pid for pid, tokens in net.initial_marking.items() if tokens > 0)

def marking_dict_to_frozenset(marking_dict):
    """
    Chuyển marking từ dict {place_id: tokens} sang frozenset {place_id}
    (Chỉ lấy places có token > 0)
    """
    return frozenset(pid for pid, tokens in marking_dict.items() if tokens > 0)

def marking_to_string(marking, place_list):
    """Chuyển marking thành string để hiển thị"""
    tokens = []
    for pid in place_list:
        if pid in marking:
            tokens.append(f"{pid}:1")
    return "{" + ", ".join(tokens) + "}" if tokens else "{empty}"

# =============================================================================
# TASK 3: SYMBOLIC REACHABILITY (BDD)
# =============================================================================

def symbolic_reachability(net, verbose=False):
    """
    Task 3: Tìm tập trạng thái đạt được bằng BDD
    """
    place_list = get_place_list(net)
    place_map = {pid: i for i, pid in enumerate(place_list)}
    trans_info = build_transition_info(net)
    initial = get_initial_marking_set(net)
    
    n_places = len(place_list)
    
    if verbose:
        print(f"\n[BDD Setup]")
        print(f"  Places: {n_places} - {place_list}")
        print(f"  Transitions: {len(trans_info)}")
        print(f"  Initial marking: {set(initial)}")
    
    # 1. Khai báo biến BDD
    X = bddvars('x', n_places)
    Y = bddvars('y', n_places)

    # 2. Mã hóa trạng thái ban đầu R0
    r0_literals = []
    for i, pid in enumerate(place_list):
        if pid in initial:
            r0_literals.append(X[i]) #Nếu có token thì X[i] = True
        else:
            r0_literals.append(~X[i]) #Nếu không có token thì X[i] = False
        #in ra để debug
        if verbose:
            val = "1" if pid in initial else "0"
            print(f"  R0 literal for place {pid}: x_{i} = {val}")
    R0 = functools.reduce(operator.and_, r0_literals)
    
    
    if verbose:
        print(f"\n[Initial Marking BDD]")
        print(f"  R0 constructed")

    # 3. Mã hóa quan hệ chuyển tiếp T(X, Y)
    T_parts = []
    
    for t_id, t_info in trans_info.items():
        pre_set = t_info['pre']
        post_set = t_info['post']
        
        if verbose:
            print(f"\n[Transition {t_id}]")
            print(f"  Pre: {pre_set}")
            print(f"  Post: {post_set}")
        
        # Enable Condition
        pre_conditions = [X[place_map[p]] for p in pre_set]
        post_only = post_set - pre_set
        post_empty_conditions = [~X[place_map[p]] for p in post_only]
        # in ra để debug
        # if verbose:
        #     for p in pre_set:
        #         i = place_map[p]
        #         print(f"    Pre condition: x_{i} = 1 (place {p})")
        #     for p in post_only:
        #         i = place_map[p]
        #         print(f"    Post-empty condition: x_{i} = 0 (place {p})")
        all_enable_conditions = pre_conditions + post_empty_conditions
        Pre_X = functools.reduce(operator.and_, all_enable_conditions) \
                if all_enable_conditions else True

        # Trạng thái sau khi fire
        Next_X_Y = []
        for i in range(n_places):
            pid = place_list[i]
            
            in_pre = pid in pre_set #kiểm tra place có trong pre không
            in_post = pid in post_set #kiểm tra place có trong post không
            
            if in_post: #nếu có trong post thì y_i = True
                y_i_formula = True
            elif in_pre: #nếu có trong pre thì y_i = False
                y_i_formula = False
            else: #nếu không có trong cả pre và post thì y_i = x_i
                y_i_formula = X[i]
    
            next_logic_i = ~(Y[i] ^ y_i_formula)
            Next_X_Y.append(next_logic_i)
            # in ra để debug
            # if verbose:
            #     if in_post:
            #         print(f"    Next condition for place {pid}: y_{i} = 1 (in post)")
            #     elif in_pre:
            #         print(f"    Next condition for place {pid}: y_{i} = 0 (in pre)")
            #     else:
            #         print(f"    Next condition for place {pid}: y_{i} = x_{i} (unchanged)")
        
        all_next_logic = functools.reduce(operator.and_, Next_X_Y) if Next_X_Y else True
        T_t = Pre_X & all_next_logic
        T_parts.append(T_t)

    T = functools.reduce(operator.or_, T_parts) if T_parts else False
    
    # if verbose:
    #     print(f"\n[Transition Relation]")
    #     print(f"  T = OR of {len(T_parts)} transition relations")

    # 4. Fixed-Point Iteration
    sub_map = {Y[i]: X[i] for i in range(n_places)}
    
    Reach = R0
    iteration = 0
    
    if verbose:
        print(f"\n[Fixed-Point Iteration]")
    
    while True:
        iteration += 1
        OldReach = Reach
        
        Img = OldReach & T
        Img_Abstracted = Img.smoothing(X)
        NewStates = Img_Abstracted.compose(sub_map)
        Reach = OldReach | NewStates
        
        if verbose:
            new_count = NewStates.satisfy_count()
            total_count = Reach.satisfy_count()
            print(f"  Iteration {iteration}: +{new_count} new states, total = {total_count}")
        
        if Reach == OldReach:
            if verbose:
                print(f"  Converged after {iteration} iterations")
            break
    
    # 5. Đếm số trạng thái
    count = Reach.satisfy_count()
    
    stats = {
        'n_places': n_places,
        'n_transitions': len(trans_info),
        'iterations': iteration,
        'reachable_states': count
    }
    
    return Reach, count, iteration, stats

def print_bdd_states(Reach_bdd, place_list, max_show=10):
    """
    In các trạng thái đạt được từ BDD
    
    Args:
        Reach_bdd: BDD Expression object
        place_list: danh sách place IDs đã sort
        max_show: số trạng thái tối đa hiển thị
    """
    n_places = len(place_list)
    X = bddvars('x', n_places)
    
    # Chuyển BDD sang list of frozensets
    all_states = []
    
    print(f"\n[Converting BDD to explicit states...]")
    for solution in Reach_bdd.satisfy_all():
        marking = frozenset(
            place_list[i] 
            for i in range(n_places)
            if solution.get(X[i], False)
        )
        all_states.append(marking)
    
    # Sắp xếp: theo số token, rồi theo alphabet
    sorted_states = sorted(all_states, key=lambda m: (len(m), sorted(m)))
    
    # In ra
    print(f"\n[Reachable States: {len(sorted_states)} states]")
    for i, marking in enumerate(sorted_states):
        if i >= max_show:
            remaining = len(sorted_states) - max_show
            print(f"    ... ({remaining} more states)")
            break
        print(f"    State {i+1}: {marking_to_string(marking, place_list)}")
    
    return sorted_states
# =============================================================================
# VALIDATION & COMPARISON
# =============================================================================

def validate_results(net, explicit_states_frozenset, bdd_count, Reach_bdd, max_show=10):
    """
    So sánh và validate kết quả giữa explicit và symbolic
    """
    place_list = get_place_list(net)
    X = bddvars('x', len(place_list))
    
    print("\n" + "=" * 70) # Tạo mấy dấu ===
    print("VALIDATION & COMPARISON")
    print("=" * 70) 
    
    # 1. So sánh số lượng
    explicit_count = len(explicit_states_frozenset)
    
    print(f"\n[Số lượng trạng thái]")
    print(f"  Explicit (Task 2 - DFS): {explicit_count}")
    print(f"  BDD (Task 3):            {bdd_count}")
    
    if explicit_count == bdd_count:
        print(f"  ✅ KHỚP!")
    else:
        print(f"  ❌ KHÔNG KHỚP! Chênh lệch: {abs(explicit_count - bdd_count)}")
        return False
    
    # 2. Chuyển BDD thành explicit set để so sánh chi tiết
    print(f"\n[Kiểm tra từng trạng thái]")
    bdd_states = set()
    
    for solution in Reach_bdd.satisfy_all():
        marking = frozenset(
            place_list[i] for i in range(len(place_list))
            if solution.get(X[i], False)
        )
        bdd_states.add(marking)
    
    # 3. So sánh tập hợp
    only_explicit = explicit_states_frozenset - bdd_states
    only_bdd = bdd_states - explicit_states_frozenset
    
    if not only_explicit and not only_bdd:
        print(f"  ✅ TẤT CẢ {explicit_count} TRẠNG THÁI KHỚP HOÀN TOÀN!")
    else:
        print(f"  ❌ CÓ SAI KHÁC:")
        if only_explicit:
            print(f"     - Chỉ có trong Explicit: {len(only_explicit)} trạng thái")
            for m in list(only_explicit)[:3]:
                print(f"       {marking_to_string(m, place_list)}")
        if only_bdd:
            print(f"     - Chỉ có trong BDD: {len(only_bdd)} trạng thái")
            for m in list(only_bdd)[:3]:
                print(f"       {marking_to_string(m, place_list)}")
        return False
    
    # 4. Hiển thị một số trạng thái mẫu
    print(f"\n[Một số trạng thái đạt được] (hiển thị tối đa {max_show}):")
    for i, marking in enumerate(sorted(explicit_states_frozenset, key=lambda m: (len(m), sorted(m)))):
        if i >= max_show:
            print(f"  ... (còn {explicit_count - max_show} trạng thái nữa)")
            break
        print(f"  {i+1}. {marking_to_string(marking, place_list)}")
    
    return True

# =============================================================================
# HÀM TEST - SỬ DỤNG KẾT QUẢ TỪ dfs.py
# =============================================================================

def run_test_with_dfs_results(pnml_file, expected_count=None, verbose=False):
    """
    Chạy test sử dụng kết quả từ petri_net.compute_reachable_markings() (DFS)
    
    Args:
        pnml_file: đường dẫn đến file .pnml
        expected_count: số trạng thái expected (optional)
        verbose: In chi tiết quá trình BDD
    """
    print("\n" + "=" * 70)
    print(f"TEST: {pnml_file}")
    print("=" * 70)
    
    # Load PNML
    try:
        net = load_pnml(pnml_file)
    except Exception as e:
        print(f"❌ Lỗi load file: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    place_list = get_place_list(net)
    print(f"\n[Thông tin Petri Net]")
    print(f"  Places: {len(net.places)} - {place_list}")
    print(f"  Transitions: {len(net.transitions)} - {[t.id for t in net.transitions]}")
    print(f"  Arcs: {len(net.arcs)}")
    # Debug: In ra các arc của BDD (này chỉ lấy kết quả từ parser_simple thôi)
    for arc in net.arcs:
        print(f"    {arc.source.id} -> {arc.target.id}")
    
    initial_set = get_initial_marking_set(net)
    print(f"  Initial marking: {marking_to_string(initial_set, place_list)}")
    
    if expected_count:
        print(f"  Expected reachable markings: {expected_count}")
    
    # Task 2: SỬ DỤNG DFS TỪ petri_net.py
    print("\n" + "-" * 70)
    print("TASK 2: EXPLICIT REACHABILITY (DFS từ petri_net.py)")
    print("-" * 70)
    
    tracemalloc.start()
    start_2 = time.perf_counter()
    
    try:
        # GỌI HÀM DFS TỪ petri_net.py
        reachable_markings_dfs = net.compute_reachable_markings()
        
        # Chuyển đổi từ list of dicts sang set of frozensets
        explicit_states_frozenset = set()
        for marking_dict in reachable_markings_dfs:
            marking_fs = marking_dict_to_frozenset(marking_dict)
            explicit_states_frozenset.add(marking_fs)
        
    except Exception as e:
        print(f"❌ Lỗi trong DFS: {e}")
        import traceback
        traceback.print_exc()
        tracemalloc.stop()
        return False
    
    end_2 = time.perf_counter()
    current_2, peak_2 = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    time_2 = (end_2 - start_2) * 1000
    
    print(f"  Số trạng thái: {len(explicit_states_frozenset)}")
    #Debug: In ra các trạng thái tìm được
    for i, marking in enumerate(sorted(explicit_states_frozenset, key=lambda m: (len(m), sorted(m)))):
        print(f"    Marking {i}: {marking_to_string(marking, place_list)}")

    print(f"  Thời gian: {time_2:.3f} ms")
    print(f"  Bộ nhớ peak: {peak_2 / 1024:.2f} KB")
    print(f"  ✅ Sử dụng DFS từ petri_net.compute_reachable_markings()")
    
    # Task 3: Symbolic
    print("\n" + "-" * 70)
    print("TASK 3: SYMBOLIC REACHABILITY (BDD)")
    print("-" * 70)
    
    tracemalloc.start()
    start_3 = time.perf_counter()
    
    try:
        Reach_bdd, count, iterations, stats = symbolic_reachability(net, verbose=verbose)
    except Exception as e:
        print(f"❌ Lỗi trong symbolic reachability: {e}")
        import traceback
        traceback.print_exc()
        tracemalloc.stop()
        return False
    
    end_3 = time.perf_counter()
    current_3, peak_3 = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    time_3 = (end_3 - start_3) * 1000
    
    print(f"  Số trạng thái: {count}")
    #Debug: In ra các trạng thái tìm được từ BDD
    if verbose or count <= 20:  # Chỉ in nếu verbose hoặc ít trạng thái
        bdd_states = print_bdd_states(Reach_bdd, place_list, max_show=15)
    print(f"  Số lần lặp fixed-point: {iterations}")
    print(f"  Thời gian: {time_3:.3f} ms")
    print(f"  Bộ nhớ peak: {peak_3 / 1024:.2f} KB")
    
    # Validation
    try:
        validation_passed = validate_results(net, explicit_states_frozenset, count, Reach_bdd, max_show=10)
    except Exception as e:
        print(f"\n❌ Lỗi trong validation: {e}")
        import traceback
        traceback.print_exc()
        validation_passed = False
    
    # Kiểm tra kết quả
    print("\n" + "=" * 70)
    print("KẾT QUẢ CUỐI CÙNG")
    print("=" * 70)
    
    success = True
    
    if not validation_passed:
        print(f"  ❌ VALIDATION FAILED")
        success = False
    elif expected_count and count != expected_count:
        print(f"  ❌ Số trạng thái không đúng: Expected={expected_count}, Got={count}")
        success = False
    else:
        msg = f"Cả DFS và BDD đều tìm thấy {count} trạng thái"
        if expected_count:
            msg += " ✅ (đúng với expected)"
        print(f"  ✅ PASS: {msg}")
    
    # Performance comparison
    speedup = time_2 / time_3 if time_3 > 0 else 0
    
    print(f"\n[Performance Comparison]")
    print(f"  DFS (Task 2): {time_2:.3f} ms, {peak_2 / 1024:.2f} KB")
    print(f"  BDD (Task 3): {time_3:.3f} ms, {peak_3 / 1024:.2f} KB")
    print(f"  Speedup:      {speedup:.2f}x {'(BDD faster)' if speedup > 1 else '(DFS faster)'}")
    
    return success

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import os
    
    test_cases = [
        ("../data/simple.pnml", 2),
        ("../data/test1_workflow.pnml", 4),
        ("../data/test2_selfloop.pnml", 3),
        ("../data/test3_deadlock.pnml", 5),
        ("../data/test4_cycle.pnml", 3),
        ("../data/test5_choice.pnml", 3),
        ("../data/test_6.pnml", 5),
    ]
    
    print("\n" + "=" * 70)
    print("PETRI NET REACHABILITY ANALYSIS")
    print("Task 2 (DFS từ petri_net.py) + Task 3 (Symbolic BDD)")
    print("=" * 70)
    
    results = []
    
    for idx, (pnml_file, expected) in enumerate(test_cases):
        if not os.path.exists(pnml_file):
            print(f"\n⚠️  File không tồn tại: {pnml_file}")
            print("    Chạy pnml_generator.py trước để tạo test cases!")
            results.append((pnml_file, False, expected))
            continue
        
        # Chỉ verbose cho test case đầu tiên
        verbose = (idx == 0)
        
        success = run_test_with_dfs_results(pnml_file, expected, verbose=verbose)
        results.append((pnml_file, success, expected))
    
    # Tổng kết
    if results:
        print("\n" + "=" * 70)
        print("TỔNG KẾT")
        print("=" * 70) 
        passed = sum(1 for _, success, _ in results if success)
        total = len(results)
        print(f"\nPassed: {passed}/{total}")
        print(f"Success rate: {passed/total*100:.1f}%\n")
        
        for pnml_file, success, expected in results:
            status = "✅ PASS" if success else "❌ FAIL"
            filename = os.path.basename(pnml_file)
            print(f"  {status}: {filename:30s} (expected: {expected} states)")
        
        if passed == total:
            print(f"\n🎉 ALL TESTS PASSED! 🎉")
            print(f"\n💡 Sử dụng DFS từ petri_net.compute_reachable_markings()")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed.")


