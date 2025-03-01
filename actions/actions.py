from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import datetime
import random

# Database mockups
doctor_database = {
    "cardiologist": ["Mon", "Wed", "Fri"],
    "pediatrician": ["Mon", "Tue", "Thu"],
    "dermatologist": ["Tue", "Thu", "Fri"],
    "neurologist": ["Mon", "Wed"],
    "gynecologist": ["Tue", "Thu", "Fri"],
    "orthopedic": ["Mon", "Wed", "Fri"],
    "ophthalmologist": ["Tue", "Wed", "Thu"],
    "ent": ["Mon", "Tue", "Fri"],
    "dentist": ["Mon", "Tue", "Wed", "Thu", "Fri"],
}

location_database = {
    "downtown": {
        "address": "123 Main St, Downtown",
        "emergency": True,
        "pathology": True,
        "specialties": ["cardiologist", "neurologist", "pediatrician", "ent"],
    },
    "north": {
        "address": "456 North Ave, Northside",
        "emergency": True,
        "pathology": True,
        "specialties": ["orthopedic", "gynecologist", "dermatologist"],
    },
    "west": {
        "address": "789 West Blvd, Westside",
        "emergency": False,
        "pathology": True,
        "specialties": ["dentist", "ophthalmologist", "dermatologist"],
    },
    "east": {
        "address": "101 East Rd, Eastside",
        "emergency": False,
        "pathology": False,
        "specialties": ["pediatrician", "dentist"],
    },
}


class ActionCheckDoctorAvailability(Action):
    def name(self) -> Text:
        return "action_check_doctor_availability"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        specialty = tracker.get_slot("doctor_specialty")
        if not specialty or specialty.lower() not in doctor_database:
            dispatcher.utter_message(
                text=f"I'm sorry, I don't have information about {specialty} specialists. We have the following specialties: "
                + ", ".join(doctor_database.keys())
            )
            return []

        available_days = doctor_database[specialty.lower()]

        # Find locations with this specialty
        available_locations = []
        for loc_name, loc_data in location_database.items():
            if specialty.lower() in loc_data["specialties"]:
                available_locations.append(loc_name)

        dispatcher.utter_message(
            text=f"Our {specialty} specialists are available on {', '.join(available_days)} at our {', '.join(available_locations)} locations."
        )

        return []


class ActionScheduleAppointment(Action):
    def name(self) -> Text:
        return "action_schedule_appointment"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        specialty = tracker.get_slot("doctor_specialty")
        date = tracker.get_slot("appointment_date")
        time = tracker.get_slot("appointment_time")
        location = tracker.get_slot("location")

        # Validate all required information is present
        if not specialty or not date or not time:
            missing = []
            if not specialty:
                missing.append("specialty")
            if not date:
                missing.append("date")
            if not time:
                missing.append("time")

            dispatcher.utter_message(
                text=f"I'm missing some information to schedule your appointment: {', '.join(missing)}"
            )
            return []

        # Check if doctor is available on that day
        day_of_week = "Unknown"
        if date.lower() == "tomorrow":
            tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
            day_of_week = tomorrow.strftime("%a")
        elif date.lower() in [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]:
            day_of_week = date[:3]

        # Validate doctor availability on the day
        if (
            specialty.lower() in doctor_database
            and day_of_week[:3] not in doctor_database[specialty.lower()]
        ):
            dispatcher.utter_message(
                text=f"I'm sorry, our {specialty} specialists are not available on {date}. "
                f"They are available on {', '.join(doctor_database[specialty.lower()])}. "
                f"Would you like to choose another date?"
            )
            return []

        # If no location is provided, suggest one
        if not location:
            for loc_name, loc_data in location_database.items():
                if specialty.lower() in loc_data["specialties"]:
                    location = loc_name
                    break

            if location:
                dispatcher.utter_message(
                    text=f"I'll schedule your appointment at our {location} location, where we have {specialty} specialists."
                )
                return [SlotSet("location", location)]
            else:
                dispatcher.utter_message(
                    text=f"I couldn't find a location with {specialty} specialists. Please contact our helpdesk."
                )
                return []

        # Check if the specialty is available at the chosen location
        if (
            location.lower() in location_database
            and specialty.lower()
            not in location_database[location.lower()]["specialties"]
        ):
            # Suggest alternative locations
            alt_locations = []
            for loc_name, loc_data in location_database.items():
                if specialty.lower() in loc_data["specialties"]:
                    alt_locations.append(loc_name)

            if alt_locations:
                dispatcher.utter_message(
                    text=f"Our {specialty} specialists are not available at the {location} location. "
                    f"They are available at our {', '.join(alt_locations)} locations. "
                    f"Would you like to schedule at one of these locations instead?"
                )
                return []

        # All validations passed, confirm appointment
        # In a real system, this would interact with an actual scheduling database
        confirmation_code = "".join(
            random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6)
        )

        dispatcher.utter_message(
            text=f"Great! I've scheduled your appointment with a {specialty} for {date} in the {time} "
            f"at our {location} location. Your confirmation code is {confirmation_code}. "
            f"You'll also receive a confirmation email shortly."
        )

        return []


