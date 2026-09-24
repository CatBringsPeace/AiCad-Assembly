
from pathlib import Path
from OCC.Core.STEPControl import STEPControl_Reader, STEPControl_Writer
from OCC.Core.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity

# Output directory
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

# Load STEP files
shapes = {}

reader = STEPControl_Reader()
status = reader.ReadFile(r"D:\Resume-grade-work\Ai-Cad-Assembly\test-files\input\Extruded Square.STEP")
if status == IFSelect_RetDone:
    reader.TransferRoots()
    shapes["Extruded Square"] = reader.OneShape()
    print("[OK] Loaded: Extruded Square")
else:
    print("[FAIL] Failed to read")

reader = STEPControl_Reader()
status = reader.ReadFile(r"D:\Resume-grade-work\Ai-Cad-Assembly\test-files\input\Square Hole.STEP")
if status == IFSelect_RetDone:
    reader.TransferRoots()
    shapes["Square Hole"] = reader.OneShape()
    print("[OK] Loaded: Square Hole")
else:
    print("[FAIL] Failed to read")


# Assembly operations


# Save assembled model
if shapes:
    compound_shape = list(shapes.values())[0]
    writer = STEPControl_Writer()
    writer.Transfer(compound_shape, IFSelect_ItemsByEntity)
    writer.Write(str(output_dir / "assembled_model.step"))
    print("[OK] Assembled model saved to output/assembled_model.step")
else:
    print("[FAIL] No shapes to assemble")
