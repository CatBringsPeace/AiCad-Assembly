"""
Rule-based handler - uses DSL parser for assembly instructions
"""

from dsl_parser import DSLParser


class RuleBasedHandler:
    def __init__(self):
        self.parser = DSLParser()
    
    def parse(self, user_input: str):
        """
        Parse user input using DSL rules.
        
        Returns dict with:
        - flag: ONLY-AI, ONLY-RULEB, RULEAI
        - method: 'rule_only' or 'rule_fallback'
        - commands: list of parsed commands
        - confidence: 0-1 score
        """
        result = self.parser.parse(user_input)
        
        return {
            "flag": result["flag"],
            "method": "rule_only",
            "commands": result["commands"],
            "confidence": result["confidence"],
            "matched": result["matched_lines"],
            "total": result["total_lines"],
        }