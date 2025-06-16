from typing import Dict, Any, List
from dataclasses import dataclass
from .ticket_parser import TicketSection

@dataclass
class ValidationError:
    field: str
    message: str
    severity: str  # 'error' or 'warning'

class TicketValidator:
    def __init__(self, template: Dict[str, Any]):
        self.template = template
        self.required_sections = [
            section['name'] for section in template['sections']
            if section.get('required', False)
        ]
    
    def validate_ticket(self, ticket: Dict[str, Any]) -> List[ValidationError]:
        """Validate a ticket against the template requirements"""
        errors = []
        
        # Check required fields
        for section_name in self.required_sections:
            if section_name not in ticket:
                errors.append(ValidationError(
                    field=section_name,
                    message=f"Required section '{section_name}' is missing",
                    severity='error'
                ))
        
        # Validate section content types
        for section in self.template['sections']:
            section_name = section['name']
            if section_name in ticket:
                content = ticket[section_name]
                
                # Validate enum values
                if section['type'] == 'enum' and content not in section.get('values', []):
                    errors.append(ValidationError(
                        field=section_name,
                        message=f"Invalid value for enum field '{section_name}'. "
                               f"Must be one of: {section.get('values')}",
                        severity='error'
                    ))
        
        return errors

class GraphValidator:
    def __init__(self, template: Dict[str, Any]):
        self.template = template
        self.valid_relationships = [
            rel['name'] for rel in template.get('relationships', [])
        ]
    
    def validate_relationship(self, source_id: str, target_id: str, rel_type: str) -> List[ValidationError]:
        """Validate a relationship between two tickets"""
        errors = []
        
        if rel_type not in self.valid_relationships:
            errors.append(ValidationError(
                field='relationship',
                message=f"Invalid relationship type '{rel_type}'. "
                       f"Must be one of: {self.valid_relationships}",
                severity='error'
            ))
        
        # Check if relationship is bidirectional
        rel_config = next(
            (rel for rel in self.template.get('relationships', [])
             if rel['name'] == rel_type),
            None
        )
        
        if rel_config and not rel_config.get('bidirectional', False):
            # Add warning for potentially incorrect direction
            errors.append(ValidationError(
                field='relationship_direction',
                message=f"Relationship '{rel_type}' is unidirectional. "
                       f"Please verify direction from {source_id} to {target_id}",
                severity='warning'
            ))
        
        return errors

    def validate_graph_structure(self, nodes: List[str], edges: List[tuple]) -> List[ValidationError]:
        """Validate the overall graph structure"""
        errors = []
        
        # Check for cycles in hierarchical relationships
        try:
            import networkx as nx
            G = nx.DiGraph()
            G.add_edges_from(edges)
            cycles = list(nx.simple_cycles(G))
            if cycles:
                errors.append(ValidationError(
                    field='graph_structure',
                    message=f"Detected cycles in hierarchical relationships: {cycles}",
                    severity='error'
                ))
        except ImportError:
            errors.append(ValidationError(
                field='dependencies',
                message="NetworkX library required for graph validation",
                severity='error'
            ))
        
        return errors