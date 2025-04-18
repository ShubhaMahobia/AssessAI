
![Logo](https://www.aimtechnologies.co/wp-content/uploads/2023/11/AI-Chatbots.jpg)


# AI Assement ChatBot

### Project Overview

This project implements a GDPR-compliant AI technical interviewer chatbot named AVA for PGAGI. The system conducts structured technical interviews using Google's Gemini API, starting with a data privacy consent request followed by collection of candidate information and theoretical technical questions based on the candidate's tech stack. The architecture follows clean modular design principles with separate components for LLM interactions, prompt templates, interview state management, and database operations. Key features include dynamic question generation, email/phone validation, GDPR-compliant data storage with SQLite/SQLAlchemy, and customizable interview flows. The chatbot maintains context throughout the conversation while storing responses only with explicit consent, providing a professional yet conversational interview experience that balances structure with natural interaction.


## Installation Instruction

1. Clone this repo into your system.
2. First of insall uv ( Faster than pip command) using the command


```bash
 pip install uv
```
3. Now insall all the requirements mentioned in the requirements.txt file

```bash
 uv add -r requirements.txt
```

4. Now create Google API Key and paste in the .env file

5. After that once all the packages are installed run the command

```bash
streamlit run app.py
```

# Usage Guide 

After running the application - 

1. It will  introduces itself and explains data storage policy
2. Respond with "yes" or "no" to provide consent
3. After that answer the question as asked by the ai chatbot


As an admin you can the database present in the directory created automatically once app is runnning

you can view the data base by installing the extension "SQLite" present in the microsoft workplace


after that click CTRL + SHIFT + P and search for OPEN DATABASE and then you can see the database present


## Tech Stack

Libraries and Technologies

### Google Generative AI: 
Primary LLM provider using the Gemini 1.5 Flash model for generating conversational responses.

### SQLAlchemy: 

ORM for database operations, providing abstraction over SQLite for storing candidate data.

### SQLite:  

Lightweight database for storing interview data and candidate information.


### Python-dotenv: 

For managing environment variables and API keys.


### UUID: 

For generating unique identifiers for candidate records.


### Regular Expressions: 

For input validation of email addresses and phone numbers.
Standard Python Libraries: Including datetime, typing, os, and json.

# Prompt Design

### 1. System Prompts
This is a system prompt which will help the ai to understand their role how react.

### 2. Information Gathering
This prompt will help to gather the requirement of the user

### 3. Technical Question Generation
This prompt will help to generate question based on the tech skills provided by the user

### 4. Response Handling
This Ensures followup questions acknowledge previous answers
## Challenges and Solutions

The main Challenges which I faced while developing the application
1. I created different different function individaully by making an integrated flow is quite difficult

2. Also I tried different different models - from gemini and chose the best one


Thank you 
Shubham Mahobia
mahobiashubham4@gmail.com
