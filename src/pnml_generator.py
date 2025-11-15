# HÀM NÀY ĐỂ TẠO TESTCASE THÔI. NHƯNG VẼ TRÊN TAPAAL RỒI NÊN KHỎI

# """
# TAPAAL-Correct PNML Generator
# Tạo file PNML theo ĐÚNG format mà TAPAAL export ra
# """

# import os

# def create_tapaal_header():
#     """Tạo header giống TAPAAL"""
#     return '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
# <pnml xmlns="http://www.pnml.org/version-2009/grammar/pnml">
#     <net id="ComposedModel" type="http://www.pnml.org/version-2009/grammar/ptnet">
#         <name>
#             <text>ComposedModel</text>
#         </name>
#         <page id="page0">
# '''

# def create_tapaal_footer():
#     """Tạo footer giống TAPAAL"""
#     return '''        </page>
#     </net>
# </pnml>
# '''

# def create_tapaal_place(place_id, name, x, y, initial_marking=0):
#     """Tạo place theo ĐÚNG format TAPAAL"""
#     return f'''            <place id="{place_id}">
#                 <graphics>
#                     <position x="{x}" y="{y}"/>
#                 </graphics>
#                 <name>
#                     <graphics>
#                         <offset x="0" y="0"/>
#                     </graphics>
#                     <text>{name}</text>
#                 </name>
#                 <initialMarking>
#                     <text>{initial_marking}</text>
#                 </initialMarking>
#             </place>
# '''

# def create_tapaal_transition(trans_id, name, x, y):
#     """Tạo transition theo ĐÚNG format TAPAAL"""
#     return f'''            <transition distribution="constant" id="{trans_id}" value="1.0">
#                 <name>
#                     <graphics>
#                         <offset x="0" y="0"/>
#                     </graphics>
#                     <text>{name}</text>
#                 </name>
#                 <graphics>
#                     <position x="{x}" y="{y}"/>
#                 </graphics>
#             </transition>
# '''

# def create_tapaal_arc(arc_id, source, target):
#     """Tạo arc theo ĐÚNG format TAPAAL"""
#     return f'''            <arc id="{arc_id}" source="{source}" target="{target}" type="normal"/>
# '''

# # =============================================================================
# # TEST CASES
# # =============================================================================

# def generate_test1_workflow():
#     """
#     Test 1: Workflow
#     Expected: 4 reachable markings
#     """
#     content = create_tapaal_header()
    
#     # Places
#     content += create_tapaal_place("wait", "wait", 120, 120, 1)
#     content += create_tapaal_place("work", "work", 255, 165, 0)
#     content += create_tapaal_place("done", "done", 375, 120, 0)
#     content += create_tapaal_place("free", "free", 120, 210, 1)
#     content += create_tapaal_place("docu", "docu", 375, 210, 0)
    
#     # Transitions
#     content += create_tapaal_transition("start", "start", 180, 165)
#     content += create_tapaal_transition("change", "change", 315, 165)
#     content += create_tapaal_transition("end", "end", 255, 270)
    
#     # Arcs
#     content += create_tapaal_arc("wait_to_start", "wait", "start")
#     content += create_tapaal_arc("free_to_start", "free", "start")
#     content += create_tapaal_arc("start_to_work", "start", "work")
#     content += create_tapaal_arc("work_to_change", "work", "change")
#     content += create_tapaal_arc("change_to_done", "change", "done")
#     content += create_tapaal_arc("change_to_docu", "change", "docu")
#     content += create_tapaal_arc("docu_to_end", "docu", "end")
#     content += create_tapaal_arc("end_to_free", "end", "free")
    
#     content += create_tapaal_footer()
#     return content

# def generate_test2_selfloop():
#     """
#     Test 2: Self-loop
#     Expected: 3 reachable markings
#     """
#     content = create_tapaal_header()
    
#     # Places
#     content += create_tapaal_place("p1", "p1", 100, 200, 1)
#     content += create_tapaal_place("p2", "p2", 300, 200, 0)
#     content += create_tapaal_place("p3", "p3", 500, 200, 0)
    
#     # Transitions
#     content += create_tapaal_transition("t1", "t1", 200, 200)
#     content += create_tapaal_transition("t2", "t2", 300, 280)
#     content += create_tapaal_transition("t3", "t3", 400, 200)
    
