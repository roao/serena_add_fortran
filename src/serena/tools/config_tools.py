import json

from serena.config.context_mode import SerenaAgentMode
from serena.tools import Tool, ToolMarkerDoesNotRequireActiveProject, ToolMarkerOptional
from serena.tools.smart_recommender import get_tool_recommendation


class ActivateProjectTool(Tool, ToolMarkerDoesNotRequireActiveProject):
    """
    Activates a project by name.
    """

    def apply(self, project: str) -> str:
        """
        Activates the project with the given name.

        :param project: the name of a registered project to activate or a path to a project directory
        """
        active_project = self.agent.activate_project_from_path_or_name(project)
        if active_project.is_newly_created:
            result_str = (
                f"Created and activated a new project with name '{active_project.project_name}' at {active_project.project_root}, language: {active_project.project_config.language.value}. "
                "You can activate this project later by name.\n"
                f"The project's Serena configuration is in {active_project.path_to_project_yml()}. In particular, you may want to edit the project name and the initial prompt."
            )
        else:
            result_str = f"Activated existing project with name '{active_project.project_name}' at {active_project.project_root}, language: {active_project.project_config.language.value}"

        if active_project.project_config.initial_prompt:
            result_str += f"\nAdditional project information:\n {active_project.project_config.initial_prompt}"
        result_str += (
            f"\nAvailable memories:\n {json.dumps(list(self.memories_manager.list_memories()))}"
            + "You should not read these memories directly, but rather use the `read_memory` tool to read them later if needed for the task."
        )
        result_str += f"\nAvailable tools:\n {json.dumps(self.agent.get_active_tool_names())}"
        return result_str


class RemoveProjectTool(Tool, ToolMarkerDoesNotRequireActiveProject, ToolMarkerOptional):
    """
    Removes a project from the Serena configuration.
    """

    def apply(self, project_name: str) -> str:
        """
        Removes a project from the Serena configuration.

        :param project_name: Name of the project to remove
        """
        self.agent.serena_config.remove_project(project_name)
        return f"Successfully removed project '{project_name}' from configuration."


class SwitchModesTool(Tool, ToolMarkerOptional):
    """
    Activates modes by providing a list of their names
    """

    def apply(self, modes: list[str]) -> str:
        """
        Activates the desired modes, like ["editing", "interactive"] or ["planning", "one-shot"]

        :param modes: the names of the modes to activate
        """
        mode_instances = [SerenaAgentMode.load(mode) for mode in modes]
        self.agent.set_modes(mode_instances)

        # Inform the Agent about the activated modes and the currently active tools
        result_str = f"Successfully activated modes: {', '.join([mode.name for mode in mode_instances])}" + "\n"
        result_str += "\n".join([mode_instance.prompt for mode_instance in mode_instances]) + "\n"
        result_str += f"Currently active tools: {', '.join(self.agent.get_active_tool_names())}"
        return result_str


class GetCurrentConfigTool(Tool, ToolMarkerOptional):
    """
    Prints the current configuration of the agent, including the active and available projects, tools, contexts, and modes.
    """

    def apply(self) -> str:
        """
        Print the current configuration of the agent, including the active and available projects, tools, contexts, and modes.
        """
        return self.agent.get_current_config_overview()


class RecommendToolTool(Tool, ToolMarkerOptional):
    """
    Recommends the most suitable tools based on your query and project characteristics.
    """

    def apply(self, query_description: str) -> str:
        """
        Get intelligent tool recommendations based on what you want to accomplish.
        This helps you choose the most appropriate tool and parameters for your task.

        :param query_description: Description of what you want to do (e.g., "find all functions named calculate", 
            "search for error handling patterns", "explore project structure")
        :return: Recommended tools with explanations and suggested parameters
        """
        # Gather project context information
        project_info = {}
        language = None
        
        if hasattr(self, 'project') and self.project:
            try:
                # Get project language if available
                if hasattr(self.project, 'project_config') and self.project.project_config:
                    language = getattr(self.project.project_config, 'language', None)
                    if language:
                        language = str(language).lower()
                
                # Get basic project statistics
                # This could be enhanced with actual file counting
                project_info = {
                    "language": language,
                    "has_active_project": True
                }
            except Exception:
                # Fallback if project info is not available
                pass
        
        recommendations = get_tool_recommendation(query_description, project_info, language)
        return recommendations
