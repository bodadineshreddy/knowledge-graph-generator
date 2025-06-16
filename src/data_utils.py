import json
import csv
from typing import List, Dict, Any
import pandas as pd
import networkx as nx
from pathlib import Path

class DataIO:
    @staticmethod
    def load_jira_json(file_path: str) -> List[Dict[str, Any]]:
        """Load Jira tickets from a JSON file"""
        with open(file_path, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def save_jira_json(tickets: List[Dict[str, Any]], file_path: str):
        """Save Jira tickets to a JSON file"""
        with open(file_path, 'w') as f:
            json.dump(tickets, f, indent=2)
    
    @staticmethod
    def load_jira_csv(file_path: str) -> List[Dict[str, Any]]:
        """Load Jira tickets from a CSV file"""
        df = pd.read_csv(file_path)
        return df.to_dict('records')
    
    @staticmethod
    def save_jira_csv(tickets: List[Dict[str, Any]], file_path: str):
        """Save Jira tickets to a CSV file"""
        df = pd.DataFrame(tickets)
        df.to_csv(file_path, index=False)
    
    @staticmethod
    def export_graph_stats(graph, output_path: str):
        """Export graph statistics to a JSON file"""
        stats = {
            'num_nodes': graph.number_of_nodes(),
            'num_edges': graph.number_of_edges(),
            'density': nx.density(graph),
            'avg_degree': sum(dict(graph.degree()).values()) / graph.number_of_nodes(),
            'connected_components': list(nx.connected_components(graph.to_undirected())),
            'degree_histogram': nx.degree_histogram(graph)
        }
        
        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=2, default=list)

class JiraAPIClient:
    def __init__(self, base_url: str, auth_token: str = None):
        self.base_url = base_url
        self.auth_token = auth_token
        
    async def fetch_tickets(self, jql_query: str) -> List[Dict[str, Any]]:
        """Fetch tickets from Jira API using JQL query"""
        # This is a placeholder - implement actual Jira API integration
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': f'Bearer {self.auth_token}',
                'Content-Type': 'application/json'
            }
            
            async with session.get(
                f'{self.base_url}/rest/api/2/search',
                params={'jql': jql_query},
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('issues', [])
                else:
                    raise Exception(f"Failed to fetch tickets: {response.status}")
    
    def transform_jira_response(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform Jira API response to our ticket format"""
        transformed = []
        for issue in issues:
            ticket = {
                'id': issue['key'],
                'title': issue['fields']['summary'],
                'text': issue['fields']['description'] or '',
                'Summary': issue['fields']['summary'],
                'Description': issue['fields']['description'] or '',
                'Priority': issue['fields']['priority']['name'],
                'links': []
            }
            
            # Transform issue links
            if 'issuelinks' in issue['fields']:
                for link in issue['fields']['issuelinks']:
                    if 'outwardIssue' in link:
                        ticket['links'].append({
                            'target_id': link['outwardIssue']['key'],
                            'type': link['type']['outward']
                        })
            
            transformed.append(ticket)
        
        return transformed