import requests
from task_dag import parse_dag_file, get_start_end_nodes
from openai import OpenAI
import json
import jsonlines
from collections import defaultdict
import os
from generate_dag import generate_dag_with_llm, save_dag_to_file
from evaluator import DialogueEvaluator

class DialoguePlanner:
    def __init__(self, graph, node_labels):
        self.graph = graph
        self.node_labels = node_labels
        start_nodes, _ = get_start_end_nodes(graph)
        self.current_node = start_nodes[0]
    
    def get_current_task(self):
        return self.node_labels.get(self.current_node, "")
    
    def get_next_nodes(self):
        return self.graph.get(self.current_node, [])
    
    def move_to_node(self, next_node):
        if next_node in self.get_next_nodes() or next_node == self.current_node:
            self.current_node = next_node
            return True
        return False

def call_model(url, messages, generate_params):
    params = {
        "messages": messages,
        "params": generate_params
    }
    response = requests.post(
        f"{url}/api/chat",
        json=params,
        timeout=60
    )
    response.raise_for_status()
    return response.json()['data']['text']

def state_classifier(user_response, current_node, next_nodes, node_labels):
    prompt = f"""You are tasked with analyzing a task-oriented dialogue system to decide the subsequent step in the conversation. 
    Your decision should be based on the current dialogue flow, the user's recent response, and predefined rules governing the flow of the dialogue.
Current node task: {node_labels[current_node]}
Possible next tasks: {[node_labels[node] for node in next_nodes]}
User response: {user_response}

Guidelines for Decision Making:

Completion Check: Evaluate whether the current task or sub-task has been fully addressed. 
If not, maintain the current step to ensure all necessary actions are completed before progressing.

Response Analysis: Analyze the user's response for cues or information that may indicate readiness to move forward or require further clarification. 
The response might necessitate revisiting previous steps or adjusting the current path.

Flow Navigation: Utilize the sub-task graph to identify potential branching paths. 
Consider any conditional logic or decision points that may alter the standard progression.

Branching Conditions: Pay special attention to any branching conditions outlined in the dialogue flow. 
Determine if the user's response satisfies the conditions required to switch to a different path or sub-task.

Objective Alignment: Ensure that the next step aligns with the overall objectives of the dialogue session, 
maintaining coherence and relevance to the user's needs.

Decision:

Based on the above guidelines, identify and respond with ONLY the step number that represents the most appropriate next action in the dialogue flow (e.g., "N1", "N2", "N3", etc.). 
Your decision should reflect a comprehensive analysis of the current dialogue context and user interaction."""
    
    messages = [{"role": "system", "content": prompt}]
    generate_params = {
        "do_sample": True,
        "max_new_tokens": 50,
        'repetition_penalty': 1.1,
    }
    
    decision = call_model("xxxxxxxxxxx", messages, generate_params)
    print("\nCurrent node:", current_node)
    print("Available next nodes:", next_nodes)
    print("\nDecision:", decision)
    
    if "stay" in decision.lower() or "option 1" in decision.lower():
        return current_node
    if "move" in decision.lower() or "option 2" in decision.lower():
        for node in next_nodes:
            if node_labels[node].lower() in decision.lower():
                return node
        if len(next_nodes) == 1:
            return next_nodes[0]
    return current_node

API_KEY = "xxxxxxxxxxxx"
OPENAI_BASE_URL = "xxxxxxxxxxxxxx"

def load_dialogue_roles():
    """
    Load dialogue role configurations and task from dialogue_task.json
    Return default role configurations if file doesn't exist
    """
    try:
        with open('dataset/dialogue_task.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            return (
                config.get('assistant_role', ''),
                config.get('user_role', ''),
                config.get('task', 'Understand the user\'s requirements and collect necessary information to assist them effectively')
            )
    except FileNotFoundError:
        print("Warning: dataset/dialogue_task.json not found, using default roles and task")
        return (
            "You are a professional assistant dedicated to helping users achieve their goals. You are skilled at understanding user needs and guiding conversations to collect necessary information.",
            "You are a user seeking assistance with your request",
            "Understand the user's requirements and collect necessary information to assist them effectively"
        )

