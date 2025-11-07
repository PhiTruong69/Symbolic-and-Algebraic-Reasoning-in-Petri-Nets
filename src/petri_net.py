# định nghĩa các class và hàm liên quan đến mạng Petri
# bao gồm các thành phần như Places, Transitions, và Arcs


# Giải thích các khái niệm về mạng Petri
# Mạng Petri là một mô hình toán học được sử dụng để mô tả và phân tích các hệ thống song song,
# phân tán và có tính tương tác cao. 
# Mạng Petri bao gồm ba thành phần chính: Places (nơi), Transitions (chuyển đổi) và Arcs (cung).
# Place được biểu diễn bằng hình tròn và đại diện cho các trạng thái hoặc điều kiện trong hệ thống.
# Transition được biểu diễn bằng hình chữ nhật và đại diện cho các sự kiện hoặc hành động có thể xảy ra.
# Arc là các cung nối giữa Places và Transitions, biểu diễn mối quan hệ và luồng điều khiển trong mạng.
# Token (token) là các đơn vị đại diện cho tài nguyên hoặc thông tin trong mạng Petri.

# Các định nghĩa:
# Marking (đánh dấu): Là sự phân bố của các token trong các place của mạng Petri tại một thời điểm cụ thể.
# Enabled Transition (chuyển đổi có thể bắn): Là một transition có thể thực hiện được nếu tất cả các
# place đầu vào của nó có đủ token theo yêu cầu.
# Firing (bắn): Là quá trình thực hiện một transition, trong đó token được lấy từ các
# place đầu vào và chuyển đến các place đầu ra theo các cung nối.
# input và output map: Là các cấu trúc dữ liệu lưu trữ thông tin
# về các place đầu vào và đầu ra của mỗi transition trong mạng Petri.

# Hình minh họa:
#    (P1) ●  →  [T1]  →  (P2) ○  →  [T2]  →  (P3) ○
#  "Việc mới"    "Bắt đầu"    "Đang làm"    "Hoàn thành"

# Giải thích các hoạt động:
# 1. Khi transition T1 được bắn, token từ place P1 sẽ được chuyển đến place P2, biểu diễn việc bắt đầu một công việc mới.
# 2. Khi transition T2 được bắn, token từ place P2 sẽ được chuyển đến place P3, biểu diễn việc hoàn thành công việc.

# File đầu vào là các file PNML (Petri Net Markup Language), một định dạng XML tiêu chuẩn để mô tả mạng Petri.
# Các file PNML chứa thông tin về các place, transition, arc và đánh dấu ban đầu của mạng Petri.

class Place: # đại diện cho một Place(hình tròn) trong mạng Petri
    
    def __init__(self, pid, name=None, tokens=0):
        self.id=pid                 #thuộc tính id của place
        self.name=name              #thuộc tính name của place
        self.tokens=tokens          #số token ban đầu trong place
    def __repr__(self):
        return f"Place(id={self.id}, name={self.name}, tokens={self.tokens})"
        
class Transition:                   # đại diện cho một Transition(hình chữ nhật) trong mạng Petri
    def __init__(self, tid, name=None):
        self.id=tid                 #thuộc tính id của transition
        self.name=name              #thuộc tính name của transition
    def __repr__(self):
        return f"Transition(id={self.id}, name={self.name})"
class Arc:                          # đại diện cho một Arc(cung nối) trong mạng Petri
    def __init__(self, aid, source, target):
        self.id = aid               # thuộc tính id của cung
        self.source = source        #place hoặc transition
        self.target = target        #place hoặc transition

    def __repr__(self):
          src_name = self.source.name or self.source.id
          tgt_name = self.target.name or self.target.id
          return f"Arc({src_name} → {tgt_name})"
       
       
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
    #===========================task 2=========================
    def buildmap(self): #xây dựng bản đồ input và output cho các transition trong mạng Petri
        self.input= {t.id: [] for t in self.transitions}
        self.output= {t.id: [] for t in self.transitions}
        for arc in self.arcs:
            if isinstance(arc.source, Place) and isinstance(arc.target, Transition):
                 # cung: Place -> Transition (place là input của transition)
                self.input[arc.target.id].append(arc.source.id)
            elif isinstance(arc.source, Transition) and isinstance(arc.target, Place):
                # cung: Transition -> Place (place là output của transition)
                self.output[arc.source.id].append(arc.target.id)
    
    def is_enabled(self, transition, marking): #kiểm tra xem transition có thể bắn được không

        for place_id in self.input[transition.id]:
            if marking.get(place_id, 0) < 1:  # giả sử mỗi cung có trọng số là 1
                return False
        return True
    def fire_transition(self, transition, marking): #bắn transition và cập nhật đánh dấu
        new_marking = marking.copy()
        for place_id in self.input[transition.id]:
            new_marking[place_id] -= 1  # giả sử mỗi cung có trọng số là 1
        for place_id in self.output[transition.id]:
            new_marking[place_id] = new_marking.get(place_id, 0) + 1  # giả sử mỗi cung có trọng số là 1
        return new_marking
    
    def compute_reachable_markings(self):
        self.buildmap()  # đảm bảo input/output map đã sẵn sàng

        visited = set() # tập hợp các đánh dấu đã thăm
        results = []    # danh sách các đánh dấu có thể đạt được

        def marking_to_tuple(mark): #chuyển đánh dấu thành tuple để dễ dàng so sánh và lưu trữ trong tập hợp
            return tuple(mark[p.id] for p in self.places) 

        def dfs(marking): #duyệt đánh dấu bằng đệ quy
            mark_tuple = marking_to_tuple(marking) 
            if mark_tuple in visited:
                return
            visited.add(mark_tuple)
            results.append(marking)

            for t in self.transitions:
                if self.is_enabled(t, marking):
                    new_marking = self.fire_transition(t, marking)
                    dfs(new_marking)

        dfs(self.initial_marking)
        return results