import type { Metadata } from 'next';
import '@fontsource/manrope/400.css';
import '@fontsource/manrope/500.css';
import '@fontsource/manrope/600.css';
import '@fontsource/manrope/700.css';
import '@fontsource/manrope/800.css';
import '@fontsource/ibm-plex-mono/400.css';
import '@fontsource/ibm-plex-mono/500.css';
import './globals.css';
import './contrast.css';
import './polish.css';
export const metadata: Metadata = { title: 'VesselRisk · Explainable coronary risk', description: 'Explore leakage-audited CAD and coronary vessel predictions in real 3D anatomy, with calibrated probabilities and transparent validation evidence.' };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
