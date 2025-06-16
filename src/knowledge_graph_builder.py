from typing import List, Dict, Any
import yaml
import networkx as nx
from .ticket_parser import TicketParser
from .graph_generator import GraphGenerator

class KnowledgeGraphBuilder:
    def __init__(self, template_path: str, similarity_threshold: float = 0.8):
        with open(template_path, 'r') as f:
            self.template = yaml.safe_load(f)
        
        self.parser = TicketParser(self.template)
        self.graph_generator = GraphGenerator(similarity_threshold)
    
    def build_knowledge_graph(self, tickets: List[Dict[str, Any]]) -> nx.MultiDiGraph:
        """Build complete knowledge graph from ticket data"""
        # Parse all tickets
        parsed_tickets = []
        for ticket in tickets:
            sections = self.parser.parse_ticket(ticket)
            parsed_tickets.append((ticket['id'], sections))
        
        # Create intra-ticket trees
        intra_ticket_trees = [
            self.graph_generator.create_intra_ticket_tree(ticket_id, sections)
            for ticket_id, sections in parsed_tickets
        ]
        
        # Create inter-ticket graph
        inter_ticket_graph = self.graph_generator.create_inter_ticket_graph(tickets)
        
        # Combine into final knowledge graph
        return self.graph_generator.combine_graphs(intra_ticket_trees, inter_ticket_graph)

def visualize_graph(graph: nx.MultiDiGraph, output_path: str = None):
    """Visualize the knowledge graph using networkx"""
    import matplotlib.pyplot as plt
    
    # Create position layout
    pos = nx.spring_layout(graph, k=1, iterations=50)
    
    # Draw nodes
    nx.draw_networkx_nodes(graph, pos, node_color='lightblue', 
                          node_size=1000, alpha=0.6)
    
    # Draw edges with different colors for different types
    edge_colors = []
    for _, _, data in graph.edges(data=True):
        if data.get('type') == 'explicit':
            edge_colors.append('red')
        elif data.get('type') == 'implicit':
            edge_colors.append('blue')
        else:
            edge_colors.append('black')
    
    nx.draw_networkx_edges(graph, pos, edge_color=edge_colors, alpha=0.5)
    
    # Draw labels
    labels = {node: f"{node[0]}\n{node[1]}" if isinstance(node, tuple) 
             else node for node in graph.nodes()}
    nx.draw_networkx_labels(graph, pos, labels, font_size=8)
    
    plt.title("Knowledge Graph Visualization")
    plt.axis('off')
    
    if output_path:
        plt.savefig(output_path, format='png', dpi=300, bbox_inches='tight')
    else:
        plt.show()