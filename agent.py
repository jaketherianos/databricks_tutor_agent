from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

import mlflow
import os
from databricks.sdk import WorkspaceClient


mlflow.openai.autolog()

host = os.environ.get('MLFLOW_TRACKING_URI')
print(host)
exp_id = os.environ.get('MLFLOW_EXPERIMENT_ID')
print(exp_id)
tok = os.environ.get('DATABRICKS_TOKEN')
print(tok)

w = WorkspaceClient()
client = w.serving_endpoints.get_open_ai_client()

@mlflow.trace(name="tutor_agent", span_type="AGENT")
def tutor_agent(topic: str):
    """
    Small Tutor Agent: Explains any topic at 3 difficulty levels
    
    Args:
        topic: The topic to explain (e.g., "transformers", "quantum computing")
    
    Returns:
        Dictionary with explanations at beginner, intermediate, and expert levels
    """
    
    levels = ["beginner", "intermediate", "expert"]
    explanations = {}
    
    print(f"\n{'='*60}")
    print(f"TUTOR AGENT: Explaining '{topic}'")
    print(f"{'='*60}\n")
    
    for level in levels:
        # Create conditional prompt based on difficulty level
        system_prompts = {
            "beginner": "You are a patient tutor explaining concepts to someone with no prior knowledge. Use simple language, everyday analogies, and avoid jargon.",
            "intermediate": "You are a tutor explaining concepts to someone with basic understanding. Use some technical terms but explain them clearly. Include practical examples.",
            "expert": "You are a tutor explaining concepts to an advanced learner. Use technical terminology, discuss nuances, trade-offs, and advanced applications."
        }
        
        response = client.chat.completions.create(
            model="databricks-llama-4-maverick",
            messages=[
                {
                    "role": "system", 
                    "content": system_prompts[level],
                },
                {
                    "role": "user",
                    "content": f"Explain {topic} in 2-3 concise paragraphs.",
                },
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        explanation = response.choices[0].message.content
        explanations[level] = explanation
        
        # Multi-format output: Print each level as we get it
        print(f"{'─'*60}")
        print(f"📚 {level.upper()} LEVEL")
        print(f"{'─'*60}")
        print(explanation)
        print()
    
    return explanations


# Example usage
if __name__ == "__main__":
    # Test the tutor agent with a topic
    topic = "transformers"  # You can change this to any topic
    results = tutor_agent(topic)
    
    print(f"\n{'='*60}")
    print("✅ Tutorial Complete!")
    print(f"Generated {len(results)} explanations for '{topic}'")
    print(f"{'='*60}\n")
