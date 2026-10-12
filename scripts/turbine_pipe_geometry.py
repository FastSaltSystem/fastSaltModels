"""Render checked turbine routing as colored outer envelopes, not fabricated pipework."""
from turbine_piping import make,check,COLORS

def add_piping(b,root,site):
    data=make();data['verification']=check(data)
    checks=data['verification']
    assert not checks['disconnected_endpoints']
    assert not checks['pipe_pair_conflicts']
    assert not checks['tight_bend_routes']
    assert not checks['wall_or_crane_conflicts']
    unexpected=[q for q in checks['equipment_and_service_conflicts'] if (q['route'],q['object'])!=('HP4 feedwater to SG interface','Cross aisle')]
    assert not unexpected,unexpected
    origin=(site.TURBINE['centre'][0]-site.TURBINE['size'][0]/2,site.TURBINE['centre'][1]-site.TURBINE['size'][1]/2,site.PAD_Z)
    for net,color in COLORS.items():b.material('tp_'+net,color,roughness=.4)
    assembly=b.assembly('turbine.piping','Turbine piping',origin)
    assembly['scope']='Outer pipe/jacket envelopes, provisional ports; no supports, valves or stress qualification'
    for q in data['routes']:
        obj=b.tube(q['name'],assembly,q['render_points'],q['spec']['jacket_od']/2,'tp_'+q['network'])
        obj['service']=q['network'];obj['route_name']=q['name'];obj['bore_m']=q['spec']['bore'];obj['jacket_allowance_m']=q['spec']['jacket_od'];obj['scope']=q['spec']['dimension_status']
        obj['below_floor_part']=q['floor_min_m']<0
        for col in list(obj.users_collection):col.objects.unlink(obj)
        b.collection('Turbine pipes | '+q['network']).objects.link(obj)
    return data
