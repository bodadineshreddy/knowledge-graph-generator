import click
import yaml
from pathlib import Path
from typing import Optional
from .knowledge_graph_builder import KnowledgeGraphBuilder
from .visualizer import GraphVisualizer
from .data_utils import DataIO, JiraAPIClient
import asyncio
import json

@click.group()
def cli():
    """Knowledge Graph Generator CLI for Jira tickets"""
    pass

@cli.command()
@click.option('--input', '-i', required=True, type=click.Path(exists=True),
              help='Input file with Jira tickets (JSON or CSV)')
@click.option('--template', '-t', required=True, type=click.Path(exists=True),
              help='YAML template file for ticket structure')
@click.option('--output', '-o', required=True, type=click.Path(),
              help='Output directory for generated files')
@click.option('--format', '-f', type=click.Choice(['spring', 'circular']), default='spring',
              help='Layout format for graph visualization')
@click.option('--threshold', type=float, default=0.7,
              help='Similarity threshold for implicit connections')
def generate(input: str, template: str, output: str, format: str, threshold: float):
    """Generate knowledge graph from Jira tickets"""
    # Create output directory
    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load input data
    input_path = Path(input)
    if input_path.suffix == '.json':
        tickets = DataIO.load_jira_json(input)
    elif input_path.suffix == '.csv':
        tickets = DataIO.load_jira_csv(input)
    else:
        raise click.BadParameter('Input file must be JSON or CSV')
    
    # Build knowledge graph
    builder = KnowledgeGraphBuilder(template, threshold)
    graph = builder.build_knowledge_graph(tickets)
    
    # Generate visualizations
    visualizer = GraphVisualizer()
    
    # Save graph visualization
    viz_path = output_dir / f'knowledge_graph_{format}.png'
    visualizer.draw_knowledge_graph(
        graph,
        title="Jira Tickets Knowledge Graph",
        output_path=str(viz_path),
        layout=format
    )
    
    # Export graph in GraphML format
    graphml_path = output_dir / 'knowledge_graph.graphml'
    visualizer.export_graphml(graph, str(graphml_path))
    
    # Export graph statistics
    stats_path = output_dir / 'graph_stats.json'
    DataIO.export_graph_stats(graph, str(stats_path))
    
    click.echo(f"Generated files in {output_dir}:")
    click.echo(f"- Graph visualization: {viz_path}")
    click.echo(f"- GraphML export: {graphml_path}")
    click.echo(f"- Graph statistics: {stats_path}")

@cli.command()
@click.option('--url', required=True, help='Jira API base URL')
@click.option('--token', required=True, help='Jira API authentication token')
@click.option('--jql', required=True, help='JQL query to fetch tickets')
@click.option('--output', '-o', required=True, type=click.Path(),
              help='Output file for fetched tickets (JSON)')
async def fetch(url: str, token: str, jql: str, output: str):
    """Fetch tickets from Jira API"""
    client = JiraAPIClient(url, token)
    
    try:
        issues = await client.fetch_tickets(jql)
        tickets = client.transform_jira_response(issues)
        
        # Save to file
        DataIO.save_jira_json(tickets, output)
        click.echo(f"Fetched {len(tickets)} tickets to {output}")
    
    except Exception as e:
        click.echo(f"Error fetching tickets: {str(e)}", err=True)
        raise click.Abort()

@cli.command()
@click.option('--graph', '-g', required=True, type=click.Path(exists=True),
              help='GraphML file to analyze')
@click.option('--output', '-o', required=True, type=click.Path(),
              help='Output file for analysis results')
def analyze(graph: str, output: str):
    """Analyze graph structure and generate metrics"""
    import networkx as nx
    
    # Load graph
    G = nx.read_graphml(graph)
    
    # Calculate various metrics
    analysis = {
        'basic_stats': {
            'num_nodes': G.number_of_nodes(),
            'num_edges': G.number_of_edges(),
            'density': nx.density(G),
            'avg_clustering': nx.average_clustering(G),
        },
        'centrality': {
            'degree': dict(nx.degree_centrality(G)),
            'betweenness': dict(nx.betweenness_centrality(G)),
            'closeness': dict(nx.closeness_centrality(G))
        },
        'components': {
            'num_components': nx.number_connected_components(G.to_undirected()),
            'largest_component_size': len(max(nx.connected_components(G.to_undirected()), key=len))
        }
    }
    
    # Save analysis results
    with open(output, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    click.echo(f"Analysis results saved to {output}")

if __name__ == '__main__':
    cli()