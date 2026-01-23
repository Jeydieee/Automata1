# automata.py
import os

class FiniteAutomata:
    def __init__(self, keyword_file="spam_keywords.txt"):
        # State 0 is the start state
        self.transitions = {}  # Format: { (state, char): next_state }
        self.output = {}       # Format: { state: "keyword_found" }
        self.fail = {}         # Failure links (for Aho-Corasick optimization)
        self.state_counter = 0
        
        # Load keywords from the external file
        self.spam_keywords = self.load_keywords(keyword_file)
        
        self.build_automata()

    def load_keywords(self, filepath):
        """Reads spam keywords from a text file, one per line."""
        keywords = []
        try:
            # check if file exists to avoid crashing
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        # strip() removes newline characters and surrounding whitespace
                        clean_word = line.strip().lower() 
                        if clean_word:  # Ensure empty lines are ignored
                            keywords.append(clean_word)
            else:
                print(f"Warning: '{filepath}' not found. Using default keywords.")
                # Fallback defaults if file is missing
                return ["win", "free", "promo", "claim now", "urgent"]
                
        except Exception as e:
            print(f"Error reading keyword file: {e}")
            return []
            
        return keywords

    def build_automata(self):
        """Constructs the Trie-based Finite Automata from keywords."""
        # ... (Rest of your existing build_automata code remains the same) ...
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