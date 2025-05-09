from typing import Dict, Any, List, Optional, Union
import time
import uuid

class Agent:
    
    def __init__(self, agent_id: str, name: str, config: Dict[str, Any]):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name
        self.config = config
        self.created_at = time.time()
        self.last_active = time.time()
        self.memory = []
        self.max_memory_size = config.get("max_memory_size", 100)
        
    def process(self, input_data: Any) -> Any:
        self.last_active = time.time()
        return self.generate_response({"input": input_data})
    
    def generate_response(self, context: Dict[str, Any]) -> str:
        return f"Response from {self.name}"
    
    def get_state(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.__class__.__name__,
            "created_at": self.created_at,
            "last_active": self.last_active,
            "memory_size": len(self.memory)
        }
        
    def add_to_memory(self, item: Any) -> None:
        self.memory.append(item)
        if len(self.memory) > self.max_memory_size:
            self.memory.pop(0)
        self.last_active = time.time()
        
    def clear_memory(self) -> None:
        self.memory = []
        
    def save(self, path: str) -> None:
        import json
        with open(path, 'w') as f:
            json.dump(self.get_state(), f)
            
    @classmethod
    def load(cls, path: str, config: Dict[str, Any]) -> 'Agent':
        import json
        with open(path, 'r') as f:
            state = json.load(f)
        return cls(state["agent_id"], state["name"], config)


