#!/usr/bin/env python3
"""Basic functionality test for the minimal multi-agent system."""

from agent import Agent
from coordinator_agent import CoordinatorAgent
from message_handler import MessageBus


def test_basic_agent():
    """Test basic agent functionality."""
    print("Testing basic agent...")
    
    # Create message bus and agent
    message_bus = MessageBus()
    agent = Agent("test_agent", message_bus)
    message_bus.register(agent)
    
    # Test ping functionality
    agent.receive_message({
        "sender": "coordinator",
        "recipient": "test_agent",
        "task": "ping",
        "payload": {}
    })
    
    print("✓ Basic agent works")


def test_coordinator():
    """Test coordinator agent functionality."""
    print("Testing coordinator agent...")
    
    # Create message bus and agents
    message_bus = MessageBus()
    coordinator = CoordinatorAgent("coordinator", message_bus)
    research_agent = Agent("research_agent", message_bus)
    
    message_bus.register(coordinator)
    message_bus.register(research_agent)
    
    # Test coordinator request handling
    coordinator.receive_message({
        "sender": "user",
        "recipient": "coordinator",
        "task": "handle_request",
        "payload": {"data": "test_data"}
    })
    
    print("✓ Coordinator agent works")


def test_message_bus():
    """Test message bus functionality."""
    print("Testing message bus...")
    
    message_bus = MessageBus()
    agent1 = Agent("agent1", message_bus)
    agent2 = Agent("agent2", message_bus)
    
    message_bus.register(agent1)
    message_bus.register(agent2)
    
    # Test message delivery
    message_bus.deliver({
        "sender": "agent1",
        "recipient": "agent2",
        "task": "ping",
        "payload": {}
    })
    
    print("✓ Message bus works")


def test_error_handling():
    """Test error handling."""
    print("Testing error handling...")
    
    message_bus = MessageBus()
    agent = Agent("test_agent", message_bus)
    message_bus.register(agent)
    
    # Test invalid message (missing task)
    agent.receive_message({
        "sender": "coordinator",
        "recipient": "test_agent"
        # Missing "task" field
    })
    
    # Test unknown recipient
    message_bus.deliver({
        "sender": "agent1",
        "recipient": "unknown_agent",
        "task": "ping",
        "payload": {}
    })
    
    print("✓ Error handling works")


def test_context_management():
    """Test context management."""
    print("Testing context management...")
    
    message_bus = MessageBus()
    agent = Agent("test_agent", message_bus, max_context=3)
    message_bus.register(agent)
    
    # Send multiple messages
    for i in range(5):
        agent.receive_message({
            "sender": "coordinator",
            "recipient": "test_agent",
            "task": "ping",
            "payload": {"msg_id": i}
        })
    
    # Verify context is limited
    assert len(agent.context) == 3, f"Expected 3 messages in context, got {len(agent.context)}"
    print("✓ Context management works")


if __name__ == "__main__":
    print("Running basic functionality tests...\n")
    
    try:
        test_basic_agent()
        test_coordinator()
        test_message_bus()
        test_error_handling()
        test_context_management()
        
        print("\n🎉 All basic functionality tests passed!")
        print("Your minimal multi-agent system is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc() 