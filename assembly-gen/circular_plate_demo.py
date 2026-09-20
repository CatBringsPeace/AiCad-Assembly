import os
from OCC.Core.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_FACE
from OCC.Core.TopoDS import topods, TopoDS_Compound
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.GeomAbs import GeomAbs_Cylinder
from OCC.Core.gp import gp_Trsf, gp_Vec
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.BRep import BRep_Builder

def read_step(filepath):
    reader = STEPControl_Reader()
    status = reader.ReadFile(filepath)
    if status == IFSelect_RetDone:
        reader.TransferRoots()
        return reader.Shape()
    else:
        raise RuntimeError(f"Failed to read STEP file: {filepath}")

def main():
    input_dir = "input"
    output_dir = "output"

    plate_path = os.path.join(input_dir, "Circular Plate.step")
    rod1_path = os.path.join(input_dir, "Rod-1-For Circular Plate.STEP")
    rod2_path = os.path.join(input_dir, "Rod2-For Circular Plate.STEP")
    rod3_path = os.path.join(input_dir, "Rod3-For Circular Plate.STEP")

    plate_shape = read_step(plate_path)

    rod_paths = [rod1_path, rod2_path, rod3_path]
    rods = []
    for path in rod_paths:
        shape = read_step(path)
        radius = None
        exp = TopExp_Explorer(shape, TopAbs_FACE)
        while exp.More():
            face = topods.Face(exp.Current())
            surf = BRepAdaptor_Surface(face)
            if surf.GetType() == GeomAbs_Cylinder:
                cyl = surf.Cylinder()
                radius = cyl.Radius()
                break
            exp.Next()
        rods.append({"shape": shape, "radius": radius, "path": path})

    # Extract cylindrical hole geometries from the plate
    raw_holes = []
    exp = TopExp_Explorer(plate_shape, TopAbs_FACE)
    while exp.More():
        face = topods.Face(exp.Current())
        surf = BRepAdaptor_Surface(face)
        if surf.GetType() == GeomAbs_Cylinder:
            cyl = surf.Cylinder()
            r = cyl.Radius()
            if r < 20.0:  # Distinguish hole cylinders from outer plate radius (~25)
                loc = cyl.Axis().Location()
                raw_holes.append({
                    "radius": r,
                    "x": loc.X(),
                    "y": loc.Y()
                })
        exp.Next()

    # Deduplicate holes if faces were split
    holes = []
    for h in raw_holes:
        if not any(abs(uh["x"] - h["x"]) < 1e-3 and abs(uh["y"] - h["y"]) < 1e-3 for uh in holes):
            holes.append(h)

    # Construct the assembly compound
    builder = BRep_Builder()
    assembly = TopoDS_Compound()
    builder.MakeCompound(assembly)
    builder.Add(assembly, plate_shape)

    used_holes = set()
    for rod in rods:
        r_rod = rod["radius"]
        best_hole_idx = None
        min_diff = 1e9

        for i, hole in enumerate(holes):
            if i in used_holes:
                continue
            diff = abs(hole["radius"] - r_rod) if r_rod is not None else 1e9
            if diff < min_diff:
                min_diff = diff
                best_hole_idx = i

        if best_hole_idx is not None:
            used_holes.add(best_hole_idx)
            matched_hole = holes[best_hole_idx]

            trsf = gp_Trsf()
            trsf.SetTranslation(gp_Vec(matched_hole["x"], matched_hole["y"], 0.0))

            transformed_rod = BRepBuilderAPI_Transform(rod["shape"], trsf, True).Shape()
            builder.Add(assembly, transformed_rod)
        else:
            builder.Add(assembly, rod["shape"])

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "assembly.step")

    writer = STEPControl_Writer()
    writer.Transfer(assembly, STEPControl_AsIs)
    writer.Write(output_path)

if __name__ == "__main__":
    main()
