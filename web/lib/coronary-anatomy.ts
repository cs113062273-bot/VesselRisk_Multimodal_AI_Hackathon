import type { Vessel } from './types';

// General reference anatomy, independent of patient inputs and model output.
// Summarized from Cleveland Clinic's coronary artery patient education pages.
export const ARTERY_GUIDE: Record<Vessel, { course: string; supply: string; source: string }> = {
  LAD: {
    course: 'Down the front toward the heart’s tip',
    supply: 'Front of the left ventricle and much of the septum',
    source: 'https://my.clevelandclinic.org/health/body/23985-left-anterior-descending-artery',
  },
  LCX: {
    course: 'Around the left side toward the back',
    supply: 'Side and back of the left ventricle',
    source: 'https://my.clevelandclinic.org/health/body/23926-circumflex-artery',
  },
  RCA: {
    course: 'Around the right side of the heart',
    supply: 'Right atrium, right ventricle and often the lower heart',
    source: 'https://my.clevelandclinic.org/health/body/21704-heart',
  },
};
