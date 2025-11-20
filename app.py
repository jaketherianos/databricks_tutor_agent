"""
Small Tutor Agent - Streamlit Web App

This is a Streamlit app that provides a web UI for the Small Tutor Agent.

Usage:
  Local: streamlit run app.py
  Databricks Apps: This file serves as the entrypoint (configure in Databricks Apps UI)

MLflow Configuration:
  - MLflow tracking should be configured via environment variables or in Databricks
  - The app uses MLflow 3 tracing and feedback APIs
  - Traces are automatically created for each tutor agent invocation
  - Human feedback (thumbs up/down + rationale) is logged to the trace
"""

import streamlit as st
import random
from typing import Dict, Optional
import mlflow
from mlflow.entities.assessment import AssessmentSource, AssessmentSourceType

# Import the tutor agent
from small_tutor_agent import run_tutor_agent


# Databricks-related topic suggestions
TOPIC_SUGGESTIONS = [
    "Unity Catalog basics",
    "Delta Lake time travel",
    "Medallion architecture in the Lakehouse",
    "Databricks SQL warehouses vs clusters",
    "Mosaic AI Model Serving",
    "Databricks Feature Store vs online features",
    "Lakeflow jobs and orchestration",
    "GenAI RAG on Databricks",
    "Databricks Apps overview",
    "Databricks Workflows and Jobs",
    "Delta Live Tables pipelines",
    "Databricks AutoML capabilities",
    "Vector Search in Databricks",
    "MLflow model registry",
    "Databricks Notebooks collaboration",
]


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "last_trace_id" not in st.session_state:
        st.session_state["last_trace_id"] = None
    if "last_topic" not in st.session_state:
        st.session_state["last_topic"] = None
    if "last_response" not in st.session_state:
        st.session_state["last_response"] = None
    if "feedback_submitted" not in st.session_state:
        st.session_state["feedback_submitted"] = False
    if "selected_topic" not in st.session_state:
        st.session_state["selected_topic"] = ""


@mlflow.trace(name="tutor_with_trace", span_type="CHAIN")
def tutor_with_trace(topic: str) -> Dict[str, str]:
    """
    Wrapper function that calls the tutor agent with MLflow tracing.
    
    Args:
        topic: The topic to explain
    
    Returns:
        Dictionary with beginner, intermediate, and expert explanations
    """
    return run_tutor_agent(topic)


def call_tutor_agent(topic: str):
    """
    Call the tutor agent and store results in session state.
    
    Args:
        topic: The topic to explain
    """
    if not topic or not topic.strip():
        st.error("Please enter a topic to explain.")
        return
    
    with st.spinner(f"🤔 Thinking about '{topic}' at three levels..."):
        try:
            # Call the tutor agent with tracing
            response = tutor_with_trace(topic)
            
            # Get the trace ID from MLflow
            trace_id = mlflow.get_last_active_trace_id()
            
            # Store in session state
            st.session_state["last_trace_id"] = trace_id
            st.session_state["last_topic"] = topic
            st.session_state["last_response"] = response
            st.session_state["feedback_submitted"] = False
            
            st.success(f"✅ Generated explanations for '{topic}'!")
            
        except Exception as e:
            st.error(f"❌ Error calling tutor agent: {str(e)}")
            st.exception(e)


def display_explanations(response: Dict[str, str]):
    """
    Display the three levels of explanations.
    
    Args:
        response: Dictionary with beginner, intermediate, and expert keys
    """
    # Beginner Level
    st.markdown("### 📚 Beginner Level")
    with st.container():
        st.info(response.get("beginner", "No beginner explanation available."))
    
    st.markdown("---")
    
    # Intermediate Level
    st.markdown("### 🎓 Intermediate Level")
    with st.container():
        st.info(response.get("intermediate", "No intermediate explanation available."))
    
    st.markdown("---")
    
    # Expert Level
    st.markdown("### 🔬 Expert Level")
    with st.container():
        st.info(response.get("expert", "No expert explanation available."))


