from typing import List, Dict, Any, Optional
import os
import random

# Import modular components
from models.llm_client import LLMClient
from templates.prompts import PromptTemplates
from templates.consent_prompts import ConsentPrompts
from utils.validators import validate_input
from utils.tech_parser import parse_tech_stack
from interview.state_manager import InterviewStateManager
from interview.question_generator import QuestionGenerator
from database.models import DatabaseManager


class ChatbotController:
    def __init__(self, api_key: str = None, db_path: str = "sqlite:///interviews.db"):
        """Initialize the ChatbotController with Gemini API.
        
        Args:
            api_key: Google API key for Gemini access
            db_path: Database connection string
        """
        # Company and interviewer information
        self.company_name = "PGAGI"
        self.interviewer_name = "AVA"
        
        # Initialize components
        self.llm_client = LLMClient(api_key=api_key, model_name="gemini-1.5-flash")
        self.prompt_templates = PromptTemplates(self.company_name, self.interviewer_name)
        self.consent_prompts = ConsentPrompts(self.company_name)
        self.state_manager = InterviewStateManager()
        self.question_generator = QuestionGenerator(self.llm_client, self.prompt_templates)
        self.db_manager = DatabaseManager(db_path)
        
        # GDPR consent state
        self.candidate_id = None
        self.consent_requested = False
        self.consent_given = False
        self.gdpr_intro_shown = False
        
        # Initialize interview state
        self.reset_chat()
        
    def get_initial_prompt(self) -> str:
        """Get initial chat prompt message.
        
        Returns:
            Initial prompt message
        """
        # Set GDPR intro flag to show we're starting a new chat
        self.gdpr_intro_shown = True
        
        # Start with the GDPR consent request first, then provide greeting
        gdpr_first_greeting = f"""Hi there! I'm {self.interviewer_name}, an AI technical interviewer for {self.company_name}.

I'll be conducting a technical interview to assess your qualifications for a developer role with our company. Before we begin, I need to inform you about our data storage policy:

{self.company_name} would like to store your interview data for evaluation and potential future hiring decisions.

{self.consent_prompts.CONSENT_REQUEST}"""
        
        return gdpr_first_greeting
    
    def process_user_input(self, user_input: str) -> str:
        """Process user input based on the current interview state.
        
        Args:
            user_input: Text input from the user
            
        Returns:
            Response message
        """
        # Check for exit command
        if user_input.strip().lower() == "exit":
            self.state_manager.mark_interview_finished()
            return "Thank you for participating in the interview. The session has been ended."
            
        if not user_input.strip():
            return "I didn't receive your response. Could you please provide an answer to the question?"
        
        # Process GDPR consent right at the beginning
        if self.gdpr_intro_shown and not self.consent_requested:
            self.consent_requested = True
            consent_response = self._process_consent_response(user_input)
            if consent_response:
                return consent_response
            
            # If we couldn't get a clear response, ask again
            return "Please respond with 'yes' or 'no' to indicate whether you consent to storing your interview data."
        
        # Check for input validation first
        current_step = self.state_manager.get_current_step()
        validation_result = validate_input(current_step, user_input)
        
        if not validation_result.get("valid", True):
            # Generate validation error message
            context = {
                "interviewer_name": self.interviewer_name,
                "company_name": self.company_name,
                "field_type": validation_result.get("field_type", ""),
                "error_message": validation_result.get("error", "")
            }
            
            message = self.llm_client.generate_response(
                self.prompt_templates.PROMPT_TEMPLATES["validation_error"], 
                context
            )
            
            if not message:
                message = validation_result.get("error", "Please provide a valid response.")
            
            return message
            
        # Record user input in our state
        self._store_user_response(user_input)
        
        # Generate next response
        next_response = self._get_next_response(user_input)
        
        # Add to chat history for display purposes only
        self.llm_client.add_to_history(user_input, next_response)
        
        return next_response
    
    def _process_consent_response(self, user_input: str) -> Optional[str]:
        """Process GDPR consent response.
        
        Args:
            user_input: User's consent response
            
        Returns:
            Response message or None if not a consent response
        """
        # Check for affirmative consent
        if user_input.lower() in ['yes', 'y', 'sure', 'okay', 'ok', 'agree', 'consent', 'i consent']:
            self.consent_given = True
            
            # Continue with the interview
            self.llm_client.add_to_history(user_input, self.consent_prompts.CONSENT_GIVEN)
            return self.consent_prompts.CONSENT_GIVEN
            
        # Handle consent refusal
        elif user_input.lower() in ['no', 'n', 'nope', 'disagree', 'do not consent', 'i do not consent']:
            # Mark consent declined, but continue interview
            self.llm_client.add_to_history(user_input, self.consent_prompts.CONSENT_DECLINED)
            return self.consent_prompts.CONSENT_DECLINED
        
        # Not a clear consent response
        return None
    
    def _store_user_response(self, user_input: str) -> None:
        """Store user's response based on current interview step.
        
        Args:
            user_input: User's input text
        """
        current_step = self.state_manager.get_current_step()
        
        # Information gathering phase
        if current_step in self.prompt_templates.INTERVIEW_FLOW:
            # Store the response in candidate info
            self.state_manager.store_candidate_info(current_step, user_input)
            
            # Special handling for tech stack
            if current_step == "tech_stack":
                technologies = parse_tech_stack(user_input)
                self.state_manager.set_tech_stack(technologies)
            
            # Progress to the next step
            steps = list(self.prompt_templates.INTERVIEW_FLOW.keys())
            current_index = steps.index(current_step)
            
            if current_index < len(steps) - 1:
                # Move to next information field
                self.state_manager.update_current_step(steps[current_index + 1])
            else:
                # If we've collected tech_stack, move to technical questions
                if current_step == "tech_stack":
                    tech_stack = self.state_manager.get_tech_stack()
                    if not tech_stack:
                        # No recognized tech, use general questions
                        tech_stack = ["general"]
                        self.state_manager.set_tech_stack(tech_stack)
                    
                    # Generate questions for each technology
                    tech_questions = self.question_generator.generate_tech_questions(tech_stack)
                    self.state_manager.store_tech_questions(tech_questions)
                    
                    # Set up for first technical question
                    self.state_manager.update_current_step("technical_questions")
                    self.state_manager.set_current_tech(tech_stack[0])
                    
                    # Create candidate record in database if consent was given
                    if self.consent_given:
                        self._create_candidate_record()
        
        # Technical questions phase
        elif current_step == "technical_questions":
            current_tech = self.state_manager.get_current_tech()
            current_question = self.state_manager.get_current_question()
            
            # Store the answer for the current question
            self.state_manager.store_answer(current_tech, current_question, user_input)
            
            # Increment the count of questions asked for current tech
            questions_asked = self.state_manager.increment_questions_asked()
            
            # If we've asked enough questions for this tech, move to next tech
            if questions_asked >= 3:
                tech_stack = self.state_manager.get_tech_stack()
                current_index = tech_stack.index(current_tech)
                
                if current_index < len(tech_stack) - 1:
                    # Move to next technology
                    next_tech = tech_stack[current_index + 1]
                    self.state_manager.set_current_tech(next_tech)
                else:
                    # We've gone through all techs, conclude the interview
                    self.state_manager.update_current_step("complete")
                    self.state_manager.mark_interview_complete()
                    
                    # Store interview responses if consent was given
                    if self.consent_given and self.candidate_id:
                        self._store_interview_responses()
    
    def _create_candidate_record(self) -> None:
        """Create a candidate record in the database."""
        # Prepare candidate data
        candidate_data = self.state_manager.get_candidate_info()
        
        # Create record with consent status
        self.candidate_id = self.db_manager.create_candidate(candidate_data, consent_given=self.consent_given)
    
    def _store_interview_responses(self) -> None:
        """Store interview responses in the database."""
        if not self.candidate_id or not self.consent_given:
            return
            
        # Prepare responses
        responses = {}
        for tech in self.state_manager.get_tech_stack():
            qa_pairs = self.state_manager.get_asked_questions(tech)
            if qa_pairs:
                responses[tech] = qa_pairs
        
        # Store in database
        self.db_manager.store_interview_responses(self.candidate_id, responses)
    
    def _get_next_response(self, user_input: str) -> str:
        """Get the next response based on current interview state and user input.
        
        Args:
            user_input: User's input text
            
        Returns:
            Next response text
        """
        current_step = self.state_manager.get_current_step()
        
        # Information gathering phase
        if current_step in self.prompt_templates.INTERVIEW_FLOW:
            # Get previous step and current question
            steps = list(self.prompt_templates.INTERVIEW_FLOW.keys())
            current_index = steps.index(current_step)
            prev_step = steps[current_index - 1] if current_index > 0 else None
            next_question = self.prompt_templates.INTERVIEW_FLOW[current_step]
            
            # Only use LLM for responses after the first question
            if prev_step:
                # Create prompt for response generation
                context = {
                    "interviewer_name": self.interviewer_name,
                    "company_name": self.company_name,
                    "prev_step": prev_step,
                    "user_input": user_input,
                    "next_question": next_question
                }
                
                response = self.llm_client.generate_response(
                    self.prompt_templates.PROMPT_TEMPLATES["info_gathering"], 
                    context
                )
                
                if response and len(response.strip()) > 0:
                    return response
                
                # Fallback to template-based response
                acknowledgment = self.prompt_templates.BASIC_ACKNOWLEDGMENTS.get(prev_step, "Thank you.")
                if "{name}" in acknowledgment:
                    acknowledgment = acknowledgment.format(name=self.state_manager.get_first_name())
                return f"{acknowledgment} {next_question}"
            else:
                return next_question
        
        # Technical questions phase
        elif current_step == "technical_questions":
            return self._get_technical_question_response(user_input)
        
        # Interview complete
        elif current_step == "complete":
            # Generate a personalized conclusion
            name = self.state_manager.get_first_name()
            technologies = ", ".join(self.state_manager.get_tech_stack())
            
            # Add GDPR notice if consent was given
            if self.consent_given:
                conclusion_message = self.consent_prompts.END_OF_INTERVIEW_DATA_NOTICE
            else:
                context = {
                    "interviewer_name": self.interviewer_name,
                    "company_name": self.company_name,
                    "candidate_name": name,
                    "technologies": technologies
                }
                
                conclusion_message = self.llm_client.generate_response(
                    self.prompt_templates.PROMPT_TEMPLATES["conclusion"], 
                    context
                )
                
                if not conclusion_message or len(conclusion_message.strip()) == 0:
                    conclusion_message = self.prompt_templates.CONCLUSION_MESSAGE
            
            # Mark interview as completely finished - cannot type anymore
            self.state_manager.mark_interview_finished()
            
            return conclusion_message
        
        # Fallback
        return "I'm not sure what to ask next. Let's restart the interview."
    
    def _get_technical_question_response(self, user_input: str) -> str:
        """Get the next technical question response.
        
        Args:
            user_input: User's input text
            
        Returns:
            Next technical question with appropriate acknowledgment
        """
        current_tech = self.state_manager.get_current_tech()
        questions_asked = self.state_manager.get_questions_asked_count()
        
        # Get available questions for this technology
        tech_questions = self.state_manager.get_tech_questions(current_tech)
        if not tech_questions or len(tech_questions) < 3:
            # If somehow we don't have questions, generate defaults
            tech_questions = [
                f"Can you explain the core principles or concepts of {current_tech}?",
                f"What are the main advantages and limitations of {current_tech} compared to alternatives?",
                f"How would you describe the architecture or structure of a typical {current_tech} application?"
            ]
        
        # First technical question for this tech (no acknowledgment needed)
        if questions_asked == 0:
            is_first_tech = current_tech == self.state_manager.get_tech_stack()[0]
            tech_stack_raw = self.state_manager.get_candidate_info().get("tech_stack", "")
            
            if is_first_tech:
                # First technology - transition from information gathering
                context = {
                    "interviewer_name": self.interviewer_name,
                    "company_name": self.company_name,
                    "tech_stack": tech_stack_raw,
                    "current_tech": current_tech,
                    "first_question": tech_questions[0]
                }
                
                response = self.llm_client.generate_response(
                    self.prompt_templates.PROMPT_TEMPLATES["tech_transition"], 
                    context
                )
                
                if response and len(response.strip()) > 0:
                    # Store the first question
                    self.state_manager.store_question(tech_questions[0])
                    return response
                    
                # Fallback to template
                transition = f"{self.prompt_templates.BASIC_ACKNOWLEDGMENTS['tech_stack']} Now I'd like to ask you some theoretical questions about {current_tech}."
                self.state_manager.store_question(tech_questions[0])
                return f"{transition}\n\n{tech_questions[0]}"
            else:
                # Not the first technology - transition from previous tech
                previous_tech_index = self.state_manager.get_tech_stack().index(current_tech) - 1
                previous_tech = self.state_manager.get_tech_stack()[previous_tech_index]
                
                context = {
                    "interviewer_name": self.interviewer_name,
                    "company_name": self.company_name,
                    "previous_tech": previous_tech,
                    "next_tech": current_tech,
                    "first_question": tech_questions[0]
                }
                
                response = self.llm_client.generate_response(
                    self.prompt_templates.PROMPT_TEMPLATES["tech_transition_next"], 
                    context
                )
                
                if response and len(response.strip()) > 0:
                    # Store the first question
                    self.state_manager.store_question(tech_questions[0])
                    return response
                
                # Fallback to template
                transition = f"Great. Now I'd like to ask you some theoretical questions about {current_tech}."
                self.state_manager.store_question(tech_questions[0])
                return f"{transition}\n\n{tech_questions[0]}"
        
        # Next questions for current tech
        else:
            # Get the next question index (it should always be equal to the current questions_asked)
            next_question_index = questions_asked
            
            # If we somehow ran out of questions, use the last one again
            if next_question_index >= len(tech_questions):
                next_question_index = len(tech_questions) - 1
            
            # Get the next question
            next_question = tech_questions[next_question_index]
            
            # Store the current question
            self.state_manager.store_question(next_question)
            
            # Get the previous question and answer
            asked_questions = self.state_manager.get_asked_questions(current_tech)
            
            # There should always be at least one previous question/answer at this point
            if asked_questions and len(asked_questions) > 0:
                previous_question = asked_questions[-1]["question"]
                previous_answer = asked_questions[-1]["answer"]
                
                # Generate response with acknowledgment and next question
                context = {
                    "interviewer_name": self.interviewer_name,
                    "company_name": self.company_name,
                    "technology": current_tech,
                    "previous_question": previous_question,
                    "previous_answer": previous_answer,
                    "next_question": next_question
                }
                
                response = self.llm_client.generate_response(
                    self.prompt_templates.PROMPT_TEMPLATES["next_tech_question"], 
                    context
                )
                
                if response and len(response.strip()) > 0:
                    return response
            
            # Fallback to template
            acknowledgment = random.choice(self.prompt_templates.ACKNOWLEDGMENT_RESPONSES)
            return f"{acknowledgment} {next_question}"
    
    def get_chat_history(self) -> List[Dict[str, str]]:
        """Get the current chat history.
        
        Returns:
            List of chat messages with roles and content
        """
        history = []
        for message in self.llm_client.get_chat_history():
            role = "assistant" if message["role"] == "model" else "user"
            if len(message["parts"]) > 0:
                content = message["parts"][0]
                history.append({"role": role, "content": content})
        return history
    
    def get_candidate_info(self) -> Dict[str, Any]:
        """Get the gathered candidate information.
        
        Returns:
            Dictionary of candidate information
        """
        return self.state_manager.get_candidate_info()
    
    def is_interview_complete(self) -> bool:
        """Check if the interview is complete.
        
        Returns:
            True if interview is complete, False otherwise
        """
        return self.state_manager.is_interview_complete()
    
    def get_current_interview_state(self) -> Dict[str, Any]:
        """Get the current interview state for debugging.
        
        Returns:
            Dictionary with current interview state
        """
        return self.state_manager.state
    
    def reset_chat(self) -> None:
        """Reset the chat session and interview state."""
        self.llm_client.reset_chat()
        self.state_manager.reset()
        
        # Reset GDPR state
        self.candidate_id = None
        self.consent_requested = False
        self.consent_given = False
        self.gdpr_intro_shown = False
    
    def can_continue_typing(self) -> bool:
        """Check if the user can continue typing in the chat.
        
        Returns:
            False if interview is finished or marked as complete with exit command, True otherwise
        """
        return not self.state_manager.is_interview_finished()
