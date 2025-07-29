# chatbot_service.py

from typing import Dict, Any, Optional, List
from utils import logger
from database_utils import db_manager  # For fetching chatbot knowledge base
import random  # For simple response selection


class ChatbotService:
    """
    Implements the Naledi intelligent chatbot functionality.
    Provides immediate, context-aware answers to user queries
    based on a table-driven knowledge base.
    """

    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
        if not self.knowledge_base:
            logger.warning(
                "Chatbot knowledge base is empty. Naledi will have limited responses."
            )

    def _load_knowledge_base(self) -> List[Dict[str, Any]]:
        """
        Loads question-answer pairs and conversational flows from the
        'chatbot' database table.
        Schema: id, category, question_keywords (comma-separated), answer, confidence_threshold (optional)
        """
        logger.info("Loading chatbot knowledge base from database.")
        query = "SELECT id, category, question_keywords, answer, confidence_threshold FROM Chatbot_Knowledge_Base;"
        kb_data = db_manager.execute_query(query)

        # Process keywords for easier matching
        for entry in kb_data:
            if entry.get("question_keywords"):
                entry["question_keywords"] = [
                    kw.strip().lower() for kw in entry["question_keywords"].split(",")
                ]
            else:
                entry["question_keywords"] = []

        logger.info(f"Loaded {len(kb_data)} entries into chatbot knowledge base.")
        return kb_data

    def _find_best_match(self, user_query: str) -> Optional[Dict[str, Any]]:
        """
        Finds the best matching answer in the knowledge base based on keywords.
        This is a simple keyword-based matching. For advanced NLU, a more
        sophisticated approach (e.g., embedding similarity) would be used.
        """
        user_query_lower = user_query.lower()
        best_match = None
        max_matches = 0

        for entry in self.knowledge_base:
            matches = sum(
                1
                for keyword in entry["question_keywords"]
                if keyword in user_query_lower
            )
            if matches > max_matches:
                max_matches = matches
                best_match = entry

        if best_match and max_matches > 0:
            # Simple confidence check (e.g., at least one keyword matched)
            # In a real system, you'd have a more robust confidence score.
            confidence = max_matches / len(user_query_lower.split())  # Simple ratio
            if confidence >= best_match.get(
                "confidence_threshold", 0.1
            ):  # Default threshold
                return best_match
        return None

    def get_chatbot_response(
        self, user_query: str, user_role: str = "Student"
    ) -> Dict[str, str]:
        """
        Generates a response to a user query.
        Can be extended to provide role-based responses.
        """
        logger.info(f"User query (Role: {user_role}): '{user_query}'")

        # Try to find a specific answer in the knowledge base
        matched_entry = self._find_best_match(user_query)

        if matched_entry:
            response = matched_entry["answer"]
            logger.info(f"Chatbot found specific answer: '{response[:50]}...'")
        else:
            # Fallback responses if no specific match is found
            fallback_responses = [
                "I'm sorry, I don't have enough information to answer that directly. Can you rephrase your question?",
                "Could you please provide more details? I'm still learning!",
                "I'm Naledi, your AI assistant. How can I help you with academic performance or platform features?",
                "I can help with questions about marks, attendance, and general platform usage. What would you like to know?",
            ]
            response = random.choice(fallback_responses)
            logger.info(f"Chatbot used fallback response: '{response[:50]}...'")

        # Example of role-based contextual response (conceptual)
        if "marks" in user_query.lower() and user_role == "Parent":
            response += (
                " As a parent, you can view your child's marks on their profile page."
            )
        elif "interventions" in user_query.lower() and user_role == "Teacher":
            response += " Teachers can manage interventions via the Interventions Management Page."

        return {"response": response}

    def add_knowledge_entry(
        self,
        category: str,
        question_keywords: List[str],
        answer: str,
        confidence_threshold: Optional[float] = None,
    ) -> bool:
        """
        Adds a new question-answer pair to the chatbot knowledge base in the database.
        This would typically be called by an administrator.
        """
        keywords_str = ",".join(question_keywords)
        query = """
        INSERT INTO Chatbot_Knowledge_Base (category, question_keywords, answer, confidence_threshold)
        VALUES (?, ?, ?, ?);
        """
        rows_affected = db_manager.execute_non_query(
            query, (category, keywords_str, answer, confidence_threshold)
        )
        if rows_affected > 0:
            logger.info(
                f"New knowledge entry added: '{question_keywords}' -> '{answer[:50]}...'"
            )
            self._load_knowledge_base()  # Reload knowledge base after adding
            return True
        else:
            logger.error(
                f"Failed to add new knowledge entry for keywords: {question_keywords}"
            )
            return False