def log_feedback(trace_id: str, thumbs_up: bool, rationale: str = ""):
    """
    Log human feedback to MLflow for the given trace.
    
    Args:
        trace_id: The MLflow trace ID
        thumbs_up: True for thumbs up, False for thumbs down
        rationale: Optional text explaining the feedback
    """
    try:
        # Create the assessment source (MLflow 3 API - only source_type is required)
        source = AssessmentSource(
            source_type=AssessmentSourceType.HUMAN
        )
        
        # Log feedback to MLflow
        mlflow.log_feedback(
            trace_id=trace_id,
            name="user_feedback",
            value=thumbs_up,
            rationale=rationale if rationale else ("Helpful" if thumbs_up else "Not helpful"),
            source=source
        )
        
        st.session_state["feedback_submitted"] = True
        st.success("✅ Feedback recorded, thank you!")
        
    except Exception as e:
        st.error(f"❌ Error logging feedback: {str(e)}")
        st.exception(e)


def render_feedback_section():
    """Render the feedback UI section."""
    if st.session_state["last_response"] is None:
        return
    
    st.markdown("---")
    st.markdown("### 💬 Feedback")
    st.write("Was this explanation helpful?")
    
    # Create columns for thumbs up/down buttons
    col1, col2, col3 = st.columns([1, 1, 4])
    
    feedback_given = False
    
    with col1:
        if st.button("👍 Yes", use_container_width=True, disabled=st.session_state["feedback_submitted"]):
            feedback_given = True
            feedback_value = True
    
    with col2:
        if st.button("👎 No", use_container_width=True, disabled=st.session_state["feedback_submitted"]):
            feedback_given = True
            feedback_value = False
    
    # Text area for optional comments
    rationale = st.text_area(
        "Why was this good or bad? (optional)",
        placeholder="Your feedback helps us improve the tutor agent...",
        disabled=st.session_state["feedback_submitted"],
        key="feedback_rationale"
    )
    
    # Log feedback if a button was clicked
    if feedback_given and st.session_state["last_trace_id"]:
        log_feedback(
            trace_id=st.session_state["last_trace_id"],
            thumbs_up=feedback_value,
            rationale=rationale
        )
    
    # Show feedback submitted message
    if st.session_state["feedback_submitted"]:
        st.info("ℹ️ Feedback already submitted for this response. Ask a new question to provide more feedback.")


def render_topic_suggestions():
    """Render topic suggestion buttons."""
    st.markdown("#### 💡 Suggested Topics")
    
    # Randomly sample 5 suggestions
    suggestions = random.sample(TOPIC_SUGGESTIONS, min(5, len(TOPIC_SUGGESTIONS)))
    
    # Create columns for suggestion buttons
    cols = st.columns(5)
    
    for idx, suggestion in enumerate(suggestions):
        with cols[idx]:
            if st.button(
                suggestion,
                key=f"suggestion_{idx}",
                use_container_width=True,
                help=f"Click to explain: {suggestion}"
            ):
                # Store the selected topic
                st.session_state["selected_topic"] = suggestion
                # Trigger the tutor agent call
                call_tutor_agent(suggestion)
                st.rerun()


def main():
    """Main application function."""
    # Page configuration
    st.set_page_config(
        page_title="Small Tutor Agent",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("🎓 Small Tutor Agent")
    st.markdown(
        "Enter a topic and I'll explain it at three levels: **beginner**, **intermediate**, and **expert**."
    )
    
    st.markdown("---")
    
    # Topic input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # If a suggestion was selected, use it as default value
        default_value = st.session_state.get("selected_topic", "")
        
        topic = st.text_input(
            "Topic",
            placeholder="e.g., Delta Lake time travel",
            value=default_value,
            key="topic_input"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Vertical spacing
        ask_button = st.button("🚀 Ask Tutor", type="primary", use_container_width=True)
    
    # Handle "Ask Tutor" button click
    if ask_button:
        call_tutor_agent(topic)
        st.rerun()
    
    # Render topic suggestions
    render_topic_suggestions()
    
    st.markdown("---")
    
    # Display results if available
    if st.session_state["last_response"] is not None:
        st.markdown(f"## 📖 Explaining: **{st.session_state['last_topic']}**")
        st.markdown("")
        
        display_explanations(st.session_state["last_response"])
        
        # Render feedback section
        render_feedback_section()


if __name__ == "__main__":
    main()

