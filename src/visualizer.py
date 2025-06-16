import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional
import numpy as np

class GraphVisualizer:
    def __init__(self, style_config: Optional[Dict[str, Any]] = None):
        self.default_style = {
            'node_size': 1000,
            'node_color': {
                'Summary': 'lightblue',
                'Description': 'lightgreen',
                'Code': 'lightyellow',
                'default': 'lightgray'
            },
            'edge_color': {
                'hierarchical': 'gray',
                'explicit': 'red',
                'implicit': 'blue',
                'has_code': 'purple',
                'default': 'black'
            },
            'font_size': 8,
            'width': 12,
            'height': 8,
            'dpi': 300,
            'edge_width': 1.5,
            'min_edge_width': 1,
            'max_edge_width': 3
        }
        self.style = {**self.default_style, **(style_config or {})}

    def draw_tree(self, tree: nx.DiGraph, title: str = "", output_path: Optional[str] = None):
        """Draw a single ticket tree using hierarchical layout"""
        plt.figure(figsize=(self.style['width'], self.style['height']), dpi=self.style['dpi'])
        
        # Use hierarchical layout for better tree visualization
        pos = nx.spring_layout(tree, k=2, iterations=50)
        
        # Draw nodes with section-based colors
        for section in set(nx.get_node_attributes(tree, 'section').values()):
            section_nodes = [n for n, d in tree.nodes(data=True) 
                           if d.get('section') == section]
            if section_nodes:
                nx.draw_networkx_nodes(
                    tree, pos,
                    nodelist=section_nodes,
                    node_color=self.style['node_color'].get(section, 
                                                          self.style['node_color']['default']),
                    node_size=self.style['node_size']
                )
        
        # Draw edges with improved styling
        nx.draw_networkx_edges(
            tree, pos,
            edge_color=self.style['edge_color']['hierarchical'],
            width=self.style['edge_width'],
            arrows=True,
            arrowsize=20
        )
        
        # Draw labels with improved formatting
        labels = {
            node: f"{data.get('section', '')}\n{str(node[1])[:20]}..."
            for node, data in tree.nodes(data=True)
        }
        nx.draw_networkx_labels(
            tree, pos,
            labels=labels,
            font_size=self.style['font_size'],
            font_weight='bold'
        )
        
        plt.title(title)
        plt.axis('off')
        
        if output_path:
            plt.savefig(output_path, bbox_inches='tight', dpi=self.style['dpi'])
            plt.close()
        else:
            plt.show()

    def draw_knowledge_graph(
        self,
        graph: nx.MultiDiGraph,
        title: str = "",
        output_path: Optional[str] = None,
        layout: str = 'spring'
    ):
        """Draw the complete knowledge graph with all relationships"""
        plt.figure(figsize=(self.style['width'], self.style['height']), dpi=self.style['dpi'])
        
        # Choose layout algorithm
        if layout == 'spring':
            pos = nx.spring_layout(graph, k=3, iterations=100)  # Increased k and iterations
        elif layout == 'circular':
            pos = nx.circular_layout(graph)
        elif layout == 'spectral':
            try:
                pos = nx.spectral_layout(graph)
            except:
                pos = nx.spring_layout(graph, k=3, iterations=100)
        else:
            pos = nx.kamada_kawai_layout(graph)

        # Draw nodes with section-based colors and better spacing
        node_sections = nx.get_node_attributes(graph, 'section')
        for section in set(node_sections.values()):
            section_nodes = [n for n, d in graph.nodes(data=True) 
                           if d.get('section') == section]
            if section_nodes:
                nx.draw_networkx_nodes(
                    graph, pos,
                    nodelist=section_nodes,
                    node_color=self.style['node_color'].get(section, 
                                                          self.style['node_color']['default']),
                    node_size=self.style['node_size'],
                    alpha=0.9
                )

        # Draw edges by type with better visibility
        edge_types = [
            ('hierarchical', '#808080', 0.7),  # Gray with medium opacity
            ('explicit', '#FF0000', 0.9),      # Red with high opacity
            ('implicit', '#0000FF', 0.6),      # Blue with lower opacity
            ('has_code', '#800080', 0.8)       # Purple with high-medium opacity
        ]
        
        for edge_type, color, alpha in edge_types:
            edges = [(u, v) for (u, v, d) in graph.edges(data=True)
                    if d.get('type', '') == edge_type]
            if edges:
                # Calculate edge widths based on relationship type and weights
                widths = []
                for (u, v) in edges:
                    edge_data = graph.get_edge_data(u, v)
                    if edge_type == 'implicit':
                        # Use similarity score for implicit edges
                        width = self.style['min_edge_width'] + (
                            float(edge_data[0].get('similarity', 0.8)) * 
                            (self.style['max_edge_width'] - self.style['min_edge_width'])
                        )
                    else:
                        # Use default width for other edge types
                        width = self.style['edge_width']
                    widths.append(width)
                
                nx.draw_networkx_edges(
                    graph, pos,
                    edgelist=edges,
                    edge_color=color,
                    width=widths,
                    arrows=True,
                    arrowsize=20,
                    alpha=alpha,
                    connectionstyle="arc3,rad=0.2"  # Curved edges for better visibility
                )

        # Draw labels with improved formatting
        labels = {}
        for node, data in graph.nodes(data=True):
            if isinstance(node, tuple):
                # Format the label to include ticket ID and truncated content
                content = data.get('content', '')[:30]
                section = data.get('section', '')
                labels[node] = f"{node[0]}\n{section}\n{content}..."
            else:
                labels[node] = str(node)

        nx.draw_networkx_labels(
            graph, pos,
            labels=labels,
            font_size=self.style['font_size'],
            font_weight='bold',
            font_color='black',
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
        )

        # Add legend
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], color=color, label=edge_type.title(), alpha=alpha,
                   linewidth=self.style['edge_width'])
            for edge_type, color, alpha in edge_types
        ]
        plt.legend(
            handles=legend_elements,
            loc='center left',
            bbox_to_anchor=(1, 0.5),
            title='Relationship Types',
            frameon=True,
            facecolor='white',
            edgecolor='black'
        )

        plt.title(title, pad=20, fontsize=14, fontweight='bold')
        plt.axis('off')
        
        if output_path:
            plt.savefig(output_path, bbox_inches='tight', dpi=self.style['dpi'])
            plt.close()
        else:
            plt.show()

    @staticmethod
    def export_graphml(graph: nx.MultiDiGraph, output_path: str):
        """Export the graph in GraphML format for external tools"""
        # Convert node tuples to strings for GraphML compatibility
        G = nx.MultiDiGraph()
        
        # Add nodes with converted IDs and all attributes
        for node in graph.nodes(data=True):
            node_id = node[0]
            if isinstance(node_id, tuple):
                node_id = f"{node_id[0]}_{node_id[1]}"
            
            # Convert all attributes to strings for GraphML compatibility
            attrs = {
                k: str(v) if not isinstance(v, (str, int, float, bool)) else v
                for k, v in node[1].items()
            }
            G.add_node(node_id, **attrs)
        
        # Add edges with converted IDs and all attributes
        for u, v, data in graph.edges(data=True):
            u_id = f"{u[0]}_{u[1]}" if isinstance(u, tuple) else u
            v_id = f"{v[0]}_{v[1]}" if isinstance(v, tuple) else v
            
            # Convert all attributes to strings for GraphML compatibility
            attrs = {
                k: str(v) if not isinstance(v, (str, int, float, bool)) else v
                for k, v in data.items()
            }
            G.add_edge(u_id, v_id, **attrs)
        
        # Write to file with all attributes preserved
        nx.write_graphml(G, output_path)