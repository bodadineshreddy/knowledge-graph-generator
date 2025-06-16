import asyncio
import yaml
import networkx as nx
from typing import List
from knowledge_graph import IssueKnowledgeGraph, EmbeddingModel
from src.visualizer import GraphVisualizer

class SampleEmbeddingModel(EmbeddingModel):
    async def embed(self, text: str) -> List[float]:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        return model.encode(text).tolist()

def create_networkx_graph(knowledge_graph):
    G = nx.MultiDiGraph()
    
    # Add nodes from all trees with better labeling
    for tree in knowledge_graph.trees:
        for node in tree.nodes:
            # Create more descriptive node labels
            label = f"{node.section}\n{node.content[:30]}..."
            G.add_node((tree.id, node.id), 
                      section=node.section,
                      content=node.content,
                      label=label)
        
        # Add hierarchical edges within each tree
        for from_node, to_node, rel_type in tree.edges:
            G.add_edge((tree.id, from_node), 
                      (tree.id, to_node), 
                      type='hierarchical',
                      relationship=rel_type)
    
    # Add explicit connections between trees
    for from_ticket, to_ticket, rel_type in knowledge_graph.explicit_connections:
        # Add edges between both summary and description nodes for better visibility
        G.add_edge((from_ticket, f"{from_ticket}_summary"),
                   (to_ticket, f"{to_ticket}_summary"),
                   type='explicit',
                   relationship=rel_type)
        if (from_ticket, f"{from_ticket}_description") in G.nodes and \
           (to_ticket, f"{to_ticket}_description") in G.nodes:
            G.add_edge((from_ticket, f"{from_ticket}_description"),
                      (to_ticket, f"{to_ticket}_description"),
                      type='explicit',
                      relationship=rel_type)
    
    # Add implicit connections with better visibility
    for from_ticket, to_ticket, similarity in knowledge_graph.implicit_connections:
        if similarity >= 0.8:
            # Connect both summary and description nodes if they exist
            if (from_ticket, f"{from_ticket}_summary") in G.nodes and \
               (to_ticket, f"{to_ticket}_summary") in G.nodes:
                G.add_edge((from_ticket, f"{from_ticket}_summary"),
                          (to_ticket, f"{to_ticket}_summary"),
                          type='implicit',
                          similarity=similarity)
            if (from_ticket, f"{from_ticket}_description") in G.nodes and \
               (to_ticket, f"{to_ticket}_description") in G.nodes:
                G.add_edge((from_ticket, f"{from_ticket}_description"),
                          (to_ticket, f"{to_ticket}_description"),
                          type='implicit',
                          similarity=similarity)
    
    return G

