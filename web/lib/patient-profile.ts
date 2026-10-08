import type { Features } from './types';

export function calculateBmi(features: Features): number | '' {
  const height = Number(features.Length);
  const weight = Number(features.Weight);
  if (!Number.isFinite(height) || height <= 0 || !Number.isFinite(weight) || weight <= 0) return '';
  const bmi = weight / (height / 100) ** 2;
  return Number.isFinite(bmi) && bmi > 0 ? bmi : '';
}

export function withCalculatedBmi(features: Features): Features {
  return { ...features, BMI: calculateBmi(features) };
}
