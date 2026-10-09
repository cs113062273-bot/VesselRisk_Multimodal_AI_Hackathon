import { pct, Reliability, score, Target } from '@/lib/types';

export default function ReliabilityDetails({ evidence, target, mode }: {
  evidence?: Reliability; target: Target; mode: 'calibration' | 'explanation';
}) {
  if (!evidence) return null;
  const result = evidence.targets[target];
  if (mode === 'explanation') return <details className="evidence-details">
    <summary>Local explanation stability · {result.local_shap.n} held-out profiles</summary>
    <p>{evidence.protocol.selection} {evidence.protocol.stability}</p>
    <div className="table-scroll"><table><thead><tr><th>Explanation comparison</th><th>Top-5 overlap · mean / minimum</th><th>Same direction · mean</th><th>Largest contribution change</th></tr></thead>
      <tbody>{result.local_shap.summary.map(row => <tr key={row.name}><td>{row.name}</td><td>{pct(row.mean_top5_overlap)} / {pct(row.min_top5_overlap)}</td><td>{pct(row.mean_sign_agreement)}</td><td>{row.max_change_pp.toFixed(1)} pp</td></tr>)}</tbody>
    </table></div>
    <p className="fine-print">Overlap measures how many of the five leading factors remain in the top five. Direction compares the original five factors. Background changes also change the reference probability. These four profiles do not establish stability for every patient.</p>
  </details>;
  const probability = result.probability;
  return <details className="evidence-details">
    <summary>Calibration evidence · patient counts, intervals & baseline</summary>
    <p>{evidence.protocol.calibration}</p>
    <div className="table-scroll"><table><thead><tr><th>Group prediction</th><th>Positive / patients</th><th>Observed fraction</th><th>Descriptive 95% interval</th></tr></thead>
      <tbody>{probability.bins.map((bin, index) => <tr key={index}><td>{pct(bin.x)}</td><td>{bin.positive} / {bin.n}</td><td>{pct(bin.y)}</td><td>{pct(bin.low)}–{pct(bin.high)}</td></tr>)}</tbody>
    </table></div>
    <p>Brier: <strong>{score(probability.brier)}</strong> · conditional 95% interval {probability.brier_ci.map(score).join('–')}. Training-prevalence baseline: <strong>{score(probability.training_prevalence_brier)}</strong> · relative error reduction: <strong>{pct(probability.brier_skill)}</strong>.</p>
    <p className="fine-print">The baseline uses only each fold&apos;s training-label prevalence, then averages the two held-out probabilities per patient. Brier difference from baseline: {probability.brier_delta_ci.map(score).join(' to ')} (conditional 95% interval; negative favors the model). {evidence.protocol.bootstrap}</p>
    <h3>Each repeat before averaging</h3>
    <table><thead><tr><th>Evaluation</th><th>ROC-AUC</th><th>Recall at 0.50</th><th>Brier</th></tr></thead><tbody>{probability.repeat_metrics.map((metric, index) => <tr key={index}><td>Repeat {index + 1}</td><td>{score(metric.roc_auc)}</td><td>{pct(metric.recall)}</td><td>{score(metric.brier)}</td></tr>)}</tbody></table>
    <p className="fine-print">Each repeat uses one held-out model per patient. The headline averages two predictions; neither evaluates the final full-cohort model on new external patients.</p>
  </details>;
}
