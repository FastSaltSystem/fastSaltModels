"""Generate a resolved coolant TOML document without starting Blender."""
import argparse
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'models')]
from textual_graphics.assembly_model import document,write
from coolant_assembly import reactor_interface,build_model,check_pid_links
import wistr_installation as layout

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'outputs/coolant-assembly/coolant.resolved.toml')
    parser.add_argument('--pid-model',type=Path,help='Optionally check equipment, flow and dimensions against the hub P&ID TOML')
    args=parser.parse_args()
    model=build_model(layout,reactor_interface(layout,ROOT),ROOT)
    doc=document(model)
    if args.pid_model:
        check=check_pid_links(doc,args.pid_model)
        print('P&ID agrees for '+str(len(check['line_tags']))+' main lines and '+str(len(check['equipment_tags']))+' equipment tags')
    write(doc,args.output)
    print(f'Resolved {len(doc["components"])} components, {len(doc["ports"])} ports, {len(doc["connections"])} routes: {args.output}')
if __name__=='__main__':main()
