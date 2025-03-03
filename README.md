# Flightly - Flight Booking and Assistance System
Live Here - https://huggingface.co/spaces/hitanshu326/FlightAI

Flightly is an intelligent flight booking system designed to help users book flights, check flight availability, and manage seat preferences, meal options, and special requests. The system also integrates a generative AI model to assist users with flight-related queries.

## Features
- **Flight Database**: Includes flight details, availability, seat preferences, and meal options for multiple destinations.
- **Booking System**: Users can book tickets by selecting destinations, dates, and ticket classes, along with seat preferences, meal requests, and other special requirements.
- **Loyalty Program**: Earn loyalty points with every booking.
- **AI Assistant**: Integration with Google Generative AI to assist users with flight-related questions and booking support.
- **CSV Database**: All booking information is stored in a CSV file for easy access and management.
  
## Flight Destinations
Currently, the system supports the following destinations:
- **London** (from New York)
- **Paris** (from Los Angeles)
- **Tokyo** (from San Francisco)
- **Berlin** (from Chicago)
- **Mumbai** (from Dubai)

Each destination has multiple ticket classes: Economy, Business, and First.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/flightai.git
    cd flightai
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up the environment variables by creating a `.env` file in the root of the project:
    ```plaintext
    GOOGLE_GENAI_API_KEY=your-api-key
    ```

4. Run the program:
    ```bash
    python main.py
    ```

## Usage

The system provides several functionalities:

1. **Booking a Ticket**:
    To book a flight ticket, call the `book_ticket` method from the `BookingSystem` class. Example:
    ```python
    booking_data = booking_system.book_ticket(
        destination="London", 
        num_tickets=1, 
        ticket_class="economy", 
        email="user@example.com", 
        date_str="2025-03-15", 
        seat_prefs={"location": "aisle"}, 
        meal_prefs={"type": "vegetarian"}, 
        special_requests="Extra legroom"
    )
    ```

2. **Checking Flight Availability**:
    To check the availability of a flight on a specific date:
    ```python
    availability = flight_db.check_availability("london", "2025-03-15", "economy")
    ```

3. **AI Assistant**:
    The AI assistant can help answer flight-related queries. Example:
    ```python
    assistant = AirlineAssistant()
    response = assistant.model.ask("What is the price for a business class ticket to London?")
    print(response)
    ```

## Data Structure

The `FlightDatabase` class contains information about:
- Available flights, seat preferences, and meal options.
- Booking availability for up to 30 days.
- Ticket pricing based on flight class.

The `BookingSystem` class manages:
- Ticket bookings with necessary details such as booking ID, confirmation code, and booking time.
- Loyalty points for each booking.
- Storing booking data in a CSV file.

## Booking Data Format

Each booking contains the following data:
- `booking_id`: Unique booking identifier.
- `confirmation_code`: A unique code generated for the booking.
- `email`: User's email address.
- `destination`: Flight destination.
- `date`: The date of the flight.
- `num_tickets`: Number of tickets booked.
- `ticket_class`: The class of the ticket (economy, business, first).
- `total_price`: The total price of the booking.
- `loyalty_points`: Loyalty points earned from the booking.
- `seat_preferences`: User's seat preference in JSON format.
- `meal_preferences`: User's meal preference in JSON format.
- `medical_assistance`: Medical assistance requirements in JSON format.
- `special_requests`: Any special requests made by the user.
- `booking_time`: The time the booking was made.

## Acknowledgments
- Uses `google-generativeai` for AI responses.
- Uses `gradio` for the frontend interface (if applicable).
- Uses `pandas` for managing booking data in CSV format.

