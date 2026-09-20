"""
DSL Parser - Rule-based assembly command parser
Converts natural syntax or DSL commands into structured operations
"""

import re
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional


@dataclass
class Command:
    """Represents a single assembly command"""
    type: str  # INSERT, ROTATE, ALIGN, etc
    obj_a: str = ""
    obj_b: str = ""
    depth: Optional[float] = None
    unit: str = "mm"
    degrees: Optional[float] = None
    axis: str = ""
    direction: str = ""
    count: Optional[int] = None
    x: float = 0
    y: float = 0
    z: float = 0
    strategy: str = ""

    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None and v != ""}


class DSLParser:
    """Parse assembly DSL into structured commands"""

    COMMAND_PATTERN = {
        "INSERT": r"INSERT\s+([\w-]+)\s+([\d.]+)(?:mm|cm|in)?\s+([\w-]+)",
        "ROTATE": r"ROTATE\s+([\w-]+)\s+([\d.]+)\s+([XYZ])",
        "ALIGN": r"ALIGN\s+([\w-]+)\s+([\w-]+)",
        "DUPLICATE": r"DUPLICATE\s+([\w-]+)\s+(\d+)",
        "STACK": r"STACK\s+([\w-]+)\s+([\w-]+)\s+(VERTICAL|HORIZONTAL)",
        "FASTEN": r"FASTEN\s+([\w-]+)\s+([\w-]+)\s+([\w-]+)",
        "OFFSET": r"OFFSET\s+([\w-]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)",
    }

    def __init__(self):
        self.commands = []
        self.parse_quality = "unknown"
        self.confidence = 0.0

    def extract_flag(self, text: str) -> Tuple[str, str]:
        """
        Extract execution flag and clean text.
        Returns: (flag, clean_text)
        """
        flags = ["ONLY-AI", "ONLY-RULEB", "RULEAI"]
        
        for flag in flags:
            if f"//{flag}" in text.upper():
                clean = re.sub(rf"//\s*{flag}\s*\n?", "", text, flags=re.IGNORECASE)
                return flag, clean.strip()
        
        return "RULEAI", text.strip()  # Default

    def parse_distance(self, dist_str: str) -> Tuple[float, str]:
        """
        Parse distance string like '20mm', '5cm', '2in'
        Returns: (value, unit)
        """
        match = re.match(r"([\d.]+)(mm|cm|in)?", dist_str.strip())
        if match:
            value = float(match.group(1))
            unit = match.group(2) or "mm"
            return value, unit
        return 0, "mm"

    def parse_single_command(self, line: str) -> Optional[Command]:
        """
        Try to parse a single DSL line.
        Returns Command or None if no match.
        """
        line = line.strip().upper()
        if not line or line.startswith("#"):
            return None

        # Try each pattern
        for cmd_type, pattern in self.COMMAND_PATTERN.items():
            match = re.match(pattern, line)
            if match:
                return self._create_command(cmd_type, match)

        return None

    def _create_command(self, cmd_type: str, match) -> Command:
        """Create Command object from regex match"""
        groups = match.groups()

        if cmd_type == "INSERT":
            depth, unit = self.parse_distance(groups[1])
            return Command(
                type="INSERT",
                obj_a=groups[0],
                depth=depth,
                unit=unit,
                obj_b=groups[2]
            )

        elif cmd_type == "ROTATE":
            return Command(
                type="ROTATE",
                obj_a=groups[0],
                degrees=float(groups[1]),
                axis=groups[2]
            )

        elif cmd_type == "ALIGN":
            return Command(
                type="ALIGN",
                obj_a=groups[0],
                obj_b=groups[1]
            )

        elif cmd_type == "DUPLICATE":
            return Command(
                type="DUPLICATE",
                obj_a=groups[0],
                count=int(groups[1])
            )

        elif cmd_type == "STACK":
            return Command(
                type="STACK",
                obj_a=groups[0],
                obj_b=groups[1],
                direction=groups[2]
            )

        elif cmd_type == "FASTEN":
            return Command(
                type="FASTEN",
                obj_a=groups[0],
                obj_b=groups[1],
                strategy=groups[2]
            )

        elif cmd_type == "OFFSET":
            return Command(
                type="OFFSET",
                obj_a=groups[0],
                x=float(groups[1]),
                y=float(groups[2]),
                z=float(groups[3])
            )

        return None

    def parse(self, text: str) -> Dict:
        """
        Main parse function.
        
        Args:
            text: Input text (DSL or natural language)
        
        Returns:
            dict with commands, parse_quality, confidence, flag
        """
        # Extract flag
        flag, clean_text = self.extract_flag(text)

        self.commands = []
        self.parse_quality = "rule"
        self.confidence = 0.0

        # Split by ; or newline
        lines = re.split(r"[;\n]", clean_text)

        matched = 0
        for line in lines:
            cmd = self.parse_single_command(line)
            if cmd:
                self.commands.append(cmd)
                matched += 1

        # Calculate confidence
        total_lines = len([l for l in lines if l.strip() and not l.startswith("#")])
        if total_lines > 0:
            self.confidence = matched / total_lines
        else:
            self.confidence = 1.0

        return {
            "flag": flag,
            "commands": [c.to_dict() for c in self.commands],
            "parse_quality": self.parse_quality,
            "confidence": self.confidence,
            "matched_lines": matched,
            "total_lines": total_lines
        }


# ─────────────────────────────────────────────────────────────
# Test & Demo
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = DSLParser()

    # Test 1: Pure DSL
    print("=" * 60)
    print("TEST 1: Pure DSL Commands")
    print("=" * 60)
    test1 = """
    INSERT screw_1 20mm hole_A
    INSERT screw_2 20mm hole_B
    ROTATE assembly 90 Z
    DUPLICATE bolt 4
    """
    result = parser.parse(test1)
    print(json.dumps(result, indent=2))

    # Test 2: With RULEAI flag
    print("\n" + "=" * 60)
    print("TEST 2: With RULEAI Flag")
    print("=" * 60)
    test2 = """
    //RULEAI
    ALIGN base frame
    FASTEN panel base SCREW
    OFFSET motor 10 5 0
    """
    result = parser.parse(test2)
    print(json.dumps(result, indent=2))

    # Test 3: ONLY-RULEB (fails on natural language)
    print("\n" + "=" * 60)
    print("TEST 3: ONLY-RULEB Flag (Natural Language - Should Fail)")
    print("=" * 60)
    test3 = """
    //ONLY-RULEB
    put the screw into the hole
    """
    result = parser.parse(test3)
    print(json.dumps(result, indent=2))

    # Test 4: Mixed valid/invalid (partial parse)
    print("\n" + "=" * 60)
    print("TEST 4: Partial Parse (50% coverage)")
    print("=" * 60)
    test4 = """
    INSERT fastener 10mm slot_A
    this is random text that wont parse
    ROTATE part 45 X
    another line that means nothing
    """
    result = parser.parse(test4)
    print(json.dumps(result, indent=2))