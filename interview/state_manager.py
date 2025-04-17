from typing import Dict, Any, List, Optional


class InterviewStateManager:
    """Manager for interview state."""
    
    def __init__(self):
        """Initialize the interview state manager."""
        self.reset()
        
    def reset(self) -> None:
        """Reset the interview state."""
        self.state = {
            "current_step": "name",
            "candidate_info": {},
            "first_name": "",
            "tech_stack": [],
            "current_tech": None,
            "questions_asked_for_current_tech": 0,
            "asked_questions": {},
            "current_question": "",
            "tech_questions": {},
            "interview_complete": False
        }
        
    def get_current_step(self) -> str:
        """Get the current interview step.
        
        Returns:
            Current step
        """
        return self.state["current_step"]
        
    def update_current_step(self, step: str) -> None:
        """Update the current interview step.
        
        Args:
            step: New step
        """
        self.state["current_step"] = step
        
    def store_candidate_info(self, step: str, value: str) -> None:
        """Store candidate information.
        
        Args:
            step: Information type
            value: Information value
        """
        self.state["candidate_info"][step] = value
        
        # Special handling for name - store it for personalization
        if step == "name":
            # Try to extract first name for more natural conversation
            name_parts = value.strip().split()
            if name_parts:
                self.state["first_name"] = name_parts[0]
            else:
                self.state["first_name"] = value.strip()
                
    def get_candidate_info(self) -> Dict[str, str]:
        """Get candidate information.
        
        Returns:
            Candidate information
        """
        return self.state["candidate_info"]
        
    def get_first_name(self) -> str:
        """Get candidate's first name.
        
        Returns:
            First name
        """
        return self.state["first_name"]
        
    def set_tech_stack(self, technologies: List[str]) -> None:
        """Set the technology stack.
        
        Args:
            technologies: List of technologies
        """
        self.state["tech_stack"] = technologies
        
    def get_tech_stack(self) -> List[str]:
        """Get the technology stack.
        
        Returns:
            Technology stack
        """
        return self.state["tech_stack"]
        
    def set_current_tech(self, tech: str) -> None:
        """Set the current technology.
        
        Args:
            tech: Technology name
        """
        self.state["current_tech"] = tech
        self.state["questions_asked_for_current_tech"] = 0
        
    def get_current_tech(self) -> str:
        """Get the current technology.
        
        Returns:
            Current technology
        """
        return self.state["current_tech"]
        
    def increment_questions_asked(self) -> int:
        """Increment the count of questions asked for the current technology.
        
        Returns:
            New count
        """
        self.state["questions_asked_for_current_tech"] += 1
        return self.state["questions_asked_for_current_tech"]
        
    def get_questions_asked_count(self) -> int:
        """Get the count of questions asked for the current technology.
        
        Returns:
            Count of questions asked
        """
        return self.state["questions_asked_for_current_tech"]
        
    def store_question(self, question: str) -> None:
        """Store the current question.
        
        Args:
            question: Question text
        """
        self.state["current_question"] = question
        
    def get_current_question(self) -> str:
        """Get the current question.
        
        Returns:
            Current question
        """
        return self.state["current_question"]
        
    def store_tech_questions(self, tech_questions: Dict[str, List[str]]) -> None:
        """Store technical questions for all technologies.
        
        Args:
            tech_questions: Dictionary of questions by technology
        """
        self.state["tech_questions"] = tech_questions
        
    def get_tech_questions(self, tech: Optional[str] = None) -> Any:
        """Get technical questions.
        
        Args:
            tech: Technology name (optional)
            
        Returns:
            All questions if tech is None, else questions for the specified technology
        """
        if tech:
            return self.state["tech_questions"].get(tech, [])
        return self.state["tech_questions"]
        
    def store_answer(self, tech: str, question: str, answer: str) -> None:
        """Store an answer to a technical question.
        
        Args:
            tech: Technology name
            question: Question text
            answer: Answer text
        """
        if tech not in self.state["asked_questions"]:
            self.state["asked_questions"][tech] = []
            
        self.state["asked_questions"][tech].append({
            "question": question,
            "answer": answer
        })
        
    def get_asked_questions(self, tech: Optional[str] = None) -> Any:
        """Get asked questions and answers.
        
        Args:
            tech: Technology name (optional)
            
        Returns:
            All asked questions if tech is None, else questions for the specified technology
        """
        if tech:
            return self.state["asked_questions"].get(tech, [])
        return self.state["asked_questions"]
        
    def mark_interview_complete(self) -> None:
        """Mark the interview as complete."""
        self.state["interview_complete"] = True
        
    def is_interview_complete(self) -> bool:
        """Check if the interview is complete.
        
        Returns:
            True if complete, False otherwise
        """
        return self.state["interview_complete"] 