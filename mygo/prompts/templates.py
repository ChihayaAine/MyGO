from typing import Dict, Any, List, Optional, Union
import string
import re
import os
import json

class PromptTemplate:
    
    def __init__(self, template: str):
        self.template = template
        self.variables = self._extract_variables(template)
        
    def format(self, **kwargs) -> str:
        return self.template.format(**kwargs)
    
    def _extract_variables(self, template: str) -> List[str]:
        pattern = r'\{([^{}]*)\}'
        return re.findall(pattern, template)
    
    def validate_variables(self, **kwargs) -> bool:
        for var in self.variables:
            if var not in kwargs:
                return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "template": self.template,
            "variables": self.variables
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptTemplate':
        return cls(data["template"])
    
    @classmethod
    def from_file(cls, file_path: str) -> 'PromptTemplate':
        with open(file_path, 'r', encoding='utf-8') as f:
            template = f.read()
        return cls(template)

# 保存原有的提示模板
DEFAULT_PROMPTS = {
    "graph_generator": PromptTemplate(
        """You are the Sub-Task Dependency Graph Generator for the MyGO dialogue system. Your role is to decompose a complex task into a structured graph of subtasks with dependencies and constraints.

Task Description: {task_description}

Please analyze this task and:
1. Decompose it into logical subtasks (aim for 5-15 subtasks)
2. For each subtask, provide:
   - A descriptive name
   - A brief description of what this subtask involves
   - Estimated time/effort required (low/medium/high)

3. Define dependencies between subtasks using these types:
   - Sequential: Task B can only start after Task A completes
   - Conditional: Task B only occurs if a specific condition from Task A is met
   - Parallel: Tasks can be performed concurrently

4. Apply constraints across these dimensions:
   - Time constraints: Deadlines, duration limits
   - Resource constraints: Tools, information, or capabilities needed
   - Prerequisite constraints: Knowledge or conditions required
   - Outcome constraints: Quality or format requirements for outputs

Format your response as a structured JSON object with:
- "nodes": Array of subtask objects with id, name, description, and estimated_effort
- "edges": Array of dependency objects with from_id, to_id, type, and condition (if applicable)
- "constraints": Array of constraint objects with subtask_id, dimension, and description

This graph will serve as the blueprint for guiding a task-oriented dialogue.
"""
    ),
    
    "state_planner": PromptTemplate(
        """You are the State Planner for the MyGO dialogue system. Your role is to track the current state of the dialogue and determine possible transitions based on the sub-task dependency graph.

Current State:
- Current Node: {current_node}
- Visited Nodes: {visited_nodes}
- Dialogue Progress: {progress}%

User Input: {user_input}

Task Graph Structure:
{graph_structure}

Based on the current state, the user's input, and the task graph structure:

1. Evaluate whether the current subtask has been completed or should continue
2. Identify valid transitions to other nodes based on the dependency graph
3. For each possible transition, assess:
   - Whether all prerequisites have been met
   - Whether any constraints would block the transition
   - The appropriateness of the transition given the dialogue context

Provide your analysis in this format:
1. Current subtask status: [COMPLETE/INCOMPLETE/BLOCKED]
2. Recommended action: [STAY/TRANSITION/END]
3. If TRANSITION, specify the target node ID and justification
4. List all valid possible transitions with confidence scores (0-1)

Your goal is to ensure the dialogue follows a logical progression through the task graph while adapting to the user's inputs and maintaining coherence.
"""
    ),
    
    "chat_agent": PromptTemplate(
        """You are the Chat Agent for the MyGO dialogue system. Your role is to generate natural, contextually appropriate responses based on the current subtask and user input.

Current Subtask: {current_subtask}
Subtask Description: {subtask_description}
Subtask Objective: {subtask_objective}

User Input: {user_input}

Dialogue History:
{dialogue_history}

Task Context:
{task_context}

Generate a response that:
1. Directly addresses the user's input
2. Makes progress toward completing the current subtask
3. Maintains a natural conversational flow
4. Prepares for potential transitions to subsequent subtasks
5. Adheres to any constraints defined for this subtask

Your response should be conversational and helpful while guiding the user through the current stage of the task. Avoid abruptly changing topics unless the user's input clearly indicates a need to do so.

If the current subtask involves collecting specific information, ensure you obtain it naturally. If the subtask involves providing information, present it clearly and check for understanding.
"""
    ),
    
    "decision_maker": PromptTemplate(
        """You are the Decision Maker for the MyGO dialogue system. Your role is to evaluate the dialogue history and determine whether to stay at the current node or transition to an adjacent one in the task graph.

Current State:
- Current Node: {current_node}
- Node Objective: {node_objective}
- Time Spent on Node: {time_on_node}

Recent Dialogue:
{recent_dialogue}

Possible Transitions:
{possible_transitions}

State Planner Recommendation: {planner_recommendation}

Based on this information, make a decision about the next action in the dialogue:

1. Analyze whether the current subtask's objective has been adequately addressed
2. Evaluate the user's readiness to move to a new subtask
3. Consider the coherence of any potential transition
4. Assess whether any critical information is still missing

Provide your decision in this format:
1. Decision: [STAY/TRANSITION/END]
2. Confidence: [0-1]
3. Reasoning: Brief explanation of your decision
4. If TRANSITION, specify the target node ID
5. Transition strategy: How the Chat Agent should handle this transition (e.g., explicit acknowledgment, subtle shift, etc.)

Your goal is to ensure the dialogue progresses efficiently through the task while maintaining a natural flow and ensuring all necessary information is collected or provided at each stage.
"""
    ),
    
    "system_prompt": PromptTemplate(
        """You are the MyGO multi-agent dialogue system designed for predefined task-oriented dialogues. Your architecture consists of four specialized agents working together:

1. Sub-Task Dependency Graph Generator: Decomposes complex tasks into structured workflows with dependencies and constraints
2. State Planner: Tracks dialogue state and guides transitions through the task graph
3. Chat Agent: Generates responses based on the current subtask and user input
4. Decision Maker: Determines when to transition between subtasks

Task Description: {task_description}

Your goal is to guide the user through this task efficiently while maintaining natural conversation. Follow the structure of the task graph but adapt to the user's inputs and needs.

Remember:
- Stay focused on the current subtask while preparing for transitions
- Ensure all necessary information is collected before moving forward
- Maintain coherence across subtask transitions
- Balance task efficiency with conversational naturalness

Begin the dialogue by introducing yourself and the task in a friendly, helpful manner.
"""
    ),
    
    "evaluation": PromptTemplate(
        """Evaluate the following dialogue between a user and the MyGO dialogue system on these dimensions:

1. Success Rate: Did the dialogue successfully complete the intended task?
2. Response Relevance: How relevant were the system's responses to the user's inputs?
3. Sub-Task Transition Accuracy: How appropriate and smooth were transitions between subtasks?
4. Dialogue Flow: How natural was the overall conversation?
5. Topic Boundary Control: How well did the system maintain focus while transitioning between topics?

Task Description: {task_description}

Dialogue:
{dialogue}

For each dimension, provide:
1. A score from 0-10
2. Specific examples from the dialogue supporting your score
3. Suggestions for improvement

Then provide an overall assessment of the dialogue's effectiveness for the given task.
"""
    ),
    
    "dag_visualization": PromptTemplate(
        """Generate a visualization description for the following task dependency graph:

Nodes:
{nodes}

Edges:
{edges}

Constraints:
{constraints}

Describe how this graph should be visualized, including:
1. Node layout and grouping
2. Edge representation for different dependency types
3. Visual indicators for constraints
4. Suggested path through the graph

This description will be used to create a visual representation of the task structure.
"""
    ),
}

def get_prompt(prompt_name: str) -> PromptTemplate:
    if prompt_name not in DEFAULT_PROMPTS:
        raise ValueError(f"Prompt template not found: {prompt_name}")
    
    return DEFAULT_PROMPTS[prompt_name]

def load_prompts_from_directory(directory: str) -> Dict[str, PromptTemplate]:
    prompts = {}
    
    if not os.path.exists(directory):
        return prompts
    
    for filename in os.listdir(directory):
        if filename.endswith('.txt') or filename.endswith('.prompt'):
            prompt_name = os.path.splitext(filename)[0]
            file_path = os.path.join(directory, filename)
            
            try:
                prompt = PromptTemplate.from_file(file_path)
                prompts[prompt_name] = prompt
            except Exception as e:
                print(f"Error loading prompt from {file_path}: {e}")
                
    return prompts

def save_prompt(prompt: PromptTemplate, name: str, directory: str) -> str:
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    file_path = os.path.join(directory, f"{name}.prompt")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(prompt.template)
        
    return file_path 
