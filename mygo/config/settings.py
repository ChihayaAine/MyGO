import json
import os
import yaml
from typing import Dict, Any, Optional, Union
import logging
import sys

def load_config(config_path: str) -> Dict[str, Any]:
    """加载配置文件"""
    if not os.path.exists(config_path):
        print(f"Warning: Config file {config_path} does not exist, using default configuration")
        return get_default_config()
    
    file_ext = os.path.splitext(config_path)[1].lower()
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            if file_ext == '.json':
                return json.load(f)
            elif file_ext in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            else:
                print(f"Unsupported configuration file format: {file_ext}")
                return get_default_config()
    except Exception as e:
        print(f"Error loading configuration file: {e}")
        return get_default_config()

def get_default_config() -> Dict[str, Any]:
    """获取默认配置"""
    return {
        "system": {
            "name": "MyGO",
            "version": "1.0.0",
            "description": "Multi-agent system for predefined task-oriented dialogue"
        },
        "graph_generator_config": {
            "model": "gpt-4o-0513",
            "temperature": 0.2,
            "max_tokens": 2000,
            "max_subtasks": 15,
            "dependency_types": ["sequential", "conditional", "parallel"],
            "constraint_dimensions": ["time", "resource", "prerequisite", "outcome"],
            "prompt_template": "graph_generator"
        },
        "state_planner_config": {
            "model": "gpt-4o-0513",
            "temperature": 0.1,
            "max_tokens": 1000,
            "transition_threshold": 0.7,
            "max_history": 50,
            "prompt_template": "state_planner"
        },
        "chat_agent_config": {
            "model": "gpt-4o-0513",
            "temperature": 0.7,
            "max_tokens": 1500,
            "max_memory_size": 100,
            "prompt_template": "chat_agent"
        },
        "decision_maker_config": {
            "model": "gpt-4o-0513",
            "temperature": 0.2,
            "max_tokens": 1000,
            "confidence_threshold": 0.6,
            "max_history_to_consider": 5,
            "prompt_template": "decision_maker"
        },
        "logging": {
            "level": "INFO",
            "file": "mygo.log",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "evaluation": {
            "metrics": [
                "success_rate",
                "response_relevance",
                "subtask_transition_accuracy",
                "dialogue_flow",
                "topic_boundary_control"
            ],
            "weights": {
                "success_rate": 0.3,
                "response_relevance": 0.2,
                "subtask_transition_accuracy": 0.2,
                "dialogue_flow": 0.15,
                "topic_boundary_control": 0.15
            }
        },
        "paths": {
            "prompts_directory": "prompts",
            "agents_directory": "agents/types",
            "output_directory": "output",
            "logs_directory": "logs"
        }
    }

def save_config(config: Dict[str, Any], config_path: str) -> None:
    """保存配置到文件"""
    directory = os.path.dirname(config_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        
    file_ext = os.path.splitext(config_path)[1].lower()
    
    with open(config_path, 'w', encoding='utf-8') as f:
        if file_ext == '.json':
            json.dump(config, f, indent=2)
        elif file_ext in ['.yaml', '.yml']:
            yaml.dump(config, f, default_flow_style=False)
        else:
            json.dump(config, f, indent=2)

def setup_logging(config: Dict[str, Any]) -> None:
    logging_config = config.get("logging", {})
    level_str = logging_config.get("level", "INFO")
    log_file = logging_config.get("file")
    log_format = logging_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    level = getattr(logging, level_str.upper(), logging.INFO)
    
    handlers = []
    
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        handlers.append(logging.FileHandler(log_file))
    
    handlers.append(logging.StreamHandler(sys.stdout))
    
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers
    )

def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    result = base_config.copy()
    
    for key, value in override_config.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
            
    return result 

def get_agent_config(config: Dict[str, Any], agent_type: str) -> Dict[str, Any]:
    config_key = f"{agent_type}_config"
    if config_key in config:
        return config[config_key]
    return {}

def create_directories(config: Dict[str, Any]) -> None:
    paths = config.get("paths", {})
    
    for path_name, path_value in paths.items():
        if path_name.endswith("_directory") and path_value:
            os.makedirs(path_value, exist_ok=True) 
