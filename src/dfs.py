from petri_net import PetriNet, Transition, Place, Arc
from parser import load_pnml
from collections import deque


if __name__ == "__main__":
    pnml_file = "data/model0.pnml"  # đường dẫn đến tệp PNML
    petri_net = load_pnml(pnml_file) # tải mạng Petri từ tệp PNML
    reachable_markings = petri_net.compute_reachable_markings()
    print(f"Total reachable markings: {len(reachable_markings)}")
    for i, marking in enumerate(reachable_markings):
        print(f"Marking {i}: {marking}")