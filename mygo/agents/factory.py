from typing import Dict, Any, Type, List, Optional
from .base import Agent, GraphGeneratorAgent, StatePlannerAgent, ChatAgent, DecisionMakerAgent, MyGOSystem
import importlib
import os
import inspect

# Agent registry
_agent_registry = {}

def register_agent(agent_type: str):
    def decorator(cls):
        _agent_registry[agent_type] = cls
        return cls
    return decorator

def create_agent(agent_type: str, agent_id: str, name: str, config: Dict[str, Any]) -> Agent:
    if agent_type not in _agent_registry:
        raise ValueError(f"Unknown agent: {agent_type}")
    
    agent_class = _agent_registry[agent_type]
    return agent_class(agent_id=agent_id, name=name, config=config)

def get_available_agent_types() -> list:
    return list(_agent_registry.keys())

# Register built-in agents
register_agent("graph_generator")(GraphGeneratorAgent)
register_agent("state_planner")(StatePlannerAgent)
register_agent("chat_agent")(ChatAgent)
register_agent("decision_maker")(DecisionMakerAgent)

def load_agents_from_directory(directory: str) -> List[str]:
    loaded_agents = []
    
    if not os.path.exists(directory):
        print(f"Warning: Directory {directory} does not exist")
        return loaded_agents
    
    for filename in os.listdir(directory):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = filename[:-3]
            module_path = f"mygo.agents.types.{module_name}"
            
            try:
                module = importlib.import_module(module_path)
                
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, Agent) and 
                        obj != Agent):
                        loaded_agents.append(name)
                        
                        # Auto-register the agent
                        agent_type = name.lower().replace("agent", "")
                        if agent_type not in _agent_registry:
                            register_agent(agent_type)(obj)
                            
            except Exception as e:
                print(f"Error loading agent module {module_path}: {e}")
                
    return loaded_agents

def create_multi_agent_system(config: Dict[str, Any]) -> MyGOSystem:
    return MyGOSystem(config)

def create_agent_pipeline(agent_configs: List[Dict[str, Any]], pipeline_config: Dict[str, Any] = None) -> Dict[str, Agent]:
    agents = {}
    
    for agent_config in agent_configs:
        agent_type = agent_config.get("type")
        agent_id = agent_config.get("id")
        agent_name = agent_config.get("name", f"Agent-{agent_id}")
        agent_specific_config = agent_config.get("config", {})
        
        agent = create_agent(
            agent_type=agent_type,
            agent_id=agent_id,
            name=agent_name,
            config=agent_specific_config
        )
        
        agents[agent_id] = agent
    
    # Configure pipeline connections if provided
    if pipeline_config and "connections" in pipeline_config:
        for connection in pipeline_config["connections"]:
            from_agent_id = connection.get("from")
            to_agent_id = connection.get("to")
            
            if from_agent_id in agents and to_agent_id in agents:
                # Set up the connection between agents
                # This is a simplified example - actual implementation would depend on your architecture
                if hasattr(agents[from_agent_id], "set_next_agent"):
                    agents[from_agent_id].set_next_agent(agents[to_agent_id])
    
    return agents 
