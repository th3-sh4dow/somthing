# ======================== Enhanced System Test ========================
# Test script for the enhanced Jarvis AI system with NLP/NLU capabilities

import asyncio
from Backend.Model import FirstLayerDMM, extract_command_parameters
from Backend.Automation import Automation

async def test_enhanced_system():
    """Test the enhanced system with various natural language commands."""
    
    print("🤖 Enhanced Jarvis AI System Test")
    print("=" * 50)
    
    # Test cases with natural language commands
    test_queries = [
        # Volume control with parameters
        "volume down 20%",
        "set volume to 50%",
        "increase volume by 15%",
        
        # Brightness control
        "set brightness to 75%",
        "brightness 30%",
        
        # App commands
        "open whatsapp",
        "start spotify",
        "close chrome",
        
        # Device commands
        "take a screenshot",
        "turn on flashlight",
        "turn off silent mode",
        "check battery percentage",
        
        # PC commands
        "open notepad in pc",
        "volume up in pc",
        "shutdown pc",
        
        # Media commands
        "play despacito on spotify",
        "play music on youtube",
        "capture photo",
        
        # Smart commands
        "what's the weather today?",
        "tell me today's news",
        "get my current location",
        
        # Mixed commands
        "open whatsapp and set volume to 40%",
        "take screenshot and turn on flashlight",
        
        # Hindi/English mixed
        "volume kam karo 25%",
        "whatsapp kholo",
        "photo khicho"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: '{query}'")
        print("-" * 40)
        
        try:
            # Get decision from enhanced Model
            decisions = FirstLayerDMM(query)
            print(f"📋 Decisions: {decisions}")
            
            # Extract parameters for each command
            for decision in decisions:
                if decision.startswith(("device ", "pc ", "mobile ")):
                    category, params = extract_command_parameters(decision)
                    if params:
                        print(f"⚙️  Parameters for '{decision}': {params}")
            
            # Execute automation (simulated)
            if any(not d.startswith("general") and not d.startswith("realtime") for d in decisions):
                print("🚀 Executing automation commands...")
                # Uncomment the line below to actually execute commands
                # result = await Automation(decisions)
                # print(f"✅ Result: {result}")
                print("✅ Commands would be executed successfully")
            else:
                print("💬 This is a conversational query")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)

def test_parameter_extraction():
    """Test parameter extraction functionality."""
    print("\n🔧 Parameter Extraction Test")
    print("=" * 50)
    
    test_commands = [
        "device volume down 20%",
        "device brightness 50%",
        "pc open notepad",
        "mobile call mom",
        "device turn on flashlight",
        "device scroll up",
        "device set reminder"
    ]
    
    for cmd in test_commands:
        category, params = extract_command_parameters(cmd)
        print(f"Command: {cmd}")
        print(f"Category: {category}")
        print(f"Parameters: {params}")
        print("-" * 30)

def test_nlp_analysis():
    """Test NLP analysis capabilities."""
    print("\n🧠 NLP Analysis Test")
    print("=" * 50)
    
    from Backend.Model import analyze_intent_with_nlp
    
    test_texts = [
        "volume down 20%",
        "open whatsapp and set brightness to 50%",
        "take a screenshot and turn on flashlight",
        "call mom and send sms to dad"
    ]
    
    for text in test_texts:
        analysis = analyze_intent_with_nlp(text)
        print(f"Text: {text}")
        print(f"Analysis: {analysis}")
        print("-" * 30)

if __name__ == "__main__":
    print("🚀 Starting Enhanced Jarvis AI System Tests...")
    
    # Run tests
    asyncio.run(test_enhanced_system())
    test_parameter_extraction()
    test_nlp_analysis()
    
    print("\n✅ All tests completed!")
    print("\n📝 Summary:")
    print("- Enhanced Model.py with advanced NLP/NLU capabilities")
    print("- Parameter extraction for volume, brightness, etc.")
    print("- Central Automation.py dispatcher")
    print("- Enhanced Android_Automation.py with detailed responses")
    print("- Support for natural language commands with parameters")
    
    print("\n🎯 Example Usage:")
    print("- 'volume down 20%' → Extracts action='down', value=20")
    print("- 'set brightness to 50%' → Extracts action='set', value=50")
    print("- 'open whatsapp' → Routes to Android automation")
    print("- 'open notepad in pc' → Routes to PC automation") 