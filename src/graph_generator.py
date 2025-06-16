import networkx as nx
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Tuple
from .ticket_parser import TicketSection

class GraphGenerator:
    def __init__(self, similarity_threshold: float = 0.8):
        self.similarity_threshold = similarity_threshold
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def create_intra_ticket_tree(self, ticket_id: str, sections: List[TicketSection]) -> nx.DiGraph:
        """Create a tree structure for a single ticket"""
        tree = nx.DiGraph()
        
        # Add nodes for each section
        for section in sections:
            tree.add_node(
                (ticket_id, section.name), 
                content=section.content,
                metadata=section.metadata
            )
            
        # Add hierarchical edges based on section order
        for i in range(len(sections) - 1):
            tree.add_edge(
                (ticket_id, sections[i].name),
                (ticket_id, sections[i + 1].name)
            )
            
        return tree
    
    def create_inter_ticket_graph(self, tickets: List[Dict[str, Any]]) -> nx.Graph:
        """Create graph of connections between tickets"""
        graph = nx.Graph()
        
        # Generate embeddings for all ticket titles
        embeddings = {
            ticket['id']: self.model.encode(ticket['title'])
            for ticket in tickets
        }
        
        # Add nodes for each ticket
        for ticket in tickets:
            graph.add_node(ticket['id'], title=ticket['title'])
            
        # Add explicit connections (if any exist in ticket data)
        for ticket in tickets:
            if 'links' in ticket:
                for link in ticket['links']:
                    graph.add_edge(
                        ticket['id'],
                        link['target_id'],
                        type='explicit',
                        relationship=link['type']
                    )
        
        # Add implicit connections based on similarity
        for i, ticket_i in enumerate(tickets):
            for j, ticket_j in enumerate(tickets[i + 1:], i + 1):
                similarity = cosine_similarity(
                    [embeddings[ticket_i['id']]], 
                    [embeddings[ticket_j['id']]]
                )[0][0]
                
                if similarity >= self.similarity_threshold:
                    graph.add_edge(
                        ticket_i['id'],
                        ticket_j['id'],
                        type='implicit',
                        weight=similarity
                    )
        
        return graph
    
    def combine_graphs(
        self, 
        intra_ticket_trees: List[nx.DiGraph], 
        inter_ticket_graph: nx.Graph
    ) -> nx.MultiDiGraph:
        """Combine intra-ticket trees and inter-ticket graph into final knowledge graph"""
        combined = nx.MultiDiGraph()
        
        # Add all intra-ticket nodes and edges
        for tree in intra_ticket_trees:
            combined.add_nodes_from(tree.nodes(data=True))
            combined.add_edges_from(tree.edges(data=True))
        
        # Add inter-ticket edges
        for u, v, data in inter_ticket_graph.edges(data=True):
            # Connect root nodes of the respective trees
            combined.add_edge(
                (u, 'Summary'), 
                (v, 'Summary'),
                **data
            )
        
        return combined