#     # Arcs
#     content += create_tapaal_arc("p1_to_t1", "p1", "t1")
#     content += create_tapaal_arc("t1_to_p2", "t1", "p2")
#     content += create_tapaal_arc("p2_to_t2", "p2", "t2")
#     content += create_tapaal_arc("t2_to_p2", "t2", "p2")  # self-loop
#     content += create_tapaal_arc("p2_to_t3", "p2", "t3")
#     content += create_tapaal_arc("t3_to_p3", "t3", "p3")
    
#     content += create_tapaal_footer()
#     return content

# def generate_test3_deadlock():
#     """
#     Test 3: Network with deadlock
#     Expected: 5 reachable markings (including 2 deadlock states)
#     """
#     content = create_tapaal_header()
    
#     # Places
#     content += create_tapaal_place("p1", "p1", 100, 150, 1)
#     content += create_tapaal_place("p2", "p2", 100, 300, 1)
#     content += create_tapaal_place("p3", "p3", 300, 150, 0)
#     content += create_tapaal_place("p4", "p4", 300, 300, 0)
#     content += create_tapaal_place("p5", "p5", 500, 225, 0)
    
#     # Transitions
#     content += create_tapaal_transition("t1", "t1", 200, 150)
#     content += create_tapaal_transition("t2", "t2", 200, 300)
#     content += create_tapaal_transition("t3", "t3", 400, 225)
    
#     # Arcs
#     content += create_tapaal_arc("p1_to_t1", "p1", "t1")
#     content += create_tapaal_arc("t1_to_p3", "t1", "p3")
#     content += create_tapaal_arc("p2_to_t2", "p2", "t2")
#     content += create_tapaal_arc("t2_to_p4", "t2", "p4")
#     content += create_tapaal_arc("p3_to_t3", "p3", "t3")
#     content += create_tapaal_arc("p4_to_t3", "p4", "t3")
#     content += create_tapaal_arc("t3_to_p5", "t3", "p5")
    
#     content += create_tapaal_footer()
#     return content

# def generate_test4_cycle():
#     """
#     Test 4: Cyclic network
#     Expected: 3 reachable markings
#     """
#     content = create_tapaal_header()
    
#     # Places (arranged in triangle)
#     content += create_tapaal_place("p1", "p1", 300, 100, 1)
#     content += create_tapaal_place("p2", "p2", 450, 300, 0)
#     content += create_tapaal_place("p3", "p3", 150, 300, 0)
    
#     # Transitions
#     content += create_tapaal_transition("t1", "t1", 375, 200)
#     content += create_tapaal_transition("t2", "t2", 300, 350)
#     content += create_tapaal_transition("t3", "t3", 225, 200)
    
#     # Arcs (cycle)
#     content += create_tapaal_arc("p1_to_t1", "p1", "t1")
#     content += create_tapaal_arc("t1_to_p2", "t1", "p2")
#     content += create_tapaal_arc("p2_to_t2", "p2", "t2")
#     content += create_tapaal_arc("t2_to_p3", "t2", "p3")
#     content += create_tapaal_arc("p3_to_t3", "p3", "t3")
#     content += create_tapaal_arc("t3_to_p1", "t3", "p1")
    
#     content += create_tapaal_footer()
#     return content

# def generate_test5_choice():
#     """
#     Test 5: Non-deterministic choice
#     Expected: 3 reachable markings
#     """
#     content = create_tapaal_header()
    
#     # Places
#     content += create_tapaal_place("p1", "p1", 200, 200, 1)
#     content += create_tapaal_place("p2", "p2", 400, 120, 0)
#     content += create_tapaal_place("p3", "p3", 400, 280, 0)
    
#     # Transitions
#     content += create_tapaal_transition("t1", "t1", 300, 160)
#     content += create_tapaal_transition("t2", "t2", 300, 240)
    
#     # Arcs
#     content += create_tapaal_arc("p1_to_t1", "p1", "t1")
#     content += create_tapaal_arc("t1_to_p2", "t1", "p2")
#     content += create_tapaal_arc("p1_to_t2", "p1", "t2")
#     content += create_tapaal_arc("t2_to_p3", "t2", "p3")
    
#     content += create_tapaal_footer()
#     return content

# def generate_test6_prodcons():
#     """
#     Test 6: Producer-Consumer pattern
#     Expected: 6 reachable markings
#     """
#     content = create_tapaal_header()
    
