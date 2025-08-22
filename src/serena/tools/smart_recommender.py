"""
Smart tool recommendation system for Serena.
Helps users choose the most appropriate tool based on their query characteristics.
"""

import re
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


class QueryType(Enum):
    """Types of user queries for tool recommendation."""
    SYMBOL_SEARCH = "symbol_search"
    TEXT_SEARCH = "text_search"
    FILE_OPERATION = "file_operation"
    CODE_NAVIGATION = "code_navigation"
    PROJECT_EXPLORATION = "project_exploration"
    CODE_ANALYSIS = "code_analysis"


class ProjectCharacteristics(Enum):
    """Project size and complexity characteristics."""
    SMALL = "small"      # < 1000 files
    MEDIUM = "medium"    # 1000-10000 files  
    LARGE = "large"      # > 10000 files
    UNKNOWN = "unknown"


@dataclass
class ToolRecommendation:
    """Recommendation for a specific tool."""
    tool_name: str
    confidence: float  # 0.0 to 1.0
    reason: str
    parameters_suggestion: Dict[str, any] = None


class SmartToolRecommender:
    """Intelligent tool recommendation system."""
    
    def __init__(self):
        # Pattern-based query classification
        self.query_patterns = {
            QueryType.SYMBOL_SEARCH: [
                r"find.*(?:function|method|class|symbol|definition)",
                r"(?:where|locate).*(?:defined|implemented)",
                r"search.*(?:symbol|class|function|method)",
                r"(?:function|class|method).*(?:called|named)",
            ],
            QueryType.TEXT_SEARCH: [
                r"search.*(?:text|string|pattern|content)",
                r"find.*(?:all|occurrences|matches|instances)",
                r"grep.*for",
                r"(?:contains|includes|has).*(?:text|string)",
            ],
            QueryType.CODE_NAVIGATION: [
                r"(?:go to|jump to|navigate to)",
                r"show.*(?:references|usages|calls)",
                r"find.*(?:references|callers|usage)",
                r"who.*(?:calls|uses|references)",
            ],
            QueryType.PROJECT_EXPLORATION: [
                r"(?:overview|structure|architecture)",
                r"what.*(?:files|directories|modules)",
                r"list.*(?:files|directories|symbols)",
                r"explore.*(?:project|codebase)",
            ],
            QueryType.FILE_OPERATION: [
                r"(?:create|write|edit|modify|update).*file",
                r"(?:read|open|show).*file",
                r"file.*(?:content|contents)",
            ],
        }
        
        # Tool capabilities and characteristics
        self.tool_profiles = {
            "find_symbol": {
                "best_for": [QueryType.SYMBOL_SEARCH, QueryType.CODE_NAVIGATION],
                "characteristics": ["precise", "fast", "symbol_aware"],
                "limitations": ["requires_exact_names", "no_fuzzy_search"],
                "optimal_project_size": [ProjectCharacteristics.MEDIUM, ProjectCharacteristics.LARGE]
            },
            "search_for_pattern": {
                "best_for": [QueryType.TEXT_SEARCH],
                "characteristics": ["flexible", "regex_support", "context_aware"],
                "limitations": ["can_be_slow", "large_results"],
                "optimal_project_size": [ProjectCharacteristics.SMALL, ProjectCharacteristics.MEDIUM]
            },
            "get_symbols_overview": {
                "best_for": [QueryType.PROJECT_EXPLORATION, QueryType.CODE_ANALYSIS],
                "characteristics": ["quick_overview", "structured"],
                "limitations": ["file_specific", "no_search"],
                "optimal_project_size": [ProjectCharacteristics.SMALL, ProjectCharacteristics.MEDIUM, ProjectCharacteristics.LARGE]
            },
            "read": {
                "best_for": [QueryType.FILE_OPERATION],
                "characteristics": ["direct_access", "simple"],
                "limitations": ["no_search", "single_file"],
                "optimal_project_size": [ProjectCharacteristics.SMALL, ProjectCharacteristics.MEDIUM]
            },
            "list_dir": {
                "best_for": [QueryType.PROJECT_EXPLORATION],
                "characteristics": ["directory_structure", "recursive"],
                "limitations": ["no_content_search"],
                "optimal_project_size": [ProjectCharacteristics.SMALL, ProjectCharacteristics.MEDIUM, ProjectCharacteristics.LARGE]
            }
        }
        
        # Fortran-specific recommendations
        self.fortran_specific_tips = {
            "modules": "For Fortran modules, use find_symbol with 'module' in name_path",
            "subroutines": "For Fortran subroutines, find_symbol works well with exact names", 
            "interfaces": "Fortran interfaces can be found using find_symbol with appropriate filters",
            "preprocessor": "For preprocessor directives like #include, use search_for_pattern",
            "common_blocks": "Search for common blocks using pattern search with 'common'",
            "derived_types": "Use find_symbol with 'type' in name_path for derived types",
            "use_statements": "Find module dependencies with search_for_pattern using 'use \\w+'",
            "type_bound_procedures": "Type-bound procedures are best found via their parent type",
            "generic_interfaces": "Generic interfaces can be located using interface name searches"
        }
        
        # Fortran search templates for quick access
        self.fortran_search_templates = {
            "module_procedures": {
                "pattern": r"^\s*(?:contains|procedure)",
                "tool": "search_for_pattern",
                "description": "Find module procedures and type-bound procedures"
            },
            "use_statements": {
                "pattern": r"^\s*use\s+(\w+)",
                "tool": "search_for_pattern", 
                "description": "Find module dependencies"
            },
            "derived_types": {
                "pattern": r"^\s*type(?:\s*,.*?)?\s*::\s*(\w+)",
                "tool": "search_for_pattern",
                "description": "Find derived type definitions"
            },
            "interfaces": {
                "pattern": r"^\s*interface\s+(\w+)",
                "tool": "search_for_pattern",
                "description": "Find generic and abstract interfaces"
            }
        }

    def classify_query(self, query: str) -> QueryType:
        """Classify user query into a query type."""
        query_lower = query.lower()
        
        for query_type, patterns in self.query_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return query_type
        
        # Default classification based on keywords
        if any(word in query_lower for word in ["find", "search", "locate", "where"]):
            if any(word in query_lower for word in ["function", "class", "method", "symbol", "definition"]):
                return QueryType.SYMBOL_SEARCH
            else:
                return QueryType.TEXT_SEARCH
        
        return QueryType.PROJECT_EXPLORATION

    def estimate_project_size(self, project_info: Dict = None) -> ProjectCharacteristics:
        """Estimate project size based on available information."""
        if not project_info:
            return ProjectCharacteristics.UNKNOWN
            
        # This could be enhanced with actual project analysis
        file_count = project_info.get("file_count", 0)
        if file_count < 1000:
            return ProjectCharacteristics.SMALL
        elif file_count < 10000:
            return ProjectCharacteristics.MEDIUM
        else:
            return ProjectCharacteristics.LARGE

    def recommend_tools(self, query: str, project_info: Dict = None, 
                       language: str = None) -> List[ToolRecommendation]:
        """Generate tool recommendations based on query and context."""
        query_type = self.classify_query(query)
        project_size = self.estimate_project_size(project_info)
        
        recommendations = []
        
        # Score each tool based on suitability
        for tool_name, profile in self.tool_profiles.items():
            confidence = 0.0
            reasons = []
            
            # Base score from query type matching
            if query_type in profile["best_for"]:
                confidence += 0.7
                reasons.append(f"Excellent for {query_type.value} tasks")
            
            # Project size compatibility
            if project_size in profile["optimal_project_size"]:
                confidence += 0.2
                reasons.append(f"Suitable for {project_size.value} projects")
            elif project_size == ProjectCharacteristics.LARGE and "can_be_slow" in profile["limitations"]:
                confidence -= 0.3
                reasons.append("May be slow on large projects")
            
            # Language-specific adjustments
            if language == "fortran":
                if tool_name == "find_symbol":
                    confidence += 0.1
                    reasons.append("Excellent for Fortran symbol navigation")
                elif tool_name == "search_for_pattern" and "preprocessor" in query.lower():
                    confidence += 0.2
                    reasons.append("Good for Fortran preprocessor directives")
                
                # Check for Fortran-specific keywords and boost appropriate tools
                fortran_keywords = ["module", "subroutine", "function", "interface", "type", "use", "common"]
                for keyword in fortran_keywords:
                    if keyword in query.lower():
                        if tool_name == "find_symbol" and keyword in ["module", "subroutine", "function", "interface"]:
                            confidence += 0.15
                            reasons.append(f"Optimal for finding Fortran {keyword}s")
                        elif tool_name == "search_for_pattern" and keyword in ["use", "common", "type"]:
                            confidence += 0.15
                            reasons.append(f"Good for searching Fortran {keyword} patterns")
            
            # Only recommend tools with reasonable confidence
            if confidence > 0.3:
                suggestion_params = self._generate_parameter_suggestions(
                    tool_name, query, query_type, project_size, language
                )
                
                recommendation = ToolRecommendation(
                    tool_name=tool_name,
                    confidence=min(confidence, 1.0),
                    reason="; ".join(reasons),
                    parameters_suggestion=suggestion_params
                )
                recommendations.append(recommendation)
        
        # Add Fortran-specific template suggestions if applicable
        if language == "fortran":
            template_recommendations = self._get_fortran_template_recommendations(query)
            recommendations.extend(template_recommendations)
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x.confidence, reverse=True)
        
        return recommendations[:3]  # Return top 3 recommendations

    def _generate_parameter_suggestions(self, tool_name: str, query: str, 
                                      query_type: QueryType, project_size: ProjectCharacteristics,
                                      language: str = None) -> Dict:
        """Generate parameter suggestions for specific tools."""
        suggestions = {}
        
        if tool_name == "search_for_pattern":
            suggestions["context_lines_before"] = 1
            suggestions["context_lines_after"] = 1
            suggestions["restrict_search_to_code_files"] = True
            
            if project_size == ProjectCharacteristics.LARGE:
                suggestions["relative_path"] = "src/"  # Suggest starting with main source directory
                
            # Fortran-specific parameter suggestions
            if language == "fortran":
                # Suggest appropriate patterns based on query
                if "module" in query.lower():
                    suggestions["substring_pattern"] = r"^\s*module\s+\w+"
                elif "use" in query.lower():
                    suggestions["substring_pattern"] = r"^\s*use\s+\w+"
                elif "interface" in query.lower():
                    suggestions["substring_pattern"] = r"^\s*interface\s+\w+"
                    suggestions["context_lines_after"] = 3
                elif "type" in query.lower():
                    suggestions["substring_pattern"] = r"^\s*type(?:\s*,.*?)?\s*::\s*\w+"
                
        elif tool_name == "find_symbol":
            suggestions["depth"] = 0  # Start with top-level symbols
            suggestions["include_body"] = False  # Avoid large outputs initially
            
            # Fortran-specific symbol search suggestions
            if language == "fortran":
                if "module" in query.lower():
                    suggestions["include_kinds"] = [2]  # Module kind
                elif any(word in query.lower() for word in ["subroutine", "function"]):
                    suggestions["include_kinds"] = [12]  # Function kind
                elif "type" in query.lower():
                    suggestions["include_kinds"] = [23]  # Struct kind for derived types
        elif tool_name == "get_symbols_overview":
            suggestions["max_answer_chars"] = 50000  # Reasonable limit for overview
            
        return suggestions

    def _get_fortran_template_recommendations(self, query: str) -> List[ToolRecommendation]:
        """Generate Fortran-specific template recommendations based on query."""
        template_recommendations = []
        
        for template_name, template_info in self.fortran_search_templates.items():
            # Check if query matches this template's purpose
            template_keywords = template_name.split('_')
            if any(keyword in query.lower() for keyword in template_keywords):
                confidence = 0.8  # High confidence for template matches
                
                # Create recommendation with pre-filled parameters
                params = {
                    "substring_pattern": template_info["pattern"],
                    "context_lines_before": template_info.get("context_lines", 1),
                    "context_lines_after": template_info.get("context_lines", 1),
                    "restrict_search_to_code_files": True
                }
                
                recommendation = ToolRecommendation(
                    tool_name=template_info["tool"],
                    confidence=confidence,
                    reason=f"Fortran template: {template_info['description']}",
                    parameters_suggestion=params
                )
                template_recommendations.append(recommendation)
                
        return template_recommendations

    def get_fortran_specific_tip(self, query: str) -> Optional[str]:
        """Get Fortran-specific recommendations based on query."""
        query_lower = query.lower()
        
        for keyword, tip in self.fortran_specific_tips.items():
            if keyword in query_lower:
                return tip
        
        # General Fortran tips
        if any(word in query_lower for word in ["module", "subroutine", "function", "interface"]):
            return ("For Fortran code analysis, start with get_symbols_overview to understand "
                   "the file structure, then use find_symbol for specific symbols.")
        
        return None

    def format_recommendations(self, recommendations: List[ToolRecommendation], 
                             query: str, language: str = None) -> str:
        """Format recommendations into a user-friendly string."""
        if not recommendations:
            return "No specific tool recommendations available for this query."
        
        result = f"**Tool Recommendations for: '{query}'**\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            result += f"{i}. **{rec.tool_name}** (confidence: {rec.confidence:.1%})\n"
            result += f"   • {rec.reason}\n"
            
            if rec.parameters_suggestion:
                result += "   • Suggested parameters:\n"
                for param, value in rec.parameters_suggestion.items():
                    result += f"     - {param}: {value}\n"
            result += "\n"
        
        # Add language-specific tip if available
        if language == "fortran":
            fortran_tip = self.get_fortran_specific_tip(query)
            if fortran_tip:
                result += f"**Fortran-specific tip:** {fortran_tip}\n"
        
        return result


# Global recommender instance
_recommender = SmartToolRecommender()


def get_tool_recommendation(query: str, project_info: Dict = None, 
                          language: str = None) -> str:
    """Public function to get tool recommendations."""
    recommendations = _recommender.recommend_tools(query, project_info, language)
    return _recommender.format_recommendations(recommendations, query, language)