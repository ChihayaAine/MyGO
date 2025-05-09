from collections import defaultdict

def get_node_label(line):
    """Extract node number and label from a line."""
    if "[" not in line:
        return line.strip(), ""
    
    node = line.split("[")[0].strip()
    label = line.split("[")[1].split("]")[0].strip()
    return node, label

def parse_dag_file(file_path):
    """
    Parse the DAG file and return the graph structure and node labels.
    The DAG file is generated by generate_dag.py and contains the dialogue flow structure.
    
    Args:
        file_path: Path to the DAG file containing the Mermaid.js format dialogue flow
        
    Returns:
        tuple: (graph, node_labels)
            - graph: A defaultdict representing edges {from_node: [to_nodes]}
            - node_labels: A dict mapping nodes to their labels {node: label}
    """
    # Initialize data structures
    graph = defaultdict(list)  # Store edges: {from_node: [to_nodes]}
    node_labels = {}  # Store node labels: {node: label}
    
    # Read and parse file
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            if "-->" in line:
                # Process edges
                from_node, to_node = line.split("-->")
                
                # Get source node information
                from_id, from_label = get_node_label(from_node)
                if from_label:
                    node_labels[from_id] = from_label
                
                # Process target node's condition markers and labels
                condition = ""
                if "|" in to_node:
                    # Example: "|Accepts| N3[Request Information]"
                    parts = to_node.split("|")
                    condition = "after user " + parts[1].strip() + ": "  # Add "after user" prefix
                    to_node = parts[-1].strip()  # Get the last part (node and label)
                
                # Get target node information
                to_id, to_label = get_node_label(to_node)
                if to_label:
                    node_labels[to_id] = condition + to_label  # Add condition marker before label
                
                # Add edge to graph (using actual node IDs)
                graph[from_id].append(to_id)
            else:
                # Process standalone node declarations
                node_id, label = get_node_label(line)
                if label:
                    node_labels[node_id] = label

    return graph, node_labels

def get_start_end_nodes(graph):
    """
    Find the start and end nodes of the graph.
    
    Args:
        graph: The graph structure as a dict {from_node: [to_nodes]}
        
    Returns:
        tuple: (start_nodes, end_nodes)
            - start_nodes: List of nodes with no incoming edges
            - end_nodes: List of nodes with no outgoing edges
    """
    all_nodes = set()
    destination_nodes = set()
    
    # Collect all nodes and destination nodes
    for source, targets in graph.items():
        all_nodes.add(source)
        for target in targets:
            all_nodes.add(target)
            destination_nodes.add(target)
    
    # Start nodes are those that never appear as targets
    start_nodes = all_nodes - destination_nodes
    # End nodes are those that have no outgoing edges
    end_nodes = {node for node in all_nodes if not graph[node]}
    
    return list(start_nodes), list(end_nodes)

def print_dag_info(graph, node_labels):
    """
    Print information about the DAG structure.
    
    Args:
        graph: The graph structure as a dict {from_node: [to_nodes]}
        node_labels: Dict mapping nodes to their labels {node: label}
    """
    print("\nDAG Structure:")
    for source, targets in graph.items():
        source_label = f" [{node_labels[source]}]" if source in node_labels else ""
        print(f"\nNode {source}{source_label} connects to:")
        for target in targets:
            target_label = f" [{node_labels[target]}]" if target in node_labels else ""
            print(f"  -> {target}{target_label}")
    
    start_nodes, end_nodes = get_start_end_nodes(graph)
    print("\nStart nodes:", start_nodes)
    print("End nodes:", end_nodes)

def main():
    """Example usage of the DAG parser"""
    file_path = "generated_dag.txt"  # Path to the DAG file generated by generate_dag.py
    
    # Parse file to get graph structure
    graph, node_labels = parse_dag_file(file_path)
    
    # Get start and end nodes
    start_nodes, end_nodes = get_start_end_nodes(graph)
    
    # Print key data structures
    print("\n=== Graph Data Structures ===")
    print("\ngraph (edges):", dict(graph))
    print("\nnode_labels:", node_labels)
    print("\nstart_nodes:", start_nodes)
    print("end_nodes:", end_nodes)
    
    # Print visualized graph structure
    print_dag_info(graph, node_labels)

if __name__ == "__main__":
    main() 