class GraphGeneratorAgent(Agent):
    
    def __init__(self, agent_id: str, name: str, config: Dict[str, Any]):
        super().__init__(agent_id, name, config)
        self.dependency_types = ["sequential", "conditional", "parallel"]
        self.constraint_dimensions = ["time", "resource", "prerequisite", "outcome"]
        
    def process(self, task_description: str) -> Dict[str, Any]:
        self.add_to_memory({"task": task_description})
        
        subtasks = self.decompose_task(task_description)
        dependencies = self.identify_dependencies(subtasks)
        constraints = self.apply_constraints(subtasks, dependencies)
        
        graph = self.build_graph(subtasks, dependencies, constraints)
        
        return graph
    
    def decompose_task(self, task_description: str) -> List[Dict[str, Any]]:
        subtasks = []
        
        # In a real implementation, this would use LLM to decompose the task
        # For demonstration, we'll create some sample subtasks
        subtask_names = [
            "Greeting and introduction",
            "Collect user information",
            "Present options",
            "Handle user selection",
            "Confirm details",
            "Complete transaction",
            "Farewell"
        ]
        
        for i, name in enumerate(subtask_names):
            subtasks.append({
                "id": f"subtask_{i+1}",
                "name": name,
                "description": f"This subtask involves {name.lower()}",
                "estimated_duration": 1 + i
            })
            
        return subtasks
    
    def identify_dependencies(self, subtasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        dependencies = []
        
        # Create sequential dependencies by default
        for i in range(len(subtasks) - 1):
            dependencies.append({
                "from": subtasks[i]["id"],
                "to": subtasks[i+1]["id"],
                "type": "sequential",
                "condition": None
            })
            
        # Add a conditional dependency example
        if len(subtasks) > 3:
            dependencies.append({
                "from": subtasks[2]["id"],
                "to": subtasks[4]["id"],
                "type": "conditional",
                "condition": "if user selects premium option"
            })
            
        return dependencies
    
    def apply_constraints(self, subtasks: List[Dict[str, Any]], dependencies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        constraints = []
        
        # Add some example constraints
        constraints.append({
            "subtask_id": subtasks[0]["id"],
            "dimension": "time",
            "constraint": "must be completed within 1 minute"
        })
        
        constraints.append({
            "subtask_id": subtasks[-1]["id"],
            "dimension": "prerequisite",
            "constraint": "must have completed all previous subtasks"
        })
        
        return constraints
    
    def build_graph(self, subtasks: List[Dict[str, Any]], dependencies: List[Dict[str, Any]], constraints: List[Dict[str, Any]]) -> Dict[str, Any]:
        graph = {
            "nodes": subtasks,
            "edges": dependencies,
            "constraints": constraints,
            "metadata": {
                "task_type": "dialogue",
                "created_at": time.time(),
                "version": "1.0"
            }
        }
        
        return graph


class StatePlannerAgent(Agent):
    
    def __init__(self, agent_id: str, name: str, config: Dict[str, Any]):
        super().__init__(agent_id, name, config)
        self.current_state = None
        self.graph = None
        self.visited_nodes = []
        
    def initialize_with_graph(self, graph: Dict[str, Any]) -> None:
        self.graph = graph
        self.current_state = self.find_start_node()
        self.visited_nodes = [self.current_state["id"]]
        
    def find_start_node(self) -> Dict[str, Any]:
        if not self.graph or "nodes" not in self.graph:
            raise ValueError("Graph not initialized or invalid")
            
        # Find node with no incoming edges
        incoming_edges = {edge["to"] for edge in self.graph["edges"]}
        
        for node in self.graph["nodes"]:
            if node["id"] not in incoming_edges:
                return node
                
        # If no clear start node, return the first node
        return self.graph["nodes"][0]
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action = input_data.get("action", "get_current_state")
        
        if action == "get_current_state":
            return self.get_current_state()
        elif action == "transition":
            next_node_id = input_data.get("next_node_id")
            return self.transition_to(next_node_id)
        elif action == "get_possible_transitions":
            return self.get_possible_transitions()
        else:
            return {"error": f"Unknown action: {action}"}
    
    def get_current_state(self) -> Dict[str, Any]:
        if not self.current_state:
            return {"error": "No current state, graph not initialized"}
            
        return {
            "current_node": self.current_state,
            "visited_nodes": self.visited_nodes,
            "progress": len(self.visited_nodes) / len(self.graph["nodes"])
        }
    
    def get_possible_transitions(self) -> Dict[str, Any]:
        if not self.current_state:
            return {"error": "No current state, graph not initialized"}
            
        possible_transitions = []
        
        for edge in self.graph["edges"]:
            if edge["from"] == self.current_state["id"]:
                # Find the target node
                target_node = None
                for node in self.graph["nodes"]:
                    if node["id"] == edge["to"]:
                        target_node = node
                        break
                
                if target_node:
                    possible_transitions.append({
                        "edge": edge,
                        "target_node": target_node
                    })
                    
        return {
            "current_node": self.current_state,
            "possible_transitions": possible_transitions
        }
    
    def transition_to(self, node_id: str) -> Dict[str, Any]:
        if not self.current_state:
            return {"error": "No current state, graph not initialized"}
            
        # Check if transition is valid
        valid_transition = False
        
        for edge in self.graph["edges"]:
            if edge["from"] == self.current_state["id"] and edge["to"] == node_id:
                valid_transition = True
                break
                
        if not valid_transition:
            return {"error": f"Invalid transition from {self.current_state['id']} to {node_id}"}
            
        # Find the target node
        target_node = None
        for node in self.graph["nodes"]:
            if node["id"] == node_id:
                target_node = node
                break
                
        if not target_node:
            return {"error": f"Target node {node_id} not found in graph"}
            
        # Update state
        self.current_state = target_node
        self.visited_nodes.append(node_id)
        
        return {
            "previous_node_id": self.visited_nodes[-2] if len(self.visited_nodes) > 1 else None,
            "current_node": self.current_state,
            "visited_nodes": self.visited_nodes,
            "progress": len(set(self.visited_nodes)) / len(self.graph["nodes"])
        }


class ChatAgent(Agent):
    
    def __init__(self, agent_id: str, name: str, config: Dict[str, Any]):
        super().__init__(agent_id, name, config)
        self.dialogue_history = []
        
    def process(self, input_data: Dict[str, Any]) -> str:
        user_input = input_data.get("user_input", "")
        current_subtask = input_data.get("current_subtask", {})
        dialogue_context = input_data.get("dialogue_context", {})
        
        # Add user input to dialogue history
        self.dialogue_history.append({"role": "user", "content": user_input})
        
        # Generate response based on current subtask and user input
        response = self.generate_response_for_subtask(user_input, current_subtask, dialogue_context)
        
        # Add response to dialogue history
        self.dialogue_history.append({"role": "assistant", "content": response})
        
        return response
    
    def generate_response_for_subtask(self, user_input: str, subtask: Dict[str, Any], context: Dict[str, Any]) -> str:
        subtask_name = subtask.get("name", "Unknown")
        
        # In a real implementation, this would use LLM to generate appropriate responses
        # For demonstration, we'll use template responses based on subtask
        
        if "greeting" in subtask_name.lower():
            return f"Hello! Welcome to our service. How can I assist you today?"
            
        elif "collect" in subtask_name.lower():
            return f"I'll need some information from you. Could you please provide your name and contact details?"
            
        elif "present" in subtask_name.lower():
            return f"We have several options available: Basic, Premium, and Enterprise. Each offers different features and pricing."
            
        elif "selection" in subtask_name.lower():
            return f"You've selected an option. Let me provide more details about your choice."
            
        elif "confirm" in subtask_name.lower():
            return f"Just to confirm, you want to proceed with the selected option. Is that correct?"
            
        elif "complete" in subtask_name.lower():
            return f"Great! I've processed your request. Your confirmation number is ABC123."
            
        elif "farewell" in subtask_name.lower():
            return f"Thank you for using our service today. Have a wonderful day!"
            
        else:
            return f"I understand you're asking about {user_input}. Let me help you with that."
    
    def get_dialogue_history(self) -> List[Dict[str, Any]]:
        return self.dialogue_history


class DecisionMakerAgent(Agent):
    
    def __init__(self, agent_id: str, name: str, config: Dict[str, Any]):
        super().__init__(agent_id, name, config)
        
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        dialogue_history = input_data.get("dialogue_history", [])
        current_state = input_data.get("current_state", {})
        possible_transitions = input_data.get("possible_transitions", [])
        
        # Make decision based on dialogue history and current state
        decision = self.make_decision(dialogue_history, current_state, possible_transitions)
        
        return decision
    
    def make_decision(self, dialogue_history: List[Dict[str, Any]], current_state: Dict[str, Any], possible_transitions: List[Dict[str, Any]]) -> Dict[str, Any]:
        # If no transitions available, stay at current node
        if not possible_transitions:
            return {
                "decision": "stay",
                "reason": "No available transitions",
                "current_node_id": current_state.get("current_node", {}).get("id")
            }
            
        # Get the last user message
        last_user_message = ""
        for message in reversed(dialogue_history):
            if message.get("role") == "user":
                last_user_message = message.get("content", "")
                break
                
        # In a real implementation, this would use LLM to analyze the dialogue and make decisions
        # For demonstration, we'll use simple heuristics
        
        # Check if user has provided necessary information for current subtask
        current_node_name = current_state.get("current_node", {}).get("name", "").lower()
        
        if "collect" in current_node_name and ("name" in last_user_message.lower() or "contact" in last_user_message.lower()):
            # User provided information, move to next node
            return self.select_next_transition(possible_transitions, "sequential")
            
        elif "present" in current_node_name and any(option in last_user_message.lower() for option in ["basic", "premium", "enterprise"]):
            # User selected an option, move to handling selection
            return self.select_next_transition(possible_transitions, "conditional" if "premium" in last_user_message.lower() else "sequential")
            
        elif "confirm" in current_node_name and any(confirm in last_user_message.lower() for confirm in ["yes", "correct", "right", "proceed"]):
            # User confirmed, move to completion
            return self.select_next_transition(possible_transitions, "sequential")
            
        elif "farewell" in current_node_name:
            # End of conversation
            return {
                "decision": "end",
                "reason": "Conversation complete",
                "current_node_id": current_state.get("current_node", {}).get("id")
            }
            
        else:
            # Default: stay at current node if unsure
            return {
                "decision": "stay",
                "reason": "User input doesn't indicate readiness to move to next subtask",
                "current_node_id": current_state.get("current_node", {}).get("id")
            }
    
    def select_next_transition(self, possible_transitions: List[Dict[str, Any]], preferred_type: str = None) -> Dict[str, Any]:
        # If preferred type specified, try to find a transition of that type
        if preferred_type:
            for transition in possible_transitions:
                if transition.get("edge", {}).get("type") == preferred_type:
                    return {
                        "decision": "transition",
                        "reason": f"User input indicates transition via {preferred_type} path",
                        "next_node_id": transition.get("target_node", {}).get("id")
                    }
                    
        # Default to first available transition
        if possible_transitions:
            return {
                "decision": "transition",
                "reason": "Moving to next logical subtask",
                "next_node_id": possible_transitions[0].get("target_node", {}).get("id")
            }
            
        # Fallback
        return {
            "decision": "stay",
            "reason": "No suitable transition found",
            "current_node_id": None
        }


class MyGOSystem:
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize agents
        self.graph_generator = GraphGeneratorAgent(
            agent_id="graph_generator",
            name="Sub-Task Dependency Graph Generator",
            config=config.get("graph_generator_config", {})
        )
        
        self.state_planner = StatePlannerAgent(
            agent_id="state_planner",
            name="State Planner",
            config=config.get("state_planner_config", {})
        )
        
        self.chat_agent = ChatAgent(
            agent_id="chat_agent",
            name="Chat Agent",
            config=config.get("chat_agent_config", {})
        )
        
        self.decision_maker = DecisionMakerAgent(
            agent_id="decision_maker",
            name="Decision Maker",
            config=config.get("decision_maker_config", {})
        )
        
        self.task_graph = None
        self.initialized = False
        
    def initialize_with_task(self, task_description: str) -> Dict[str, Any]:
        # Generate task graph
        self.task_graph = self.graph_generator.process(task_description)
        
        # Initialize state planner with graph
        self.state_planner.initialize_with_graph(self.task_graph)
        
        # Get initial state
        initial_state = self.state_planner.get_current_state()
        
        self.initialized = True
        
        return {
            "status": "initialized",
            "task_graph": self.task_graph,
            "initial_state": initial_state
        }
    
    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        if not self.initialized:
            return {"error": "System not initialized with task"}
            
        # Get current state from planner
        current_state = self.state_planner.get_current_state()
        current_subtask = current_state.get("current_node", {})
        
        # Get possible transitions
        transitions_data = self.state_planner.get_possible_transitions()
        possible_transitions = transitions_data.get("possible_transitions", [])
        
        # Generate chat response
        chat_input = {
            "user_input": user_input,
            "current_subtask": current_subtask,
            "dialogue_context": {
                "visited_nodes": current_state.get("visited_nodes", []),
                "progress": current_state.get("progress", 0)
            }
        }
        
        chat_response = self.chat_agent.process(chat_input)
        
        # Make decision about state transition
        decision_input = {
            "dialogue_history": self.chat_agent.get_dialogue_history(),
            "current_state": current_state,
            "possible_transitions": possible_transitions
        }
        
        decision = self.decision_maker.process(decision_input)
        
        # Execute transition if needed
        if decision.get("decision") == "transition":
            next_node_id = decision.get("next_node_id")
            transition_result = self.state_planner.transition_to(next_node_id)
            new_state = transition_result
        else:
            new_state = current_state
            
        return {
            "user_input": user_input,
            "response": chat_response,
            "decision": decision,
            "previous_state": current_state,
            "new_state": new_state
        }
    
    def get_system_state(self) -> Dict[str, Any]:
        if not self.initialized:
            return {"status": "not_initialized"}
            
        return {
            "status": "active",
            "current_state": self.state_planner.get_current_state(),
            "dialogue_history_length": len(self.chat_agent.get_dialogue_history()),
            "task_graph_nodes": len(self.task_graph.get("nodes", [])),
            "task_graph_edges": len(self.task_graph.get("edges", []))
        }
