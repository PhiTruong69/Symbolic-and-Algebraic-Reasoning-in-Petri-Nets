TAPAAL-Compatible PNML Test Cases
====================================

These files are generated with EXACT TAPAAL format.
They should load perfectly in TAPAAL without errors.

Test Cases:
-----------
1. simple.pnml              : p1 -> p2 (2 markings)
2. test1_workflow.pnml      : Workflow pattern (4 markings)
3. test2_selfloop.pnml      : Self-loop (3 markings)
4. test3_deadlock.pnml      : Network with deadlocks (5 markings)
5. test4_cycle.pnml         : Cyclic flow (3 markings)
6. test5_choice.pnml        : Non-deterministic choice (3 markings)
7. test6_prodcons.pnml      : Producer-Consumer (6 markings)
8. test7_philosophers.pnml  : Dining Philosophers (8 markings)

Usage in TAPAAL:
---------------
- File → Open → Select .pnml file
- Should load immediately
- Use Simulator tab to test
- Tools → Verify Query to analyze

Usage in Python (Task 1 - Parser):
----------------------------------
These files follow standard PNML format and can be parsed with:
- xml.etree.ElementTree (Python standard library)
- lxml
- pm4py

Expected Output from Parser:
---------------------------
Example for test1_workflow.pnml:
  Places: {wait, work, done, free, docu}
  Initial marking: {wait, free}
  Transitions: {start, change, end}
  Arcs: 8 total

Format Details:
--------------
- XML namespace: http://www.pnml.org/version-2009/grammar/pnml
- Net type: http://www.pnml.org/version-2009/grammar/ptnet
- Structure: pnml > net > page > (places, transitions, arcs)
- Initial marking: <initialMarking><text>N</text></initialMarking>
- Arc type: "normal" (for P/T nets)

Notes:
------
- All coordinates are positioned for clear visualization
- Arc IDs follow convention: source_to_target
- Works with TAPAAL 3.6+, 4.0+