def main():
    # Initialize configuration
    global MODEL_URL, API_KEY, OPENAI_BASE_URL
    MODEL_URL = "xxxxxxxxxxxxxxxxx"
    API_KEY = "xxxxxxxxxxxxxxxxx"
    OPENAI_BASE_URL = "xxxxxxxxxxxxxxx"
    
    # Initialize evaluator
    evaluator = DialogueEvaluator(API_KEY, OPENAI_BASE_URL)
    
    # Load dialogue role configurations and task
    assistant_role, user_role, task = load_dialogue_roles()
    
    # Store all evaluation results
    all_evaluations = []
    
    print(f"\n=== Starting Dialogue ===")
    print(f"Assistant Role: {assistant_role}")
    print(f"User Role: {user_role}")
    
    # Example task
    print("\n=== Task ===")
    print("Task:", task)
    
    # 1. Task decomposition and DAG generation
    print("\n=== Task Decomposition and DAG Generation ===")
    print("Task:", task)
    
    # Generate DAG using LLM
    try:
        dag_text = generate_dag_with_llm(MODEL_URL, task)
        dag_file = save_dag_to_file(dag_text)
        
        # Print generated DAG text
        print("\n=== Generated DAG ===")
        with open(dag_file, 'r') as f:
            print(f.read())
        
        # Parse DAG
        graph, node_labels = parse_dag_file(dag_file)
        
        # Print parsed data structures
        print("\n=== Parsed DAG Structure ===")
        print("Graph (edges):", dict(graph))
        print("\nNode labels:", node_labels)
        
        start_nodes, end_nodes = get_start_end_nodes(graph)
        print("\nStart nodes:", start_nodes)
        print("End nodes:", end_nodes)
        
        print("\n=== Starting Conversation ===")
        
        # Initialize planner and start dialogue
        planner = DialoguePlanner(graph, node_labels)
        
        # 2. Start dialogue loop
        dialogue_history = []
        while True:
            current_task = planner.get_current_task()
            next_nodes = planner.get_next_nodes()
            
            # If no next nodes, end dialogue
            if not next_nodes:
                dialogue_prompt = f"""#Role:
{assistant_role}
The dialogue should now end.
Generate a polite farewell message to end the conversation. The message should include:
1. Thank the user for their time
2. Express appreciation for their cooperation
3. Wish them all the best"""
                
                messages = [
                    {"role": "system", "content": dialogue_prompt}
                ]
                generate_params = {
                    "do_sample": True,
                    "max_new_tokens": 100,
                    'repetition_penalty': 1.1,
                }
                
                farewell = call_model(MODEL_URL, messages, generate_params)
                print("Assistant:", farewell)
                dialogue_history.append({"role": "assistant", "content": farewell})
                print(dialogue_history)
                
                # Add evaluation after dialogue ends
                print("\n=== Evaluating Dialogue Quality ===")
                evaluation_result = evaluator.evaluate_dialogue(dialogue_history)
                if evaluation_result:
                    print("\nDialogue Evaluation:")
                    print(json.dumps(evaluation_result, ensure_ascii=False, indent=2))
                    
                    # Save dialogue and evaluation to file
                    output = {
                        "dialogue_history": dialogue_history,
                        "evaluation": evaluation_result
                    }
                    with open("dialogue_evaluation.json", "w", encoding="utf-8") as f:
                        json.dump(output, f, ensure_ascii=False, indent=2)
                
                break
            
            # Model A: Dialogue model generates response
            dialogue_prompt = f"""You are {assistant_role}, dedicated to assisting users in completing their tasks with expertise and professionalism. 
The task is {task}. With extensive experience and numerous successful interactions, you are committed to providing warm, friendly, and professional assistance. 
Your expertise ensures that users receive the best possible guidance, and you strive to help them achieve their goals efficiently. 

Sub-Task Graph: {dag_text}

Please strictly adhere to the steps of this sub-task graph, without skipping or reversing any steps.

Current Dialogue Sub-Task: {current_task}

You must always focus on the sub-task of this step in this round of dialogue!

Dialogue history: {dialogue_history}

Generate appropriate response:"""
            
            messages = [
                {"role": "system", "content": dialogue_prompt}
            ]
            generate_params = {
                "do_sample": True,
                "max_new_tokens": 100,
                'repetition_penalty': 1.1,
            }
            
            assistant_response = call_model(MODEL_URL, messages, generate_params)
            print("Assistant:", assistant_response)
            dialogue_history.append({"role": "assistant", "content": assistant_response})
            
            # Model B: User model generates response
            user_prompt = f"""You are {user_role}，answer as concisely as possible, don't repeat topics already discussed. Don't actively expand topics unless asked. Reply in a colloquial manner.
Dialogue history: {dialogue_history}
The other party's most recent message is: {assistant_response}
Generate appropriate response:"""
            messages = [
                {"role": "system", "content": user_prompt},
            ]
            
            user_response = call_model(MODEL_URL, messages, generate_params)
            print("User:", user_response)
            dialogue_history.append({"role": "user", "content": user_response})
            
            # Model C: State classifier decides next step
            next_node = state_classifier(user_response, planner.current_node, next_nodes, node_labels)
            
            planner.move_to_node(next_node)
        
        # Evaluate dialogue quality
        evaluation_result = evaluator.evaluate_dialogue(dialogue_history)
        if evaluation_result:
            # Save results
            all_evaluations.append({
                "role_idx": 0,
                "role": assistant_role,
                "dialogue_history": dialogue_history,
                "evaluation": evaluation_result
            })
    
    except Exception as e:
        print(f"Error in dialogue process: {str(e)}")
    
    # Calculate overall evaluation results
    print("\n=== Overall Evaluation Results ===")
    evaluator.save_evaluation_results(all_evaluations)

if __name__ == "__main__":
    main() 