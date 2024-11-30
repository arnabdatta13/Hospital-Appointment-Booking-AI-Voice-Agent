from openai import OpenAI
from IPython.display import Image
import json
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

MODEL = "gpt-4o-2024-08-06"

appointment_delete_tool ={
    "type": "function",  # Correct tool type
    "function": {
        "name": "delete_appointment_tool",
        "description": "Deletes an appointment based on the provided appointment ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "appointment_id": {"type": "string", "description": "The unique ID of the appointment that the user wants to delete."},
            },
            "required": ["appointment_id"],
            "additionalProperties": False
        },
        "strict": True
    }
}



appointment_changing_tool = {
  "type": "function",
  "function": {
    "name": "change_appointment_tool",
    "description": "Changes the details of an existing appointment based on the provided appointment ID.",
    "parameters": {
      "type": "object",
      "properties": {
        "appointment_id": {
          "type": "string",
          "description": "The unique ID of the appointment that the user wants to change."
        },
        "changing_data": {
          "type": "string",
          "description": "An object containing the new appointment details. It can include one or more of the following details : new_date, new_time, new_phone_number."
        },
      },
      "required": ["appointment_id","changing_data"],  # Only appointment_id is required
      "additionalProperties": False
    },
    "strict": True
  }
}




# Appointment booking tool
appointment_tool = {
    "type": "function",
    "function": {
        "name": "appointment_tool",
        "description": "Book an appointment by providing all necessary details like problem issue, hospital division, hospital name, user details, and appointment timing.",
        "parameters": {
            "type": "object",
            "properties": {
                "problem_details": {"type": "string", "description": "The issue or problem for which the appointment is being booked"},
                "hospital_division": {"type": "string", "description": "The division or region where the hospital is located"},
                "hospital_name": {"type": "string", "description": "The name of the hospital where the appointment is being booked"},
                "user_name": {"type": "string", "description": "The name of the user booking the appointment"},
                "user_phone_number": {"type": "string", "description": "The phone number of the user booking the appointment"},
                "appointment_date": {"type": "string", "description": "The date of the appointment (e.g., YYYY-MM-DD)"},
                "time": {"type": "string", "description": "The time of the appointment (e.g., HH:MM)"},
            },
            "required": [
                "problem_details",
                "hospital_division",
                "hospital_name",
                "user_name",
                "user_phone_number",
                "appointment_date",
                "time",
            ],
            "additionalProperties": False
        },
        "strict": True
    }
}


# Emergency appointment booking tool
emergency_appointment_booking_tool = {
    "type": "function",
    "function": {
        "name": "emergency_appointment_tool",
        "description": "Book an emergency appointment by providing necessary details like problem details, hospital, user name, phone number and date.",
        "parameters": {
            "type": "object",
            "properties": {
                "problem_details": {"type": "string", "description": "Details of the problem requiring an emergency appointment"},
                "hospital": {"type": "string", "description": "The name of the hospital where the emergency appointment is being booked"},
                "user_name": {"type": "string", "description": "The name of the user booking the emergency appointment"},
                "user_phone_number": {"type": "string", "description": "The phone number of the user booking the emergency appointment"},
                "appointment_date": {"type": "string", "description": "The date of the appointment (e.g., YYYY-MM-DD)"},
            },
            "required": [
                "problem_details",
                "hospital",
                "user_name",
                "user_phone_number",
                "appointment_date",
            ],
            "additionalProperties": False
        },
        "strict": True
    }
}



appointment_database= {}
# Available time slots database (dictionary)
available_time_slots = {
    "2024-08-21": {
        "09:00": True,
        "10:00": True,
        "11:00": True,
        "12:00": True,
        "13:00": True,
        "14:00": True,
        "15:00": True,
    },
    "2024-08-22": {
        "09:00": True,
        "10:00": True,
        "11:00": True,
        "12:00": True,
        "13:00": True,
        "14:00": True,
        "15:00": True,
    },
    # Add more dates and times as needed
}

# Function to check if a slot is available
def check_slot_availability(date, time):
    if date in available_time_slots and time in available_time_slots[date]:
        return available_time_slots[date][time]
    else:
        return False

# Function to book a slot
def book_slot(date, time):
    if check_slot_availability(date, time):
        available_time_slots[date][time] = False
        print(f"Slot booked: {date} at {time}")
    else:
        print(f"Slot not available: {date} at {time}")


def generate_appointment_id(phone_number):
    return f"{phone_number}"

