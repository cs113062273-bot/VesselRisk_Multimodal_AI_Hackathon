const BINARY = new Set(['DM','HTN','Typical Chest Pain','Q Wave','St Elevation','St Depression','Tinversion','Current Smoker','EX-Smoker','FH','Edema']);

export function measurementText(name: string, value: number | string, unit = ''): string {
  if (value === 'Fmale') return 'Female';
  if (value === 'Y' || (BINARY.has(name) && Number(value) === 1)) return 'Yes';
  if (value === 'N' || (BINARY.has(name) && Number(value) === 0)) return 'No';
  if (name === 'Region RWMA') return `Category ${value}`;
  const text = typeof value === 'number' ? String(Number(value.toFixed(2))) : value;
  return `${text}${unit ? ` ${unit}` : ''}`;
}