# Example Usage:
if __name__ == "__main__":
    # Ensure db_manager is connected for this test
    try:
        db_manager.connect()
        # Create a dummy Chatbot_Knowledge_Base table if it doesn't exist
        db_manager.execute_non_query(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Chatbot_Knowledge_Base')
            CREATE TABLE Chatbot_Knowledge_Base (
                id INT IDENTITY(1,1) PRIMARY KEY,
                category NVARCHAR(100),
                question_keywords NVARCHAR(MAX),
                answer NVARCHAR(MAX),
                confidence_threshold FLOAT
            );
        """
        )
        db_manager.execute_non_query(
            "INSERT INTO Chatbot_Knowledge_Base (category, question_keywords, answer, confidence_threshold) VALUES ('General', 'hello,hi,hey', 'Hello! How can I assist you today?', 0.5) WHERE NOT EXISTS (SELECT 1 FROM Chatbot_Knowledge_Base WHERE question_keywords LIKE '%hello%');"
        )
        db_manager.execute_non_query(
            "INSERT INTO Chatbot_Knowledge_Base (category, question_keywords, answer, confidence_threshold) VALUES ('Marks', 'marks,grades,score', 'You can view your academic marks on your student profile page.', 0.3) WHERE NOT EXISTS (SELECT 1 FROM Chatbot_Knowledge_Base WHERE question_keywords LIKE '%marks%');"
        )
        db_manager.execute_non_query(
            "INSERT INTO Chatbot_Knowledge_Base (category, question_keywords, answer, confidence_threshold) VALUES ('Attendance', 'attendance,absent,present', 'Attendance records are available on your profile. Remember, weekends and holidays are excluded from calculations.', 0.4) WHERE NOT EXISTS (SELECT 1 FROM Chatbot_Knowledge_Base WHERE question_keywords LIKE '%attendance%');"
        )
        db_manager.execute_non_query(
            "INSERT INTO Chatbot_Knowledge_Base (category, question_keywords, answer, confidence_threshold) VALUES ('Interventions', 'intervention,support,help', 'Interventions are personalized actions to help improve your performance. Speak to your teacher for details.', 0.3) WHERE NOT EXISTS (SELECT 1 FROM Chatbot_Knowledge_Base WHERE question_keywords LIKE '%intervention%');"
        )

        chatbot = ChatbotService()

        print("\n--- Chatbot Interactions ---")
        print(chatbot.get_chatbot_response("Hi Naledi, how are you?"))
        print(
            chatbot.get_chatbot_response(
                "Where can I see my grades?", user_role="Student"
            )
        )
        print(
            chatbot.get_chatbot_response(
                "What about my attendance?", user_role="Parent"
            )
        )
        print(
            chatbot.get_chatbot_response(
                "Tell me about the support options.", user_role="Teacher"
            )
        )
        print(
            chatbot.get_chatbot_response(
                "I need help with something very specific that you probably don't know."
            )
        )

        # Test adding a new entry
        print("\n--- Adding new knowledge entry ---")
        new_entry_added = chatbot.add_knowledge_entry(
            "Contact",
            ["contact", "support", "reach out"],
            "For further assistance, please contact your school administrator or use the 'Contact Us' page.",
            0.6,
        )
        print(f"New entry added: {new_entry_added}")

        if new_entry_added:
            print(chatbot.get_chatbot_response("How can I contact support?"))

    except Exception as e:
        logger.error(f"An error occurred during chatbot_service test: {e}")
    finally:
        db_manager.close()