def save_appointment(appointment_type,treatment_details,location,hospital_name,user_name, phone_number, date, time):
    # Generate a unique appointment ID
    appointment_id = generate_appointment_id(phone_number)
    
    # Save the appointment data to the database
    appointment_database[appointment_id] = {
        "appointment_type":appointment_type,
        "treatment": treatment_details,
        "location":location,
        "hospital_name":hospital_name,
        "user_name": user_name,
        "phone_number": phone_number,
        "date": date,
        "time": time,
    }
    print(appointment_database)
    print(f"Appointment saved for {user_name} on {date} at {time}")
    return appointment_id

# Tool execution logic
def execute_tool(tool_calls, messages):
    global conversation_messages
    global treatment_data_store

    for tool_call in tool_calls:
        print(tool_call)
        tool_name = tool_call.function.name
        print(tool_name)
        tool_arguments = json.loads(tool_call.function.arguments)
        print(tool_arguments)
        
        if tool_name == "appointment_tool":
            # Extract the date and time from the tool arguments
            problem_details = tool_arguments["problem_details"]
            location = tool_arguments["hospital_division"]
            hospital_name = tool_arguments["hospital_name"]
            name = tool_arguments["user_name"]
            phone_number = tool_arguments["user_phone_number"]
            date = tool_arguments["appointment_date"]
            time = tool_arguments["time"]

            # Check if the slot is available before booking
            if check_slot_availability(date, time):
                # Book the slot by marking it as False (booked)
                book_slot(date, time)
                
                # Save the appointment to the database
                appointment_id = save_appointment("Normal",problem_details,location,hospital_name,name, phone_number, date, time)
                
                # Log the appointment details
                print(f"Appointment booked successfully for {name} on {date} at {time}. Your appointment ID is {appointment_id}.Are you need anything else?")
                
                # Append the appointment confirmation to the messages
                messages.append({
                    "role": "assistant",
                    "content": f"Appointment booked successfully for {name} on {date} at {time}. Your appointment ID is {appointment_id}.Are you need anything else?"
                })
            else:
                # Inform the user that the selected slot is unavailable
                print(f"Sorry, the time slot {time} on {date} is unavailable. Please choose another time.")
                messages.append({
                    "role": "assistant", 
                    "content": f"Sorry, the time slot {time} on {date} is unavailable. Please choose another time."
                })


        elif tool_name == "emergency_appointment_tool":
            # Handle emergency appointment logic
            problem_details = tool_arguments["problem_details"]
            hospital = tool_arguments["hospital"]
            name = tool_arguments["user_name"]
            phone_number = tool_arguments["user_phone_number"]
            date = tool_arguments["appointment_date"]

            
            # Save the emergency appointment
            appointment_id = save_appointment("Emergency",problem_details,"N/A" ,hospital, name, phone_number, date, "N/A")

            print(f"Emergency appointment booked successfully for {name} at {hospital} on {date}. Your appointment ID is {appointment_id}. Do you need anything else?")
            messages.append({
                "role": "assistant",
                "content": f"Emergency appointment booked successfully for {name} at {hospital} on {date}. Your appointment ID is {appointment_id}. Do you need anything else?"
            })


        elif tool_name == "delete_appointment_tool":
            appointment_id = tool_arguments["appointment_id"]
            if appointment_id in appointment_database:
                del appointment_database[appointment_id]
                print(f"Appointment {appointment_id} deleted successfully. Do you need anything else?")
                messages.append({
                    "role": "assistant",
                    "content": f"Appointment {appointment_id} deleted successfully. Do you need anything else?"
                })
            else:
                print(f"Appointment ID {appointment_id} not found. Please provide a valid appointment ID.")
                messages.append({
                    "role": "assistant",
                    "content": f"Appointment ID {appointment_id} not found. Please provide a valid appointment ID."
                })

        elif tool_name == "change_appointment_tool":
            appointment_id = tool_arguments["appointment_id"]
            new_details = json.loads(tool_arguments["changing_data"])  # Parse the JSON string to a dictionary
            
            # Assuming you want to update the appointment with new details
            if appointment_id in appointment_database:
                appointment = appointment_database[appointment_id]
                
                # Check if the new date is provided
                if "new_date" in new_details:
                    new_date = new_details["new_date"]
                    current_time = appointment["time"]  # Keep the existing time
                    if appointment["appointment_type"] == "Emergency":
                        appointment["date"] = new_date
                        print(f"Appointment {appointment_id} date updated to {new_date}. Do you need anything else?")
                        messages.append({
                            "role": "assistant",
                            "content": f"Appointment {appointment_id} date updated to {new_date}. Do you need anything else?"
                        })
                    else:
                        # Check if the new date and current time is available
                        if check_slot_availability(new_date, current_time):
                            appointment["date"] = new_date
                            print(f"Appointment {appointment_id} date updated to {new_date}. Do you need anything else?")
                            messages.append({
                                "role": "assistant",
                                "content": f"Appointment {appointment_id} date updated to {new_date}. Do you need anything else?"
                            })
                        else:
                            print( f"Sorry, the current time slot {current_time} on the new date {new_date} is unavailable.Please provide a another date.")
                            messages.append({
                                "role": "assistant",
                                "content": f"Sorry, the current time slot {current_time} on the new date {new_date} is unavailable.Please provide a another date."
                            })
                
                # Check if the new time is provided
                if "new_time" in new_details:
                    new_time = new_details["new_time"]
                    current_date = appointment["date"]  # Keep the existing date
                    
                    # Check if the new time and current date is available
                    if check_slot_availability(current_date, new_time):
                        appointment["time"] = new_time
                        print(f"Appointment {appointment_id} time updated to {new_time}. Do you need anything else?")
                        messages.append({
                            "role": "assistant",
                            "content": f"Appointment {appointment_id} time updated to {new_time}. Do you need anything else?"
                        })
                    else:
                        print(f"Sorry, the time slot {new_time} on the current date {current_date} is unavailable.Please provide a another time.")
                        messages.append({
                            "role": "assistant",
                            "content": f"Sorry, the time slot {new_time} on the current date {current_date} is unavailable.Please provide a another time."
                        })

                #print(f"Appointment {appointment_id} updated successfully. Do you need anything else?")
            else:
                print(f"Appointment ID {appointment_id} not found. Please provide a valid appointment ID.")
                messages.append({
                    "role": "assistant",
                    "content": f"Appointment ID {appointment_id} not found. Please provide a valid appointment ID."
                })


    return messages

