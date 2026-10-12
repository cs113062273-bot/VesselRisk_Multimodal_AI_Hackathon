import type { CSSProperties } from 'react';
import type { Target } from './types';

// Target identity matches the report. Probability and SHAP direction use
// their own semantic colors; these colors do not encode disease likelihood.
export const TARGET_COLORS: Record<Target, { color: string; ink: string; tint: string }> = {
  CAD: { color: '#168e8b', ink: '#0d7775', tint: '#edf7f6' },
  LAD: { color: '#4f8bba', ink: '#356c96', tint: '#eef4f9' },
  LCX: { color: '#c59841', ink: '#8a651f', tint: '#faf5e9' },
  RCA: { color: '#cf7874', ink: '#a94c49', tint: '#fcf0ee' },
};

export function targetColorStyle(target: Target): CSSProperties {
  const { color, ink, tint } = TARGET_COLORS[target];
  return { '--target-color': color, '--target-ink': ink, '--target-tint': tint } as CSSProperties;
}
