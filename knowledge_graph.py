from typing import List, Tuple, Dict, Any
import numpy as np
from dataclasses import dataclass
from abc import ABC, abstractmethod
from src.logging_utils import GraphLogger

@dataclass
class TicketNode:
    id: str
    section: str
    content: str

@dataclass
class TicketTree:
    id: str
    nodes: List[TicketNode]
    edges: List[Tuple[str, str, str]]  # (fromNode, toNode, relationshipType)

@dataclass
class KnowledgeGraph:
    trees: List[TicketTree]
    explicit_connections: List[Tuple[str, str, str]]  # (fromTicket, toTicket, relationshipType)
    implicit_connections: List[Tuple[str, str, float]]  # (fromTicket, toTicket, similarityScore)

class EmbeddingModel(ABC):
    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        pass

class IssueKnowledgeGraph:
    def __init__(self, embedding_model: EmbeddingModel, threshold: float = 0.7):
        if not isinstance(embedding_model, EmbeddingModel):
            raise ValueError("embedding_model must be an instance of EmbeddingModel")
        if not 0 <= threshold <= 1:
            raise ValueError("threshold must be between 0 and 1")
        
        self.embedding_model = embedding_model
        self.similarity_threshold = threshold
        self.logger = GraphLogger()

    async def parse_ticket_with_rules(self, ticket: Dict) -> List[TicketNode]:
        """Implement rule-based parsing logic with improved validation"""
        if not isinstance(ticket, dict):
            raise ValueError("ticket must be a dictionary")
        if 'id' not in ticket:
            raise ValueError("ticket must have an 'id' field")

        nodes = []
        
        # Handle Summary field - try multiple possible field names
        summary_content = ticket.get('Summary') or ticket.get('summary') or ticket.get('title', '')
        if summary_content:
            nodes.append(TicketNode(
                id=f"{ticket['id']}_summary",
                section="Summary",
                content=str(summary_content)
            ))
        
        # Handle Description field - try multiple possible field names
        description_content = ticket.get('Description') or ticket.get('description') or ticket.get('text', '')
        if description_content:
            nodes.append(TicketNode(
                id=f"{ticket['id']}_description",
                section="Description",
                content=str(description_content)
            ))
        
        # Handle Priority field
        priority = ticket.get('Priority') or ticket.get('priority', '')
        if priority:
            nodes.append(TicketNode(
                id=f"{ticket['id']}_priority",
                section="Priority",
                content=str(priority)
            ))
        
        # Extract code sections if present in description
        if description_content:
            code_sections = self._extract_code_sections(str(description_content))
            for i, code in enumerate(code_sections):
                nodes.append(TicketNode(
                    id=f"{ticket['id']}_code_{i}",
                    section="Code",
                    content=code
                ))
        
        return nodes

    def _extract_code_sections(self, text: str) -> List[str]:
        """Enhanced code section extraction supporting multiple formats"""
        code_sections = []
        lines = text.split('\n')
        in_code_block = False
        current_block = []
        code_block_markers = ['```', '~~~', '    ']  # Support multiple code block styles
        
        for line in lines:
            # Check for markdown style code blocks
            if any(line.strip().startswith(marker) for marker in code_block_markers[:2]):
                if in_code_block:
                    if current_block:
                        code_sections.append('\n'.join(current_block))
                        current_block = []
                in_code_block = not in_code_block
                continue
            
            # Check for indented code blocks
            if not in_code_block and line.startswith('    '):
                in_code_block = True
            elif in_code_block and not line.startswith('    ') and line.strip():
                if current_block:
                    code_sections.append('\n'.join(current_block))
                    current_block = []
                in_code_block = False
            
            if in_code_block:
                # Remove code block markers and language specifiers
                clean_line = line.strip()
                if not any(clean_line.startswith(marker) for marker in code_block_markers):
                    current_block.append(line.strip())
        
        # Add any remaining code block
        if current_block:
            code_sections.append('\n'.join(current_block))
        
        return code_sections

    async def parse_ticket_with_llm(self, ticket: Dict, template: Dict) -> List[TicketNode]:
        """Implement LLM-based parsing logic"""
        nodes = []
        # This is where you would implement the LLM parsing logic
        # The implementation depends on your LLM integration
        # Example structure:
        try:
            # Extract sections based on template
            for section in template.get('sections', []):
                section_name = section['name']
                section_content = await self._extract_section_with_llm(ticket, section)
                if section_content:
                    nodes.append(TicketNode(
                        id=f"{ticket['id']}_{section_name.lower()}",
                        section=section_name,
                        content=section_content
                    ))
        except Exception as e:
            print(f"Error in LLM parsing: {str(e)}")
        
        return nodes

    async def _extract_section_with_llm(self, ticket: Dict, section: Dict) -> str:
        """Helper method for LLM-based section extraction"""
        # Implement your LLM logic here
        return ""

    def construct_ticket_tree(self, nodes: List[TicketNode]) -> TicketTree:
        """Construct tree structure from nodes with improved validation"""
        if not nodes:
            return TicketTree(id="", nodes=[], edges=[])
        
        # Find the root node (prefer Summary, fallback to first node)
        root_node = next(
            (node for node in nodes if node.section == "Summary"),
            nodes[0]
        )
        ticket_id = root_node.id.split('_')[0]
        edges = []
        
        # Create hierarchical structure
        for node in nodes:
            if node != root_node:
                edges.append((root_node.id, node.id, "contains"))
            
            # Add relationships between specific sections
            if node.section == "Code":
                # Connect code sections to their parent description
                for potential_parent in nodes:
                    if potential_parent.section == "Description":
                        edges.append((potential_parent.id, node.id, "has_code"))
                        break
        
        return TicketTree(
            id=ticket_id,
            nodes=nodes,
            edges=edges
        )

    async def find_implicit_connections(self, trees: List[TicketTree]) -> List[Tuple[str, str, float]]:
        """Find implicit connections between tickets based on similarity"""
        connections = []
        
        for i, tree1 in enumerate(trees):
            for tree2 in trees[i+1:]:
                similarity = await self.calculate_similarity(tree1, tree2)
                if similarity >= self.similarity_threshold:
                    connections.append((tree1.id, tree2.id, similarity))
        
        return connections

    async def calculate_similarity(self, tree1: TicketTree, tree2: TicketTree) -> float:
        """Calculate similarity between two tickets"""
        try:
            # Get ticket titles
            title1 = self.get_ticket_title(tree1)
            title2 = self.get_ticket_title(tree2)
            
            # Calculate embeddings
            embedding1 = await self.embedding_model.embed(title1)
            embedding2 = await self.embedding_model.embed(title2)
            
            return self.cosine_similarity(embedding1, embedding2)
        except Exception as e:
            print(f"Error calculating similarity: {str(e)}")
            return 0.0

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

    def find_explicit_connections(self, tickets: List[Dict]) -> List[Tuple[str, str, str]]:
        """Find explicit connections from ticket metadata"""
        connections = []
        
        for ticket in tickets:
            # Check for linked tickets
            if 'links' in ticket:
                for link in ticket['links']:
                    connections.append((
                        ticket['id'],
                        link['ticket_id'],
                        link['relationship']  # e.g., "clones", "blocks", "relates_to"
                    ))
        
        return connections

    async def build_graph(self, tickets: List[Dict], template: Dict) -> KnowledgeGraph:
        """Build the complete knowledge graph with logging"""
        trees = []
        
        # Process each ticket
        for ticket in tickets:
            try:
                rule_based_nodes = await self.parse_ticket_with_rules(ticket)
                llm_based_nodes = await self.parse_ticket_with_llm(ticket, template)
                all_nodes = rule_based_nodes + llm_based_nodes
                
                tree = self.construct_ticket_tree(all_nodes)
                trees.append(tree)
                
                # Log ticket processing
                self.logger.log_ticket_processing(
                    ticket_id=tree.id,
                    nodes_count=len(tree.nodes),
                    edges_count=len(tree.edges)
                )
            except Exception as e:
                self.logger.log_error(
                    context="ticket_processing",
                    error=e,
                    data={"ticket_id": ticket.get("id", "unknown")}
                )

        # Find explicit connections
        explicit_connections = self.find_explicit_connections(tickets)
        for from_id, to_id, rel_type in explicit_connections:
            self.logger.log_connection(
                from_id=from_id,
                to_id=to_id,
                connection_type="explicit",
                metadata={"relationship": rel_type}
            )

        # Generate implicit connections
        implicit_connections = await self.find_implicit_connections(trees)
        for from_id, to_id, similarity in implicit_connections:
            self.logger.log_connection(
                from_id=from_id,
                to_id=to_id,
                connection_type="implicit",
                metadata={"similarity": similarity}
            )

        return KnowledgeGraph(
            trees=trees,
            explicit_connections=explicit_connections,
            implicit_connections=implicit_connections
        )

    def get_ticket_title(self, tree: TicketTree) -> str:
        """Extract title from ticket tree"""
        for node in tree.nodes:
            if node.section == "Summary":
                return node.content
            elif node.section == "Description":
                return node.content[:50]  # Use description start if no summary
        return tree.id  # Fallback to ID if no content found