import math
def wind_components(wind_dir, wind_speed, runway_heading):
    if wind_dir is None or wind_speed is None:
        return (None, None)
    angle = abs((wind_dir - runway_heading + 360) % 360)
    theta = math.radians(angle)
    head = wind_speed * math.cos(theta)
    cross = abs(wind_speed * math.sin(theta))
    return (head, cross)
def pick_best_runway(runways, wind_dir, wind_speed):
    candidates = []
    for r in runways:
        headings = r['heading'] if isinstance(r['heading'], list) else [r['heading']]
        for h in headings:
            head, cross = wind_components(wind_dir, wind_speed, h)
            candidates.append({'runway': r['name'], 'heading': h, 'headwind': head, 'crosswind': cross})
    if not candidates:
        return {'runway': None, 'heading': None, 'headwind':0, 'crosswind':0}
    pos = [c for c in candidates if c['headwind'] is not None and c['headwind']>=0]
    if pos:
        best = sorted(pos, key=lambda x:(-x['headwind'], x['crosswind']))[0]
    else:
        best = sorted(candidates, key=lambda x:(-(x['headwind'] or 0), x['crosswind']))[0]
    return best
