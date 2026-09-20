import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_SOLID, TopAbs_FACE


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

INPUT_DIR = Path("input")

SUPPORTED_EXTENSIONS = {".step", ".stp"}


# ---------------------------------------------------------
# Gemini
# ---------------------------------------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY was not found. "
        "Put it in your .env file."
    )

client = genai.Client(api_key=api_key)


# ---------------------------------------------------------
# STEP analysis
# ---------------------------------------------------------

def analyze_step_file(path: Path) -> dict:
    """
    Read a STEP file and extract basic geometry information.
    """

    reader = STEPControl_Reader()

    status = reader.ReadFile(str(path))

    if status != IFSelect_RetDone:
        raise RuntimeError(f"Failed to read STEP file: {path}")

    reader.TransferRoots()

    shape = reader.OneShape()

    # Count solids
    solid_count = 0

    explorer = TopExp_Explorer(shape, TopAbs_SOLID)

    while explorer.More():
        solid_count += 1
        explorer.Next()

    # Count faces
    face_count = 0

    explorer = TopExp_Explorer(shape, TopAbs_FACE)

    while explorer.More():
        face_count += 1
        explorer.Next()

    # Bounding box
    bbox = Bnd_Box()
    brepbndlib_Add(shape, bbox)

    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()

    return {
        "filename": path.name,
        "path": str(path),
        "solids": solid_count,
        "faces": face_count,
        "bounding_box": {
            "xmin": xmin,
            "ymin": ymin,
            "zmin": zmin,
            "xmax": xmax,
            "ymax": ymax,
            "zmax": zmax,
        },
    }


# ---------------------------------------------------------
# Find STEP files
# ---------------------------------------------------------

def find_step_files():
    """
    Find all STEP/STP files in the input directory.
    """

    if not INPUT_DIR.exists():
        raise RuntimeError(
            f"Input directory does not exist: {INPUT_DIR}"
        )

    files = [
        p
        for p in INPUT_DIR.iterdir()
        if p.is_file()
        and p.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    if not files:
        raise RuntimeError(
            "No STEP files found in the input directory."
        )

    return sorted(files)


# ---------------------------------------------------------
# Build CAD description for Gemini
# ---------------------------------------------------------

def build_cad_description(step_files):
    descriptions = []

    for index, path in enumerate(step_files, start=1):

        print(f"Analyzing: {path.name}")

        info = analyze_step_file(path)

        descriptions.append(
            f"""
PART {index}

Filename:
{info["filename"]}

Solids:
{info["solids"]}

Faces:
{info["faces"]}

Bounding box:
X: {info["bounding_box"]["xmin"]:.3f} -> {info["bounding_box"]["xmax"]:.3f}
Y: {info["bounding_box"]["ymin"]:.3f} -> {info["bounding_box"]["ymax"]:.3f}
Z: {info["bounding_box"]["zmin"]:.3f} -> {info["bounding_box"]["zmax"]:.3f}
"""
        )

    return "\n".join(descriptions)


# ---------------------------------------------------------
# Generate PythonOCC code
# ---------------------------------------------------------

def generate_code(cad_description, user_instruction):

    prompt = f"""
You are an expert mechanical CAD engineer and PythonOCC/Open CASCADE
programmer.

The user has provided multiple STEP files representing components
that need to be assembled.

You must interpret the user's natural-language assembly instruction
and generate Python code using PythonOCC / Open CASCADE.

IMPORTANT:
- Generate actual executable PythonOCC code.
- pythonocc-core 7.9.3 is being used.
- Do not merely describe what the code should do.
- Return ONLY Python code.
- Do not use Markdown code fences.
- Do not include explanations outside the code.
- Use the STEP filenames exactly as provided.
- The generated program should read the STEP files from the "input"
  directory.
- The generated program should create the requested assembly.
- Save the resulting assembly as a STEP file in the "output" directory.
- Preserve the original geometry.
- Use Open CASCADE transformations and assembly operations.
- Do not invent dimensions when they can be obtained from the geometry.
- If exact mating information cannot be determined from the available
  geometry, make the most reasonable geometric inference.

CAD FILE INFORMATION:

{cad_description}


USER ASSEMBLY INSTRUCTION:

{user_instruction}
"""

    response = client.models.generate_content(
        model="gemini-3.6",
        contents=prompt,
    )

    return response.text


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print("=" * 70)
    print("CAD AI - STEP Assembly Code Generator")
    print("=" * 70)

    # Find STEP files
    step_files = find_step_files()

    print("\nSTEP files found:")

    for file in step_files:
        print(f"  - {file.name}")

    # Analyze geometry
    print("\nAnalyzing STEP geometry...\n")

    cad_description = build_cad_description(step_files)

    print("\nCAD information:")
    print(cad_description)

    # Get user instruction
    print("\n" + "=" * 70)
    print("Assembly instruction")
    print("=" * 70)

    user_instruction = input(
        "\nDescribe the assembly operation:\n> "
    )

    if not user_instruction.strip():
        raise RuntimeError("No assembly instruction provided.")

    # Generate PythonOCC
    print("\nGenerating PythonOCC code...\n")

    generated_code = generate_code(
        cad_description,
        user_instruction,
    )

    # Print generated code
    print("\n" + "=" * 70)
    print("GENERATED PYTHONOCC CODE")
    print("=" * 70)

    print(generated_code)

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()