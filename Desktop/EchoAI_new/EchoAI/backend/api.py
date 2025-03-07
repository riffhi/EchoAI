from livekit.agents import llm
import enum
from typing import Annotated, Dict, List, Optional
import logging
from db_driver import DatabaseDriver
import datetime

logger = logging.getLogger("smartphone-assistant")
logger.setLevel(logging.INFO)

DB = DatabaseDriver()

class AppCategory(enum.Enum):
    SOCIAL = "social"
    PRODUCTIVITY = "productivity"
    ENTERTAINMENT = "entertainment"
    FINANCE = "finance"
    HEALTH = "health"
    UTILITY = "utility"

class DeviceType(enum.Enum):
    ANDROID = "android"
    IOS = "ios"

class AssistantFnc(llm.FunctionContext):
    def __init__(self):
        super().__init__()
        
        self._user_profile = {
            "name": "",
            "device_type": ""
        }
        
        self._pending_action = None
        self._apps = {}
        self._calendar_events = []
        
    def has_user_profile(self):
        return self._user_profile["name"] != ""
    
    def has_pending_action(self):
        return self._pending_action is not None
    
    def get_pending_action(self):
        return self._pending_action
    
    def execute_pending_action(self):
        self._pending_action = None
        return "Action executed successfully"
    
    def cancel_pending_action(self):
        self._pending_action = None
        return "Action canceled"
    
    @llm.ai_callable(description="Create or update user profile")
    def create_user_profile(
        self, 
        name: Annotated[str, llm.TypeInfo(description="User's name")],
        device_type: Annotated[str, llm.TypeInfo(description="User's device type (android/ios)")]
    ):
        logger.info("Creating user profile - name: %s, device_type: %s", name, device_type)
        
        # Standardize device type input
        if device_type.lower() in ["android", "google", "pixel", "samsung", "oneplus"]:
            device_type = DeviceType.ANDROID.value
        elif device_type.lower() in ["ios", "iphone", "apple"]:
            device_type = DeviceType.IOS.value
        else:
            device_type = DeviceType.ANDROID.value  # Default to Android
            
        self._user_profile = {
            "name": name,
            "device_type": device_type
        }
        
        # Initialize with some demo apps based on device type
        if device_type == DeviceType.ANDROID.value:
            self._apps = {
                "gmail": AppCategory.PRODUCTIVITY.value,
                "chrome": AppCategory.UTILITY.value,
                "youtube": AppCategory.ENTERTAINMENT.value,
                "maps": AppCategory.UTILITY.value,
                "photos": AppCategory.UTILITY.value,
                "calendar": AppCategory.PRODUCTIVITY.value,
                "whatsapp": AppCategory.SOCIAL.value,
                "spotify": AppCategory.ENTERTAINMENT.value,
                "netflix": AppCategory.ENTERTAINMENT.value,
                "banking": AppCategory.FINANCE.value,
                "fitbit": AppCategory.HEALTH.value
            }
        else:  # iOS
            self._apps = {
                "mail": AppCategory.PRODUCTIVITY.value,
                "safari": AppCategory.UTILITY.value,
                "youtube": AppCategory.ENTERTAINMENT.value,
                "maps": AppCategory.UTILITY.value,
                "photos": AppCategory.UTILITY.value,
                "calendar": AppCategory.PRODUCTIVITY.value,
                "messages": AppCategory.SOCIAL.value,
                "apple music": AppCategory.ENTERTAINMENT.value,
                "apple tv": AppCategory.ENTERTAINMENT.value,
                "health": AppCategory.HEALTH.value,
                "wallet": AppCategory.FINANCE.value
            }
            
        return f"Profile created for {name} with {device_type} device. I've set up your common apps. What would you like to do?"
    
    @llm.ai_callable(description="Switch to a different app")
    def switch_app(
        self,
        app_name: Annotated[str, llm.TypeInfo(description="Name of the app to switch to")]
    ):
        logger.info("Switching to app: %s", app_name)
        
        app_name = app_name.lower()
        found_app = None
        
        # Try to find exact match
        if app_name in self._apps:
            found_app = app_name
        else:
            # Try to find partial match
            for app in self._apps:
                if app_name in app or app in app_name:
                    found_app = app
                    break
        
        if found_app:
            self._pending_action = f"Switch to {found_app} app"
            return f"I'm ready to switch to {found_app}. Would you like me to proceed?"
        else:
            return f"I couldn't find an app matching '{app_name}'. Available apps are: {', '.join(self._apps.keys())}"
    
    @llm.ai_callable(description="Run metrics analysis on an app")
    def analyze_app_metrics(
        self,
        app_name: Annotated[str, llm.TypeInfo(description="Name of the app to analyze")],
        metric_type: Annotated[str, llm.TypeInfo(description="Type of metrics to analyze (usage, performance, battery, data)")]
    ):
        logger.info("Analyzing app metrics - app: %s, metric_type: %s", app_name, metric_type)
        
        app_name = app_name.lower()
        found_app = None
        
        # Try to find exact match
        if app_name in self._apps:
            found_app = app_name
        else:
            # Try to find partial match
            for app in self._apps:
                if app_name in app or app in app_name:
                    found_app = app
                    break
        
        if not found_app:
            return f"I couldn't find an app matching '{app_name}'. Available apps are: {', '.join(self._apps.keys())}"
        
        metric_type = metric_type.lower()
        
        self._pending_action = f"Analyze {metric_type} metrics for {found_app}"
        return f"I'm ready to analyze {metric_type} metrics for {found_app}. This will access your app usage data. Would you like me to proceed?"
    
    @llm.ai_callable(description="Initiate a financial transaction")
    def initiate_transaction(
        self,
        app_name: Annotated[str, llm.TypeInfo(description="Name of the payment or banking app to use")],
        transaction_type: Annotated[str, llm.TypeInfo(description="Type of transaction (payment, transfer, subscription)")],
        amount: Annotated[float, llm.TypeInfo(description="Amount for the transaction")],
        recipient: Annotated[str, llm.TypeInfo(description="Recipient of the transaction (person, business, account)")] = None
    ):
        logger.info("Initiating transaction - app: %s, type: %s, amount: %f, recipient: %s", 
                   app_name, transaction_type, amount, recipient)
        
        app_name = app_name.lower()
        finance_apps = [app for app, category in self._apps.items() if category == AppCategory.FINANCE.value]
        
        found_app = None
        if app_name in finance_apps:
            found_app = app_name
        else:
            # If no specific app is mentioned or found, use the first finance app
            if finance_apps:
                found_app = finance_apps[0]
        
        if not found_app:
            return "I couldn't find any finance or payment apps on your device."
        
        transaction_details = f"Transaction type: {transaction_type}, Amount: ${amount:.2f}"
        if recipient:
            transaction_details += f", Recipient: {recipient}"
            
        self._pending_action = f"Initiate {transaction_type} of ${amount:.2f}" + (f" to {recipient}" if recipient else "") + f" using {found_app}"
        return f"I'm ready to initiate the following transaction using {found_app}:\n{transaction_details}\n\nThis requires security verification. Would you like to proceed?"
    
    @llm.ai_callable(description="Manage calendar events")
    def manage_calendar(
        self,
        action: Annotated[str, llm.TypeInfo(description="Calendar action (add, view, delete, update)")],
        event_title: Annotated[str, llm.TypeInfo(description="Title of the calendar event")] = None,
        event_date: Annotated[str, llm.TypeInfo(description="Date of the event (YYYY-MM-DD)")] = None,
        event_time: Annotated[str, llm.TypeInfo(description="Time of the event (HH:MM)")] = None,
        duration_minutes: Annotated[int, llm.TypeInfo(description="Duration of the event in minutes")] = 60
    ):
        logger.info("Managing calendar - action: %s, title: %s, date: %s, time: %s", 
                  action, event_title, event_date, event_time)
        
        action = action.lower()
        
        if action == "view":
            if len(self._calendar_events) == 0:
                return "You don't have any events scheduled in your calendar."
            
            events_str = "Here are your scheduled events:\n"
            for i, event in enumerate(self._calendar_events, 1):
                events_str += f"{i}. {event['title']} on {event['date']} at {event['time']} ({event['duration']} minutes)\n"
            return events_str
        
        elif action == "add":
            if not event_title or not event_date:
                return "I need at least an event title and date to add to your calendar."
            
            if event_time is None:
                event_time = "12:00"  # Default to noon
                
            # Validate date format
            try:
                datetime.datetime.strptime(event_date, '%Y-%m-%d')
            except ValueError:
                return "Please provide the date in YYYY-MM-DD format."
                
            # Create new event dictionary
            new_event = {
                "title": event_title,
                "date": event_date,
                "time": event_time,
                "duration": duration_minutes
            }
            
            self._pending_action = f"Add event '{event_title}' on {event_date} at {event_time} for {duration_minutes} minutes to calendar"
            return f"I'm ready to add the following event to your calendar:\n{event_title} on {event_date} at {event_time} for {duration_minutes} minutes.\n\nWould you like to confirm this?"
        
        elif action == "delete":
            if len(self._calendar_events) == 0:
                return "You don't have any events to delete."
                
            matching_events = []
            for i, event in enumerate(self._calendar_events):
                if event_title and event_title.lower() in event['title'].lower():
                    matching_events.append((i, event))
            
            if not matching_events:
                return f"I couldn't find any events with the title '{event_title}'."
                
            if len(matching_events) == 1:
                idx, event = matching_events[0]
                self._pending_action = f"Delete event '{event['title']}' on {event['date']} at {event['time']}"
                return f"I'm ready to delete the event '{event['title']}' on {event['date']} at {event['time']}. Would you like to proceed?"
            else:
                events_str = "I found multiple matching events. Please specify which one to delete:\n"
                for i, (idx, event) in enumerate(matching_events, 1):
                    events_str += f"{i}. {event['title']} on {event['date']} at {event['time']}\n"
                return events_str
        
        elif action == "update":
            if len(self._calendar_events) == 0:
                return "You don't have any events to update."
                
            if not event_title:
                return "I need at least the event title to find the event you want to update."
                
            matching_events = []
            for i, event in enumerate(self._calendar_events):
                if event_title and event_title.lower() in event['title'].lower():
                    matching_events.append((i, event))
            
            if not matching_events:
                return f"I couldn't find any events with the title '{event_title}'."
                
            if len(matching_events) == 1:
                idx, event = matching_events[0]
                updates = []
                if event_date:
                    updates.append(f"date to {event_date}")
                if event_time:
                    updates.append(f"time to {event_time}")
                if duration_minutes != 60:
                    updates.append(f"duration to {duration_minutes} minutes")
                
                if not updates:
                    return "Please specify what you want to update (date, time, or duration)."
                
                update_str = ", ".join(updates)
                self._pending_action = f"Update event '{event['title']}' ({update_str})"
                return f"I'm ready to update the event '{event['title']}' on {event['date']} at {event['time']}. I'll change {update_str}. Would you like to proceed?"
            else:
                events_str = "I found multiple matching events. Please specify which one to update:\n"
                for i, (idx, event) in enumerate(matching_events, 1):
                    events_str += f"{i}. {event['title']} on {event['date']} at {event['time']}\n"
                return events_str
        
        else:
            return f"I don't recognize the calendar action '{action}'. Available actions are: add, view, delete, update."
    
    @llm.ai_callable(description="Execute a voice command for natural language control of the device")
    def execute_voice_command(
        self,
        command: Annotated[str, llm.TypeInfo(description="The natural language command to execute")]
    ):
        logger.info("Executing voice command: %s", command)
        
        command = command.lower()
        
        # Detect command type
        if any(keyword in command for keyword in ["open", "launch", "start", "switch to", "go to"]):
            # App switching command
            for app_name in self._apps.keys():
                if app_name in command:
                    self._pending_action = f"Open the {app_name} app"
                    return f"I'll open {app_name} for you. Would you like me to proceed?"
            
            return "I couldn't identify which app you want to open. Could you specify the app name?"
            
        elif any(keyword in command for keyword in ["stats", "usage", "analyze", "metrics", "performance"]):
            # Metrics analysis command
            metric_type = "usage"  # Default
            for metric in ["usage", "performance", "battery", "data"]:
                if metric in command:
                    metric_type = metric
            
            for app_name in self._apps.keys():
                if app_name in command:
                    self._pending_action = f"Analyze {metric_type} for {app_name}"
                    return f"I'll analyze {metric_type} metrics for {app_name}. Would you like me to proceed?"
            
            return "I couldn't identify which app you want to analyze. Could you specify the app name?"
            
        elif any(keyword in command for keyword in ["pay", "send", "transfer", "transaction", "purchase"]):
            # Transaction command
            finance_apps = [app for app, category in self._apps.items() if category == AppCategory.FINANCE.value]
            if not finance_apps:
                return "I couldn't find any finance apps on your device."
                
            # Extract amount (simple pattern match)
            amount = None
            words = command.split()
            for i, word in enumerate(words):
                if word.startswith("$"):
                    try:
                        amount = float(word[1:])
                    except ValueError:
                        pass
                elif i > 0 and words[i-1] in ["send", "pay", "transfer"]:
                    try:
                        amount = float(word)
                    except ValueError:
                        pass
            
            if not amount:
                return "I couldn't identify the amount for the transaction. Could you specify an amount?"
                
            # Try to extract recipient
            recipient = None
            if "to" in command:
                to_index = command.find("to")
                recipient_part = command[to_index + 3:]
                recipient = recipient_part.split()[0]
                
            transaction_type = "payment"
            if "transfer" in command:
                transaction_type = "transfer"
                
            app_to_use = finance_apps[0]
            for app in finance_apps:
                if app in command:
                    app_to_use = app
                    
            transaction_details = f"Transaction type: {transaction_type}, Amount: ${amount:.2f}"
            if recipient:
                transaction_details += f", Recipient: {recipient}"
                
            self._pending_action = f"Make a {transaction_type} of ${amount:.2f}" + (f" to {recipient}" if recipient else "") + f" using {app_to_use}"
            return f"I'm ready to execute the following transaction using {app_to_use}:\n{transaction_details}\n\nThis requires security verification. Would you like to proceed?"
            
        elif any(keyword in command for keyword in ["calendar", "schedule", "appointment", "meeting", "event"]):
            # Calendar command
            if any(keyword in command for keyword in ["add", "create", "new", "schedule"]):
                # Extract event title (simple approach)
                title = None
                if "called" in command:
                    title_part = command.split("called")[1].strip()
                    title = title_part.split(" on ")[0].strip()
                elif "titled" in command:
                    title_part = command.split("titled")[1].strip()
                    title = title_part.split(" on ")[0].strip()
                
                if not title:
                    return "I couldn't identify the event title. Could you specify a title for the event?"
                    
                # Extract date (simple approach)
                date = None
                if "on" in command:
                    date_part = command.split("on")[1].strip()
                    # This is very simplistic - would need better date parsing in a real app
                    date = date_part.split()[0]
                    if not date.count('-') == 2:
                        date = datetime.datetime.now().strftime('%Y-%m-%d')  # Default to today
                        
                if not date:
                    date = datetime.datetime.now().strftime('%Y-%m-%d')  # Default to today
                
                # Extract time (simple approach)
                time = None
                if "at" in command:
                    time_part = command.split("at")[1].strip()
                    time = time_part.split()[0]
                    if ":" not in time:
                        time = "12:00"  # Default to noon
                
                if not time:
                    time = "12:00"  # Default to noon
                    
                self._pending_action = f"Add event '{title}' on {date} at {time} to calendar"
                return f"I'm ready to add the following event to your calendar:\n{title} on {date} at {time}.\n\nWould you like to confirm this?"
                
            elif any(keyword in command for keyword in ["show", "view", "list", "what", "check"]):
                return "I'll check your calendar. Note that in this demo, you don't have any events yet. You can add events using commands like 'add a meeting called Team Sync on 2025-03-10 at 14:00'."
                
            elif any(keyword in command for keyword in ["delete", "remove", "cancel"]):
                return "I'll check for events to delete. Note that in this demo, you don't have any events yet. You can add events first and then delete them."
                
            elif any(keyword in command for keyword in ["update", "change", "modify", "edit"]):
                return "I'll check for events to update. Note that in this demo, you don't have any events yet. You can add events first and then update them."
                
            else:
                return "I'm not sure what you want to do with your calendar. You can add, view, delete, or update events."
        
        else:
            return "I'm not sure what you're asking me to do. I can help with opening apps, analyzing app metrics, making transactions, and managing your calendar."