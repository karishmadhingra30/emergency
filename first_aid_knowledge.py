#!/usr/bin/env python3
"""
First Aid Knowledge Base
Contains emergency first aid information for common injuries and conditions.
"""

FIRST_AID_DATA = {
    "bleeding": {
        "title": "How to Stop Bleeding",
        "steps": [
            "1. Apply direct pressure with a clean cloth or bandage",
            "2. Maintain pressure for 10-15 minutes without checking",
            "3. If blood soaks through, add more cloth on top (don't remove the first layer)",
            "4. Elevate the injured area above heart level if possible",
            "5. Once bleeding stops, apply a bandage",
            "6. Seek medical help if bleeding is severe or doesn't stop"
        ],
        "warnings": [
            "⚠️ For severe bleeding, call emergency services immediately",
            "⚠️ Use a tourniquet only as a last resort for life-threatening bleeding"
        ]
    },

    "burns": {
        "title": "First Aid for Burns",
        "steps": [
            "1. Remove person from heat source",
            "2. Cool the burn with cool (not cold) running water for 10-20 minutes",
            "3. Remove jewelry and tight clothing before swelling starts",
            "4. Cover burn with sterile, non-stick bandage or clean cloth",
            "5. Give over-the-counter pain reliever if needed",
            "6. Do NOT apply ice, butter, or ointments"
        ],
        "warnings": [
            "⚠️ Seek immediate medical help for burns larger than 3 inches",
            "⚠️ Get emergency help for burns on face, hands, feet, genitals, or major joints",
            "⚠️ Third-degree burns (white or charred skin) need immediate medical attention"
        ]
    },

    "cpr": {
        "title": "CPR Instructions (Adult)",
        "steps": [
            "1. Check responsiveness - tap shoulder and shout",
            "2. Call emergency services (911/local emergency number)",
            "3. Place person on firm, flat surface",
            "4. Position hands: center of chest, between nipples",
            "5. Compressions: Push hard and fast - at least 2 inches deep",
            "6. Rate: 100-120 compressions per minute",
            "7. After 30 compressions, give 2 rescue breaths",
            "8. Continue until help arrives or person starts breathing"
        ],
        "warnings": [
            "⚠️ If untrained, do hands-only CPR (skip rescue breaths)",
            "⚠️ Don't stop CPR until professional help arrives"
        ]
    },

    "fracture": {
        "title": "Treating Fractures (Broken Bones)",
        "steps": [
            "1. Don't move the person unless necessary",
            "2. Immobilize the injured area",
            "3. Apply ice packs to reduce swelling (wrapped in cloth)",
            "4. Treat for shock if needed - keep person warm",
            "5. For open fracture, don't push bone back in",
            "6. Cover wound with sterile bandage",
            "7. Get medical help immediately"
        ],
        "warnings": [
            "⚠️ Don't try to realign the bone",
            "⚠️ Don't test bone's ability to move",
            "⚠️ All fractures need professional medical evaluation"
        ]
    },

    "choking": {
        "title": "Choking - Heimlich Maneuver",
        "steps": [
            "1. Ask 'Are you choking?' - if they can't speak, act immediately",
            "2. Stand behind person and wrap arms around waist",
            "3. Make a fist with one hand, place above navel",
            "4. Grasp fist with other hand",
            "5. Give quick, upward thrusts into abdomen",
            "6. Repeat until object is expelled",
            "7. If person becomes unconscious, begin CPR"
        ],
        "warnings": [
            "⚠️ For pregnant women or obese people, give chest thrusts instead",
            "⚠️ For infants under 1 year, use back blows and chest thrusts"
        ]
    },

    "shock": {
        "title": "Treating Shock",
        "steps": [
            "1. Call emergency services",
            "2. Lay person down with feet elevated 12 inches",
            "3. Keep person still and comfortable",
            "4. Loosen tight clothing",
            "5. Cover person with blanket to maintain body temperature",
            "6. Don't give anything to eat or drink",
            "7. Turn head to side if vomiting"
        ],
        "warnings": [
            "⚠️ Don't elevate head if there's a head, neck, or back injury",
            "⚠️ Don't elevate legs if it causes pain or potential harm"
        ]
    },

    "head_injury": {
        "title": "Head Injury Care",
        "steps": [
            "1. Keep person still and calm",
            "2. If bleeding, apply gentle pressure with clean cloth",
            "3. Apply ice pack to reduce swelling (wrapped in cloth)",
            "4. Watch for signs of concussion (confusion, vomiting, drowsiness)",
            "5. Don't remove objects embedded in skull",
            "6. Don't move person if neck injury is suspected",
            "7. Get immediate medical attention"
        ],
        "warnings": [
            "⚠️ Call emergency services for severe head injuries",
            "⚠️ Watch for changes in consciousness for 24 hours",
            "⚠️ Seek immediate help if person loses consciousness"
        ]
    },

    "heat_stroke": {
        "title": "Heat Stroke Treatment",
        "steps": [
            "1. Call emergency services immediately",
            "2. Move person to cool, shaded area",
            "3. Remove excess clothing",
            "4. Cool person with whatever means available:",
            "   - Cool water on skin",
            "   - Ice packs on neck, armpits, groin",
            "   - Fan while misting with water",
            "5. If conscious, give small sips of cool water",
            "6. Monitor body temperature"
        ],
        "warnings": [
            "⚠️ Heat stroke is life-threatening - always call emergency services",
            "⚠️ Don't give aspirin or acetaminophen",
            "⚠️ Don't give anything to drink if person is not fully conscious"
        ]
    },

    "hypothermia": {
        "title": "Hypothermia Treatment",
        "steps": [
            "1. Call emergency services",
            "2. Move person to warm, dry location",
            "3. Remove wet clothing",
            "4. Warm person gradually with blankets or body heat",
            "5. Cover head and neck (but not face)",
            "6. Give warm, non-alcoholic drinks if conscious",
            "7. Don't warm too quickly - can cause heart problems"
        ],
        "warnings": [
            "⚠️ Don't use direct heat (heating pad, hot water)",
            "⚠️ Don't give alcohol",
            "⚠️ Handle person gently - rough movement can trigger cardiac arrest"
        ]
    },

    "heart_attack": {
        "title": "Heart Attack Response",
        "symptoms": [
            "- Chest pain or discomfort",
            "- Pain in arms, back, neck, jaw, or stomach",
            "- Shortness of breath",
            "- Cold sweat, nausea, lightheadedness"
        ],
        "steps": [
            "1. Call emergency services immediately",
            "2. Help person sit down and rest comfortably",
            "3. Loosen tight clothing",
            "4. If person takes heart medication (nitroglycerin), help them take it",
            "5. Give aspirin if available and person is not allergic",
            "6. Be ready to perform CPR if needed",
            "7. Stay with person until help arrives"
        ],
        "warnings": [
            "⚠️ Time is critical - call emergency services immediately",
            "⚠️ Don't delay calling for help"
        ]
    },

    "stroke": {
        "title": "Stroke Recognition (FAST)",
        "symptoms": [
            "F - Face drooping (one side of face numb or drooping)",
            "A - Arm weakness (one arm weak or numb)",
            "S - Speech difficulty (slurred speech or hard to understand)",
            "T - Time to call emergency services"
        ],
        "steps": [
            "1. Call emergency services immediately",
            "2. Note time symptoms started",
            "3. Keep person calm and comfortable",
            "4. Lay person on their side if vomiting",
            "5. Don't give anything to eat or drink",
            "6. Stay with person until help arrives"
        ],
        "warnings": [
            "⚠️ Every minute counts - call emergency services immediately",
            "⚠️ Don't drive person to hospital yourself - wait for ambulance"
        ]
    },

    "poisoning": {
        "title": "Poisoning First Aid",
        "steps": [
            "1. Call Poison Control Center immediately (1-800-222-1222 in US)",
            "2. Don't give anything to eat or drink unless instructed",
            "3. Don't induce vomiting unless told to do so",
            "4. If person vomits naturally, turn head to side",
            "5. Keep poison container for reference",
            "6. Follow Poison Control instructions exactly"
        ],
        "warnings": [
            "⚠️ Call emergency services if person is unconscious or having seizures",
            "⚠️ Different poisons require different treatments"
        ]
    },

    "snake_bite": {
        "title": "Snake Bite Treatment",
        "steps": [
            "1. Call emergency services immediately",
            "2. Keep person calm and still (movement spreads venom)",
            "3. Remove jewelry and tight clothing before swelling",
            "4. Position bite below heart level if possible",
            "5. Clean bite with soap and water",
            "6. Cover with clean, dry bandage",
            "7. Try to remember snake's appearance for identification"
        ],
        "warnings": [
            "⚠️ Don't apply ice or tourniquet",
            "⚠️ Don't cut the wound or try to suck out venom",
            "⚠️ Don't give person alcohol or caffeine"
        ]
    },

    "allergic_reaction": {
        "title": "Severe Allergic Reaction (Anaphylaxis)",
        "symptoms": [
            "- Difficulty breathing or wheezing",
            "- Swelling of face, lips, or throat",
            "- Rapid pulse",
            "- Dizziness or fainting",
            "- Skin rash or hives"
        ],
        "steps": [
            "1. Call emergency services immediately",
            "2. Check if person has epinephrine auto-injector (EpiPen)",
            "3. Help person use auto-injector if available",
            "4. Have person lie down with feet elevated",
            "5. If breathing stops, begin CPR",
            "6. Stay with person until help arrives",
            "7. Second dose may be needed after 5-15 minutes"
        ],
        "warnings": [
            "⚠️ Anaphylaxis is life-threatening - call emergency services",
            "⚠️ Even after epinephrine, person needs hospital evaluation"
        ]
    },

    "sprain": {
        "title": "Sprain Treatment (RICE Method)",
        "steps": [
            "1. REST - Stop activity immediately",
            "2. ICE - Apply ice for 15-20 minutes every 2-3 hours",
            "3. COMPRESSION - Wrap with elastic bandage (not too tight)",
            "4. ELEVATION - Raise injured area above heart level",
            "5. Take over-the-counter pain reliever if needed",
            "6. Avoid using injured area for 48 hours",
            "7. See doctor if pain/swelling doesn't improve in 2-3 days"
        ],
        "warnings": [
            "⚠️ If you can't bear weight, see a doctor (may be fracture)",
            "⚠️ Severe sprains may require medical attention"
        ]
    }
}


