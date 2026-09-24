# Assembly DSL - Domain Specific Language Specification

## Command Syntax

### **Basic Structure**
```
COMMAND OBJ1 PARAMS OBJ2
```

### **Available Commands**

#### 1. INSERT
Insert ObjA into ObjB at specified depth
```
INSERT ObjA <depth> ObjB
INSERT ObjA 10mm ObjB
INSERT screw 20 hole_A          # depth in mm (default)
INSERT fastener 5cm slot_B      # cm suffix
```

#### 2. ROTATE
Rotate object around axis by degrees
```
ROTATE ObjA <degrees> <axis>
ROTATE ObjA 90 X
ROTATE part_B 45 Z
ROTATE assembly 180 Y
```

#### 3. ALIGN
Align ObjA with ObjB (snap together)
```
ALIGN ObjA ObjB
ALIGN part_A part_B
ALIGN housing base
```

#### 4. DUPLICATE
Create N copies of object
```
DUPLICATE ObjA <count>
DUPLICATE screw 4
DUPLICATE bolt 8
```

#### 5. STACK
Stack objects vertically or horizontally
```
STACK ObjA ObjB <direction>
STACK part_A part_B VERTICAL
STACK plate_1 plate_2 HORIZONTAL
```

#### 6. FASTEN
Secure ObjA to ObjB (bolt, screw, weld)
```
FASTEN ObjA ObjB <type>
FASTEN shaft housing BOLT
FASTEN panel frame SCREW
FASTEN bracket base WELD
```

#### 7. OFFSET
Move object by X,Y,Z offset
```
OFFSET ObjA <x> <y> <z>
OFFSET part_A 10 0 5          # mm
OFFSET housing 2cm 0 1cm
```

---

## Parameter Types

| Type | Example | Notes |
|------|---------|-------|
| OBJECT | `ObjA`, `screw_1`, `hole_A` | Part name (alphanumeric + underscore) |
| NUMBER | `10`, `20.5` | Integer or float |
| DISTANCE | `10mm`, `5cm`, `2in` | Default: mm |
| AXIS | `X`, `Y`, `Z` | Capital letter |
| DIRECTION | `VERTICAL`, `HORIZONTAL` | Case-insensitive |
| STRATEGY | `BOLT`, `SCREW`, `WELD` | Fastening method |

---

## Multi-Command Syntax

Commands separated by `;` or newline:

```
INSERT screw_1 20 hole_A; ROTATE assembly 90 Z; DUPLICATE screw_1 3
```

Or:
```
INSERT screw_1 20 hole_A
ROTATE assembly 90 Z
DUPLICATE screw_1 3
```

---

## Flags

Control parsing behavior:

```
//ONLY-AI
<user input in natural language>

//ONLY-RULEB
INSERT screw 20 hole_A; ROTATE part 90 Z

//RULEAI (default)
<can be natural language or DSL - tries rules first, AI as fallback>
```

---

## Example Sequences

### **Simple Assembly**
```
INSERT screw_1 20 hole_A
INSERT screw_2 20 hole_B
ALIGN panel_1 frame
FASTEN panel_1 frame SCREW
```

### **With Duplicates**
```
DUPLICATE screw 4
INSERT screw 20 hole_main
INSERT screw 20 hole_support_1
INSERT screw 20 hole_support_2
INSERT screw 20 hole_support_3
```

### **Complex Assembly**
```
ALIGN base frame
OFFSET motor 10 5 0
ROTATE motor 90 Z
FASTEN motor base BOLT
DUPLICATE connector 2
INSERT connector 15 port_A
INSERT connector 15 port_B
```

---

## Return Format (JSON)

Parser outputs:
```json
{
  "commands": [
    {
      "type": "INSERT",
      "obj_a": "screw_1",
      "depth": 20,
      "obj_b": "hole_A",
      "unit": "mm"
    },
    {
      "type": "ROTATE",
      "obj": "assembly",
      "degrees": 90,
      "axis": "Z"
    }
  ],
  "parse_quality": "rule",
  "confidence": 0.95
}
```