#     # Places
#     content += create_tapaal_place("ready", "ready", 100, 150, 1)
#     content += create_tapaal_place("item", "item", 250, 150, 0)
#     content += create_tapaal_place("idle", "idle", 250, 250, 1)
    
#     # Transitions
#     content += create_tapaal_transition("produce", "produce", 175, 150)
#     content += create_tapaal_transition("consume", "consume", 325, 200)
#     content += create_tapaal_transition("stop_prod", "stop_prod", 100, 250)
#     content += create_tapaal_transition("stop_cons", "stop_cons", 250, 320)
    
#     # Arcs
#     content += create_tapaal_arc("ready_to_produce", "ready", "produce")
#     content += create_tapaal_arc("produce_to_item", "produce", "item")
#     content += create_tapaal_arc("produce_to_ready", "produce", "ready")
#     content += create_tapaal_arc("item_to_consume", "item", "consume")
#     content += create_tapaal_arc("idle_to_consume", "idle", "consume")
#     content += create_tapaal_arc("consume_to_idle", "consume", "idle")
#     content += create_tapaal_arc("ready_to_stop_prod", "ready", "stop_prod")
#     content += create_tapaal_arc("idle_to_stop_cons", "idle", "stop_cons")
    
#     content += create_tapaal_footer()
#     return content

# def generate_test7_philosophers():
#     """
#     Test 7: Dining Philosophers (2 philosophers, 2 forks)
#     Expected: 8 reachable markings
#     """
#     content = create_tapaal_header()
    
#     # Places
#     content += create_tapaal_place("p1", "phil1_thinking", 100, 100, 1)
#     content += create_tapaal_place("p2", "phil2_thinking", 100, 250, 1)
#     content += create_tapaal_place("f1", "fork1", 300, 100, 1)
#     content += create_tapaal_place("f2", "fork2", 300, 250, 1)
#     content += create_tapaal_place("e1", "phil1_eating", 500, 100, 0)
#     content += create_tapaal_place("e2", "phil2_eating", 500, 250, 0)
    
#     # Transitions
#     content += create_tapaal_transition("pickup1", "pickup1", 250, 150)
#     content += create_tapaal_transition("putdown1", "putdown1", 550, 150)
#     content += create_tapaal_transition("pickup2", "pickup2", 250, 300)
#     content += create_tapaal_transition("putdown2", "putdown2", 550, 300)
    
#     # Arcs for philosopher 1
#     content += create_tapaal_arc("p1_to_pickup1", "p1", "pickup1")
#     content += create_tapaal_arc("f1_to_pickup1", "f1", "pickup1")
#     content += create_tapaal_arc("f2_to_pickup1", "f2", "pickup1")
#     content += create_tapaal_arc("pickup1_to_e1", "pickup1", "e1")
#     content += create_tapaal_arc("e1_to_putdown1", "e1", "putdown1")
#     content += create_tapaal_arc("putdown1_to_p1", "putdown1", "p1")
#     content += create_tapaal_arc("putdown1_to_f1", "putdown1", "f1")
#     content += create_tapaal_arc("putdown1_to_f2", "putdown1", "f2")
    
#     # Arcs for philosopher 2
#     content += create_tapaal_arc("p2_to_pickup2", "p2", "pickup2")
#     content += create_tapaal_arc("f1_to_pickup2", "f1", "pickup2")
#     content += create_tapaal_arc("f2_to_pickup2", "f2", "pickup2")
#     content += create_tapaal_arc("pickup2_to_e2", "pickup2", "e2")
#     content += create_tapaal_arc("e2_to_putdown2", "e2", "putdown2")
#     content += create_tapaal_arc("putdown2_to_p2", "putdown2", "p2")
#     content += create_tapaal_arc("putdown2_to_f1", "putdown2", "f1")
#     content += create_tapaal_arc("putdown2_to_f2", "putdown2", "f2")
    
#     content += create_tapaal_footer()
#     return content

# def generate_simple():
#     """
#     Simple test: p1 -> p2
#     Expected: 2 reachable markings
#     """
#     content = create_tapaal_header()
    
#     # Places
#     content += create_tapaal_place("p1", "p1", 150, 200, 1)
#     content += create_tapaal_place("p2", "p2", 350, 200, 0)
    
#     # Transition
#     content += create_tapaal_transition("t1", "t1", 250, 200)
    
