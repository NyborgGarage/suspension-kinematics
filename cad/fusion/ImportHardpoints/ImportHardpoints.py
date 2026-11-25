"""Import suspension hardpoints into Fusion.

Reads the CSV exported by the suspension prototype ("Export for CAD") and creates, in the
active component:

* a sketch "Hardpoints <file name>" on the XY plane, with one sketch point per hardpoint and
  sketch lines for the links (arms, tie rod, steering axis, strut, damper);
* one named construction point per hardpoint, so the points are listed by name in the
  browser, for example "FL · Lower arm · inner forward".

Coordinates: ISO 8855 (X forward, Y left, Z up) in millimetres. The Fusion API works in
centimetres, so every value is divided by 10. The design should be Z-up; in a Y-up design
the suspension appears lying on its side.

Install once: Utilities > Add-Ins > Scripts and Add-Ins, Scripts tab, press the green "+"
next to "My Scripts" and choose this folder. Then select ImportHardpoints and press Run.
"""
import csv
import os
import traceback

try:  # Fusion's modules only exist inside Fusion; the plain functions below work without them.
    import adsk.core
    import adsk.fusion
except ImportError:  # running the tests outside Fusion
    adsk = None

# Pairs of point ids joined by a sketch line, per corner. Pairs whose points are not in the
# file are skipped, so the same list covers every suspension type.
LINKS = [
    ('upperArmInnerForward', 'upperArmOuter'),
    ('upperArmInnerRearward', 'upperArmOuter'),
    ('lowerArmInnerForward', 'lowerArmOuter'),
    ('lowerArmInnerRearward', 'lowerArmOuter'),
    ('tieRodInner', 'tieRodOuter'),
    ('lowerArmOuter', 'upperArmOuter'),   # steering axis, double wishbone
    ('lowerArmOuter', 'strutTopMount'),   # steering axis, MacPherson
    ('strutLower', 'strutTopMount'),      # strut (damper) axis, MacPherson
    ('damperLower', 'damperUpper'),
    # multilink: five links
    ('upperForwardLinkInner', 'upperForwardLinkOuter'),
    ('upperRearwardLinkInner', 'upperRearwardLinkOuter'),
    ('lowerForwardLinkInner', 'lowerForwardLinkOuter'),
    ('lowerRearwardLinkInner', 'lowerRearwardLinkOuter'),
    # strut with lateral links: the two lateral links and the trailing rod
    ('forwardLinkInner', 'forwardLinkOuter'),
    ('rearwardLinkInner', 'rearwardLinkOuter'),
    ('trailingRodForward', 'trailingRodRearward'),
    # trailing arm: pivot axis, and the arm from each pivot to the wheel centre
    ('trailingArmPivotInboard', 'trailingArmPivotOutboard'),
    ('trailingArmPivotInboard', 'wheelCentre'),
    ('trailingArmPivotOutboard', 'wheelCentre'),
]

REQUIRED_COLUMNS = ('name', 'id', 'corner', 'x_mm', 'y_mm', 'z_mm')


def read_hardpoints(path):
    """Read the hardpoints CSV. Returns dicts with name, id, corner and x, y, z in mm."""
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError('Not a hardpoints CSV, missing column(s): ' + ', '.join(missing))
        points = []
        for row in reader:
            if not row.get('id'):
                continue
            points.append({
                'name': row['name'], 'id': row['id'], 'corner': row['corner'],
                'x': float(row['x_mm']), 'y': float(row['y_mm']), 'z': float(row['z_mm']),
            })
    return points


def link_pairs(points):
    """Pairs of points (same corner) to join with lines, in file order of the corners."""
    by_key = {(p['corner'], p['id']): p for p in points}
    corners = []
    for p in points:
        if p['corner'] not in corners:
            corners.append(p['corner'])
    pairs = []
    for corner in corners:
        for a, b in LINKS:
            if (corner, a) in by_key and (corner, b) in by_key:
                pairs.append((by_key[(corner, a)], by_key[(corner, b)]))
    return pairs


def mm_to_cm(p):
    """Fusion's API length unit is the centimetre."""
    return (p['x'] / 10.0, p['y'] / 10.0, p['z'] / 10.0)


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox('Open or create a design first.')
            return

        dlg = ui.createFileDialog()
        dlg.title = 'Choose the hardpoints CSV'
        dlg.filter = 'CSV files (*.csv);;All files (*.*)'
        if dlg.showOpen() != adsk.core.DialogResults.DialogOK:
            return
        points = read_hardpoints(dlg.filename)
        if not points:
            ui.messageBox('The file contains no points.')
            return

        comp = design.activeComponent
        sketch = comp.sketches.add(comp.xYConstructionPlane)
        sketch.name = 'Hardpoints ' + os.path.splitext(os.path.basename(dlg.filename))[0]
        sketch.isComputeDeferred = True
        sketch_points = {}
        for p in points:
            model_point = adsk.core.Point3D.create(*mm_to_cm(p))
            sketch_points[(p['corner'], p['id'])] = sketch.sketchPoints.add(sketch.modelToSketchSpace(model_point))
        pairs = link_pairs(points)
        for a, b in pairs:
            sketch.sketchCurves.sketchLines.addByTwoPoints(
                sketch_points[(a['corner'], a['id'])], sketch_points[(b['corner'], b['id'])])
        sketch.isComputeDeferred = False

        named = 0
        try:
            for p in points:
                point_input = comp.constructionPoints.createInput()
                point_input.setByPoint(sketch_points[(p['corner'], p['id'])])
                construction_point = comp.constructionPoints.add(point_input)
                construction_point.name = p['name']
                named += 1
        except Exception:
            pass  # e.g. not allowed in this design type; the sketch points are still there

        ui.messageBox('Imported {} points into the sketch "{}", with {} link lines and {} named construction points.'
                      .format(len(points), sketch.name, len(pairs), named))
    except Exception:
        if ui:
            ui.messageBox('Import failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    pass
