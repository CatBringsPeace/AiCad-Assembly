import os

from OCC.Core.STEPControl import (
    STEPControl_Reader,
    STEPControl_Writer,
    STEPControl_AsIs,
)
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.gp import gp_Trsf, gp_Vec
from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Core.BRep import BRep_Builder


def load_step(filename):
    reader = STEPControl_Reader()

    filepath = os.path.join("input", filename)
    status = reader.ReadFile(filepath)

    if status != 1:
        raise RuntimeError(f"Failed to read STEP file: {filepath}")

    reader.TransferRoots()
    return reader.OneShape()


# Load components
plate = load_step("Circular Plate.step")
rod1 = load_step("Rod-1-For Circular Plate.STEP")
rod2 = load_step("Rod2-For Circular Plate.STEP")
rod3 = load_step("Rod3-For Circular Plate.STEP")


def transform_shape(shape, dx, dy, dz):
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(dx, dy, dz))

    transformer = BRepBuilderAPI_Transform(shape, trsf, True)
    return transformer.Shape()


# Position rods
rod1_placed = transform_shape(rod1, 15, 0, -40)
rod2_placed = transform_shape(rod2, 0, 15, -40)
rod3_placed = transform_shape(rod3, -15, 0, -40)


# Create assembly compound
compound = TopoDS_Compound()
builder = BRep_Builder()

builder.MakeCompound(compound)

builder.Add(compound, plate)
builder.Add(compound, rod1_placed)
builder.Add(compound, rod2_placed)
builder.Add(compound, rod3_placed)


# Save output
os.makedirs("output", exist_ok=True)

writer = STEPControl_Writer()
writer.Transfer(compound, STEPControl_AsIs)

output_path = os.path.join("output", "assembly.step")
status = writer.Write(output_path)

if status != 1:
    raise RuntimeError(f"Failed to write STEP file: {output_path}")

print(f"Assembly saved to: {output_path}")