import type { Features } from './types';

export type InputSource = 'cohort_record' | 'cohort_default' | 'entered' | 'imported' | 'derived';
export type InputSources = Record<string, InputSource>;
export const SOURCE_LABELS: Record<InputSource, string> = {
  cohort_record: 'Cohort record', cohort_default: 'Cohort default', entered: 'User entered',
  imported: 'Imported', derived: 'Calculated from height & weight',
};
export function sourcesFor(features: Features, source: InputSource): InputSources {
  return Object.fromEntries(Object.keys(features).map(name => [name, source]));
}
export function sourceSummary(sources: InputSources): string {
  const labels: Record<InputSource, string> = {
    cohort_record: 'from cohort record', cohort_default: 'cohort defaults', entered: 'user entered',
    imported: 'imported', derived: 'calculated',
  };
  return (Object.keys(labels) as InputSource[]).flatMap(source => {
    const n = Object.values(sources).filter(value => value === source).length;
    return n ? [`${n} ${labels[source]}`] : [];
  }).join(' · ');
}
