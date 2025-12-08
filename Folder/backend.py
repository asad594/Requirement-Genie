import requests
import os
import re
from datetime import datetime
import pathlib
import time


class Backend:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://openrouter.ai/api/v1/chat/completions"

        # System instructions
        self.conversation = [
            {
                "role": "system",
                "content": (
                    "You are an expert Business Analyst and Requirements Engineer. "
                    "Your job is to professionally gather, clarify, and document all types of requirements for any software system.\n\n"
                    "Follow these rules:\n"
                    "1. Use a professional BA tone.\n"
                    "2. Always ask clarifying questions before finalizing requirements.\n"
                    "3. Never assume — if anything is vague, incomplete, or ambiguous, ask for details.\n"
                    "4. Convert all requirements into clear, testable, structured output.\n"
                    "5. Categorize requirements ONLY into: Business (BR), Functional (FR), Non-Functional (NFR), Security (SR), and UI/UX (UX).\n"
                    "6. Use 'The system shall…' for functional requirements.\n"
                    "7. Use measurable language for non-functional requirements (e.g., response time < 2 seconds).\n"
                    "8. Ask each question one by one.\n",

                )
            }
        ]

        # Initialize requirements storage structure (Only 5 categories)
        self.requirements = {
            "Business Requirements": [],
            "Functional Requirements": [],
            "Non-Functional Requirements": [],
            "Security Requirements": [],
            "UI/UX Requirements": []
        }

        # Explicit prefix mapping for the file format
        self.prefix_map = {
            "Business Requirements": "BR",
            "Functional Requirements": "FR",
            "Non-Functional Requirements": "NFR",
            "Security Requirements": "SR",
            "UI/UX Requirements": "UX"
        }

        # Question flow - EXACTLY matching user's provided list structure + the tail questions
        self.questions = [
            "What is the official name of the project?",
            "What are the main user roles in the system?",
            "What are the main user roles (e.g., Admin, Guest, Member) involved in the system?",
            "Describe the complete registration and login process for these users.",
            "What specific information must be captured in the user's profile?",
            "Describe the main dashboard. What widgets or data summaries should users see immediately?",
            "What is the core workflow or primary task a user performs in the system?",
            "Does the system require a search functionality? If so, what data fields are searchable?",
            "Describe any reporting capabilities. What specific reports must be generated?",
            "Detail the notification system. Who gets notified, when, and via what channels (Email, SMS)?",
            "Are there any payment or transaction features? Describe the checkout flow.",
            "Detail any data import or export features (e.g., Download as PDF/CSV).",
            "What is the expected maximum response time for a web page load (e.g., < 2 seconds)?",
            "How many concurrent users must the system support at peak times?",
            "What is the required system uptime availability (e.g., 99.9%)?",
            "Detail the security requirements regarding data encryption (At rest? In transit?).",
            "What are the specific authentication standards (e.g., OAuth2, MFA, SSO)?",
            "Describe the backup frequency and data retention policy.",
            "What is the maximum acceptable recovery time (RTO) in case of a system failure?",
            "Which specific browsers and devices must be supported (e.g., Chrome, Safari, Mobile)?",
            "Are there specific accessibility standards to meet (e.g., WCAG 2.1 AA)?",
            "Does the system need to support multiple languages or localizations?",
            "Describe reporting and analytics needs.",
            "Do you need multi-language support?",
            "Are there integration requirements with other systems?",
            "Any accessibility requirements (e.g., screen readers)?",
            "Do you need mobile app support?",
            "Any deployment or hosting preferences?",
            "Describe workflow or business rules important for the system.",
            "What are your backup and data recovery expectations?",
            "Any other features or constraints you want to mention?"
        ]

        self.index = 0
        self.message_history = []
        self.project_name = None
        self.project_named = False

        # Create generic file first
        desktop = pathlib.Path.home() / "Desktop"
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.file_path = desktop / f"Requirements_{timestamp}.txt"
        self._initialize_file()

        # Initial greeting
        self.initial_greeting = self.get_initial_greeting()
        self._add_history("Bot", self.initial_greeting)

        # Topic change detection state
        self.topic_warning_pending = False
        self.pending_input = ""

    # -------------------------
    def _initialize_file(self):
        self._write_srs_document()

    # -------------------------
    def _write_srs_document(self):
        """Rewrites the entire SRS document cleanly with 5 specific categories."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write("=====================================\n")
                if self.project_name:
                    f.write(f"PROJECT NAME: {self.project_name.replace('_', ' ')}\n")
                else:
                    f.write("PROJECT NAME: TBD\n")
                f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=====================================\n\n")

                # Iterate through ordered categories
                for category, items in self.requirements.items():
                    f.write(f"### {category}\n")
                    prefix = self.prefix_map.get(category, "REQ")

                    if not items:
                        f.write(f"- {prefix}-01 None\n")
                    else:
                        for i, item in enumerate(items, 1):
                            f.write(f"- {prefix}-{i:02d} {item}\n")
                    f.write("\n")

                f.write("================================================\n")
        except Exception as e:
            print(f"Error writing file: {e}")

    # -------------------------
    def _add_history(self, sender, text):
        self.message_history.append({
            "sender": sender,
            "text": text,
            "timestamp": datetime.now().strftime("%H:%M")
        })

    def _save_to_file(self, sender, text):
        pass  # Chat logs not saved to SRS file to keep it clean

    # -------------------------
    def classify(self, text):
        """Robust classification into 5 categories using AI with keyword fallback."""
        # 1. Try AI Classification if API Key matches OpenRouter/Standard pattern
        if self.api_key and self.api_key.startswith("sk-or-v1-"):
            try:
                system_prompt = (
                    "You are a Senior Business Analyst. Classify the following requirement text into exactly ONE of these categories:\n"
                    "- Business Requirements\n"
                    "- Functional Requirements\n"
                    "- Non-Functional Requirements\n"
                    "- Security Requirements\n"
                    "- UI/UX Requirements\n\n"
                    "Rules:\n"
                    "1. 'student performance' (academic) goes to Functional, BUT 'system performance', 'response time', 'latency' MUST go to Non-Functional.\n"
                    "2. If the text mentions 'grades' but primarily describes system speed, availability, or reliability, classify as Non-Functional.\n"
                    "3. 'login', 'auth', 'encryption' = Security Requirements.\n"
                    "4. 'color', 'layout', 'dashboard' = UI/UX Requirements.\n"
                    "5. Reply ONLY with the exact category name. Nothing else."
                )
                
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text}
                    ]
                }
                headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                response = requests.post(self.url, json=payload, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    category = response.json()["choices"][0]["message"]["content"].strip()
                    valid_categories = [
                        "Business Requirements", "Functional Requirements", 
                        "Non-Functional Requirements", "Security Requirements", "UI/UX Requirements"
                    ]
                    # Fuzzy match or exact match
                    for vc in valid_categories:
                        if vc.lower() in category.lower():
                            return vc
            except Exception as e:
                print(f"AI Classification failed: {e}")

        # 2. Fallback to Regex / Keywords (Improved)
        text_lower = text.lower()
        
        def checks(keywords):
            for k in keywords:
                # \b matches word boundary. 
                if re.search(rf"\b{re.escape(k)}", text_lower):
                    return True
            return False

        # Priority mapping
        # Removed "role" to prevent misclassification of functional user roles as security
        if checks(["security", "encryption", "auth", "password", "otp", "oauth", "sso", "mfa", "permission", "privacy", "compliant", "audit", "access control"]):
            return "Security Requirements"

        if checks(["ui", "ux", "design", "color", "layout", "logo", "screen", "widget", "dashboard", "visual", "theme", "browser", "mobile", "css", "font", "style", "image", "button", "click", "navigation", "interface"]):
            return "UI/UX Requirements"

        # Refined NFR keywords to avoid false positives like "student performance"
        if checks(["system performance", "app performance", "latency", "uptime", "availability", "scale", "concurrent", "response time", "backup", "recovery", "reliability", "rto", "throughput", "capacity", "page load", "fast", "slow", "seconds", "ms"]):
            return "Non-Functional Requirements"
        
        # Check for isolated 'performance' only if not preceded by 'student', 'class', etc.
        # But easier to just default to FR if it's ambiguous in regex mode. 
        # We will assume generic "performance" is NFR *unless* it's clearly functional? 
        # Actually, let's keep "performance" out of the simple list to be safe, or use exact phrases.
        
        if checks(["business", "goal", "revenue", "profit", "strategy", "market", "audience", "budget", "cost", "stakeholder", "compliance", "regulation", "timeline"]):
            return "Business Requirements"

        # Default bucket for features, workflows, data, integrations, etc.
        return "Functional Requirements"

    # -------------------------
    def save_requirement(self, answer):
        category = self.classify(answer)
        clean_text = answer.strip()
        if clean_text not in self.requirements[category]:
            self.requirements[category].append(clean_text)
            self._write_srs_document()

    # -------------------------
    def get_initial_greeting(self):
        try:
            if not self.api_key.startswith("sk-or-v1-"):
                return (
                    "Good day! I am Requirement Genie, your professional software analyst assistant. "
                    "I am here to help you systematically gather and document your software project requirements. "
                    "To start, may I know the name of your project?"
                )

            return (
                "Good day! I am Requirement Genie, your professional software analyst assistant. "
                "I am here to help you systematically gather and document your software project requirements. "
                "To start, may I know the name of your project?"
            )
        except:
            return (
                "Good day! I am Requirement Genie, your professional software analyst assistant. "
                "I am here to help you systematically gather and document your software project requirements. "
                "To start, may I know the name of your project?"
            )

    # -------------------------
    def load_messages_from_file(self, file_path=None):
        if file_path:
            self.file_path = pathlib.Path(file_path)

    def _detect_topic_shift(self, user_input):
        """Uses AI to detect if the user input is off-topic or a topic switch."""
        try:
            # Only check if we have enough context (project name)
            if not self.project_name:
                return False

            system_prompt = (
                "You are a strict Requirements Manager. "
                f"The current project is: '{self.project_name}'. "
                "Your task is to check if the User's input is RELEVANT to this project or if it indicates a TOPIC SWITCH "
                "(e.g., suddenly talking about a different system, like switching from LMS to Bank Management) "
                "or is completely OUT OF THE BOX/IRRELEVANT. "
                "Ignore minor digressions. Focus on substantial context switches. "
                "Reply with 'YES' if it is a topic switch or out-of-context. "
                "Reply with 'NO' if it is relevant requirements data."
            )

            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
            }
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            
            # Fast timeout to not block UI too long
            response = requests.post(self.url, json=payload, headers=headers, timeout=5)
            if response.status_code == 200:
                answer = response.json()["choices"][0]["message"]["content"].strip().upper()
                return "YES" in answer
            return False
        except Exception as e:
            print(f"Topic check error: {e}")
            return False

    def get_response(self, user_input):
        user_input = user_input.strip()
        if not user_input:
            return "Please provide a valid input."

        user_input_lower = user_input.lower()

        # Check for summary
        if "summary" in user_input_lower or "recheck" in user_input_lower:
            self._write_srs_document()
            return f"Requirements saved. Here is the summary:\n{self.summary()}"

        # If project name not yet set (and index 0)
        if self.index == 0 and not self.project_named:
            self.project_name = user_input.replace(" ", "_")

            # Rename file if first question (project name)
            desktop = pathlib.Path.home() / "Desktop"
            new_path = desktop / f"{self.project_name}.txt"
            try:
                os.rename(self.file_path, new_path)
                self.file_path = new_path
                self.project_named = True
            except:
                pass

            self._write_srs_document()
            self._add_history("User", user_input)
            self.conversation.append({"role": "user", "content": f"The project name is {self.project_name}."})

            self.index += 1

            next_q = self.questions[self.index]
            bot_reply = f"Thank you. The project is set to {self.project_name}. {next_q}"

            if self.api_key and self.api_key.startswith("sk-or-v1-"):
                try:
                    # Provide context to AI to ask the first real question
                    payload = {
                        "model": "gpt-4o-mini",
                        "messages": self.conversation + [{"role": "system",
                                                          "content": f"The user just set the project name. The next required topic is: {next_q}. Acknowledge the name and ask the question naturally."}]
                    }
                    headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                    response = requests.post(self.url, json=payload, headers=headers, timeout=10)
                    if response.status_code == 200:
                        bot_reply = response.json()["choices"][0]["message"]["content"]
                        self.conversation.append({"role": "assistant", "content": bot_reply})
                except Exception as e:
                    print(f"API Error: {e}")

            self._add_history("Bot", bot_reply)
            return bot_reply

        # Validate Context
        is_relevant, _ = self.validate_context(user_input)
        if not is_relevant:
            bot_reply = f"It seems your input may not be related to the project context ({self.project_name}). Please provide relevant requirements."
            self._add_history("User", user_input)
            self._add_history("Bot", bot_reply)
            return bot_reply

        # NEW: Check for Topic Shift / Out of Box
        if self.project_named and self.api_key and self.api_key.startswith("sk-or-v1-"):
            is_shift_check_needed = True
            
            if self.topic_warning_pending:
                self.topic_warning_pending = False
                if user_input.lower() in ["yes", "continue", "proceed", "confirm", "ignore"]:
                    self._add_history("User", user_input)
                    user_input = self.pending_input
                    is_shift_check_needed = False
                else:
                    bot_reply = "Okay, keeping to the current topic. Please continue."
                    self._add_history("User", user_input)
                    self._add_history("Bot", bot_reply)
                    return bot_reply
            
            if is_shift_check_needed and self._detect_topic_shift(user_input):
                self.topic_warning_pending = True
                self.pending_input = user_input
                bot_reply = (
                    f"I noticed you mentioned something that seems outside the scope of '{self.project_name}' "
                    "or involves a different topic. "
                    "Are you changing the project context? "
                    "Type 'Yes' to proceed with adding this requirement, or clarify otherwise."
                )
                self._add_history("User", user_input)
                self._add_history("Bot", bot_reply)
                return bot_reply

        # Save user input as requirement
        self._add_history("User", user_input)
        self.conversation.append({"role": "user", "content": user_input})
        self.save_requirement(user_input)

        self.index += 1

        # Determine next question or completion
        if self.index < len(self.questions):
            next_question = self.questions[self.index]
            bot_reply = f"Thank you. {next_question}"

            # Try AI Generation for flexibility
            if self.api_key and self.api_key.startswith("sk-or-v1-"):
                try:
                    # We nudge the AI to cover the next question from our list
                    context_nudge = f"The user just answered. The NEXT requirement topic to cover is: '{next_question}'. Ask about this naturally, or follow up on the previous answer if it was unclear."

                    messages = self.conversation + [{"role": "system", "content": context_nudge}]
                    payload = {"model": "gpt-4o-mini", "messages": messages}
                    headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

                    response = requests.post(self.url, json=payload, headers=headers, timeout=10)
                    if response.status_code == 200:
                        bot_reply = response.json()["choices"][0]["message"]["content"]
                        self.conversation.append({"role": "assistant", "content": bot_reply})
                    else:
                        print(f"API Fail: {response.status_code}")
                except Exception as e:
                    print(f"API Error: {e}")

        else:
            bot_reply = (
                    "All requirements collected. Here is the summary:\n" + self.summary()
            )

        self._add_history("Bot", bot_reply)
        return bot_reply

    # -------------------------
    def validate_context(self, user_input):
        """
        Checks if the input is relevant to the project context.
        Returns (is_relevant, is_complete)
        """
        input_lower = user_input.lower().strip()

        # Always allow first message
        if self.index == 0:
            return True, True

        # 1. Check if it contains part of the project name
        if self.project_name:
            proj_parts = self.project_name.lower().replace("_", " ").split()
            # If any significant part of project name is in input
            if any(p in input_lower for p in proj_parts if len(p) > 3):
                return True, True

        # 2. Check for common software requirement keywords
        keywords = [
            "system", "user", "admin", "login", "data", "report", "dashboard",
            "security", "payment", "api", "integration", "app", "web", "mobile",
            "feature", "function", "page", "screen", "button", "access", "role",
            "email", "sms", "notification", "search", "filter", "upload", "download"
        ]
        if any(k in input_lower for k in keywords):
            return True, True

        # 3. Check for specific yes/no/none answers
        if input_lower in ["yes", "no", "none", "n/a", "not applicable", "tbd"]:
            return True, True

        # 4. Length check - if it's a long sentence, assume it's attempting to describe something
        if len(user_input.split()) >= 3:
            return True, True

        return False, False

    def summary(self):
        """Returns a string summary."""
        lines = []
        for cat, reqs in self.requirements.items():
            lines.append(f"### {cat}")
            if not reqs:
                lines.append("- None")
            else:
                for r in reqs:
                    lines.append(f"- {r}")
            lines.append("")
        return "\n".join(lines)