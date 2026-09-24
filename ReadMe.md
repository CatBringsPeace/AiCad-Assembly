# AI-Assisted CAD Assembly System

**AI-powered CAD assembly using natural language and DSL commands.**

## Quick Start

```bash
conda activate cadassembly
python cad_assembly_gui.py
```

1. Click **📂 Add STEP Files** - load your CAD models
2. Type assembly instructions (DSL or natural language)
3. Click **⚙ Run Assembly** - generates code and creates `output/assembled_model.step`

## Rule-Based DSL Syntax

| Command | Syntax | Example |
|---------|--------|---------|
| **INSERT** | `INSERT part1 depth part2` | `INSERT Rod-1 20 Housing` |
| **ROTATE** | `ROTATE part degrees axis` | `ROTATE Shaft 90 Z` |
| **ALIGN** | `ALIGN part1 part2` | `ALIGN EndCap Base` |
| **DUPLICATE** | `DUPLICATE part count` | `DUPLICATE Bolt 4` |
| **STACK** | `STACK part1 part2 direction` | `STACK Plate-1 Plate-2 VERTICAL` |
| **FASTEN** | `FASTEN part1 part2 type` | `FASTEN Panel Frame SCREW` |
| **OFFSET** | `OFFSET part x y z` | `OFFSET Motor 10 5 0` |

## Flags (Optional)

```
//ONLY-RULEB       → Use DSL parser only
//ONLY-AI          → Use Gemini API only  
//RULEAI (default) → Try DSL first, AI if confidence < 70%
```

## Example Assembly

```
//RULEAI
INSERT Rod-1 20 Circular-Plate
INSERT Rod-2 15 Circular-Plate
ROTATE Assembly 90 Z
DUPLICATE Bolt 4
```

**Output:** Fused, transformed STEP model saved to `output/assembled_model.step`

## Features

✅ Multi-file STEP assembly  
✅ Geometric transformations (INSERT, ROTATE, ALIGN)  
✅ Rule-based parsing (instant, 80% coverage)  
✅ AI fallback (Gemini API for complex cases)  
✅ Real PythonOCC execution  
✅ Dynamic part name buttons  
✅ Multi-line instruction editor  

## Requirements

```
conda
google-generativeai>=0.6.0
python-dotenv>=1.0.0
pythonocc-core>=7.9.3
```

## File Structure

```
cad-assembly/
├── cad_assembly_gui.py          (GUI)
├── dsl_parser.py                (Rule-based parser)
├── assembly_orchestrator.py     (DSL + AI routing)
├── handlers/
│   ├── rule_based_handler.py
│   └── ai_handler.py
├── output/                      (Generated STEP files)
└── .env                         (GEMINI_API_KEY)
```