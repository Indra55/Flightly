import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import google.generativeai as genai
import gradio as gr
import pandas as pd
import hashlib
import re

class FlightDatabase:
    def __init__(self):
        self.meal_options = {
            "regular": ["vegetarian", "non-vegetarian", "vegan", "halal", "kosher"],
            "special": ["diabetic", "gluten-free", "low-sodium", "low-fat"]
        }
        self.seat_preferences = {
            "location": ["window", "aisle", "middle"],
            "section": ["front", "middle", "back"],
            "special": ["extra legroom", "bassinet", "wheelchair accessible"]
        }
        self.flights = {
            "london": {
                "source_city": "New York",  
                "economy": {"price": 799, "duration": "8h 15m", "airline": "British Airways", "baggage": "1 checked bag, 1 carry-on", "currency": "GBP", "flight_type": "non-stop", "departure_airports": ["Heathrow", "Gatwick"], "arrival_airports": ["London Heathrow"]},
                "business": {"price": 2399, "duration": "8h 15m", "airline": "British Airways", "baggage": "2 checked bags, 1 carry-on", "currency": "GBP", "flight_type": "non-stop", "departure_airports": ["Heathrow", "Gatwick"], "arrival_airports": ["London Heathrow"]},
                "first": {"price": 4999, "duration": "8h 15m", "airline": "British Airways", "baggage": "3 checked bags, 2 carry-ons", "currency": "GBP", "flight_type": "non-stop", "departure_airports": ["Heathrow", "Gatwick"], "arrival_airports": ["London Heathrow"]},
                "meal_service": True,
                "special_assistance": ["wheelchair", "medical oxygen", "special meals"],
                "seat_config": {
                    "economy": {"rows": "20-50", "layout": "3-3-3"},
                    "business": {"rows": "10-19", "layout": "2-2-2"},
                    "first": {"rows": "1-9", "layout": "1-2-1"}
                }
            },
            "paris": {
                "source_city": "Los Angeles",  
                "economy": {"price": 899, "duration": "6h 30m", "airline": "Air France", "baggage": "1 checked bag, 1 carry-on", "currency": "EUR", "flight_type": "non-stop", "departure_airports": ["Charles de Gaulle", "Orly"], "arrival_airports": ["Charles de Gaulle"]},
                "business": {"price": 2699, "duration": "6h 30m", "airline": "Air France", "baggage": "2 checked bags, 1 carry-on", "currency": "EUR", "flight_type": "non-stop", "departure_airports": ["Charles de Gaulle", "Orly"], "arrival_airports": ["Charles de Gaulle"]},
                "first": {"price": 5399, "duration": "6h 30m", "airline": "Air France", "baggage": "3 checked bags, 2 carry-ons", "currency": "EUR", "flight_type": "non-stop", "departure_airports": ["Charles de Gaulle", "Orly"], "arrival_airports": ["Charles de Gaulle"]}
            },
            "tokyo": {
                "source_city": "San Francisco",   
                "economy": {"price": 1400, "duration": "12h 50m", "airline": "ANA", "baggage": "1 checked bag, 1 carry-on", "currency": "JPY", "flight_type": "non-stop", "departure_airports": ["Narita", "Haneda"], "arrival_airports": ["Narita"]},
                "business": {"price": 4200, "duration": "12h 50m", "airline": "ANA", "baggage": "2 checked bags, 1 carry-on", "currency": "JPY", "flight_type": "non-stop", "departure_airports": ["Narita", "Haneda"], "arrival_airports": ["Narita"]},
                "first": {"price": 8400, "duration": "12h 50m", "airline": "ANA", "baggage": "3 checked bags, 2 carry-ons", "currency": "JPY", "flight_type": "non-stop", "departure_airports": ["Narita", "Haneda"], "arrival_airports": ["Narita"]}
            },
            "berlin": {
                "source_city": "Chicago",   
                "economy": {"price": 499, "duration": "8h 0m", "airline": "Lufthansa", "baggage": "1 checked bag, 1 carry-on", "currency": "EUR", "flight_type": "non-stop", "departure_airports": ["Berlin Tegel", "Berlin Schönefeld"], "arrival_airports": ["Berlin Tegel"]},
                "business": {"price": 1499, "duration": "8h 0m", "airline": "Lufthansa", "baggage": "2 checked bags, 1 carry-on", "currency": "EUR", "flight_type": "non-stop", "departure_airports": ["Berlin Tegel", "Berlin Schönefeld"], "arrival_airports": ["Berlin Tegel"]},
                "first": {"price": 2999, "duration": "8h 0m", "airline": "Lufthansa", "baggage": "3 checked bags, 2 carry-ons", "currency": "EUR", "flight_type": "non-stop", "departure_airports": ["Berlin Tegel", "Berlin Schönefeld"], "arrival_airports": ["Berlin Tegel"]}
            },
            "mumbai": {
                "source_city": "Dubai",   
                "economy": {"price": 1999, "duration": "9h 30m", "airline": "Emirates", "baggage": "1 checked bag, 1 carry-on", "currency": "INR", "flight_type": "one-stop", "departure_airports": ["Chhatrapati Shivaji International"], "arrival_airports": ["Chhatrapati Shivaji International"]},
                "business": {"price": 2499, "duration": "9h 30m", "airline": "Emirates", "baggage": "2 checked bags, 1 carry-on", "currency": "INR", "flight_type": "one-stop", "departure_airports": ["Chhatrapati Shivaji International"], "arrival_airports": ["Chhatrapati Shivaji International"]},
                "first": {"price": 3999, "duration": "9h 30m", "airline": "Emirates", "baggage": "3 checked bags, 2 carry-ons", "currency": "INR", "flight_type": "one-stop", "departure_airports": ["Chhatrapati Shivaji International"], "arrival_airports": ["Chhatrapati Shivaji International"]}
            }
        }
        self.seat_availability = self._initialize_seats()
        self.date_range = {
            "min_date": datetime.now(),
            "max_date": datetime.now() + timedelta(days=30)  # Change to 30 days instead of 365
        }
        
    def _initialize_seats(self):
        availability = {}
        today = datetime.now()
        for city in self.flights:
            availability[city] = {}
            for i in range(30):  
                date = today + timedelta(days=i)
                date_str = date.strftime('%m-%d')
                availability[city][date_str] = {
                    "economy": 100,
                    "business": 20,
                    "first": 10
                }
        return availability
    
    def check_availability(self, city, date_str, ticket_class):
        date_str = date_str[5:] 
        if city.lower() in self.seat_availability:
            if date_str in self.seat_availability[city.lower()]:
                return self.seat_availability[city.lower()][date_str][ticket_class.lower()]
        return 0
    
    def get_price(self, city, ticket_class):
        city = city.lower()
        ticket_class = ticket_class.lower()
        return self.flights.get(city, {}).get(ticket_class, {}).get('price', None)
    
    def is_valid_date(self, date_str):
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            if date < self.date_range["min_date"]:
                return False, "Cannot book for past dates"
            if date > self.date_range["max_date"]:
                return False, f"Bookings only available within next 30 days (until {self.date_range['max_date'].strftime('%Y-%m-%d')})"
            return True, "Date is valid"
        except ValueError:
            return False, "Invalid date format. Use YYYY-MM-DD"
    
    def get_available_dates(self, city):
        available_dates = []
        now = datetime.now()
        for i in range(30):  # Show next 30 days availability
            date = now + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            if self.check_availability(city, date_str, 'economy') > 0:
                available_dates.append(date_str)
        return available_dates

