import { motion } from 'framer-motion';
import FeatureCard from './FeatureCard';
import {
  Zap,
  Brain,
  Shield,
  BarChart3,
  Lock,
  Workflow,
} from 'lucide-react';

/**
 * FeaturesSection Component
 * Design: Futuristic Trust - Glassmorphism
 * 
 * Showcases key features with staggered animations and glassmorphic cards.
 */
const features = [
  {
    icon: Zap,
    title: 'Lightning Fast',
    description: 'Analyze media in under 1 second with our optimized AI engine.',
  },
  {
    icon: Brain,
    title: 'Advanced AI',
    description: 'Deep learning models trained on millions of authentic and fake media.',
  },
  {
    icon: Shield,
    title: 'Highly Accurate',
    description: '99.8% detection accuracy with minimal false positives.',
  },
  {
    icon: BarChart3,
    title: 'Detailed Reports',
    description: 'Get comprehensive analysis reports with confidence scores.',
  },
  {
    icon: Lock,
    title: 'Privacy First',
    description: 'Your data is encrypted and never stored or shared.',
  },
  {
    icon: Workflow,
    title: 'Easy Integration',
    description: 'Simple API for seamless integration into your workflow.',
  },
];

export default function FeaturesSection() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2,
      },
    },
  };

  return (
    <section className="relative py-20 md:py-32 overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-primary/5 to-transparent pointer-events-none" />

      <div className="container relative z-10">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 } as any}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <div className="inline-block glass-card px-4 py-2 mb-6">
            <span className="text-sm font-semibold text-primary">KEY FEATURES</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
            Powerful Detection
            <br />
            <span className="neon-glow">Capabilities</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Our advanced AI system provides comprehensive deepfake detection with industry-leading accuracy.
          </p>
        </motion.div>

        {/* Features grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {features.map((feature, idx) => (
            <FeatureCard
              key={idx}
              icon={feature.icon}
              title={feature.title}
              description={feature.description}
              index={idx}
            />
          ))}
        </motion.div>
      </div>
    </section>
  );
}
