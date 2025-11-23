import xml.etree.ElementTree as ET
from petri_net import PetriNet, Place, Transition, Arc

def load_pnml(file_path):
    """
    Hàm để tải và phân tích cú pháp tệp PNML
    
    FIXED: Xử lý XML namespace đúng cách
    Vẽ bằng tapaal phải xài namespace: http://www.pnml.org/version-2009/grammar/pnml
    """
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Lấy tất cả namespaces trong file
    namespaces = dict([node for _, node in ET.iterparse(file_path, events=['start-ns'])])
    
    # Helper functions để tìm elements với/không namespace
    def find_all_elements(parent, tag):
        """Tìm tất cả elements với tag, xử lý namespace"""
        # Thử không namespace trước
        elements = parent.findall(f'.//{tag}')
        if elements:
            return elements
        
        # Thử với từng namespace
        for ns_prefix, ns_uri in namespaces.items():
            elements = parent.findall(f'.//{{{ns_uri}}}{tag}')
            if elements:
                return elements
        
        return []
    
    def find_element(parent, path):
        """Tìm một element theo path, xử lý namespace"""
        # Thử không namespace
        elem = parent.find(path)
        if elem is not None:
            return elem
        
        # Thử với namespace
        for ns_prefix, ns_uri in namespaces.items():
            # Thay thế mỗi tag trong path với namespace
            parts = path.split('/')
            ns_parts = []
            for part in parts:
                if part and not part.startswith('.'):
                    ns_parts.append(f'{{{ns_uri}}}{part}')
                else:
                    ns_parts.append(part)
            ns_path = '/'.join(ns_parts)
            
            elem = parent.find(ns_path)
            if elem is not None:
                return elem
        
        return None
    
    # Parse places
    places = {}
    for p in find_all_elements(root, 'place'):
        pid = p.get('id')
        if not pid:
            continue
        
        # Tìm name
        name_tag = find_element(p, './name/text')
        name = name_tag.text if name_tag is not None and name_tag.text else pid
        
        # Tìm initial marking
        tokens_tag = find_element(p, './initialMarking/text')
        tokens = 0
        if tokens_tag is not None and tokens_tag.text:
            try:
                tokens = int(tokens_tag.text.strip())
            except ValueError:
                tokens = 0
        
        places[pid] = Place(pid, name, tokens)
    
    # Parse transitions
    transitions = {}
    for t in find_all_elements(root, 'transition'):
        tid = t.get('id')
        if not tid:
            continue
        
        name_tag = find_element(t, './name/text')
        name = name_tag.text if name_tag is not None and name_tag.text else tid
        transitions[tid] = Transition(tid, name)
    
    # Parse arcs
    arcs = []
    for arc in find_all_elements(root, 'arc'):
        aid = arc.get('id')
        src = arc.get('source')
        tgt = arc.get('target')
        
        if not src or not tgt:
            continue
        
        source_obj = places.get(src) or transitions.get(src)
        target_obj = places.get(tgt) or transitions.get(tgt)
        
        if source_obj and target_obj:
            arcs.append(Arc(aid, source_obj, target_obj))
        else:
            print(f" Warning: Arc {aid} references non-existent source or target")
    
    # Build initial marking dictionary
    initial_marking = {pid: p.tokens for pid, p in places.items()}
    
    return PetriNet(list(places.values()), list(transitions.values()), arcs, initial_marking)


if __name__ == "__main__":
    import os
    
    # Test parser với các file mẫu
    test_files = [
        "data/test1_workflow.pnml"

    ]
    
    for pnml_file in test_files:
        if not os.path.exists(pnml_file):
            print(f"  File không tồn tại: {pnml_file}")
            continue
        
        print(f"\n{'='*60}")
        print(f"Testing: {pnml_file}")
        print('='*60)
        
        try:
            petri_net = load_pnml(pnml_file)
            print(f"Load thành công!")
            print(f"   {petri_net}")
            print(f"\nPlaces ({len(petri_net.places)}):")
            for p in petri_net.places:
                print(f"   - {p}")
            print(f"\nTransitions ({len(petri_net.transitions)}):")
            for t in petri_net.transitions:
                print(f"   - {t}")
            print(f"\nArcs ({len(petri_net.arcs)}):")
            for a in petri_net.arcs:
                print(f"   - {a}")
            print(f"\nInitial Marking:")
            for pid, tokens in petri_net.initial_marking.items():
                if tokens > 0:
                    print(f"   - {pid}: {tokens}")
        except Exception as e:
            print(f"Lỗi: {e}")
            import traceback
            traceback.print_exc()