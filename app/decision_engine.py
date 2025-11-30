from .utils import safe_float
BASE_VISIBILITY_KM=5.0; BASE_WIND_KT=20.0
def apply_weather_rules(w):
    vis=safe_float(w.get('visibility_km')); wind=safe_float(w.get('wind_speed_kt'))
    clouds=w.get('clouds',[])
    cloud_base=None
    if clouds:
        bases=[c.get('base_ft_agl') for c in clouds if c.get('base_ft_agl')]
        if bases: cloud_base=min(bases)
    conds=(w.get('conditions') or '').upper()
    return {'visibility_ok':vis is not None and vis>=BASE_VISIBILITY_KM,'cloud_base_ok':cloud_base is None or cloud_base>=1500,'wind_ok':wind is not None and wind<=BASE_WIND_KT,'significant_weather_ok': not any(x in conds for x in ['TS','RA','FG']),'visibility_km':vis,'cloud_base_ft':cloud_base,'wind_kt':wind,'conditions':conds}
def combine_with_poh_limits(weather_eval,poh_limits):
    reasons=[]
    vis=weather_eval.get('visibility_km'); min_vis=poh_limits.get('min_visibility_km_recommendation') or BASE_VISIBILITY_KM
    if vis is None: visibility_ok=False; reasons.append('Visibility unknown')
    else: visibility_ok=vis>=min_vis; 
    wind=weather_eval.get('wind_kt'); poh_max=poh_limits.get('max_wind_kt_recommendation') or BASE_WIND_KT
    wind_ok = wind is not None and wind<=poh_max
    if wind is None: reasons.append('Wind unknown')
    elif not wind_ok: reasons.append(f'Wind {wind}kt > {poh_max}')
    sig_ok=weather_eval.get('significant_weather_ok')
    if not sig_ok: reasons.append('Significant weather')
    cloud_ok = weather_eval.get('cloud_base_ft') is None or weather_eval.get('cloud_base_ft')>=1500
    if not cloud_ok: reasons.append('Low cloud base')
    decision_go = all([visibility_ok, wind_ok, sig_ok, cloud_ok])
    return {'reasons':reasons,'visibility_ok':visibility_ok,'wind_ok':wind_ok,'significant_weather_ok':sig_ok,'cloud_base_ok':cloud_ok,'decision_go':decision_go}
