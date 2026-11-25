"""Export suspension hardpoints from Fusion back to the suspension prototype.

Finds the named construction points that ImportHardpoints created (names such as
"FL · Lower arm · inner forward") in the active component, and writes them to a CSV that the
prototype reads with "Import CSV" (under CAD exchange). Move the sketch points in Fusion, the
construction points follow, then run this script.

Points are matched by name in the prototype, so the id column is left empty. Names that do not
start with a corner (FL, FR, RL, RR) are skipped.

Coordinates: ISO 8855 (X forward, Y left, Z up) in millimetres. The Fusion API works in
centimetres, so every value is multiplied by 10.

Install once: Utilities > Add-Ins > Scripts and Add-Ins, Scripts tab, press the green "+"
next to "My Scripts" and choose this folder. Then select ExportHardpoints and press Run.
"""
import csv
import io
import re
import traceback

try:  # Fusion's modules only exist inside Fusion; the plain functions below work without them.
    import adsk.core
    import adsk.fusion
except ImportError:  # running the tests outside Fusion
    adsk = None

CORNER_NAME = re.compile(r'^\s*(FL|FR|RL|RR)\s*·')


def corner_of(name):
    """'FL · Lower arm · inner forward' -> 'FL'; None for names that are not hardpoints."""
    m = CORNER_NAME.match(name or '')
    return m.group(1) if m else None


def cm_to_mm(x, y, z):
    """Fusion's API length unit is the centimetre."""
    return (x * 10.0, y * 10.0, z * 10.0)


def hardpoints_csv(points):
    """points: (name, x_mm, y_mm, z_mm) tuples. Returns CSV text with the prototype's columns."""
    out = io.StringIO()
    w = csv.writer(out, lineterminator='\r\n')
    w.writerow(['name', 'id', 'corner', 'x_mm', 'y_mm', 'z_mm'])
    for name, x, y, z in points:
        corner = corner_of(name)
        if corner and 'Derived' not in name:
            w.writerow([name, '', corner] + ['{:.3f}'.format(v) for v in (x, y, z)])
    return out.getvalue()


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox('Open the design with the hardpoints first.')
            return
        comp = design.activeComponent
        points = []
        for i in range(comp.constructionPoints.count):
            cp = comp.constructionPoints.item(i)
            if corner_of(cp.name):
                g = cp.geometry
                points.append((cp.name,) + cm_to_mm(g.x, g.y, g.z))
        if not points:
            ui.messageBox('No hardpoints found. The construction points must be named like '
                          '"FL · Lower arm · inner forward" (as ImportHardpoints names them).')
            return
        dlg = ui.createFileDialog()
        dlg.title = 'Save the hardpoints CSV'
        dlg.filter = 'CSV files (*.csv)'
        dlg.initialFilename = 'hardpoints-from-fusion.csv'
        if dlg.showSave() != adsk.core.DialogResults.DialogOK:
            return
        with open(dlg.filename, 'w', newline='', encoding='utf-8-sig') as f:
            f.write(hardpoints_csv(points))
        ui.messageBox('Wrote {} points to {}.\nIn the prototype: CAD exchange > Import CSV.'.format(len(points), dlg.filename))
    except Exception:
        if ui:
            ui.messageBox('Export failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    pass
