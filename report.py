"""Build the report from all preserved primary trials and adjudicated scores."""
from collections import Counter
from datetime import datetime,timedelta
from pathlib import Path
import json
import statistics
from common import HERE,tasks,save

def main():
    protocol=json.loads((HERE/'results/primary/PROTOCOL.json').read_text(encoding='utf-8'))
    records=[]; starts=[]; ends=[]; usage=Counter()
    for path in sorted((HERE/'results/primary').glob('*/result.json')):
        record=json.loads(path.read_text(encoding='utf-8'))
        record['artifact']=path.parent.name
        settings=json.loads((path.parent/'settings.json').read_text(encoding='utf-8'))
        start=datetime.fromisoformat(settings['utc_start']);starts.append(start)
        ends.append(start+timedelta(seconds=record['agent_seconds']))
        for item in record['usage']:
            usage.update(item)
        record['frozen_complete_pass']=record['complete_pass']
        record['adjudicated_complete_pass']=record['complete_pass']
        if record['case']=='05_set_equivalence':
            correction=json.loads((HERE/'validation/adjudication'/record['artifact']/'result.json').read_text(encoding='utf-8'))
            record['adjudicated_complete_pass']=correction['adjudicated_complete_pass'] and record['cli_exit_code']==0
            record['adjudicated_checks']=correction['grade']
        if record['category'] in ['infrastructure_failure','time_budget_exhausted']:
            record['reported_category']=record['category']
            record['adjudicated_complete_pass']=False
        else:
            record['reported_category']='complete_repair' if record['adjudicated_complete_pass'] else 'semantic_or_regression_failure'
        records.append(record)
    assert len(records)==protocol['planned_trials']==42
    models={}
    for model in protocol['models']:
        rows=[r for r in records if r['model']==model]
        counts=Counter(r['reported_category'] for r in rows)
        cases={t['id']:{'passed':sum(r['adjudicated_complete_pass'] for r in rows if r['case']==t['id']),
                       'frozen_passed':sum(r['frozen_complete_pass'] for r in rows if r['case']==t['id']),
                       'attempts':sum(r['case']==t['id'] for r in rows)} for t in tasks()}
        substantive=counts['complete_repair']+counts['semantic_or_regression_failure']
        models[model]={'attempts':len(rows),'passed':counts['complete_repair'],'frozen_passed':sum(r['frozen_complete_pass'] for r in rows),
                       'substantive_attempts':substantive,'categories':dict(counts),'cases':cases,
                       'all_three_pass_cases':sum(c['passed']==3 for c in cases.values())}
    durations=[r['agent_seconds'] for r in records]
    report={'protocol':protocol,'trials':len(records),'models':models,'categories':dict(Counter(r['reported_category'] for r in records)),
            'frozen_passes':sum(r['frozen_complete_pass'] for r in records),'adjudicated_passes':sum(r['adjudicated_complete_pass'] for r in records),
            'agent_runtime_seconds':{'sum':round(sum(durations),2),'median':round(statistics.median(durations),2),'min':min(durations),'max':max(durations),
              'first_start_to_last_agent_exit':round((max(ends)-min(starts)).total_seconds(),2)},
            'first_agent_start_utc':min(starts).isoformat(),'last_agent_exit_utc':max(ends).isoformat(),
            'usage':dict(usage),'command_count':sum(r['command_count'] for r in records),'records':records}
    save(HERE/'results/report.json',report)
    lines=['# Measured results','','The expanded primary study contains all 42 planned attempts. No substantive attempt was replaced. Final task scores use the disclosed case05 correction; frozen scores remain available.','',
           '| Case | gpt-6-astra | gpt-6.1-sol |','|---|---:|---:|']
    for t in tasks():
        vals=[models[m]['cases'][t['id']]['passed'] for m in protocol['models']]
        lines.append(f"| {t['id']} — {t['title']} | {vals[0]} / 3 | {vals[1]} / 3 |")
    lines+=['','| Model / medium reasoning | Corrected complete repairs | Frozen complete repairs | All three correct |','|---|---:|---:|---:|']
    for m,r in models.items():
        lines.append(f"| `{m}` | {r['passed']} / {r['attempts']} | {r['frozen_passed']} / {r['attempts']} | {r['all_three_pass_cases']} / 7 cases |")
    lines+=['',f"Overall: **{report['adjudicated_passes']} / 42 complete repairs** after adjudication; **{report['frozen_passes']} / 42** under the original frozen grading.",
            '',f"Outcome categories: `{json.dumps(report['categories'],sort_keys=True)}`.",
            '', 'The primary score is the complete-repair fraction across substantive attempts. Infrastructure and time-budget outcomes, if present above, are excluded from that semantic denominator and remain visible as attempts. This task-level score requires every required, preservation, and regression check to pass. Assertion counts are not independent samples.',
            '', '## Runtime and access', '',
            f"Generation ran from {report['first_agent_start_utc']} to approximately {report['last_agent_exit_utc']} (agent start/exit span). Median agent time: {statistics.median(durations):.1f} seconds; range {min(durations):.1f}–{max(durations):.1f} seconds. Summed agent time: {sum(durations)/60:.1f} minutes, with three concurrent workers. The elapsed agent span was {(max(ends)-min(starts)).total_seconds()/60:.1f} minutes; extraction and grading add overhead.",
            '',f"Recorded CLI usage totals: `{json.dumps(dict(usage),sort_keys=True)}`. Cached input tokens, when present, are a subset of input tokens and must not be added again. Completed command executions: {report['command_count']}.",
            '', 'Access was through an authenticated local subscription. Incremental dollar cost was unavailable; no cost estimate is invented. Replaying saved patches or running the demo makes zero model calls. Allow roughly 5–15 minutes for full replay on a comparable machine, plus first-time environment installation; use the delivered clean-replay timing for the observed host.',
            '', '## Scope and accounting', '',
            'Each trial used a new repository and unique ephemeral session. Exact requested IDs, medium reasoning, provider-default unspecified temperature, 1,200-second budget, timestamps, prompts, raw events, patches, commands, and usage are retained. Immutable backend revisions and seeds were not exposed.',
            '', 'The earlier two discovery attempts and six fixed confirmations are separate: all eight showed the selected equality/geometry regression. They are not part of this 42-attempt score. Cases share one library; cases01/02 share a base revision and case03 derives from case01. There are seven scoped repair tasks, not seven independent domains or seven proven failure mechanisms.',
            '', 'The case05 correction accepts both outcomes explicitly permitted by the prompt. See `validation/ADJUDICATION.md`, unchanged raw `results/primary/`, and independently rerun `validation/adjudication/`. All passing tasks and corrections are retained.',
            '', 'See `FAILURE_ANALYSIS.md` for failure traces and practical interpretation. These small targeted samples establish observed repeatability in this setup, not a general error rate or model ranking.']
    if len({m['passed'] for m in models.values()})==1:
        lines += ['', 'The two models have the same aggregate complete-repair score in this study. No between-model performance separation is claimed.']
    (HERE/'RESULTS.md').write_bytes(('\n'.join(lines)+'\n').encode())
    analysis=['# Failure analysis','','The key question is whether a repair preserves the contracts used outside the focused reproducer. A complete task pass requires the requested fix and relevant preserved behavior.','']
    for task in tasks():
        rows=[r for r in records if r['case']==task['id']]
        failures=[r for r in rows if r['reported_category']=='semantic_or_regression_failure']
        analysis += [f"## {task['id']} — {task['title']}",'',f"Complete repairs: {sum(r['adjudicated_complete_pass'] for r in rows)} / {len(rows)}. Substantive failures: {len(failures)}.",'']
        if not failures:
            analysis.append('No model failure is claimed for this task in this study. Successful repairs are retained as positive evidence and a boundary on the central finding.')
        for r in failures:
            g=r.get('adjudicated_checks',r['checks'])
            names=[c['name'] for c in g['failed_checks']]
            analysis += [f"- `{r['artifact']}`: requested behavior {'passes' if g['required_pass'] else 'fails'}; preservation {'passes' if g['preservation_pass'] else 'fails'}. Failed behavior checks: {', '.join(names) or 'none; inspect regression failure below'}. Frozen suite: {g['regression']['summary']}",
                         f"  Evidence: [prompt](results/primary/{r['artifact']}/prompt.txt), [patch](results/primary/{r['artifact']}/submission.patch), [final](results/primary/{r['artifact']}/final.txt), [events](results/primary/{r['artifact']}/events.jsonl), [oracle](results/primary/{r['artifact']}/checks/oracle.json)."]
        if task['id'].startswith('01'):
            analysis+=['','Mechanism: shared core equality returns NotImplemented for an unsupported operand, but GeometryEntity.__ne__ directly negates self.__eq__. The geometry result becomes false for inequality with None or an unrelated object. Lines, rays, segments, and the deduplication consumer expose one underlying contract-propagation error. The consumer can silently lose its first edge even after the reported integration bug and original focused tests pass. The evaluator one-line rescue and local demo establish causality. No deletion or weakening of tests is needed for this failure.']
            analysis+=['','A useful trace is Sol repetition 3: its patch also repairs the direct equality callback used by `.has()`, and its final report discusses that additional consumer. It still leaves the geometry caller unchanged. This narrows the interpretation to incomplete propagation of the contract; the record does not support saying the agent never considered downstream effects. Its independently restored original focused suite passes with 95 passed and one expected failure.']
        if task['id'].startswith('03'):
            analysis+=['','This prompt exposes the downstream symptom directly and explicitly requires preserving the foreign-object fix. Its result measures diagnosis with a visible regression, which differs from anticipating that regression while fixing the original bug. It does not establish a universally effective prompting intervention.']
        if task['id'].startswith('05'):
            analysis+=['','The raw frozen suite had an overly strict expectation for a permitted stale-test change. Every candidate was rechecked after a documented one-assertion correction. Such evaluator false negatives are not model-failure evidence.']
        analysis+=['']
    analysis+=['## Limits and insight','','A local reproducer plus a green focused suite is incomplete evidence when a patch changes a shared API. The demonstrated failure is a nonlocal regression in real historical software, not malicious intent, current-production impact, or a general inability to debug. The authored consumer makes the consequence inspectable. Reference repairs, accepted alternatives, and successful model cases establish that correct behavior is attainable.','',
              'Public historical tasks may be contaminated by training data. Source versions are intentionally old. Tasks were selected after exploratory work and include correlated derivatives. Three sessions per model/case are a small targeted sample. The deterministic grader is finite and can miss untested behavior; preflight controls and mathematical checks reduce but do not eliminate evaluator error.']
    (HERE/'FAILURE_ANALYSIS.md').write_bytes(('\n'.join(analysis)+'\n').encode())
    print(json.dumps({'trials':len(records),'categories':report['categories'],'models':models},indent=2))

if __name__=='__main__':main()
