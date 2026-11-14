import React from 'react';
import { Zap, ShieldCheck, BarChart3, Rocket } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Landing() {
  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-50 px-6 py-20">
      <div className="max-w-7xl mx-auto space-y-32">
        {/* Hero */}
        <section className="text-center space-y-8">
          <h1 className="text-7xl font-extrabold tracking-tighter bg-gradient-to-r from-indigo-400 to-emerald-400 bg-clip-text text-transparent">
            Build Smarter, Faster.
          </h1>
          <p className="text-2xl text-neutral-400 max-w-2xl mx-auto">
            The next-gen platform to accelerate your development workflow. Intelligent insights, seamless deployments.
          </p>
          <Link to="/onboarding" className="inline-block bg-white text-neutral-950 px-8 py-3 rounded-full font-semibold hover:bg-neutral-200 transition">
            Get Started
          </Link>
        </section>

        {/* Stats */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[ 
            { label: 'Deploys/Min', value: '450+' }, 
            { label: 'Dev Velocity', value: '3x' }, 
            { label: 'Reliability', value: '99.99%' } 
          ].map(stat => (
            <div key={stat.label} className="border border-neutral-800 p-8 rounded-2xl bg-neutral-900/50 text-center">
              <div className="text-5xl font-bold tracking-tight text-emerald-400">{stat.value}</div>
              <div className="text-neutral-400 mt-2 font-medium">{stat.label}</div>
            </div>
          ))}
        </section>

        {/* Features */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[ 
            { title: 'Blazing Fast', desc: 'Optimized build pipelines for instant feedback.', icon: Zap }, 
            { title: 'Enterprise Secure', desc: 'Bank-grade protection for your deployments.', icon: ShieldCheck }, 
            { title: 'Insight Driven', desc: 'Real-time analytics to boost performance.', icon: BarChart3 } 
          ].map(feat => (
            <div key={feat.title} className="border border-neutral-800 p-8 rounded-2xl bg-neutral-900/50 hover:border-neutral-700 transition">
              <feat.icon className="w-10 h-10 text-indigo-400 mb-6" />
              <h3 className="text-2xl font-semibold mb-3">{feat.title}</h3>
              <p className="text-neutral-400 leading-relaxed">{feat.desc}</p>
            </div>
          ))}
        </section>
      </div>
    </main>
  );
}
