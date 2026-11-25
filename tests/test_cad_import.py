"""Tests for the CAD import scripts, run without Fusion or FreeCAD.

The fixture tests/data/example-hardpoints.csv is the prototype's "Export for CAD" output for
the example double-wishbone front corner (with the byte-order mark that "Download CSV" adds).
Expected values come from the example geometry: wheel centre at (0, 760, 300) mm on the left,
mirrored to y = -760 on the right.

Run:  py tests/test_cad_import.py      (or: pytest tests/test_cad_import.py)
"""
import csv
import importlib.util
import os
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, 'tests', 'data', 'example-hardpoints.csv')
FUSION_SCRIPT = os.path.join(ROOT, 'cad', 'fusion', 'ImportHardpoints', 'ImportHardpoints.py')
FREECAD_MACRO = os.path.join(ROOT, 'cad', 'freecad', 'ImportHardpoints.FCMacro')


def load_fusion():
    spec = importlib.util.spec_from_file_location('import_hardpoints_fusion', FUSION_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_freecad():
    namespace = {'HARDPOINTS_NO_RUN': True, '__name__': 'import_hardpoints_freecad'}
    with open(FREECAD_MACRO, encoding='utf-8') as f:
        exec(compile(f.read(), FREECAD_MACRO, 'exec'), namespace)
    return namespace


def by_key(points):
    return {(p['corner'], p['id']): p for p in points}


def test_reads_both_corners():
    points = load_fusion().read_hardpoints(CSV_PATH)
    # 11 double-wishbone hardpoints + 2 derived points, for FL and FR
    assert len(points) == 26
    assert {p['corner'] for p in points} == {'FL', 'FR'}


def test_right_corner_is_the_mirror_image():
    pts = by_key(load_fusion().read_hardpoints(CSV_PATH))
    assert (pts[('FL', 'wheelCentre')]['x'], pts[('FL', 'wheelCentre')]['y'], pts[('FL', 'wheelCentre')]['z']) == (0, 760, 300)
    assert pts[('FR', 'wheelCentre')]['y'] == -760
    for (corner, pid), p in pts.items():
        if corner == 'FL':
            q = pts[('FR', pid)]
            assert (q['x'], q['y'], q['z']) == (p['x'], -p['y'], p['z'])


def test_names_follow_the_corner_part_point_scheme():
    pts = by_key(load_fusion().read_hardpoints(CSV_PATH))
    assert pts[('FL', 'lowerArmInnerForward')]['name'] == 'FL · Lower arm · inner forward'
    assert pts[('FR', 'upperArmOuter')]['name'] == 'FR · Upper arm · outer (ball joint)'


def test_double_wishbone_links():
    module = load_fusion()
    pairs = module.link_pairs(module.read_hardpoints(CSV_PATH))
    # per corner: 2 upper-arm legs, 2 lower-arm legs, tie rod, steering axis, damper
    assert len(pairs) == 14
    ids = {(a['id'], b['id']) for a, b in pairs}
    assert ('lowerArmOuter', 'upperArmOuter') in ids
    assert not any('strut' in a or 'strut' in b for a, b in ids)
    assert all(a['corner'] == b['corner'] for a, b in pairs)


def test_fusion_converts_millimetres_to_centimetres():
    module = load_fusion()
    pts = by_key(module.read_hardpoints(CSV_PATH))
    assert module.mm_to_cm(pts[('FL', 'wheelCentre')]) == (0.0, 76.0, 30.0)


def test_freecad_macro_reads_the_same_points():
    fusion, freecad = load_fusion(), load_freecad()
    assert freecad['read_hardpoints'](CSV_PATH) == fusion.read_hardpoints(CSV_PATH)
    assert len(freecad['link_pairs'](freecad['read_hardpoints'](CSV_PATH))) == 14
    assert freecad['object_name']('HP_FL_lowerArmOuter') == 'HP_FL_lowerArmOuter'
    assert freecad['object_name']('Link_FL a-b') == 'Link_FL_a_b'


def load_fusion_export():
    path = os.path.join(ROOT, 'cad', 'fusion', 'ExportHardpoints', 'ExportHardpoints.py')
    spec = importlib.util.spec_from_file_location('export_hardpoints_fusion', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fusion_export_converts_centimetres_to_millimetres():
    assert load_fusion_export().cm_to_mm(0.0, 76.0, 30.0) == (0.0, 760.0, 300.0)


def test_fusion_export_round_trip():
    # Import -> (Fusion keeps the names) -> export must give the same names and millimetres back.
    export = load_fusion_export()
    points = load_fusion().read_hardpoints(CSV_PATH)
    text = export.hardpoints_csv([(p['name'], p['x'], p['y'], p['z']) for p in points] + [('Sketch point 7', 1, 2, 3)])
    path = os.path.join(tempfile.mkdtemp(), 'from-fusion.csv')
    with open(path, 'w', newline='', encoding='utf-8') as f:
        f.write(text)
    with open(path, newline='', encoding='utf-8') as f:   # ids are empty on purpose: read the rows directly
        rows = list(csv.DictReader(f))
    # 11 hardpoints per corner; the 2 derived points per corner and the unnamed point are left out
    assert len(rows) == 22
    wc = [r for r in rows if r['name'] == 'FL · Wheel · centre'][0]
    assert (wc['corner'], float(wc['x_mm']), float(wc['y_mm']), float(wc['z_mm'])) == ('FL', 0.0, 760.0, 300.0)
    assert all(r['id'] == '' for r in rows)
    assert export.corner_of('RR · Toe link · outer') == 'RR' and export.corner_of('Sketch point 7') is None


def test_wrong_file_is_rejected():
    module = load_fusion()
    with tempfile.NamedTemporaryFile('w', suffix='.csv', delete=False, encoding='utf-8') as f:
        f.write('a,b,c\n1,2,3\n')
        path = f.name
    try:
        module.read_hardpoints(path)
    except ValueError as e:
        assert 'missing column' in str(e)
    else:
        raise AssertionError('expected ValueError')
    finally:
        os.remove(path)


if __name__ == '__main__':
    tests = [v for k, v in sorted(globals().items()) if k.startswith('test_') and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print('pass ', t.__name__)
        except Exception as e:  # report and continue
            failed += 1
            print('FAIL ', t.__name__, '-', repr(e))
    print('{} of {} tests passed'.format(len(tests) - failed, len(tests)))
    raise SystemExit(1 if failed else 0)
