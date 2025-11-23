import pulp
from task3 import (
    symbolic_reachability,
    get_place_list,
    build_transition_info,
    get_initial_marking_set,
)
from parser_simple import load_pnml
from pyeda.inter import bddvars
import time


# Helper: ILP analysis for 1 transition
def explain_transition_enable(tid, info, marking):
    pre = info["pre"]
    post = info["post"]
    post_only = post - pre
    reasons = []

    # Check PRE
    for p in pre:
        if p not in marking:
            reasons.append(f"    - pre-place {p} has no token: DISABLED.")
            return False, "\n".join(reasons)
    # If reached here: all pre have token
    for p in pre:
        reasons.append(f"    - pre-place {p} has token.")

    # Check POST-ONLY
    for p in post_only:
        if p in marking:
            reasons.append(f"    - post-only place {p} already has token: DISABLED.")
            return False, "\n".join(reasons)
    # If reached here: all post-only empty
    for p in post_only:
        reasons.append(f"    - post-only place {p} empty.")

    # If no pre and no post-only -> always enabled
    if len(pre) == 0 and len(post_only) == 0:
        reasons.append("    - no pre & post-only: automatically enabled.")

    # If all conditions satisfied: enabled
    return True, "\n".join(reasons)


# ILP Deadlock checker for 1 marking is deadlock or not
def ilp_check_deadlock(marking, net, place_list, trans_info, debug=False):
    # ILP feasibility model (objective is irrelevant)
    model = pulp.LpProblem("DeadlockCheck", pulp.LpMinimize)

    # Variables: x_p (place token), z_t (enabled transition)
    x = {pid: pulp.LpVariable(f"x_{pid}", cat="Binary") for pid in place_list}
    z = {tid: pulp.LpVariable(f"z_{tid}", cat="Binary") for tid in trans_info}

    # Fix marking: x_p = 1 if place has token
    for pid in place_list:
        model += (x[pid] == (1 if pid in marking else 0))

    # Constraints: transition enable logic
    for tid, info in trans_info.items():
        pre = info["pre"]
        post = info["post"]
        post_only = post - pre

        # Transition with no pre -> always enabled
        if len(pre) == 0:
            model += z[tid] == 1
            continue

        # pre: z_t ≤ x_p  
        for p in pre:
            model += z[tid] <= x[p]
        # post: z_t ≤ 1 - x_p (post only must be empty)
        for p in post_only:
            model += z[tid] <= (1 - x[p])

        # Force z_t = 1 if all conditions satisfied
        k = len(pre) + len(post_only)
        lhs = (pulp.lpSum([x[p] for p in pre]) + pulp.lpSum([(1 - x[p]) for p in post_only]))
        # If all conditions satisfied, lhs = k => z >= 1 => z = 1; Otherwise, lhs < k => z >= negative number ⇒ no effect
        model += z[tid] >= lhs - (k - 1)

    # Deadlock = assume all z_t = 0 (sum(z_t) = 0 just a constraint, not objective function: ILP with not optimize)
    model += pulp.lpSum(z.values()) == 0

    # Solve
    status = model.solve(pulp.PULP_CBC_CMD(msg=False))

    # # Debug print: which transition is actually enabled
    # if debug:
    #     for tid, info in trans_info.items():
    #         print(f"Transition {tid}:")
    #         ok, msg = explain_transition_enable(tid, info, marking)
    #         print(msg)
    #         print(f"        => Transition: {'ENABLED' if ok else 'DISABLED'}")

    print("=> ILP solver result:", pulp.LpStatus[status])

    # Accept feasible or optimal
    return pulp.LpStatus[status] in ["Optimal", "Feasible"]


# Detect all deadlocks using ILP, ignore final states
def detect_deadlocks_ILP(reachable_markings, net, debug_each=False):
    place_list = get_place_list(net)
    trans_info = build_transition_info(net)

    # # Keywords for detecting final state places
    # final_keywords = ["end", "done", "finish", "final"]
    # # Identify final places based on keywords
    # final_places = {
    #     p.id for p in net.places
    #     if any(key in p.id.lower() for key in final_keywords)
    # }
    # Identify final places automatically: places with no outgoing transitions
    final_places = {
        p.id for p in net.places
        if not any(p.id in t["pre"] for t in trans_info.values())
    }


    deadlocks = []

    print("\nILP DEADLOCK DETECTION")
    if final_places:
        print(f"- Final places detected automatically: {sorted(final_places)}.")
    else:
        print("- No final places detected.")

    for m in reachable_markings:
        print(f"\nChecking marking {sorted(m)}:")
        # Check if marking is final 
        if final_places & m:
            print(f"=> Marking {sorted(m)} contains final place -> FINAL MARKING, no deadlock")
            continue

        is_dead = ilp_check_deadlock(m, net, place_list, trans_info, debug=debug_each)
        if is_dead:
            print("  => DEADLOCK")
            deadlocks.append(m)
        else:
            print("  => Not deadlock")

    return deadlocks


# Main function
def run_task4(pnml_file, debug_ilp=False):
    print("\nTASK 4: BDD + ILP DEADLOCK DETECTION")
    print("=" * 40)
    
    start_total = time.time()

    # Load model
    net = load_pnml(pnml_file)
    place_list = get_place_list(net)
    trans_info = build_transition_info(net)

    # Initial marking
    initial_marking = get_initial_marking_set(net)
    print(f"\nInitial marking: {sorted(initial_marking)}")
    print(f"Places ({len(place_list)}): {place_list}")
    
    print("\nTransitions:")
    for tid, info in trans_info.items():
        print(f"  Transition '{tid}':")
        print(f"    Pre  = {sorted(info['pre'])}")
        print(f"    Post = {sorted(info['post'])}")
    
    # BDD reachability
    start_bdd = time.time()
    Reach_bdd, count, iters, stats = symbolic_reachability(net, verbose=False)
    end_bdd = time.time()
    # Convert BDD to explicit markings
    X = bddvars('x', len(place_list))
    reachable = []
    # Feasible markings
    for idx, sol in enumerate(Reach_bdd.satisfy_all()):
        marking_dict = {place_list[i]: 1 if sol.get(X[i], 0) else 0 for i in range(len(place_list))}
        reachable.append(frozenset(pid for pid, v in marking_dict.items() if v > 0))
        print(f"Marking {idx}: {marking_dict}")
    print(f"Total reachable markings: {len(reachable)}")
    
    # ILP Deadlock checking
    start_ilp = time.time()
    dead = detect_deadlocks_ILP(reachable, net, debug_each=debug_ilp)
    end_ilp = time.time()

    print("\nDEADLOCK SUMMARY")
    if not dead:
        print("=> No deadlocks in this Petri Net.")
    else:
        print(f"=> Found {len(dead)} deadlocks:")
        for m in dead:
            print("    -", sorted(m))

    print("\nRUNNING-TIME SUMMARY")
    print(f"- BDD reachability time: {end_bdd - start_bdd:.4f} seconds")
    print(f"- ILP deadlock detection time: {end_ilp - start_ilp:.4f} seconds")
    return dead


# MAIN
if __name__ == "__main__":
    run_task4("data/test_deadlock.pnml", debug_ilp=True)
