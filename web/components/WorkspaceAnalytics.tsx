'use client';

import { useEffect, useRef, useState } from 'react';
import { Info } from 'lucide-react';
import { pct, Prediction, Target } from '@/lib/types';
import InfoPopover from './InfoPopover';
import styles from './WorkspaceAnalytics.module.css';

export default function WorkspaceAnalytics({ prediction, target, dirty }: {
  prediction: Prediction | null; target: Target;
  dirty: boolean;
}) {
  const risk = prediction?.targets[target];
  const content = useRef<HTMLElement>(null);
  const [width, setWidth] = useState(360);
  useEffect(() => {
    const element = content.current;
    if (!element) return;
    const observer = new ResizeObserver(([entry]) => setWidth(entry.contentRect.width));
    observer.observe(element);
    return () => observer.disconnect();
  }, []);
  const ticks = [0, .25, .5, .75, 1];
  const modelX = (probability: number) => 12 + probability * (width - 36);
  if (!risk) return null;

  return <section className={`${styles.panel} ${dirty && prediction ? styles.stale : ''}`} aria-label="Patient prediction variation">
    <div className={styles.content}>
      <section className={styles.patientChart} aria-label="Patient model comparison" ref={content}>
        <div className={styles.chartHeading}><div><h3>Do the models agree?</h3></div>
          <InfoPopover label="About patient model comparison" title="Comparing calibrated predictions" buttonClassName={styles.info} trigger={<Info size={15}/>}>
            <p>Each bar is a calibrated prediction from a different model family for this patient. The checked model supplies the displayed probability and its explanation.</p>
            <p>The spread measures model disagreement. It does not measure how likely this prediction is to be correct.</p>
          </InfoPopover>
        </div>
        {risk ? <>
          <div className={styles.chartMeta}><span>{dirty ? 'Previous prediction' : 'Calibrated probability'}</span><span>{(risk.agreement_spread * 100).toFixed(1)} pp spread</span></div>
          <figure className={styles.figure} aria-label={`${target} patient predictions by model`}>
            <svg viewBox={`0 0 ${width} 170`} className={styles.modelPlot} role="img" aria-label={`${target} calibrated predictions: ${risk.agreement.map(model => `${model.family} ${pct(model.probability)}`).join(', ')}. ${risk.family} is the displayed model.`}>
              {ticks.map(tick => <g key={tick} className={styles.grid}><line x1={modelX(tick)} x2={modelX(tick)} y1="29" y2="135"/><text x={modelX(tick)} y="158" textAnchor="middle">{tick * 100}%</text></g>)}
              {risk.agreement.map((model, index) => {
                const selected = model.family === risk.family;
                const y = 20 + index * 42;
                return <g key={model.family} data-model={model.family} data-probability={model.probability} data-selected={selected} className={selected ? styles.selected : styles.otherModel}>
                  <title>{model.family}: {pct(model.probability)}{selected ? ', displayed model' : ''}</title>
                  <text x="12" y={y} className={styles.modelLabel}>{model.family}{selected ? ' ✓' : ''}</text>
                  <text x={width - 12} y={y} textAnchor="end" className={styles.modelValue}>{pct(model.probability)}</text>
                  <rect x="12" y={y + 10} width={model.probability * (width - 36)} height="13" rx="2"/>
                </g>;
              })}
            </svg>
            
          </figure>
        </> : null}
      </section>

      <section className={styles.variation} aria-label="Variation across fitted models">
        <div className={styles.chartHeading}><h3>Across fitted models</h3>
          <InfoPopover label="About fitted model variation" title="Observed prediction range" buttonClassName={styles.info} trigger={<Info size={15}/>}>
            <p>The same patient is evaluated by {risk.range_models} fitted prediction models. This differs from the three model families shown alongside.</p>
            <p>This is a descriptive range, not a clinical confidence interval or a guarantee of correctness.</p>
          </InfoPopover>
        </div>
        <div className={styles.chartMeta}>{risk.range_models} fitted models</div>
        <div className={styles.rangeValue}>{pct(risk.resampling_range[0])}<span>to</span>{pct(risk.resampling_range[1])}</div>
        <div className={styles.rangeAxis} aria-hidden="true"><i style={{left:`${risk.resampling_range[0]*100}%`,width:`${(risk.resampling_range[1]-risk.resampling_range[0])*100}%`}}/><b style={{left:`${risk.probability*100}%`}}/></div>
        <div className={styles.rangeTicks}><span>0%</span><span>100%</span></div>
        <p className={styles.rangeNote}>Observed range, not a confidence interval.</p>
        <span className={styles.selectedModel}>{risk.family} supplies this explanation</span>
      </section>
    </div>
  </section>;
}
