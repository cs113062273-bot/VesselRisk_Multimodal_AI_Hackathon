'use client';

import { useEffect, useId, useRef, useState, type ReactNode } from 'react';
import { X } from 'lucide-react';

/** A non-modal explanation, positioned by its toolbar/card without changing layout. */
export default function InfoPopover({ label, title, trigger, children, buttonClassName = '', align = 'end' }: {
  label: string; title: string; trigger: ReactNode; children: ReactNode;
  buttonClassName?: string; align?: 'start' | 'end';
}) {
  const [open, setOpen] = useState(false);
  const id = useId();
  const button = useRef<HTMLButtonElement>(null);
  const panel = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!open) return;
    panel.current?.focus({ preventScroll: true });
    const outside = (event: PointerEvent) => {
      const node = event.target as Node;
      if (!panel.current?.contains(node) && !button.current?.contains(node)) setOpen(false);
    };
    const escape = (event: KeyboardEvent) => {
      if (event.key !== 'Escape') return;
      event.preventDefault();
      event.stopPropagation();
      setOpen(false);
      button.current?.focus({ preventScroll: true });
    };
    document.addEventListener('pointerdown', outside);
    document.addEventListener('keydown', escape, true);
    return () => {
      document.removeEventListener('pointerdown', outside);
      document.removeEventListener('keydown', escape, true);
    };
  }, [open]);
  return <>
    <button ref={button} className={buttonClassName} aria-label={label} title={label} aria-haspopup="dialog" aria-expanded={open} aria-controls={open ? id : undefined} onClick={() => setOpen(!open)}>{trigger}</button>
    {open && <div ref={panel} id={id} className={`context-popover popover-${align}`} role="dialog" aria-label={title} tabIndex={-1}>
      <div className="popover-heading"><h3>{title}</h3><button className="icon-button" aria-label={`Close ${label.toLowerCase()}`} onClick={() => { setOpen(false); button.current?.focus({ preventScroll: true }); }}><X size={16}/></button></div>
      {children}
    </div>}
  </>;
}