class BookingSystem:
    def __init__(self):
        # Use absolute path for CSV file
        self.db_file = os.path.join(os.path.dirname(__file__), 'bookings.csv')
        self.flight_db = FlightDatabase()
        self._initialize_db()
        
    def _initialize_db(self):
        columns = [
            "booking_id", "confirmation_code", "email", "destination", "date",
            "num_tickets", "ticket_class", "total_price", "loyalty_points",
            "seat_preferences", "meal_preferences", "medical_assistance",
            "special_requests", "booking_time"
        ]
        if not os.path.exists(self.db_file):
            pd.DataFrame(columns=columns).to_csv(self.db_file, index=False)
        
    def generate_booking_id(self):
        return f"BK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def calculate_loyalty_points(self, price):
        return int(price * 0.1)  
    
    def validate_email(self, email):
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def generate_confirmation_code(self, booking_id):
        return hashlib.md5(booking_id.encode()).hexdigest()[:8].upper()
    
    def find_booking(self, email):
        """Find an existing booking by email."""
        if os.path.exists(self.db_file):
            df = pd.read_csv(self.db_file)
            booking = df[df["email"] == email]
            if not booking.empty:
                return booking.iloc[0].to_dict()
        return None
    
    def update_booking(self, email, new_data):
        """Update an existing booking in the CSV file."""
        if os.path.exists(self.db_file):
            df = pd.read_csv(self.db_file)
            if email in df["email"].values:
                # Update the row with the new data
                for key, value in new_data.items():
                    df.loc[df["email"] == email, key] = value
                df.to_csv(self.db_file, index=False)
                return True
        return False
    
    def book_ticket(self, destination, num_tickets, ticket_class, email, date_str, full_name,
                   seat_prefs=None, meal_prefs=None, medical_needs=None, special_requests=None):
        try:
            print("\n📌 Attempting to save booking...")  
            print(f"✈️ Destination: {destination}, 🎟️ Tickets: {num_tickets}, 🏷️ Class: {ticket_class}")
            print(f"📧 Email: {email}, 📆 Date: {date_str}, 📝 Name: {full_name}")

            if not email or not self.validate_email(email):
                print("❌ Invalid Email!")  
                return {"error": "Invalid email address"}
            
            # Check if a booking already exists for this email
            existing_booking = self.find_booking(email)
            if existing_booking:
                print("🔄 Updating existing booking...")
                # Update the existing booking with new data
                new_data = {
                    "destination": destination.lower(),
                    "date": date_str,
                    "num_tickets": num_tickets,
                    "ticket_class": ticket_class,
                    "seat_preferences": json.dumps(seat_prefs or {}),
                    "meal_preferences": json.dumps(meal_prefs or {}),
                    "medical_assistance": json.dumps(medical_needs or []),
                    "special_requests": special_requests or "",
                    "booking_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                self.update_booking(email, new_data)
                return {"success": True, "booking_details": {**existing_booking, **new_data}}
            else:
                print("🆕 Creating new booking...")
                # Create a new booking
                booking_id = self.generate_booking_id()
                confirmation_code = self.generate_confirmation_code(booking_id)
                total_price = num_tickets * self.flight_db.get_price(destination.lower(), ticket_class)
                loyalty_points = self.calculate_loyalty_points(total_price)

                booking_data = {
                    "booking_id": booking_id,
                    "confirmation_code": confirmation_code,
                    "full_name": full_name,
                    "email": email,
                    "destination": destination.lower(),
                    "date": date_str,
                    "num_tickets": num_tickets,
                    "ticket_class": ticket_class,
                    "total_price": total_price,
                    "loyalty_points": loyalty_points,
                    "seat_preferences": json.dumps(seat_prefs or {}),
                    "meal_preferences": json.dumps(meal_prefs or {}),
                    "medical_assistance": json.dumps(medical_needs or []),
                    "special_requests": special_requests or "",
                    "booking_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

                # Append new booking data
                updated_df = pd.concat([pd.read_csv(self.db_file), pd.DataFrame([booking_data])], ignore_index=True)
                updated_df.to_csv(self.db_file, index=False)

                print("✅ Booking saved successfully!")
                return {"success": True, "booking_details": booking_data}

        except Exception as e:
            print(f"❌ Error while saving booking: {str(e)}")
            return {"error": f"Booking process failed: {str(e)}"}

class AirlineAssistant:
    def __init__(self):
        load_dotenv()
        genai.configure(api_key=os.getenv('GOOGLE_GENAI_API_KEY', 'your-key-if-not-using-env'))
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.booking_system = BookingSystem()
        flight_db = self.booking_system.flight_db
        
        self.system_message = f"""
### Role
You are a helpful and efficient flight booking assistant for FlightAI. Your goal is to assist users in booking flights, checking availability, and understanding pricing and loyalty points.

### Flight Data
- Destinations: {', '.join(flight_db.flights.keys())}
- Classes: Economy, Business, First
- Meal Options: {', '.join(flight_db.meal_options['regular'] + flight_db.meal_options['special'])}
- Seat Preferences: {', '.join(flight_db.seat_preferences['location'] + flight_db.seat_preferences['section'] + flight_db.seat_preferences['special'])}

### Process
1. **Understand User Request**:
   - Identify the user's intent (e.g., book flight, check availability, ask about price).
   - Ask clarifying questions to gather missing details (e.g., seat preference, meal preferences, medical needs).

2. **Validate Information**:
   - Ensure all required details are provided and valid:
     - Full Name (letters and spaces only)
     - Phone Number (exactly 10 digits)
     - Passport Number (6-9 uppercase alphanumeric characters)
     - Email Address (valid format: example@domain.com)
   - Validate meal preferences, seat preferences, and medical assistance requests.

3. **Provide Information**:
   - For availability requests: Check and clearly state availability for the requested destination, date, and class.
   - For price inquiries: Provide the price for the specified destination and class.
   - Explain loyalty points earned (10% of the total price).

4. **Confirm Booking**:
   - Confirm booking details with the user.
   - Proceed with booking if all details are correct and provide a confirmation message with booking ID and confirmation code.
   - If there are issues (e.g., invalid input, missing details, no availability), inform the user clearly and guide them on how to proceed.

### Rules
- Always check flight availability before confirming a booking.
- Be concise and professional in responses.
- Clearly present booking details, confirmations, and any validation errors.
- Confirm all special requirements and medical needs.
- Verify meal preferences match dietary restrictions.
- Ensure requested seats are available in the chosen class.

### Date Selection Rules
- Bookings available up to 365 days in advance.
- Dates must be in YYYY-MM-DD format.
- No bookings for past dates.
- Subject to seat availability.

### Example Conversations
1. **User**: "I want to book a flight to London."
   **Assistant**: "Sure! Could you please provide your full name, email, passport number, and travel date?"

2. **User**: "What's the price for a business class ticket to Tokyo?"
   **Assistant**: "A business class ticket to Tokyo costs $4200. Would you like to proceed with booking?"

3. **User**: "I need a vegetarian meal."
   **Assistant**: "Noted! Your vegetarian meal preference has been added to your booking."
"""
        self.current_booking = {}
        self.conversation_state = "initial"
        self.required_fields = ["full_name", "phone", "passport", "email", "destination", "date", "num_tickets", "ticket_class"]
        
    def validate_booking_details(self, details):
        return all(field in details for field in self.required_fields)
        
    def process_booking(self, details):
        print("\n⚙️ Processing booking with details:", json.dumps(details, indent=2))  # Debug print

        try:
            result = self.booking_system.book_ticket(
                destination=details.get("destination", ""),
                num_tickets=int(details.get("num_tickets", 1)),  # Default to 1 if missing
                ticket_class=details.get("ticket_class", "economy"),  # Default to economy
                email=details.get("email", ""),
                date_str=details.get("date", ""),
                full_name=details.get("full_name", ""),
                seat_prefs=details.get("seat_preferences"),
                meal_prefs=details.get("meal_preferences"),
                medical_needs=details.get("medical_assistance"),
                special_requests=details.get("special_requests")
            )
            
            print("\n🎟️ Booking Result:", result)  # Debug print

            return result
        except Exception as e:
            print(f"❌ Booking failed: {str(e)}")
            return {"error": f"Booking process failed: {str(e)}"}

        
    def extract_booking_details(self, message):
        # Enhanced information extraction
        import re
        
        # Extract email
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, message)
        if emails:
            self.current_booking["email"] = emails[0]
            
        # Extract phone numbers
        phone_pattern = r'\b\d{10}\b'
        phones = re.findall(phone_pattern, message)
        if phones:
            self.current_booking["phone"] = phones[0]
            
        # Extract passport numbers (6-9 alphanumeric characters)
        passport_pattern = r'\b[A-Z0-9]{6,9}\b'
        passports = re.findall(passport_pattern, message.upper())
        if passports:
            self.current_booking["passport"] = passports[0]
            
        # Extract dates
        date_pattern = r'\d{4}-\d{2}-\d{2}'
        dates = re.findall(date_pattern, message)
        if dates:
            is_valid, _ = self.booking_system.flight_db.is_valid_date(dates[0])
            if is_valid:
                self.current_booking["date"] = dates[0]
                
        # Extract number of tickets
        num_pattern = r'\b(\d+)\s+(?:ticket|tickets|seat|seats)\b'
        num_matches = re.findall(num_pattern, message.lower())
        if num_matches:
            self.current_booking["num_tickets"] = int(num_matches[0])
            
        # Extract destination
        for city in self.booking_system.flight_db.flights.keys():
            if city.lower() in message.lower():
                self.current_booking["destination"] = city
                break
                
        # Extract ticket class
        classes = ["economy", "business", "first"]
        for ticket_class in classes:
            if ticket_class in message.lower():
                self.current_booking["ticket_class"] = ticket_class
                break
                
        # Extract seat preferences
        seat_prefs = self.booking_system.flight_db.seat_preferences
        for location in seat_prefs["location"]:
            if location in message.lower():
                self.current_booking.setdefault("seat_preferences", {})["location"] = location
                break
                
        # Extract meal preferences
        meal_options = self.booking_system.flight_db.meal_options
        for meal_type in meal_options["regular"] + meal_options["special"]:
            if meal_type in message.lower():
                self.current_booking.setdefault("meal_preferences", []).append(meal_type)
            
    def chat(self, message, history):
        print("\n=========================")
        print(f"📩 User Message: {message}")  # Log user input

        messages = [self.system_message]

        # 🛠️ Extract booking details from message
        self.extract_booking_details(message)
        print(f"📝 Extracted Booking Details: {json.dumps(self.current_booking, indent=2)}")  

        # 🗂️ Add current booking state to LLM context
        context = f"""Current booking details: {json.dumps(self.current_booking, indent=2)}
        Conversation state: {self.conversation_state}
        """
        messages.append(context)

        # 💬 Add conversation history
        for human, assistant in history:
            messages.append(human)
            messages.append(assistant)
        messages.append(message)

        # 🚀 Generate LLM response
        response = self.model.generate_content(messages)
        response_text = response.text
        print(f"🤖 LLM Response Before Booking Check: {response_text}")

        # ✅ Update the booking after every response
        if "email" in self.current_booking:
            print("📝 Updating booking details in CSV...")
            booking_result = self.booking_system.book_ticket(
                destination=self.current_booking.get("destination", ""),
                num_tickets=int(self.current_booking.get("num_tickets", 1)),
                ticket_class=self.current_booking.get("ticket_class", "economy"),
                email=self.current_booking["email"],
                date_str=self.current_booking.get("date", ""),
                full_name=self.current_booking.get("full_name", ""),
                seat_prefs=self.current_booking.get("seat_preferences"),
                meal_prefs=self.current_booking.get("meal_preferences"),
                medical_needs=self.current_booking.get("medical_assistance"),
                special_requests=self.current_booking.get("special_requests")
            )
            print(f"🎟️ Booking Result: {booking_result}")

        print(f"📤 Final Response Sent: {response_text}")
        print("=========================")

        return response_text

 
def create_interface():
    assistant = AirlineAssistant()
    
    # Glassmorphism UI with cool blue and black tones
    custom_css = """
    .gradio-container {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
        text-align: center;
        padding: 20px;
    }
    
    .chat-message-container {
        border-radius: 12px;
        padding: 14px;
        margin: 8px 0;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .chat-message-container.user {
        background: rgba(0, 122, 255, 0.2);
        color: #ffffff;
    }
    
    .chat-message-container.bot {
        background: rgba(0, 150, 255, 0.2);
        color: #ffffff;
    }
    
    h1 {
        color: #ffffff;
        font-weight: 700;
        font-size: 2.2rem;
        letter-spacing: 0.5px;
    }
    
    button {
        background: rgba(0, 122, 255, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 12px 20px;
        font-size: 16px;
        color: #fff;
        border-radius: 10px;
        cursor: pointer;
        transition: transform 0.2s ease, background 0.3s ease;
        backdrop-filter: blur(8px);
    }
    
    button:hover {
        transform: scale(1.05);
        background: rgba(0, 122, 255, 0.6);
    }
    """
    
    return gr.ChatInterface(
        fn=assistant.chat,
        title="FLIGHTLY ✈️ | Glass AI Travel Assistant",
        description="Find flights, book trips, and plan your next adventure in a sleek glassmorphic UI.",
        css=custom_css,
        examples=[
            "Find me the cheapest flight to Tokyo.",
            "Show me first-class flights to London.",
            "I need a business-class ticket to Los Angeles next Friday.",
            "Do you have flights with pet-friendly options?"
        ],
        cache_examples=False,
    )

if __name__ == "__main__":
    interface = create_interface()
    interface.launch(share=True)