def get_first_aid_info(query: str) -> dict:
    """
    Get first aid information based on query keywords.

    Args:
        query: User's question or keyword

    Returns:
        Dictionary with first aid information or general help message
    """
    query_lower = query.lower()

    # Keyword mapping
    keywords = {
        "bleeding": ["bleeding", "blood", "cut", "wound", "laceration"],
        "burns": ["burn", "scald", "fire", "heat burn"],
        "cpr": ["cpr", "cardiac", "not breathing", "unconscious", "chest compression"],
        "fracture": ["fracture", "broken bone", "break", "bone"],
        "choking": ["choking", "heimlich", "can't breathe", "airway blocked"],
        "shock": ["shock", "pale", "clammy"],
        "head_injury": ["head injury", "head wound", "concussion", "head trauma"],
        "heat_stroke": ["heat stroke", "heat exhaustion", "overheating"],
        "hypothermia": ["hypothermia", "cold", "freezing"],
        "heart_attack": ["heart attack", "chest pain", "cardiac arrest"],
        "stroke": ["stroke", "face drooping", "arm weakness"],
        "poisoning": ["poison", "poisoning", "toxic", "ingested"],
        "snake_bite": ["snake", "bite", "venomous"],
        "allergic_reaction": ["allergy", "allergic", "anaphylaxis", "epipen"],
        "sprain": ["sprain", "twisted", "ankle", "wrist"]
    }

    # Find matching condition
    for condition, keywords_list in keywords.items():
        if any(keyword in query_lower for keyword in keywords_list):
            return {
                "condition": condition,
                "info": FIRST_AID_DATA[condition],
                "found": True
            }

    # No specific match found
    return {
        "found": False,
        "message": "I can provide first aid information for:\n" +
                  "• Bleeding and wounds\n" +
                  "• Burns\n" +
                  "• CPR\n" +
                  "• Fractures (broken bones)\n" +
                  "• Choking\n" +
                  "• Shock\n" +
                  "• Head injuries\n" +
                  "• Heat stroke\n" +
                  "• Hypothermia\n" +
                  "• Heart attack\n" +
                  "• Stroke\n" +
                  "• Poisoning\n" +
                  "• Snake bites\n" +
                  "• Allergic reactions\n" +
                  "• Sprains\n\n" +
                  "Please specify what kind of first aid help you need."
    }


def format_first_aid_response(info_dict: dict) -> str:
    """
    Format first aid information as a readable text response.

    Args:
        info_dict: Dictionary with first aid information

    Returns:
        Formatted string response
    """
    if not info_dict.get("found"):
        return info_dict.get("message", "First aid information not found.")

    info = info_dict["info"]
    response = f"🏥 **{info['title']}**\n\n"

    # Add symptoms if present
    if "symptoms" in info:
        response += "**Symptoms:**\n"
        for symptom in info["symptoms"]:
            response += f"{symptom}\n"
        response += "\n"

    # Add steps
    if "steps" in info:
        response += "**Steps:**\n"
        for step in info["steps"]:
            response += f"{step}\n"
        response += "\n"

    # Add warnings
    if "warnings" in info:
        response += "**Important Warnings:**\n"
        for warning in info["warnings"]:
            response += f"{warning}\n"

    return response


if __name__ == "__main__":
    # Test the knowledge base
    test_queries = ["bleeding", "burns", "cpr", "heart attack"]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        info = get_first_aid_info(query)
        print(format_first_aid_response(info))
