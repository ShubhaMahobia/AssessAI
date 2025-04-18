import re
from typing import List, Dict, Any


def parse_tech_stack(tech_stack_input: str, max_techs: int = 4) -> List[str]:
    """Parse the tech stack input and identify technologies.
    
    Args:
        tech_stack_input: User's tech stack description
        max_techs: Maximum number of technologies to return
        
    Returns:
        List of technologies
    """
    # Split by commas and clean up
    technologies = [tech.strip().lower() for tech in tech_stack_input.split(',')]
    
    # Remove empty items
    technologies = [tech for tech in technologies if tech]
    
    # Limit to max_techs technologies to keep interview reasonable length
    technologies = technologies[:max_techs]
    
    # Default to general if no technologies specified
    if not technologies:
        technologies = ["general"]
        
    return technologies


def parse_questions_from_response(response: str) -> List[str]:
    """Parse questions from the LLM response.
    
    Args:
        response: Response from the LLM
        
    Returns:
        List of questions
    """
    questions = []
    if response:
        # Simple parsing: split by numbers and clean up
        for line in response.split('\n'):
            line = line.strip()
            if line and (line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
                # Remove the number prefix
                question = re.sub(r'^\d+\.?\s*', '', line)
                questions.append(question)
    
    return questions


def get_default_questions(tech: str) -> List[str]:
    """Get default questions for a technology.
    
    Args:
        tech: Technology name
        
    Returns:
        List of default questions
    """
    return [
        f"What are the main features or characteristics of {tech}?",
        f"What are the advantages of using {tech} compared to alternatives?",
        f"What is a common challenge when working with {tech}?"
    ] 