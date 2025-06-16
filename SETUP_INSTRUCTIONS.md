# Knowledge Graph Generator Project Setup Instructions

## Project Description
Create a knowledge graph generator that creates both intra-ticket and inter-ticket relationships from Jira ticket data. This project implements a system to visualize and analyze relationships between tickets using graph-based representations.

## Setup Steps

1. **Create a New Project Directory**
```bash
mkdir knowledge-graph-generator
cd knowledge-graph-generator
```

2. **Initialize Git Repository**
```bash
git init
```

3. **Project Structure**
Create the following directory structure:
```
.
├── src/
│   ├── __init__.py
│   ├── cli.py
│   ├── data_utils.py
│   ├── graph_generator.py
│   ├── knowledge_graph_builder.py
│   ├── llm_parser.py
│   ├── logging_utils.py
│   ├── ticket_parser.py
│   ├── validator.py
│   └── visualizer.py
├── logs/
├── example_usage.py
├── knowledge_graph.py
├── README.md
├── requirements.txt
└── template.yaml
```

4. **Dependencies**
Create requirements.txt with the following dependencies:
```
networkx>=3.1
sentence-transformers>=2.2.0
scikit-learn>=1.0.2
pyyaml>=6.0.0
matplotlib>=3.7.0
torch>=2.0.0
numpy>=1.21.0
click>=8.0.0
pandas>=2.0.0
aiohttp>=3.8.0
```

5. **Install Dependencies**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

6. **Project Files Implementation**

Each file in the project serves a specific purpose:

- `src/cli.py`: Command-line interface for the application
- `src/data_utils.py`: Data loading and processing utilities
- `src/graph_generator.py`: Core graph generation logic
- `src/knowledge_graph_builder.py`: Main knowledge graph construction
- `src/llm_parser.py`: Language model-based text parsing
- `src/logging_utils.py`: Logging configuration and utilities
- `src/ticket_parser.py`: Ticket content parsing logic
- `src/validator.py`: Data validation utilities
- `src/visualizer.py`: Graph visualization tools

7. **Configuration**
Create template.yaml with the following structure:
```yaml
sections:
  - name: Summary
    required: true
    type: text
  - name: Description
    required: true
    type: text
  - name: Priority
    required: true
    type: enum
    values: [High, Medium, Low]

relationships:
  - name: clone
    type: explicit
  - name: blocks
    type: explicit
  - name: relates_to
    type: explicit

similarity_threshold: 0.8
```

8. **GitHub Repository Setup**
```bash
# Configure Git
git config --global user.name "your-username"
git config --global user.email "your-email"

# Add .gitignore
curl -o .gitignore https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore

# Create repository on GitHub using gh CLI
gh auth login
gh repo create knowledge-graph-generator --public --description "A knowledge graph generator that creates both intra-ticket and inter-ticket relationships from Jira ticket data"

# Push to GitHub
git add .
git commit -m "Initial commit with knowledge graph generator implementation"
git branch -M main
git remote add origin git@github.com:username/knowledge-graph-generator.git
git push -u origin main
```

## Usage Example

1. **Basic Usage**
```python
python -m src.cli generate \
  --input tickets.json \
  --template template.yaml \
  --output output_dir \
  --format spring \
  --threshold 0.7
```

2. **Fetch Tickets from Jira**
```python
python -m src.cli fetch \
  --url https://your-jira-instance.com \
  --token your-api-token \
  --jql "project = PROJ" \
  --output tickets.json
```

3. **Analyze Graph**
```python
python -m src.cli analyze \
  --graph output_dir/knowledge_graph.graphml \
  --output output_dir/analysis.json
```

## Key Features

- Parses ticket content into hierarchical tree structures
- Generates explicit connections based on ticket links
- Creates implicit connections using semantic similarity
- Visualizes the resulting knowledge graph
- Configurable ticket structure via YAML templates
- CLI interface for easy interaction
- Multiple visualization layouts (spring, circular)
- Graph analysis and metrics calculation
- Direct Jira API integration

## Development Guidelines

1. Follow Python best practices and PEP 8 style guide
2. Write unit tests for new features
3. Document code using docstrings
4. Use type hints for better code maintainability
5. Keep the code modular and maintainable

## Additional Resources

- [NetworkX Documentation](https://networkx.org/documentation/stable/)
- [Sentence Transformers Documentation](https://www.sbert.net/)
- [Click Documentation](https://click.palletsprojects.com/)
- [Jira REST API Documentation](https://developer.atlassian.com/server/jira/platform/rest-apis/)