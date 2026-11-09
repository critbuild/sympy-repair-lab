"""A desktop demo backed by actual, isolated SymPy executions.

Run `python demo.py`; use --headless for a machine-readable verification.
"""
from pathlib import Path
import argparse
import concurrent.futures
from datetime import datetime,timezone
import json
import os
import queue
import subprocess
import sys
import tempfile
import threading
import time
from common import HERE,tasks,extract,environment,save

SCENES={
    'Closed square':[[[0,0],[4,0]],[[4,0],[4,3]],[[4,3],[0,3]],[[0,3],[0,0]]],
    'Two edges':[[[0,0],[2,2]],[[2,2],[4,0]]],
    'Repeated edge':[[[0,0],[4,0]],[[0,0],[4,0]],[[4,0],[4,3]],[[4,3],[0,3]]],
}
MODES=['Original checkout','Recorded agent repair','Corrected repair']
BG='#101925';PANEL='#182536';TEXT='#edf3f7';MUTED='#a6b6c8';TEAL='#6ee7c4';CORAL='#ff9a8b';BORDER='#304458'

class Engine:
    def __init__(self,work=None):
        self.work=Path(work).resolve() if work else Path(tempfile.mkdtemp(prefix='sympy-repair-demo-'))
        self.work.mkdir(parents=True,exist_ok=True)
        self.roots={}
    def prepare(self):
        definitions=tasks()
        baseline=next(t for t in definitions if t['id'].startswith('01'))
        recovery=next(t for t in definitions if t['id'].startswith('03'))
        for index,mode in enumerate(MODES):
            root=self.work/('source-'+str(index))
            extract(baseline if index==0 else recovery,root,reference=index==2)
            self.roots[mode]=root
    def run_mode(self,mode,edges):
        start=time.monotonic()
        proc=subprocess.run([sys.executable,str(HERE/'demo/execute_scene.py')],cwd=self.roots[mode],env=environment(self.roots[mode]),input=json.dumps({'edges':edges}),text=True,encoding='utf-8',capture_output=True,timeout=30)
        if proc.returncode:
            raise RuntimeError(mode+': '+proc.stderr[-2000:])
        result=json.loads(proc.stdout)
        result['seconds']=round(time.monotonic()-start,3)
        result['mode']=mode
        return result
    def run(self,scene):
        edges=SCENES[scene]
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            values=list(pool.map(lambda m:self.run_mode(m,edges),MODES))
        record={'scenario':scene,'executed_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version.split()[0],'source_revision':'d1320814eda6549996190618a21eaf212cfd4d1e','recorded_patch':'gpt-6-astra, discovery session 01a1bc8f-6ad1-7421-b692-2aee46e2ba0c','correction':'Evaluator-authored one-line GeometryEntity.__ne__ fix','modes':values}
        save(self.work/('run-'+scene.lower().replace(' ','-')+'.json'),record)
        return record

def gui(engine):
    import tkinter as tk
    from tkinter import ttk,filedialog
    root=tk.Tk();root.title('SymPy Repair Lab');root.geometry('1440x920');root.minsize(1120,820);root.configure(bg=BG)
    style=ttk.Style(root);style.theme_use('clam')
    style.configure('TCombobox',fieldbackground=PANEL,background=PANEL,foreground=TEXT,arrowcolor=TEAL,padding=7)
    style.map('TCombobox',fieldbackground=[('readonly',PANEL)],foreground=[('readonly',TEXT)])
    def label(parent,text,size=12,color=TEXT,bold=False,**kw):
        return tk.Label(parent,text=text,bg=parent.cget('bg'),fg=color,font=('Segoe UI',size,'bold' if bold else 'normal'),**kw)
    header=tk.Frame(root,bg=BG);header.pack(fill='x',padx=30,pady=(22,8))
    label(header,'SYMPY REPAIR LAB  /  EXECUTABLE EVIDENCE',11,TEAL,True).pack(anchor='w')
    label(header,'The bug is fixed. An edge disappears.',27,TEXT,True).pack(anchor='w',pady=(7,4))
    label(header,'Compare actual library executions before the change, after a recorded agent repair, and after correcting the regression.',12,MUTED).pack(anchor='w')
    toolbar=tk.Frame(root,bg=BG);toolbar.pack(fill='x',padx=30,pady=12)
    label(toolbar,'Scene',11,MUTED).pack(side='left',padx=(0,10))
    scene=tk.StringVar(value='Closed square')
    combo=ttk.Combobox(toolbar,textvariable=scene,values=list(SCENES),state='readonly',width=19);combo.pack(side='left')
    status=tk.StringVar(value='Preparing three clean source trees...')
    result_holder={'record':None}
    cards=[]
    body=tk.Frame(root,bg=BG);body.pack(fill='both',expand=True,padx=24,pady=(0,8))
    for col,mode in enumerate(MODES):
        body.grid_columnconfigure(col,weight=1,uniform='cards');body.grid_rowconfigure(0,weight=1)
        card=tk.Frame(body,bg=PANEL,highlightbackground=BORDER,highlightthickness=1)
        card.grid(row=0,column=col,sticky='nsew',padx=6)
        label(card,str(col+1).zfill(2)+'  '+mode,15,TEXT,True).pack(anchor='w',padx=18,pady=(15,3))
        provenance=['Pinned SymPy baseline','Actual GPT-6 Astra production patch','Same patch + one-line geometry fix'][col]
        label(card,provenance,10,MUTED).pack(anchor='w',padx=18)
        canvas=tk.Canvas(card,bg=PANEL,highlightthickness=0,height=260);canvas.pack(fill='both',expand=True,padx=8,pady=7)
        count=tk.StringVar(value='Waiting for execution');compat=tk.StringVar(value='');first=tk.StringVar(value='')
        label(card,'',14,TEXT,True,textvariable=count).pack(anchor='w',padx=18,pady=(0,9))
        label(card,'',11,MUTED,textvariable=compat).pack(anchor='w',padx=18,pady=(0,5))
        label(card,'',11,MUTED,textvariable=first).pack(anchor='w',padx=18,pady=(0,16))
        cards.append((canvas,count,compat,first))
    detail=tk.Frame(root,bg=PANEL);detail.pack(fill='x',padx=30,pady=(4,9))
    label(detail,'WHAT THE CONSUMER DOES',10,TEAL,True).grid(row=0,column=0,sticky='w',padx=17,pady=(12,5))
    code='previous = None\nfor edge in edges:\n    if edge != previous:\n        kept.append(edge)\n    previous = edge'
    tk.Label(detail,text=code,bg=PANEL,fg=TEXT,justify='left',font=('Consolas',12)).grid(row=1,column=0,sticky='nw',padx=17,pady=(0,12))
    explanation='The shared equality method now returns NotImplemented.\nThe geometry subclass still negates that sentinel directly.\n\nBroken:     return not self.__eq__(other)\nCorrected:  return not self == other'
    tk.Label(detail,text=explanation,bg=PANEL,fg=MUTED,justify='left',font=('Consolas',11)).grid(row=1,column=1,sticky='nw',padx=(35,17),pady=(0,12))
    trace=tk.StringVar(value='Each run launches Python against three separate source trees; no model is called by this demo.')
    label(root,'',10,MUTED,textvariable=trace,anchor='w',justify='left').pack(fill='x',padx=30,pady=(0,4))
    label(root,'',10,TEAL,textvariable=status,anchor='w').pack(fill='x',padx=30,pady=(0,16))
    events=queue.Queue()
    def draw(record):
        expected=len(record['modes'][0]['kept_indices'])
        for index,data in enumerate(record['modes']):
            canvas,count,compat,first=cards[index]
            canvas.delete('all');w=max(canvas.winfo_width(),300);h=max(canvas.winfo_height(),230)
            points=[p for edge in data['input_edges'] for p in edge]
            xs=[p[0] for p in points];ys=[p[1] for p in points]
            scale=min((w-100)/max(max(xs)-min(xs),1),(h-70)/max(max(ys)-min(ys),1))
            cx=w/2;cy=h/2;mx=(max(xs)+min(xs))/2;my=(max(ys)+min(ys))/2
            xy=lambda p:(cx+(p[0]-mx)*scale,cy-(p[1]-my)*scale)
            kept=set(data['kept_indices'])
            for n,(a,b) in enumerate(data['input_edges']):
                color=TEAL if n in kept else CORAL
                canvas.create_line(*xy(a),*xy(b),fill=color,width=5 if n in kept else 3,dash=() if n in kept else (6,5))
                ax,ay=xy(a);bx,by=xy(b)
                canvas.create_text((ax+bx)/2+10,(ay+by)/2-16,text=str(n+1),fill=color,font=('Segoe UI',11,'bold'))
            for p in {tuple(p) for p in points}:
                px,py=xy(p);canvas.create_oval(px-5,py-5,px+5,py+5,fill=TEXT,outline=PANEL,width=2)
            count.set(f"{len(kept)} / {expected} expected edges retained")
            compat.set('Foreign equality: '+('fixed' if data['foreign_equality']==[True,True] else 'original bug remains'))
            first.set('First edge != None: '+str(data['trace'][0]['unequal']))
        trace.set('Recorded repair trace:  '+ '  |  '.join(f"edge {t['index']+1}: {'keep' if t['kept'] else 'drop'}" for t in record['modes'][1]['trace']))
        status.set('Executed '+record['executed_utc'].replace('T',' ')[:19]+' UTC  |  Python '+record['python']+'  |  Records saved locally')
    def execute(prepare=False):
        run_button.configure(state='disabled');combo.configure(state='disabled');export_button.configure(state='disabled')
        status.set('Preparing pinned source...' if prepare else 'Running the consumer on actual SymPy...')
        selected=scene.get()
        def work():
            try:
                if prepare:engine.prepare()
                events.put(('result',engine.run(selected)))
            except Exception as e:
                events.put(('error',str(e)))
        threading.Thread(target=work,daemon=True).start()
    def export():
        record=result_holder['record']
        if record:
            path=filedialog.asksaveasfilename(parent=root,defaultextension='.json',initialfile='sympy-demo-execution.json',filetypes=[('JSON execution record','*.json')])
            if path:save(Path(path),record);status.set('Execution record exported.')
    run_button=tk.Button(toolbar,text='Run on actual SymPy',command=execute,bg=TEAL,fg=BG,activebackground='#8ef3d7',relief='flat',padx=16,pady=8,font=('Segoe UI',11,'bold'))
    run_button.pack(side='left',padx=14)
    export_button=tk.Button(toolbar,text='Export execution record',command=export,bg=PANEL,fg=TEXT,relief='flat',padx=14,pady=8,font=('Segoe UI',10));export_button.pack(side='right')
    def poll():
        try:
            while True:
                kind,value=events.get_nowait()
                if kind=='result':
                    result_holder['record']=value;draw(value);export_button.configure(state='normal')
                else:status.set('Execution failed: '+value)
                run_button.configure(state='normal');combo.configure(state='readonly')
        except queue.Empty:pass
        root.after(80,poll)
    root.after(100,lambda:execute(True));poll();root.mainloop()

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--headless',action='store_true');ap.add_argument('--scenario',choices=list(SCENES),default='Closed square');ap.add_argument('--work',type=Path);args=ap.parse_args()
    if sys.version_info[:2]!=(3,9):raise SystemExit('Use Python 3.9 with requirements.txt installed.')
    engine=Engine(args.work)
    if args.headless:
        engine.prepare();record=engine.run(args.scenario);print(json.dumps(record,indent=2))
    else:gui(engine)
