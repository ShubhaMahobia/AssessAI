# AssessAI - Assessment Chatbot

An intelligent assessment chatbot powered by Google's Gemini LLM, built with Streamlit.

## Features

- Interactive chat interface for user assessment
- Ability to upload files or input text for analysis
- Comprehensive assessment of various types of content:
  - Resumes and CVs
  - Project descriptions
  - Code samples
  - Professional content
- Detailed feedback with strengths, areas for improvement, and recommendations

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your Google API key for Gemini:
   - Option 1: Set the `GOOGLE_API_KEY` environment variable
   - Option 2: Create a `.env` file with `GOOGLE_API_KEY=your_api_key_here`
   - Option 3: Input your API key directly in the web interface

4. Run the Streamlit app:
   ```
   streamlit run main.py
   ```

## Project Structure

- `main.py`: Streamlit application entry point
- `chatbot_controller.py`: Handles Gemini LLM integration and chat logic
- `utils/prompt_templates.py`: Contains prompt templates for assessment

## Additional Features

- Chat history management
- Responsive layout design
- Clear explanations and guidance throughout the assessment process

## Requirements

- Python 3.8+
- Streamlit
- Google Generative AI SDK
- Internet connection for API access

## License

This project is for educational purposes.