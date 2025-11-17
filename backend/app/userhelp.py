from groq import Groq
from sqlalchemy.orm import Session
from . import models, schemas
from .models import User, Plan, Task
import os
import json
from typing import List, Dict

class AITaskGenerator:
    def __init__(self):
        # Get API key from environment variable
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set. Please set it in your .env file.")
        self.client = Groq(api_key=api_key)
    
    def generate_tasks_for_goal(
        self, 
        goal: str, 
        user_id: int, 
        plan_id: int, 
        db: Session,
        num_tasks: int = 5
    ) -> List[Task]:
        """
        Generate tasks based on a user's goal using AI.
        """
        
        # Verify user and plan exist
        user = db.query(User).filter(User.id == user_id).first()
        plan = db.query(Plan).filter(Plan.id == plan_id).first()
        
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        if not plan:
            raise ValueError(f"Plan with ID {plan_id} not found")
        
        # Create AI prompt
        prompt = f"""
You are a task planning assistant. A user named {user.name} wants to achieve the following goal:

Goal: {goal}
Plan Name: {plan.name}
Plan Description: {plan.description or "No additional description"}

Generate {num_tasks} specific, actionable, and measurable tasks to help them achieve this goal.
Each task should:
- Be clear and specific
- Be achievable within a reasonable timeframe
- Build upon previous tasks logically
- Include concrete actions

Return ONLY a valid JSON array of tasks in this exact format:
[
  {{
    "title": "Task title (max 100 characters)",
    "description": "Detailed description of what needs to be done and why (max 500 characters)"
  }}
]

Do not include any other text, explanations, or markdown formatting. Just the JSON array.
"""
        
        try:
            # Call Groq API
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful task planning assistant that generates actionable tasks in JSON format only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse AI response
            response_content = chat_completion.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if response_content.startswith("```"):
                response_content = response_content.split("```")[1]
                if response_content.startswith("json"):
                    response_content = response_content[4:]
            
            # Parse JSON
            tasks_data = json.loads(response_content)
            
            # Create tasks in database
            created_tasks = []
            for task_data in tasks_data:
                new_task = Task(
                    title=task_data["title"][:100],
                    description=task_data["description"][:500],
                    user_id=user_id,
                    plan_id=plan_id
                )
                db.add(new_task)
                created_tasks.append(new_task)
            
            # Commit all tasks at once
            db.commit()
            
            # Refresh all tasks to get their IDs
            for task in created_tasks:
                db.refresh(task)
            
            return created_tasks
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to generate tasks: {str(e)}")
    
    def get_task_suggestions(self, goal: str) -> str:
        """
        Get general suggestions for a goal without creating tasks in the database.
        """
        prompt = f"""
A user wants to achieve the following goal:
{goal}

Provide 3-5 helpful suggestions or tips for achieving this goal. Be concise and practical.
"""
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that provides practical advice."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.3-70b-versatile",  # FIXED: Changed from openai/gpt-oss-120b
                temperature=0.7,
                max_tokens=500
            )
            
            return chat_completion.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Failed to get suggestions: {str(e)}")

# Create a singleton instance
ai_task_generator = AITaskGenerator()