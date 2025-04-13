from extract_triples import extract_triples
import os
import networkx as nx # type: ignore

class Rote:
    def __init__(self):
        pass # maybe this will be used one day
        
    def build_triples(self, unstruct_data_input):
        
        # check if argument is path or string
        if os.path.isfile(unstruct_data_input):
            with open(unstruct_data_input, "r", encoding="utf-8") as f:
                unstruct_data_string = f.read()
        else:
            unstruct_data_string = unstruct_data_input

        print("Creating triples...")
        self.triples = extract_triples(unstruct_data_string)
        print("Triples construction complete!")
            
    def print_triples(self):
        for triple in self.triples:
            print(triple)
            
    def build_nx_graph(self):
        self.nx_graph = nx.MultiDiGraph()  # allows multiple edges and direction (good for KGs)

        for triple in self.triples:
            head = triple["head"]
            relation = triple["relation"]
            tail = triple["tail"]
            self.nx_graph.add_edge(head, tail, label=relation)
    
    def recall(self, node):
        from collections import defaultdict

        relation_map_out = defaultdict(list)  # For node as head
        relation_map_in = defaultdict(list)   # For node as tail

        # Outgoing: node as head
        for neighbor in self.nx_graph[node]:
            for edge_data in self.nx_graph[node][neighbor].values():
                relation = edge_data['label']
                relation_map_out[relation].append(neighbor)

        # Incoming: node as tail
        for other_node in self.nx_graph.nodes:
            if node in self.nx_graph[other_node]:
                for edge_data in self.nx_graph[other_node][node].values():
                    relation = edge_data['label']
                    relation_map_in[relation].append(other_node)

        context_lines = []

        # Format outgoing facts (node as head)
        for relation, tails in relation_map_out.items():
            tail_str = " and ".join(tails)
            context_lines.append(f"{node} {relation} {tail_str}")

        # Format incoming facts (node as tail)
        for relation, heads in relation_map_in.items():
            head_str = ", ".join(heads[:-1])
            if len(heads) > 1:
                head_str += f", and {heads[-1]}"
            else:
                head_str = heads[0]
            context_lines.append(f"{head_str} {relation} {node}")

        return "\n".join(context_lines)