class ActionFindNearestEmergency(Action):
    def name(self) -> Text:
        return "action_find_nearest_emergency"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        emergency_type = tracker.get_slot("emergency_type")
        user_location = tracker.get_slot("location")

        # If we have a location from the user, check if it has emergency services
        if user_location and user_location.lower() in location_database:
            if location_database[user_location.lower()]["emergency"]:
                return [SlotSet("location", user_location)]

        # Find the nearest emergency location
        emergency_locations = []
        for loc_name, loc_data in location_database.items():
            if loc_data["emergency"]:
                emergency_locations.append((loc_name, loc_data["address"]))

        if emergency_locations:
            # For a real application, you would calculate the actual nearest location
            # For our demo, we'll just take the first one
            nearest = emergency_locations[0]
            dispatcher.utter_message(
                text=f"For your {emergency_type} emergency, please go to our {nearest[0]} location at {nearest[1]} immediately, or call 911."
            )
            return [SlotSet("location", nearest[0])]

        # If no emergency locations found
        dispatcher.utter_message(
            text="Please call 911 immediately or go to the nearest hospital emergency room."
        )
        return []


class ActionFindNearestPathology(Action):
    def name(self) -> Text:
        return "action_find_nearest_pathology"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        test_type = tracker.get_slot("test_type")
        user_location = tracker.get_slot("location")

        # If we have a location from the user, check if it has pathology services
        if user_location and user_location.lower() in location_database:
            if location_database[user_location.lower()]["pathology"]:
                return [SlotSet("location", user_location)]

        # Find all pathology locations
        pathology_locations = []
        for loc_name, loc_data in location_database.items():
            if loc_data["pathology"]:
                pathology_locations.append((loc_name, loc_data["address"]))

        if pathology_locations:
            # For a real application, you would calculate the actual nearest location
            # For our demo, we'll just take the first one
            nearest = pathology_locations[0]

            if test_type:
                dispatcher.utter_message(
                    text=f"For your {test_type} test, our nearest pathology center is at our {nearest[0]} location: {nearest[1]}. "
                    f"The center is open from 7 AM to 7 PM on weekdays and 8 AM to 2 PM on weekends. "
                    f"No appointment is needed for most basic tests."
                )
            else:
                dispatcher.utter_message(
                    text=f"Our nearest pathology center is at our {nearest[0]} location: {nearest[1]}. "
                    f"The center is open from 7 AM to 7 PM on weekdays and 8 AM to 2 PM on weekends. "
                    f"No appointment is needed for most basic tests."
                )

            return [SlotSet("location", nearest[0])]

        # If no pathology locations found
        dispatcher.utter_message(
            text="I'm sorry, I couldn't find pathology services in our system. Please call our main helpline for assistance."
        )
        return []


class ActionHumanHandoff(Action):
    def name(self) -> Text:
        return "action_human_handoff"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # In a real system, this would trigger a notification to a human agent
        # and possibly put the user in a queue

        dispatcher.utter_message(
            text="I understand this requires personal attention. I'm transferring you to our healthcare team. "
            "A representative will be with you shortly. Your conversation ID is: HC"
            + "".join(random.choices("0123456789", k=6))
        )

        return []
