import React, { useEffect, useState } from 'react';
import { MetricScores } from '../types';
import { Shield, GitMerge, Zap, Target } from 'lucide-react';

interface MetricsGridProps { metrics: MetricScores; }

function BarMini({ score, color, bg }: { score: number; color: string; bg: string }) {
  const bars = 20;
  const filled = Math.round((score / 100) * bars);
  const [animated, setAnimated] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setAnimated(true), 80);
    return () => clearTimeout(t);
  }, []);

  return (
    <div className="flex items-end gap-[2px] h-9 rounded-lg overflow-hidden px-1.5 py-1" style={{ background: bg }}>
      {Array.from({ length: bars }).map((_, i) => {
        const isFilled = i < filled;
        const isLast   = i === filled - 1;
        const height   = isFilled
          ? 35 + Math.sin((i / filled) * Math.PI) * 58
          : 12 + (i % 3) * 6;
        return (
          <div
            key={i}
            className="flex-1 rounded-t-[2px] transition-all duration-700"
            style={{
              height: animated ? `${height}%` : '8%',
              transitionDelay: `${i * 28}ms`,
              background: isFilled ? color : 'rgba(0,0,0,0.07)',
              opacity: isFilled ? (isLast ? 1 : 0.75) : 0.3,
              boxShadow: isLast ? `0 0 6px ${color}` : 'none',
            }}
          />
        );
      })}
    </div>
  );
}

export const MetricsGrid: React.FC<MetricsGridProps> = ({ metrics }) => {
  const getRating = (score: number, type: 'coupling' | 'other') => {
    if (type === 'coupling') {
      if (score < 40) return { label: 'Excellent — Low', css: 'badge-emerald' };
      if (score < 65) return { label: 'Moderate',        css: 'badge-gold'    };
      return                { label: 'High Risk',         css: 'badge-coral'   };
    } else {
      if (score >= 80) return { label: 'Highly Optimised', css: 'badge-emerald' };
      if (score >= 60) return { label: 'Satisfactory',     css: 'badge-gold'    };
      return                  { label: 'Review Required',   css: 'badge-coral'   };
    }
  };

  const cards = [
    {
      name: 'Scalability',
      score: metrics.scalability,
      icon: Zap,
      color: '#00d4e8',
      bg: 'rgba(0,212,232,0.07)',
      iconBg: 'var(--cyan-soft)',
      iconColor: 'var(--cyan-deep)',
      desc: 'Capacity to distribute load and auto-scale services independently.',
      rating: getRating(metrics.scalability, 'other'),
    },
    {
      name: 'Coupling Metric',
      score: metrics.coupling,
      icon: GitMerge,
      color: '#ff5c5c',
      bg: 'rgba(255,92,92,0.06)',
      iconBg: 'var(--coral-soft)',
      iconColor: 'var(--coral)',
      desc: 'Inter-service sync dependency level. Lower enables frictionless deployment.',
      rating: getRating(metrics.coupling, 'coupling'),
    },
    {
      name: 'Fault Isolation',
      score: metrics.fault_isolation,
      icon: Shield,
      color: '#f7b731',
      bg: 'rgba(247,183,49,0.08)',
      iconBg: 'var(--gold-soft)',
      iconColor: '#b45309',
      desc: 'Failure containment via circuit-breakers, queues, and async safeguards.',
      rating: getRating(metrics.fault_isolation, 'other'),
    },
    {
      name: 'Cohesion Score',
      score: metrics.cohesion ?? 70,
      icon: Target,
      color: '#7c3aed',
      bg: 'rgba(124,58,237,0.06)',
      iconBg: 'var(--violet-soft)',
      iconColor: 'var(--violet)',
      desc: 'How tightly related functional requirements are within each service boundary.',
      rating: getRating(metrics.cohesion ?? 70, 'other'),
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={card.name}
            className="glass-panel rounded-2xl p-5 relative overflow-hidden stagger-in border-[var(--border-light)] group"
            style={{
              animationDelay: `${idx * 0.09}s`,
            }}
          >
            {/* Subtle top color strip */}
            <div
              className="absolute top-0 left-0 right-0 h-0.5 rounded-t-2xl"
              style={{ background: `linear-gradient(90deg, ${card.color}, transparent)` }}
            />

            {/* Header */}
            <div className="flex items-start justify-between mb-3">
              <div>
                <p className="section-label mb-1">{card.name}</p>
                <h3 className="font-display text-3xl font-bold text-[var(--text-primary)] tracking-tight">
                  {card.score}
                  <span className="text-base font-normal text-[var(--text-muted)] ml-0.5">%</span>
                </h3>
              </div>
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center transition-transform duration-300 group-hover:scale-110"
                style={{ background: card.iconBg, border: `1px solid ${card.color}25` }}
              >
                <Icon size={17} style={{ color: card.iconColor }} />
              </div>
            </div>

            {/* Animated bar chart */}
            <BarMini score={card.score} color={card.color} bg={card.bg} />

            <p className="text-[11px] text-[var(--text-secondary)] mt-3 leading-relaxed">{card.desc}</p>

            <div className="mt-3 pt-3 border-t border-[var(--border-light)] flex items-center justify-between">
              <span className="section-label">Status</span>
              <span className={`text-[9px] px-2.5 py-0.5 rounded-full font-bold ${card.rating.css}`}>
                {card.rating.label}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
};