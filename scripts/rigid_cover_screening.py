"""Linear vertical grillage screening; SI; requires NumPy (bundled with Blender).
3 DOF/node: downward displacement and two rotations. Prismatic Euler beams,
Saint-Venant thin-wall box torsion, perfect rigid joints. Not a design-code check.
"""
import math
import numpy as np

def section(h,b,t):
    area=b*h-(b-2*t)*(h-2*t)
    I=(b*h**3-(b-2*t)*(h-2*t)**3)/12
    J=4*((b-t)*(h-t))**2/(2*(b+h-2*t)/t)
    return area,I,J

def element(a,b,E,G,I,J):
    dx=b[0]-a[0];dy=b[1]-a[1];L=math.hypot(dx,dy);ux,uy=dx/L,dy/L
    # slope dw/ds = uy*rx - ux*ry, twist about the beam = ux*rx + uy*ry.
    T=np.zeros((6,6));T[0,0]=T[2,3]=1
    T[1,1:3]=[uy,-ux];T[3,4:6]=[uy,-ux]
    T[4,1:3]=[ux,uy];T[5,4:6]=[ux,uy]
    B=E*I/L**3*np.array([[12,6*L,-12,6*L],[6*L,4*L*L,-6*L,2*L*L],[-12,-6*L,12,-6*L],[6*L,2*L*L,-6*L,4*L*L]])
    k=np.zeros((6,6));k[:4,:4]=B;k[4:,4:]=G*J/L*np.array([[1,-1],[-1,1]])
    return T.T@k@T,T,k,L

def verify():
    # Single cantilever against the exact tip force solution, in two orientations.
    errors=[]
    for b in [(2.,0.),(0.,2.)]:
        k,T,kl,L=element((0,0),b,140e9,53.846e9,1e-5,2e-5)
        f=np.array([1000.,0.,0.]);u=np.linalg.solve(k[3:,3:],f)
        exact=1000*L**3/(3*140e9*1e-5);errors.append(abs(u[0]/exact-1))
    assert max(errors)<1e-10
    return {'cantilever_tip_solution_relative_errors':errors}

def network(cfg):
    nodes=[];lookup={};edges=[];rowids={}
    def node(x,y):
        key=(round(x,9),round(y,9))
        if key not in lookup:lookup[key]=len(nodes);nodes.append((x,y))
        return lookup[key]
    xs=cfg.stations()
    for n,x in enumerate(xs):
        hw=0 if n in (0,len(xs)-1) else cfg.halfwidth(x)
        rowids[x]=[node(x,-hw),node(x,0),node(x,hw)]
    unique=set()
    def edge(i,j,kind):
        key=tuple(sorted((i,j)))
        if i!=j and key not in unique:unique.add(key);edges.append((i,j,kind))
    for a,b in zip(xs,xs[1:]):
        for side in range(3):edge(rowids[a][side],rowids[b][side],'longitudinal')
    hookrows=sorted(set(p[0] for p in cfg.points()))
    for x in xs:
        if x not in hookrows and not any(abs(x-v)<1e-6 for v in (cfg.cross_rows() if hasattr(cfg,'cross_rows') else (.9,1.8,2.7,3.6,4.02))):continue
        ys=[-cfg.halfwidth(x),0,cfg.halfwidth(x)]
        if x in hookrows:ys+= [p[1] for p in cfg.points() if p[0]==x]
        ids=[node(x,y) for y in sorted(set(ys))]
        for a,b in zip(ids,ids[1:]):edge(a,b,'crossbeam')
    hooks=[node(x,y) for x,y,_ in cfg.points()]
    seats=[node(x,y) for x,y in cfg.supports()]
    return nodes,edges,rowids,hooks,seats

def solve(cfg,total_mass,lift_only=False):
    tests=verify();nodes,edges,rowids,hooks,seats=network(cfg)
    A,I,J=section(**{'h':cfg.RHS['height'],'b':cfg.RHS['width'],'t':cfg.RHS['wall']})
    N=len(nodes);K=np.zeros((3*N,3*N));F=np.zeros(3*N);parts=[]
    for i,j,kind in edges:
        k,T,kl,L=element(nodes[i],nodes[j],cfg.E,cfg.E/(2*(1+cfg.NU)),I,J)
        ids=[3*i+n for n in range(3)]+[3*j+n for n in range(3)]
        K[np.ix_(ids,ids)]+=k;parts.append((ids,T,kl,L,kind))
    # Tributary areas from exact wedge plan sampled in x; distribute to three
    # longitudinal rails as two simply supported transverse tray half-spans.
    xs=sorted(rowids);trib=[]
    for n,x in enumerate(xs):
        lo=0 if n==0 else (xs[n-1]+x)/2
        hi=cfg.COVER['radius'] if n==len(xs)-1 else (x+xs[n+1])/2
        area=0
        for q in range(100):
            xx=lo+(q+.5)*(hi-lo)/100;r=cfg.COVER['radius']
            area+=2*min(xx/math.sqrt(3),math.sqrt(max(0,r*r-xx*xx)))*(hi-lo)/100
        trib.append(area)
    for x,ar in zip(xs,trib):
        for n,fraction in enumerate((.25,.5,.25)):F[3*rowids[x][n]]+=total_mass*9.80665*ar/sum(trib)*fraction
    result={}
    cases=[('lifted',hooks)] if lift_only else [('lifted',hooks),('seated',seats)]
    for name,supports in cases:
        fixed=sorted(set(3*i for i in supports));free=[i for i in range(3*N) if i not in fixed]
        u=np.zeros(3*N);u[free]=np.linalg.solve(K[np.ix_(free,free)],F[free]);reaction=K@u-F
        residual=np.max(np.abs((K@u-F)[free]));assert residual<1e-5
        reactions=[-float(reaction[3*i]) for i in supports]
        assert abs(sum(reactions)-total_mass*9.80665)<1e-5
        assert min(reactions)>0, (name,'uplift requires contact analysis',reactions)
        moments=[]
        for ids,T,kl,L,kind in parts:
            force=kl@T@u[ids];moments.extend([abs(float(force[1])),abs(float(force[3]))])
        result[name]={'max_downward_deflection_mm':max(u[::3])*1000,'apex_deflection_mm':float(u[3*rowids[xs[0]][0]])*1000,
                      'max_gross_bending_stress_MPa':max(moments)*cfg.RHS['height']/2/I/1e6,
                      'support_reactions_N':reactions,'free_dof_residual_N_or_Nm':float(residual),
                      'nodal_displacements_m':u[::3].tolist()}
    result.update({'nodes_xy_m':nodes,'edges':edges,'mass_input_kg':total_mass,'E_Pa':cfg.E,'section_area_m2':A,'section_I_m4':I,'section_J_m4':J,
                   'verification':tests,'scope':'Linear gross-section grillage screening. Actual steel mass distribution approximated by area load; rigid joints, equal support elevations. No thermal strain, local holes, welds, fatigue, buckling, dynamics or full suspension balance.'})
    return result
