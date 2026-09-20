
from pathlib import Path
from OCC.Core.STEPControl import STEPControl_Reader, STEPControl_Writer
from OCC.Core.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity

# File paths
input_dir = Path("input")
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

# Load STEP files
shapes = {}

reader = STEPControl_Reader()
status = reader.ReadFile(str(input_dir / "Rod-3.STEP"))
if status == IFSelect_RetDone:
    reader.TransferRoots()
    shapes["Rod-3"] = reader.OneShape()
else:
    print("Failed to read {str(input_dir / 'Rod-3.STEP')}")

reader = STEPControl_Reader()
status = reader.ReadFile(str(input_dir / "Circular_Plate.step"))
if status == IFSelect_RetDone:
    reader.TransferRoots()
    shapes["Circular_Plate"] = reader.OneShape()
else:
    print("Failed to read {str(input_dir / 'Circular_Plate.step')}")

reader = STEPControl_Reader()
status = reader.ReadFile(str(input_dir / "Rod-1.STEP"))
if status == IFSelect_RetDone:
    reader.TransferRoots()
    shapes["Rod-1"] = reader.OneShape()
else:
    print("Failed to read {str(input_dir / 'Rod-1.STEP')}")

reader = STEPControl_Reader()
status = reader.ReadFile(str(input_dir / "Rod-2.STEP"))
if status == IFSelect_RetDone:
    reader.TransferRoots()
    shapes["Rod-2"] = reader.OneShape()
else:
    print("Failed to read {str(input_dir / 'Rod-2.STEP')}")

# Assembly operations
    # INSERT ROD-1 100.0mm into CIRCULAR_PLATE
    # INSERT ROD-2 80.0mm into CIRCULAR_PLATE
    # INSERT ROD-3 70.0mm into CIRCULAR_PLATE


# Save assembled model
if shapes:
    compound_shape = list(shapes.values())[0]
    writer = STEPControl_Writer()
    writer.Transfer(compound_shape, IFSelect_ItemsByEntity)
    writer.Write(str(output_dir / "assembled_model.step"))
    print("Assembled model saved to output/assembled_model.step")
