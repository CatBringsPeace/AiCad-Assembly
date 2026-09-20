import os
import OCC.Core.STEPControl as STEPControl
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.TopoDS import topods, TopoDS_Compound
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_FACE, TopAbs_WIRE
from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.GeomAbs import GeomAbs_Plane
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax1, gp_Trsf, gp_Vec
from OCC.Core.BRepBndLib import brepbndlib
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.GProp import GProp_GProps
from OCC.Core.BRepGProp import BRepGProp
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform


def load_step(filename):
    reader = STEPControl.STEPControl_Reader()
    status = reader.ReadFile(filename)
    if status == IFSelect_RetDone:
        reader.TransferRoots()
        return reader.OneShape()
    else:
        raise Exception(f"Failed to load {filename}")


def save_step(shape, filename):
    writer = STEPControl.STEPControl_Writer()
    writer.Transfer(shape, STEPControl.STEPControl_AsIs)
    writer.Write(filename)


def analyze_part1(shape):
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    max_z = -1e9
    while exp.More():
        face = topods.Face(exp.Current())
        surf = BRepAdaptor_Surface(face)
        if surf.GetType() == GeomAbs_Plane:
            gp_pln = surf.Plane()
            pos = gp_pln.Location()
            z = pos.Z()
            if z > max_z:
                max_z = z
        exp.Next()

    exp.ReInit()
    boss_top_face = None
    min_dist = 1e-3
    while exp.More():
        face = topods.Face(exp.Current())
        surf = BRepAdaptor_Surface(face)
        if surf.GetType() == GeomAbs_Plane:
            gp_pln = surf.Plane()
            pos = gp_pln.Location()
            if abs(pos.Z() - max_z) < min_dist:
                boss_top_face = face
                break
        exp.Next()

    if boss_top_face is None:
        raise Exception("Could not find boss top face")

    props = GProp_GProps()
    BRepGProp.SurfaceProperties(boss_top_face, props)
    g_pt = props.CentreOfMass()
    X_boss, Y_boss = g_pt.X(), g_pt.Y()

    exp.ReInit()
    z_boss_base = max_z
    while exp.More():
        face = topods.Face(exp.Current())
        surf = BRepAdaptor_Surface(face)
        if surf.GetType() == GeomAbs_Plane:
            gp_pln = surf.Plane()
            normal = gp_pln.Axis().Direction()
            if abs(normal.Z()) < 1e-3:
                bbox = Bnd_Box()
                brepbndlib.Add(face, bbox)
                xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
                if abs(zmax - max_z) < 1e-2:
                    if zmin < z_boss_base:
                        z_boss_base = zmin
        exp.Next()

    return X_boss, Y_boss, z_boss_base


def analyze_part2(shape):
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    max_z = -1e9
    while exp.More():
        face = topods.Face(exp.Current())
        surf = BRepAdaptor_Surface(face)
        if surf.GetType() == GeomAbs_Plane:
            gp_pln = surf.Plane()
            pos = gp_pln.Location()
            if pos.Z() > max_z:
                max_z = pos.Z()
        exp.Next()

    exp.ReInit()
    top_face = None
    min_dist = 1e-3
    while exp.More():
        face = topods.Face(exp.Current())
        surf = BRepAdaptor_Surface(face)
        if surf.GetType() == GeomAbs_Plane:
            gp_pln = surf.Plane()
            pos = gp_pln.Location()
            if abs(pos.Z() - max_z) < min_dist:
                wire_exp = TopExp_Explorer(face, TopAbs_WIRE)
                wire_count = 0
                while wire_exp.More():
                    wire_count += 1
                    wire_exp.Next()
                if wire_count > 1:
                    top_face = face
                    break
        exp.Next()

    if top_face is None:
        exp.ReInit()
        while exp.More():
            face = topods.Face(exp.Current())
            surf = BRepAdaptor_Surface(face)
            if surf.GetType() == GeomAbs_Plane:
                gp_pln = surf.Plane()
                pos = gp_pln.Location()
                if abs(pos.Z() - max_z) < min_dist:
                    top_face = face
                    break
            exp.Next()

    if top_face is None:
        raise Exception("Could not find top face of Part 2")

    wire_exp = TopExp_Explorer(top_face, TopAbs_WIRE)
    wires = []
    while wire_exp.More():
        wire = topods.Wire(wire_exp.Current())
        props = GProp_GProps()
        BRepGProp.LinearProperties(wire, props)
        length = props.Mass()
        wires.append((wire, length))
        wire_exp.Next()

    if len(wires) > 1:
        wires.sort(key=lambda x: x[1])
        inner_wire = wires[0][0]
    elif len(wires) == 1:
        inner_wire = wires[0][0]
    else:
        raise Exception("No wires found in top face of Part 2")

    props = GProp_GProps()
    BRepGProp.LinearProperties(inner_wire, props)
    g_pt = props.CentreOfMass()
    X_hole, Y_hole = g_pt.X(), g_pt.Y()

    return X_hole, Y_hole, max_z


# Main execution
if __name__ == "__main__":
    part1_path = os.path.join("input", "Extruded Square.STEP")
    part2_path = os.path.join("input", "Square Hole.STEP")

    part1 = load_step(part1_path)
    part2 = load_step(part2_path)

    X_boss, Y_boss, z_boss_base = analyze_part1(part1)
    X_hole, Y_hole, Z_hole_top = analyze_part2(part2)

    P_boss_base = gp_Pnt(X_boss, Y_boss, z_boss_base)
    P_hole_top = gp_Pnt(X_hole, Y_hole, Z_hole_top)

    trsf_rot = gp_Trsf()
    axis = gp_Ax1(P_boss_base, gp_Dir(1, 0, 0))
    trsf_rot.SetRotation(axis, 3.141592653589793)

    trsf_trans = gp_Trsf()
    translation_vec = gp_Vec(P_boss_base, P_hole_top)
    trsf_trans.SetTranslation(translation_vec)

    trsf_total = trsf_trans.Multiplied(trsf_rot)

    transform_api = BRepBuilderAPI_Transform(part1, trsf_total, True)
    transformed_part1 = transform_api.Shape()

    builder = BRep_Builder()
    assembly = TopoDS_Compound()
    builder.MakeCompound(assembly)
    builder.Add(assembly, transformed_part1)
    builder.Add(assembly, part2)

    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", "assembly.step")
    save_step(assembly, output_path)