async def main():
    # Load template
    with open('template.yaml', 'r') as f:
        template = yaml.safe_load(f)

    # Initialize the knowledge graph with embedding model
    graph_builder = IssueKnowledgeGraph(
        embedding_model=SampleEmbeddingModel(),
        threshold=template.get('similarity_threshold', 0.8)
    )

    # Example ticket data
    tickets = [
        {
            "id": "ENT-22970",
            "title": "Issue with login authentication",
            "text": "Users unable to login after recent deployment",
            "Summary": "Authentication failure after deployment",
            "Description": "Multiple users reported inability to login after the latest deployment. Error 500 occurring.",
            "Priority": "High",
            "links": [
                {"ticket_id": "PORT-133061", "relationship": "clone"},
                {"ticket_id": "SEC-789", "relationship": "relates_to"}
            ]
        },
        {
            "id": "PORT-133061",
            "title": "Clone: Login authentication issue",
            "text": "Clone of ENT-22970 for portal team investigation",
            "Summary": "Investigation of login failures",
            "Description": "Portal team investigation of authentication failures reported in ENT-22970",
            "Priority": "High",
            "links": [
                {"ticket_id": "SEC-789", "relationship": "relates_to"}
            ]
        },
        {
            "id": "ENT-1744",
            "title": "Login system performance analysis",
            "text": "Analysis of login system performance",
            "Summary": "Login performance investigation",
            "Description": "Comprehensive analysis of login system performance and bottlenecks",
            "Priority": "Medium",
            "links": [
                {"ticket_id": "PERF-456", "relationship": "blocks"}
            ]
        },
        {
            "id": "SEC-789",
            "title": "Security review for authentication system",
            "Summary": "Security audit of login system",
            "Description": "Conducting security review of the authentication system following recent failures. Need to verify all security protocols and access controls.",
            "Priority": "High",
            "links": [
                {"ticket_id": "SEC-790", "relationship": "blocks"}
            ]
        },
        {
            "id": "SEC-790",
            "title": "Implement 2FA for login system",
            "Summary": "Add two-factor authentication",
            "Description": "Implementation of two-factor authentication to enhance security of the login system. This is a requirement from the security audit.",
            "Priority": "High",
            "links": [
                {"ticket_id": "PORT-133061", "relationship": "relates_to"}
            ]
        },
        {
            "id": "PERF-456",
            "title": "Optimize database queries for login",
            "Summary": "Login query optimization",
            "Description": "Optimize database queries in the login flow to improve performance. Current queries are causing slowdown during peak hours.",
            "Priority": "Medium",
            "links": [
                {"ticket_id": "ENT-1744", "relationship": "relates_to"}
            ]
        },
        {
            "id": "UI-234",
            "title": "Improve login page UX",
            "Summary": "Login page UX improvements",
            "Description": "Enhance user experience on the login page. Add better error messages and loading states.",
            "Priority": "Low",
            "links": [
                {"ticket_id": "UI-235", "relationship": "blocks"}
            ]
        },
        {
            "id": "UI-235",
            "title": "Implement new login page design",
            "Summary": "New login page implementation",
            "Description": "Implement the new design for login page including responsive layout and improved accessibility features.",
            "Priority": "Low",
            "links": [
                {"ticket_id": "UI-234", "relationship": "relates_to"}
            ]
        },
        {
            "id": "INFRA-567",
            "title": "Load balancer configuration for auth service",
            "Summary": "Auth service load balancing",
            "Description": "Configure load balancer for the authentication service to handle increased traffic and improve reliability.",
            "Priority": "Medium",
            "links": [
                {"ticket_id": "PERF-456", "relationship": "relates_to"},
                {"ticket_id": "ENT-1744", "relationship": "relates_to"}
            ]
        },
        {
            "id": "DOC-890",
            "title": "Update authentication system documentation",
            "Summary": "Update auth system docs",
            "Description": "Update technical documentation for the authentication system including new security measures and performance optimizations.",
            "Priority": "Low",
            "links": [
                {"ticket_id": "SEC-790", "relationship": "relates_to"},
                {"ticket_id": "PERF-456", "relationship": "relates_to"}
            ]
        }
    ]

    # Build knowledge graph
    knowledge_graph = await graph_builder.build_graph(tickets, template)
    
    # Convert to NetworkX graph
    nx_graph = create_networkx_graph(knowledge_graph)

    # Initialize visualizer with optimized settings for clarity
    visualizer = GraphVisualizer({
        'node_size': 2000,          # Larger nodes for better text visibility
        'font_size': 9,             # Slightly larger font
        'width': 20,                # Wider figure
        'height': 15,               # Taller figure
        'dpi': 300,                 # High resolution
        'edge_width': 2,            # Thicker edges
        'min_edge_width': 1.5,      # Minimum edge width
        'max_edge_width': 4,        # Maximum edge width for important relationships
        'node_color': {
            'Summary': '#E6F3FF',    # Light blue
            'Description': '#E6FFE6', # Light green
            'Priority': '#FFE6E6',    # Light red
            'Code': '#FFFFD4',       # Light yellow
            'default': '#F5F5F5'     # Light gray
        },
        'edge_color': {
            'hierarchical': '#666666', # Dark gray
            'explicit': '#FF4444',     # Bright red
            'implicit': '#4444FF',     # Bright blue
            'has_code': '#AA44FF',     # Purple
            'default': '#999999'       # Medium gray
        }
    })

    # Generate visualizations with improved layout
    print("\nGenerating visualizations...")
    
    # Draw complete knowledge graph with better layout
    visualizer.draw_knowledge_graph(
        nx_graph,
        title="Jira Tickets Knowledge Graph",
        output_path="knowledge_graph_spring.png",
        layout='kamada_kawai'  # Using Kamada-Kawai layout for better node distribution
    )
    
    print("\nVisualization files generated:")
    print("- knowledge_graph_spring.png")

if __name__ == "__main__":
    asyncio.run(main())