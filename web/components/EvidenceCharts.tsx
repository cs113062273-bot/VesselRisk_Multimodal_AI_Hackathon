'use client';

import { useState } from 'react';
import { Evidence, pct, score, Target, TARGETS, VesselRefinement } from '@/lib/types';
import { targetColorStyle } from '@/lib/target-colors';

export function TargetOverview({ evidence, target, onTarget }: {
  evidence: Evidence; target: Target; onTarget: (target: Target) => void;
}) {
  const [metric, setMetric] = useState<'auc' | 'recall'>('auc');
  const auc = metric === 'auc';
  return <section className="target-overview" aria-labelledby="overview-title">
    <div className="evidence-chart-heading">
      <div><h2 id="overview-title">Four targets, one view.</h2><p>{auc ? 'How well do the models separate positive from negative cases?' : 'Of patients with a positive recorded outcome, how many were detected?'}</p></div>
      <div className="chart-metric-switch" role="group" aria-label="Overview metric">
        <button aria-pressed={auc} onClick={() => setMetric('auc')}>ROC-AUC</button>
        <button aria-pressed={!auc} onClick={() => setMetric('recall')}>Recall at 0.50</button>
      </div>
    </div>
    <div className="overview-axis" aria-hidden="true"><span/>
      <div>{[0, .25, .5, .75, 1].map(t => <span key={t} style={{ left: `${t * 100}%` }}>{auc ? t.toFixed(2) : `${t * 100}%`}</span>)}</div><span/>
    </div>
    {TARGETS.map(t => {
      const ev = evidence.targets[t];
      const value = auc ? ev.metrics.roc_auc : ev.metrics.recall;
      const [low, high] = ev.auc_ci;
      return <button key={t} className="overview-row" style={targetColorStyle(t)} aria-label={`Inspect ${t} validation`} aria-describedby={`overview-value-${t}`} aria-pressed={target === t} onClick={() => onTarget(t)}>
        <strong>{t}</strong>
        <span className={`overview-track ${auc ? 'auc-track' : 'recall-track'}`} aria-hidden="true">
          {auc ? <><i className="chance-line"/><i className="overview-interval" style={{ left: `${low * 100}%`, width: `${(high - low) * 100}%` }}/><i className="overview-dot" style={{ left: `${value * 100}%` }}/></> : <i className="overview-fill" style={{ width: `${value * 100}%` }}/>}</span>
        <span className="overview-value" id={`overview-value-${t}`}><b>{auc ? score(value) : pct(value)}</b><small>{auc ? `${score(low)}–${score(high)}` : `${ev.metrics.confusion_matrix[1][1]} / ${ev.positive} positives`}</small></span>
      </button>;
    })}
    <p className="chart-caption">{auc ? 'Dot: ROC-AUC · whisker: 95% conditional bootstrap interval · dashed line: chance (0.50). Higher is better; AUC is not percent correct.' : 'Detected positives / all recorded positives. The fixed 0.50 research cutoff is the same for all four targets.'} Select a row to inspect its evidence.</p>
  </section>;
}

export function ThresholdTradeoff({ refinement, target, positive, negative }: {
  refinement: VesselRefinement; target: Target; positive: number; negative: number;
}) {
  // Compare operating points within the same frozen policy, never across model searches.
  const fixed = refinement.variants.find(v => v.policy === 'Frozen baseline' && v.operating_point === '0.50');
  const selected = refinement.variants.find(v => v.policy === 'Frozen baseline' && v.operating_point === 'Nested F1');
  if (!fixed || !selected) return null;
  const f = fixed.metrics.confusion_matrix, s = selected.metrics.confusion_matrix;
  const rows = [
    { key: 'misses', title: 'Missed positives', denominator: positive, base: f[1][0], research: s[1][0], population: 'recorded positives' },
    { key: 'alarms', title: 'False positives', denominator: negative, base: f[0][1], research: s[0][1], population: 'recorded negatives' },
  ];
  // Both panels share one zero-based scale, rounded above the largest count.
  const max = Math.max(20, Math.ceil(Math.max(...rows.flatMap(r => [r.base, r.research])) / 20) * 20);
  const change = (before: number, after: number) => `${Math.abs(after - before)} ${after < before ? 'fewer' : after > before ? 'more' : 'change in'}`;
  return <div className="threshold-tradeoff" aria-label={`${target} threshold tradeoff`}>
    <div className="tradeoff-headline"><strong>{change(f[1][0], s[1][0])} missed positives</strong><span>with</span><strong>{change(f[0][1], s[0][1])} false positives</strong></div>
    <div className="tradeoff-panels">{rows.map(row => <section className="tradeoff-panel" key={row.key} aria-label={row.title}>
      <h4>{row.title}</h4><p>Among {row.denominator} {row.population}</p>
      {[{ label: 'Fixed 0.50', count: row.base, mode: 'fixed' }, { label: 'Training-selected F1', count: row.research, mode: 'selected' }].map(bar => <div className={`tradeoff-row ${bar.mode}`} key={bar.mode}>
        <span>{bar.label}</span><div className="tradeoff-track" aria-hidden="true"><i style={{ width: `${bar.count / max * 100}%` }}/></div><b>{bar.count}</b>
      </div>)}
      <div className="tradeoff-axis" aria-hidden="true"><span/><div><span>0</span><span>{max / 2}</span><span>{max}</span></div><span/></div>
    </section>)}</div>
    <p className="chart-caption">Bars count patients on the same scale. Same models and probabilities; only the decision thresholds change. Recall: {pct(fixed.metrics.recall)} → {pct(selected.metrics.recall)}. Training-fold cutoffs: {selected.fold_threshold_min.toFixed(2)}–{selected.fold_threshold_max.toFixed(2)}. The workspace keeps 0.50.</p>
  </div>;
}
