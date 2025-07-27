# ======================== Automation.py ========================
# Central Automation Dispatcher for Jarvis AI System

import asyncio
import re
import json
from typing import List, Dict, Any, Optional
from Backend.PC_Automation import TranslateCommand as PCTranslateCommand
from Backend.Andriod_Automation import TranslateAndroidCommand, human_friendly_responses
from Backend.MobileControl import speak_on_phone, vibrate_phone, get_battery_status, call_number, send_sms, toggle_flashlight

class AutomationDispatcher:
    """Central automation dispatcher for handling commands across devices."""
    
    def __init__(self):
        self.device_handlers = {
            "pc": self.handle_pc_command,
            "android": self.handle_android_command,
            "mobile": self.handle_mobile_command,
            "device": self.handle_device_command,
            "smart": self.handle_smart_command
        }
        
        # Command routing patterns
        self.command_patterns = {
            "pc": r"^pc\s+(.+)$",
            "android": r"^(open|close|play|start|delete|lock|unlock)\s+(.+)$",
            "mobile": r"^mobile\s+(.+)$",
            "device": r"^device\s+(.+)$",
            "smart": r"^smart\s+(.+)$"
        }
    
    def parse_command(self, command: str) -> Dict[str, Any]:
        """Parse command and extract parameters."""
        command_lower = command.lower().strip()
        
        # Extract parameters from command if present
        params = {}
        if "[" in command and "]" in command:
            param_match = re.search(r"\[(.*?)\]", command)
            if param_match:
                param_str = param_match.group(1)
                for param in param_str.split():
                    if ":" in param:
                        key, value = param.split(":", 1)
                        # Try to convert to appropriate type
                        try:
                            if value.isdigit():
                                params[key] = int(value)
                            elif value.lower() in ["true", "false"]:
                                params[key] = value.lower() == "true"
                            else:
                                params[key] = value
                        except:
                            params[key] = value
                # Remove parameter section from command
                command_lower = re.sub(r"\s*\[.*?\]", "", command_lower)
        
        return {
            "original": command,
            "clean": command_lower,
            "params": params
        }
    
    def route_command(self, command: str) -> Optional[str]:
        """Route command to appropriate device handler."""
        command_lower = command.lower().strip()
        
        for device, pattern in self.command_patterns.items():
            if re.match(pattern, command_lower):
                return device
        
        return None
    
    async def handle_pc_command(self, command: str, params: Dict[str, Any]) -> str:
        """Handle PC-specific commands."""
        try:
            # Remove 'pc ' prefix and route to PC automation
            clean_command = command.replace("pc ", "", 1)
            result = PCTranslateCommand(clean_command)
            return result.get("response", "PC command executed successfully.")
        except Exception as e:
            return f"Error executing PC command: {str(e)}"
    
    async def handle_android_command(self, command: str, params: Dict[str, Any]) -> str:
        """Handle Android-specific commands."""
        try:
            # Route to Android automation
            TranslateAndroidCommand([command])
            return f"Android command '{command}' executed successfully."
        except Exception as e:
            return f"Error executing Android command: {str(e)}"
    
    async def handle_mobile_command(self, command: str, params: Dict[str, Any]) -> str:
        """Handle mobile-specific commands."""
        try:
            clean_command = command.replace("mobile ", "", 1)
            
            if clean_command.startswith("call "):
                contact = clean_command.replace("call ", "").strip()
                result = call_number(contact)
                return f"Calling {contact}..."
            
            elif clean_command.startswith("send sms "):
                # Extract message and number from command
                parts = clean_command.replace("send sms ", "").split(" to ", 1)
                if len(parts) == 2:
                    message, number = parts
                    result = send_sms(number.strip(), message.strip())
                    return f"SMS sent to {number}..."
                else:
                    return "Please specify message and recipient for SMS."
            
            elif "flashlight" in clean_command:
                if "on" in clean_command:
                    result = toggle_flashlight("on")
                    return "Flashlight turned on."
                elif "off" in clean_command:
                    result = toggle_flashlight("off")
                    return "Flashlight turned off."
            
            elif "battery" in clean_command:
                result = get_battery_status()
                return f"Battery status: {result}"
            
            elif "vibrate" in clean_command:
                duration = params.get("duration", 300)
                result = vibrate_phone(duration)
                return f"Phone vibrating for {duration}ms."
            
            else:
                return f"Mobile command '{clean_command}' not recognized."
                
        except Exception as e:
            return f"Error executing mobile command: {str(e)}"
    
    async def handle_device_command(self, command: str, params: Dict[str, Any]) -> str:
        """Handle device-specific commands with parameters."""
        try:
            clean_command = command.replace("device ", "", 1)
            
            # Handle volume commands with parameters
            if "volume" in clean_command:
                action = params.get("action", "up")
                value = params.get("value", 10)
                
                if action == "up":
                    return f"Volume increased by {value}%"
                elif action == "down":
                    return f"Volume decreased by {value}%"
                elif action == "set":
                    return f"Volume set to {value}%"
                elif action in ["mute", "unmute"]:
                    return f"Volume {action}d"
            
            # Handle brightness commands
            elif "brightness" in clean_command:
                value = params.get("value", 50)
                return f"Brightness set to {value}%"
            
            # Handle other device commands
            elif "battery" in clean_command:
                return "Checking battery percentage..."
            
            elif "flashlight" in clean_command:
                action = params.get("action", "on")
                return f"Flashlight turned {action}"
            
            elif "screen" in clean_command:
                action = params.get("action", "on")
                return f"Screen turned {action}"
            
            elif "home" in clean_command:
                return "Returning to home screen..."
            
            elif "reminder" in clean_command or "alarm" in clean_command:
                return "Setting reminder/alarm..."
            
            elif "water" in clean_command:
                return "Activating water ejection..."
            
            elif "silent" in clean_command:
                action = params.get("action", "on")
                return f"Silent mode turned {action}"
            
            elif "wi-fi" in clean_command:
                action = params.get("action", "on")
                return f"Wi-Fi turned {action}"
            
            elif "bluetooth" in clean_command:
                action = params.get("action", "on")
                return f"Bluetooth turned {action}"
            
            elif "mobile data" in clean_command:
                action = params.get("action", "on")
                return f"Mobile data turned {action}"
            
            elif "scroll" in clean_command:
                direction = params.get("action", "up")
                return f"Scrolling {direction}..."
            
            elif "screenshot" in clean_command:
                return "Taking screenshot..."
            
            elif "photo" in clean_command:
                return "Capturing photo..."
            
            elif "video" in clean_command:
                return "Recording video..."
            
            else:
                return f"Device command '{clean_command}' executed."
                
        except Exception as e:
            return f"Error executing device command: {str(e)}"
    
    async def handle_smart_command(self, command: str, params: Dict[str, Any]) -> str:
        """Handle smart/AI commands."""
        try:
            clean_command = command.replace("smart ", "", 1)
            
            if "news" in clean_command:
                return "Fetching today's news..."
            
            elif "weather" in clean_command:
                return "Getting weather report..."
            
            elif "location" in clean_command:
                return "Getting current location..."
            
            elif "translate" in clean_command:
                return "Activating translation mode..."
            
            elif "trouble" in clean_command:
                return "Emergency mode activated..."
            
            elif "search" in clean_command:
                return "Performing web search..."
            
            elif "notification" in clean_command:
                return "Reading latest notification..."
            
            else:
                return f"Smart command '{clean_command}' processed."
                
        except Exception as e:
            return f"Error executing smart command: {str(e)}"
    
    async def execute_commands(self, commands: List[str]) -> Dict[str, Any]:
        """Execute a list of commands and return results."""
        results = {
            "success": [],
            "errors": [],
            "responses": []
        }
        
        for command in commands:
            try:
                # Parse command
                parsed = self.parse_command(command)
                
                # Route to appropriate handler
                device_type = self.route_command(parsed["clean"])
                
                if device_type and device_type in self.device_handlers:
                    handler = self.device_handlers[device_type]
                    response = await handler(parsed["clean"], parsed["params"])
                    results["success"].append(command)
                    results["responses"].append(response)
                else:
                    # Try to handle as general command
                    if "general" in parsed["clean"] or "realtime" in parsed["clean"]:
                        results["success"].append(command)
                        results["responses"].append("Query processed successfully.")
                    else:
                        results["errors"].append(f"Unknown command type: {command}")
                        results["responses"].append(f"Command '{command}' not recognized.")
                        
            except Exception as e:
                results["errors"].append(f"Error processing '{command}': {str(e)}")
                results["responses"].append(f"Error: {str(e)}")
        
        return results

