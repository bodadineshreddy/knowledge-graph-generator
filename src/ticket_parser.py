from dataclasses import dataclass
from typing import Dict, Any, List, Optional

@dataclass
class TicketSection:
    name: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class TicketParser:
    def __init__(self, template: Dict[str, Any]):
        self.template = template
        self.sections = [section['name'] for section in template['sections']]
        self.required_sections = [
            section['name'] for section in template['sections'] 
            if section.get('required', False)
        ]
    
    def validate_section(self, section_name: str, content: str) -> bool:
        """Validate section content against template rules"""
        section_config = next(
            (s for s in self.template['sections'] if s['name'] == section_name),
            None
        )
        if not section_config:
            return False
            
        if section_config['type'] == 'enum':
            return content in section_config.get('values', [])
        return True
    
    def parse_ticket(self, ticket: Dict[str, Any]) -> List[TicketSection]:
        """Parse a ticket into sections according to template"""
        sections = []
        
        # Parse predefined sections
        for section_name in self.sections:
            if section_name in ticket:
                content = ticket[section_name]
                if self.validate_section(section_name, content):
                    sections.append(TicketSection(
                        name=section_name,
                        content=content,
                        metadata={'source': 'predefined'}
                    ))
        
        # Parse remaining content using text analysis
        if 'text' in ticket:
            remaining_sections = [
                s for s in self.required_sections 
                if s not in [section.name for section in sections]
            ]
            for section_name in remaining_sections:
                # Here we would typically use LLM or other text analysis
                # For now, just create an empty section
                sections.append(TicketSection(
                    name=section_name,
                    content='',
                    metadata={'source': 'parsed', 'confidence': 0.0}
                ))
        
        return sections