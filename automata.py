# automata.py

class FiniteAutomata:
    def __init__(self):
        # State 0 is the start state
        self.transitions = {}  # Format: { (state, char): next_state }
        self.output = {}       # Format: { state: "keyword_found" }
        self.fail = {}         # Failure links (for Aho-Corasick optimization)
        self.state_counter = 0
        self.spam_keywords = ["win", "free", "promo", "claim now", "urgent", "winner", "click here"]
        self.build_automata()

    def build_automata(self):
        """Constructs the Trie-based Finite Automata from keywords."""
        self.transitions = {}
        self.output = {}
        self.state_counter = 0
        
        for keyword in self.spam_keywords:
            current_state = 0
            for char in keyword:
                if (current_state, char) not in self.transitions:
                    self.state_counter += 1
                    self.transitions[(current_state, char)] = self.state_counter
                    current_state = self.state_counter
                else:
                    current_state = self.transitions[(current_state, char)]
            
            # Mark this state as a "Final State" (Spam detected)
            self.output[current_state] = keyword
    
    def scan_text(self, text):
        """
        Runs the text through the automata state by state.
        Returns detailed logs of state transitions for visualization.
        """
        text = text.lower()
        current_state = 0
        detected_patterns = []
        transition_log = []

        for char in text:
            start_node = current_state
            
            # Check if transition exists for character
            if (current_state, char) in self.transitions:
                current_state = self.transitions[(current_state, char)]
                status = "Transition"
            else:
                # If no transition, reset to start (Simplified DFA behavior)
                # In full Aho-Corasick, we would follow failure links
                if (0, char) in self.transitions:
                     current_state = self.transitions[(0, char)]
                else:
                    current_state = 0
                status = "Reset"

            # Check if we are in a Final State
            if current_state in self.output:
                keyword = self.output[current_state]
                detected_patterns.append(keyword)
                status = f"MATCH: {keyword}"
                # Reset after match to find next word
                current_state = 0 

            transition_log.append({
                "char": char,
                "from_state": start_node,
                "to_state": current_state,
                "status": status
            })

        return detected_patterns, transition_log