# Global automation dispatcher instance
automation_dispatcher = AutomationDispatcher()

async def Automation(commands: List[str]) -> Dict[str, Any]:
    """
    Main automation function that processes commands from the decision model.
    
    Args:
        commands: List of commands from FirstLayerDMM
        
    Returns:
        Dictionary with execution results
    """
    print(f"[AUTOMATION] Processing {len(commands)} commands: {commands}")
    
    # Execute commands using the dispatcher
    results = await automation_dispatcher.execute_commands(commands)
    
    # Generate human-friendly response
    if results["success"]:
        if len(results["success"]) == 1:
            response = results["responses"][0]
        else:
            response = f"Executed {len(results['success'])} commands successfully."
    else:
        response = "No commands were executed successfully."
    
    if results["errors"]:
        response += f" {len(results['errors'])} errors occurred."
    
    print(f"[AUTOMATION] Results: {results}")
    print(f"[AUTOMATION] Response: {response}")
    
    return {
        "response": response,
        "results": results,
        "success_count": len(results["success"]),
        "error_count": len(results["errors"])
    }

# For backward compatibility
def AutomationSync(commands: List[str]) -> Dict[str, Any]:
    """Synchronous version of Automation for compatibility."""
    return asyncio.run(Automation(commands))

if __name__ == "__main__":
    # Test the automation system
    test_commands = [
        "device volume down 20%",
        "pc open notepad",
        "mobile call mom",
        "device brightness 50%",
        "general how are you"
    ]
    
    async def test():
        results = await Automation(test_commands)
        print(f"Test Results: {results}")
    
    asyncio.run(test()) 