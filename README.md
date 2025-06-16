# Knowledge Graph Generator for Jira Tickets

This project implements a knowledge graph generator that creates both intra-ticket and inter-ticket relationships from Jira ticket data.

## Features

- Parses ticket content into hierarchical tree structures
- Generates explicit connections based on ticket links
- Creates implicit connections using semantic similarity
- Visualizes the resulting knowledge graph
- Configurable ticket structure via YAML templates
- CLI interface for easy interaction
- Multiple visualization layouts (spring, circular)
- Graph analysis and metrics calculation
- Direct Jira API integration

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Define your ticket structure in `template.yaml`
2. Prepare your ticket data in the required format
3. Run the example:
```bash
python example_usage.py
```

## CLI Usage

### Generate Knowledge Graph
```bash
python -m src.cli generate \
  --input tickets.json \
  --template template.yaml \
  --output output_dir \
  --format spring \
  --threshold 0.7
```

### Fetch Tickets from Jira
```bash
python -m src.cli fetch \
  --url https://your-jira-instance.com \
  --token your-api-token \
  --jql "project = PROJ" \
  --output tickets.json
```

### Analyze Graph
```bash
python -m src.cli analyze \
  --graph output_dir/knowledge_graph.graphml \
  --output output_dir/analysis.json
```

## Graph Structure

The knowledge graph consists of two main components:

1. **Intra-ticket Trees**: Each ticket is represented as a tree with nodes for different sections (Summary, Description, Priority, etc.)
2. **Inter-ticket Graph**: Connections between tickets, including both explicit links and implicit similarity-based relationships

## Configuration

Modify `template.yaml` to customize:
- Required ticket sections
- Section types and validation rules
- Hierarchical relationships
- Valid relationship types

## Graph Analysis

The tool can generate various graph metrics:
- Basic statistics (nodes, edges, density)
- Centrality measures (degree, betweenness, closeness)
- Component analysis
- Clustering coefficients

## Output Files

The generator produces several files:
- PNG visualizations with different layouts
- GraphML format for use with external tools
- JSON files with graph statistics and analysis
- Detailed metric reports