# định nghĩa các class và hàm liên quan đến mạng Petri
# bao gồm các thành phần như Places, Transitions, và Arcs


class Place: # đại diện cho một Place(hình tròn) trong mạng Petri
    def __init__(self, pid, name=None, tokens=0):
        self.id=pid
        self.name=name
        self.tokens=tokens
    def __repr__(self):
        return f"Place(id={self.id}, name={self.name}, tokens={self.tokens})"
        
class Transition: # đại diện cho một Transition(hình chữ nhật) trong mạng Petri
    def __init__(self, tid, name=None):
        self.id=tid
        self.name=name
    def __repr__(self):
        return f"Transition(id={self.id}, name={self.name})"
class Arc:
    def __init__(self, aid, source, target):
        self.id = aid # thuộc tính id của cung
        self.source = source #place hoặc transition
        self.target = target #place hoặc transition

    def __repr__(self):
        return f"Arc({self.source} -> {self.target})"
       
       
class PetriNet:
    def __init__(self, places, transitions, arcs, initial_marking):
        self.places = places
        self.transitions = transitions
        self.arcs = arcs
        self.initial_marking = initial_marking # từ đánh dấu ban đầu

    def __repr__(self):
        return (f"PetriNet("
                f"{len(self.places)} places, "
                f"{len(self.transitions)} transitions, "
                f"{len(self.arcs)} arcs)")