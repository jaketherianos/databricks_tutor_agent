"""
Simple test of the difficulty_scorer

Tests the difficulty alignment scorer with sample tutor responses.
"""

from scorers import difficulty_scorer

# Sample tutor response
test_inputs = {
    "topic": "Delta Lake"
}

test_outputs = {
    "beginner": "Delta Lake is like a special storage system for data. It keeps track of changes, similar to how Google Docs shows you the history of a document.",
    "intermediate": "Delta Lake is an open-source storage layer that brings ACID transactions to data lakes. It uses a transaction log to track changes and enables time travel queries.",
    "expert": "Delta Lake implements MVCC-based snapshot isolation through a versioned transaction log. It supports optimistic concurrency control, Z-ordering for data skipping, and incremental processing via structured streaming checkpoints."
}

print("Testing difficulty_scorer...")
print("=" * 60)
print(f"Topic: {test_inputs['topic']}")
print()

# Call the scorer
result = difficulty_scorer(test_inputs, test_outputs)

print("Result:")
print(f"  Assessment: {result}")
print("=" * 60)

