import xml.etree.ElementTree as ET
from petri_net import PetriNet, Place, Transition, Arc

def load_pnml(file_path): # hàm để tải và phân tích cú pháp tệp PNML
    tree = ET.parse(file_path)
    root = tree.getroot()

    places = {}
    for p in root.findall('.//place'):
        pid = p.get('id')
        name_tag = p.find('./name/text')
        name = name_tag.text if name_tag is not None else pid

        tokens_tag = p.find('./initialMarking/text')
        tokens = int(tokens_tag.text) if tokens_tag is not None else 0
        
        places[pid] = Place(pid, name, tokens)

    transitions = {}
    for t in root.findall('.//transition'):
        tid = t.get('id')
        name_tag = t.find('./name/text')
        name = name_tag.text if name_tag is not None else tid
        transitions[tid] = Transition(tid, name)

    arcs = []
    for arc in root.findall('.//arc'):
        aid = arc.get('id')
        src = arc.get('source')
        tgt = arc.get('target')
        arcs.append(Arc(aid, places.get(src) or transitions.get(src),
                             places.get(tgt) or transitions.get(tgt)))

    initial_marking = {pid: p.tokens for pid, p in places.items()}
    return PetriNet(list(places.values()), list(transitions.values()), arcs, initial_marking)



if __name__ == "__main__":
    pnml_file = "data/simple.pnml"  # đường dẫn đến tệp PNML
    petri_net = load_pnml(pnml_file)
    print(petri_net)
    print("Places:", petri_net.places)
    print("Transitions:", petri_net.transitions)
    print("Arcs:", petri_net.arcs)