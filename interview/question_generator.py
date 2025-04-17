from typing import Dict, List, Any
from models.llm_client import LLMClient
from utils.tech_parser import parse_questions_from_response, get_default_questions


class QuestionGenerator:
    """Generator for interview questions."""
    
    def __init__(self, llm_client: LLMClient, prompt_templates: Any):
        """Initialize the question generator.
        
        Args:
            llm_client: LLM client for generating responses
            prompt_templates: Templates for prompts
        """
        self.llm_client = llm_client
        self.prompt_templates = prompt_templates
        
    def generate_tech_questions(self, tech_stack: List[str]) -> Dict[str, List[str]]:
        """Generate technical questions for each technology in the stack.
        
        Args:
            tech_stack: List of technologies
            
        Returns:
            Dictionary of questions by technology
        """
        tech_questions = {}
        
        for tech in tech_stack:
            # Generate questions for this technology using LLM
            prompt = self.prompt_templates.PROMPT_TEMPLATES["tech_question_generation"]
            context = {"technology": tech}
            
            response = self.llm_client.generate_response(prompt, context)
            
            # Parse questions from the response
            questions = parse_questions_from_response(response)
            
            # If we didn't get 3 questions, generate some defaults
            default_questions = get_default_questions(tech)
            
            while len(questions) < 3:
                questions.append(default_questions[len(questions)])
            
            # Store questions
            tech_questions[tech] = questions[:3]  # Ensure exactly 3 questions
        
        return tech_questions 