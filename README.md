# MyGO: Mapping Your Goals with Multi-Agent for Predefined Task-Oriented Dialogue in LLMs

Conversational AI powered by Large Language Models (LLMs) has become a pivotal area of research in computer science, significantly advancing task-oriented dialogue (TOD) systems. However, traditional TOD systems primarily focus on addressing tasks initiated by users, often overlooking scenarios where the system itself predefines tasks to be completed through dialogue. In such system-predefined task settings, dialogues can easily drift from the intended complex task objectives, leading to inefficiencies. To address these limitations, we propose MyGO, a novel multi-agent system that leverages a sub-task graph to guide dialogue generation. By decomposing system-defined objectives into structured workflows, MyGO ensures alignment with task objectives while adapting to user inputs. Through experimental results, MyGO demonstrates superior performance across various evaluation metrics, showcasing its ability to manage complex tasks with precision and coherence while maintaining focus on task objectives. MyGO paves a new direction for conversational AI and lays a solid foundation for future advancements in multi-agent dialogue systems.

## Contributions

- We address a critical gap in TOD systems by introducing a novel scenario where the system proactively guides users through complex predefined workflows, rather than merely responding to user initiatives. This paradigm shift significantly broadens the scope and applicability of TOD systems to domains requiring structured guidance.

- We propose MyGO, a multi-agent system that enhances TOD management by integrating specialized agents and decomposing tasks into a structured graph with three dependency types and four constraint dimensions. This approach ensures efficient dialogue processes and clear dependency representation.

- We introduce comprehensive evaluation criteria and a dataset across 14 domains for predefined TODs, assessing metrics like Success Rate, Response Relevance, and Sub-Task Transition Accuracy, providing detailed insights to improve dialogue quality.

- Extensive experiments demonstrate that MyGO achieves state-of-the-art performance on our constructed benchmarks, showcasing precise sub-task transitions and coherent dialogue flow, and advancing multi-agent TOD system capabilities.

## MyGO 🤖

Our multi-agent dialogue system, highlighting its key components and processes. The system is structured around four main agents: the Sub-Task Dependency Graph Generator, State Planner, Chat Agent and Decision Maker. The Sub-Task Dependency Graph Generator constructs the task as a graph, utilizing three types of dependencies and four constraint dimensions to accurately map out the task's structure. The State Planner is responsible for maintaining the task's state, using the sub-task graph to track progression and guide transitions. The Chat Agent generates responses based on the current sub-task objective, constraints, and dialogue memory, ensuring contextually appropriate communication. The Decision Maker evaluates user input and conversation history to determine whether to remain at the current node, proceed forward, or rollback to a previous node, optimizing navigation through the sub-task graph. This decision is guided by the planner strategy and state management, ensuring logical and efficient task execution. An overview of our framework is illustrated below:

![MyGO FrameWork](resource/fig1.png)

## Sub-Task Dependency Graph Generator ⚖️

The Sub-Task Dependency Graph Generator transforms complex tasks into structured sub-task graphs through three-phase processing: task decomposition, dependency modeling, and constraint integration.

The workflow of Sub-Task Dependency Graph Generator is shown below:
![Graph Generation](resource/fig2.png)