# Example database
hospital_database = {
    "emergency_hospitals": ["General Hospital A", "City Care Emergency", "QuickAid Clinic"],
    "divisions": {
        "North": ["Northside Hospital", "HealthFirst North"],
        "South": ["South General Hospital", "CarePlus South"],
        "East": ["EastMed Center", "BrightCare East"],
        "West": ["WestEnd Medical", "Sunrise Health West"]
    },
    "basic_treatments": {
        "fever": "Stay hydrated and take over-the-counter medication like paracetamol. If symptoms persist, consult a doctor.",
        "cold": "Rest, drink warm fluids, and use saline nasal spray. Over-the-counter decongestants can help.",
        "headache": "Rest in a quiet, dark room. Over-the-counter pain relievers like ibuprofen can help."
    }
}

# Formatting data for the prompt
emergency_hospitals_list = ", ".join(hospital_database["emergency_hospitals"])
division_hospitals_list = {
    division: ", ".join(hospitals)
    for division, hospitals in hospital_database["divisions"].items()
}
basic_treatments_list = "\n".join(
    [f"- {condition}: {treatment}" for condition, treatment in hospital_database["basic_treatments"].items()]
)


prompt = f"""
# Context
You are Emili, a friendly and professional virtual assistant for AI Health Mate. Your primary role is to assist users in:

1. **Booking Appointments**: Regular and emergency appointments.
2. **Changing Appointments**: Modifying existing appointments.
3. **Deleting Appointments**: Removing existing appointments.
4. **Providing Basic Home Treatment**: Offering guidance for simple ailments treatable from home.

# Task Flow

1. **Greet the User**:
   - Start each interaction with a warm and empathetic greeting.
   - Example: "Hello, I’m Emili from AI Health Mate! How can I assist you today?"

2. **Address Treatment, Location, and Hospital First**:
   - Always start by addressing the user's treatment needs, location, and hospital selection before proceeding to book or manage appointments.

3. **Identify the Problem**:
   - If the user wants to book an appointment or seeks basic treatment, begin by asking the user to describe their problem.
   - Example: "Could you please describe the issue you're facing?"
   - **Skip this step if the user wants to change or delete an existing appointment.**

4. **Classify the Problem**:
   - Based on the problem described:
     - **Serious Issues**: If the problem seems serious, recommend an emergency appointment.
     - **Basic Issues**: If it’s a simple issue, provide a basic home treatment solution.
     - **Regular Appointments**: If they want to consult a doctor, guide them through the booking process.

5. **Handle Emergency Appointments**:
   - If the problem is serious:
     1. Inform the user of the need for an emergency appointment.
     2. Present the following list of hospitals offering emergency appointments:
        {emergency_hospitals_list}
     3. Let the user select the hospital.
     4. Collect the following details **one by one**:
        - **Step 1**: Ask for the user's **name**.
        - **Step 2**: Ask for the user's **phone number**.
        - **Step 3**: Ask for the user's preferred **appointment date**.
     5. Confirm each piece of information with the user before proceeding to the next step.
     6. Call the **emergency appointment booking tool** to confirm the appointment.

6. **Provide Basic Treatment**:
   - If the issue is treatable at home, refer to the following predefined treatments:
     {basic_treatments_list}
   - Example: "For a mild fever, stay hydrated and take over-the-counter medication like paracetamol. If symptoms persist, consult a doctor."

7. **Handle Regular Appointments**:
   - If the user wants to book a regular appointment:
     1. Ask the user to specify their **division** (region they are from).
     2. Based on the division, suggest the following hospitals:
        {json.dumps(division_hospitals_list, indent=2)}
     3. Once the user selects a hospital, collect the following details **one by one**:
        - **Step 1**: Ask for the user's **name**.
        - **Step 2**: Ask for the user's **phone number**.
        - **Step 3**: Ask for the user's preferred **appointment date**.
        - **Step 4**: Once the user provides the date, suggest all available time slots for that date from the database:
          {available_time_slots} and also Ask the user for their preferred **time** and confirm availability.

     4. Confirm each piece of information with the user before proceeding to the next step.
     5. Call the **appointment booking tool** to finalize the appointment.

8. **Handle Appointment Changes**:
   - If the user wants to modify an existing appointment:
     1. Ask the user for their **appointment ID**.
     2. Ask what they want to change (e.g., date, time).
     3. Collect the new details **one by one** and confirm each before proceeding.
     4. Call the **appointment change tool** to update the appointment.
     5. Confirm the updated details and provide a new appointment ID if necessary.

9. **Handle Appointment Deletion**:
   - If the user wants to delete an appointment:
     1. Ask the user for their **appointment ID**.
     2. Confirm with the user that they want to delete the appointment.
     3. Call the **appointment deletion tool** to remove the appointment.
     4. Inform the user that the appointment has been successfully deleted.

10. **Handle Incorrect Input**:
    - If the user provides incorrect information:
      1. Politely ask them to correct it.
      2. Confirm the corrected information before proceeding.

# Style

1. **Professional and Empathetic**:
   - Maintain a friendly and professional tone throughout the conversation.
   - Show genuine concern for the user's health and wellbeing.

2. **Clear and Concise**:
   - Use simple and direct language. Avoid medical jargon unless necessary.

3. **Step-by-Step Assistance**:
   - Ask one question at a time and wait for the user’s response before proceeding.

# Guidelines

1. **Emergency Handling**:
   - Always prioritize emergencies. Provide a hospital list and ensure the user gets their appointment swiftly.

2. **Basic Treatment**:
   - Use predefined treatment solutions for common issues. Avoid giving medical advice outside the scope of the database.

3. **Regular Appointments**:
   - Ensure all details are collected in the right order and confirmed before running the booking tool.

4. **Database Usage**:
   - Use hospital and treatment information from the database for recommendations.

5. **Respect User Decisions**:
   - If the user decides not to proceed with an appointment or treatment, acknowledge their choice respectfully.
"""


conversation_messages = []
# Handle appointment booking logic
def handle_appointment_booking_agent(query, conversation_messages):
    global current_agent
    messages = [{"role": "system", "content": prompt}]
    conversation_messages.append({"role": "user", "content": query})
    messages.extend(conversation_messages)

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.1,
        tools= [appointment_tool , emergency_appointment_booking_tool,appointment_changing_tool,appointment_delete_tool],
    )
    if response.choices[0].message.content is not None:
        print(response.choices[0].message.content)
        conversation_messages.append({"role": "assistant", "content": response.choices[0].message.content})
        
    tool_calls = response.choices[0].message.tool_calls
    if tool_calls:
        for tool_call in tool_calls:
            if tool_call:
                execute_tool([tool_call], conversation_messages)
                return  # Exit after handling

            
while True:
    user = input()
    handle_appointment_booking_agent(user,conversation_messages)