#     # Arcs
#     content += create_tapaal_arc("p1_to_t1", "p1", "t1")
#     content += create_tapaal_arc("t1_to_p2", "t1", "p2")
    
#     content += create_tapaal_footer()
#     return content

# # =============================================================================
# # MAIN
# # =============================================================================

# def main():
#     """Generate all test files"""
    
#     output_dir = "data"
#     os.makedirs(output_dir, exist_ok=True)
    
#     test_cases = [
#         ("simple.pnml", generate_simple, "Simple (2 markings)"),
#         ("test1_workflow.pnml", generate_test1_workflow, "Workflow (4 markings)"),
#         ("test2_selfloop.pnml", generate_test2_selfloop, "Self-loop (3 markings)"),
#         ("test3_deadlock.pnml", generate_test3_deadlock, "Deadlock (5 markings)"),
#         ("test4_cycle.pnml", generate_test4_cycle, "Cycle (3 markings)"),
#         ("test5_choice.pnml", generate_test5_choice, "Choice (3 markings)"),
#         #("test6_prodcons.pnml", generate_test6_prodcons, "Producer-Consumer (6 markings)"),
#         #("test7_philosophers.pnml", generate_test7_philosophers, "Dining Philosophers (8 markings)"),
#     ]
    
#     print("=" * 70)
#     print("TAPAAL-CORRECT PNML GENERATOR")
#     print("=" * 70)
#     print("Format: Exactly matching TAPAAL export format\n")
    
#     for filename, generator, description in test_cases:
#         filepath = os.path.join(output_dir, filename)
#         content = generator()
        
#         with open(filepath, 'w', encoding='utf-8') as f:
#             f.write(content)
        
#         print(f"✅ Generated: {filename:30s} - {description}")
    
#     print("\n" + "=" * 70)
#     print(f"All files saved to: {output_dir}/")
#     print("\nTO OPEN IN TAPAAL:")
#     print("1. Open TAPAAL")
#     print("2. File → Open")
#     print(f"3. Navigate to {output_dir}/")
#     print("4. Select any .pnml file")
#     print("5. Should load perfectly! ✅")
#     print("=" * 70)
    
#     # Create README
#     readme_path = os.path.join(output_dir, "README.txt")
#     with open(readme_path, 'w', encoding='utf-8') as f:
#         f.write("""TAPAAL-Compatible PNML Test Cases
# ====================================

# These files are generated with EXACT TAPAAL format.
# They should load perfectly in TAPAAL without errors.

# Test Cases:
# -----------
# 1. simple.pnml              : p1 -> p2 (2 markings)
# 2. test1_workflow.pnml      : Workflow pattern (4 markings)
# 3. test2_selfloop.pnml      : Self-loop (3 markings)
# 4. test3_deadlock.pnml      : Network with deadlocks (5 markings)
# 5. test4_cycle.pnml         : Cyclic flow (3 markings)
# 6. test5_choice.pnml        : Non-deterministic choice (3 markings)
# 7. test6_prodcons.pnml      : Producer-Consumer (6 markings)
# 8. test7_philosophers.pnml  : Dining Philosophers (8 markings)

# Usage in TAPAAL:
# ---------------
# - File → Open → Select .pnml file
# - Should load immediately
# - Use Simulator tab to test
# - Tools → Verify Query to analyze

# Usage in Python (Task 1 - Parser):
# ----------------------------------
# These files follow standard PNML format and can be parsed with:
# - xml.etree.ElementTree (Python standard library)
# - lxml
# - pm4py

# Expected Output from Parser:
# ---------------------------
# Example for test1_workflow.pnml:
#   Places: {wait, work, done, free, docu}
#   Initial marking: {wait, free}
#   Transitions: {start, change, end}
#   Arcs: 8 total

# Format Details:
# --------------
# - XML namespace: http://www.pnml.org/version-2009/grammar/pnml
# - Net type: http://www.pnml.org/version-2009/grammar/ptnet
# - Structure: pnml > net > page > (places, transitions, arcs)
# - Initial marking: <initialMarking><text>N</text></initialMarking>
# - Arc type: "normal" (for P/T nets)

# Notes:
# ------
# - All coordinates are positioned for clear visualization
# - Arc IDs follow convention: source_to_target
# - Works with TAPAAL 3.6+, 4.0+
# """)
    
#     print(f"\n📄 Created README: {readme_path}")

# if __name__ == "__main__":
#     main()