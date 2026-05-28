import React from 'react';
import { MetricScores } from '../types';
import { Shield, GitMerge, Activity, Zap } from 'lucide-react';

interface MetricsGridProps {
  metrics: MetricScores;
}

export const MetricsGrid: React.FC<MetricsGridProps> = ({ metrics }) => {
  const getRating = (score: number, type: 'coupling' | 'other') => {
    if (type === 'coupling') {
      if (score < 40) return { label: 'Excellent (Low)', color: 'text-emerald-400', bg: 'bg-emerald-500/10' };
      if (score < 65) return { label: 'Moderate', color: 'text-yellow-400', bg: 'bg-yellow-500/10' };
      return { label: 'High Coupling (Risk)', color: 'text-rose-400', bg: 'bg-rose-500/10' };
    } else {
      if (score >= 80) return { label: 'Highly Optimized', color: 'text-emerald-400', bg: 'bg-emerald-500/10' };
      if (score >= 60) return { label: 'Satisfactory', color: 'text-yellow-400', bg: 'bg-yellow-500/10' };
      return { label: 'Degraded (Review Required)', color: 'text-rose-400', bg: 'bg-rose-500/10' };
    }
  };

  const cards = [
    {
      name: 'Scalability Score',
      score: metrics.scalability,
      icon: Zap,
      color: 'from-amber-500 to-orange-500',
      textColor: 'text-amber-400',
      desc: 'Capacity of system to distribute transaction load & auto-scale services independently.',
      rating: getRating(metrics.scalability, 'other')
    },
    {
      name: 'Coupling Metric',
      score: metrics.coupling,
      icon: GitMerge,
      color: 'from-purple-500 to-indigo-500',
      textColor: 'text-purple-400',
      desc: 'Level of inter-service sync calls. Low coupling enables friction-free deployability.',
      rating: getRating(metrics.coupling, 'coupling')
    },
    {
      name: 'Maintainability Index',
      score: metrics.maintainability,
      icon: Activity,
      color: 'from-emerald-500 to-teal-500',
      textColor: 'text-emerald-400',
      desc: 'Code complexity estimation, domain isolation boundary clarity, and database autonomy.',
      rating: getRating(metrics.maintainability, 'other')
    },
    {
      name: 'Fault Isolation',
      score: metrics.fault_isolation,
      icon: Shield,
      color: 'from-rose-500 to-pink-500',
      textColor: 'text-rose-400',
      desc: 'Containment level of failures using circuit-breakers, queues, and async boundary safeguards.',
      rating: getRating(metrics.fault_isolation, 'other')
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <div key={card.name} className="glass-panel p-5 rounded-2xl relative overflow-hidden transition-all duration-300 hover:border-slate-700">
            {/* Background Glow */}
            <div className={`absolute top-0 right-0 w-24 h-24 bg-gradient-to-br ${card.color} opacity-5 blur-2xl rounded-full`} />
            
            <div className="flex items-start justify-between">
              <div>
                <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">{card.name}</span>
                <h3 className="text-3xl font-extrabold mt-1 tracking-tight text-white">{card.score}%</h3>
              </div>
              <div className={`p-2.5 rounded-xl bg-slate-800/80 ${card.textColor} border border-slate-700/50`}>
                <Icon size={20} />
              </div>
            </div>

            {/* Meter Bar */}
            <div className="w-full bg-slate-800/85 h-2 rounded-full mt-4 overflow-hidden border border-slate-700/30">
              <div 
                className={`h-full bg-gradient-to-r ${card.color} rounded-full transition-all duration-1000`}
                style={{ width: `${card.score}%` }}
              />
            </div>

            <p className="text-xs text-gray-400/90 mt-3.5 leading-relaxed font-light">{card.desc}</p>
            
            <div className="mt-3.5 pt-3.5 border-t border-slate-800/80 flex items-center justify-between">
              <span className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold">Status Assessment</span>
              <span className={`text-xs px-2.5 py-0.5 rounded-full font-medium ${card.rating.color} ${card.rating.bg}`}>
                {card.rating.label}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
};
