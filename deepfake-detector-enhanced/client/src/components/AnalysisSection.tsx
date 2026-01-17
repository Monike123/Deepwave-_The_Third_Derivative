import { motion } from 'framer-motion';
import { CheckCircle, AlertCircle, TrendingUp } from 'lucide-react';

/**
 * AnalysisSection Component
 * Design: Futuristic Trust - Glassmorphism
 * 
 * Demonstrates the analysis process with animated elements and 3D perspective effects.
 */
export default function AnalysisSection() {
  const steps = [
    {
      number: '01',
      title: 'Upload Media',
      description: 'Submit your image or video for analysis',
      icon: TrendingUp,
    },
    {
      number: '02',
      title: 'AI Processing',
      description: 'Advanced algorithms analyze the content',
      icon: TrendingUp,
    },
    {
      number: '03',
      title: 'Get Results',
      description: 'Receive detailed authenticity report',
      icon: CheckCircle,
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: {
      opacity: 1,
      x: 0,
      transition: { duration: 0.6 } as any,
    },
  };

  return (
    <section className="relative py-20 md:py-32 overflow-hidden">
      {/* Background elements */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-secondary/5 to-transparent pointer-events-none" />

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
            <span className="text-sm font-semibold text-primary">HOW IT WORKS</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
            Simple, Fast,
            <br />
            <span className="neon-glow">Reliable</span>
          </h2>
        </motion.div>

        {/* Process steps */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16"
        >
          {steps.map((step, idx) => {
            const Icon = step.icon;
            return (
              <motion.div
                key={idx}
                variants={itemVariants}
                whileHover={{ y: -8 } as any}
                className="relative"
              >
                {/* Connection line */}
                {idx < steps.length - 1 && (
                  <div className="hidden md:block absolute top-20 left-1/2 w-full h-1 bg-gradient-to-r from-primary/50 to-transparent" />
                )}

                {/* Card */}
                <div className="glass-card p-8 rounded-xl relative z-10">
                  {/* Step number */}
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 20, repeat: Infinity, ease: "linear" } as any}
                    className="absolute -top-4 -right-4 w-16 h-16 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-2xl font-bold text-primary-foreground"
                  >
                    {step.number}
                  </motion.div>

                  {/* Icon */}
                  <motion.div
                    whileHover={{ scale: 1.2, rotate: 360 }}
                    transition={{ duration: 0.6 } as any}
                    className="w-12 h-12 rounded-lg bg-primary/20 flex items-center justify-center mb-4"
                  >
                    <Icon className="w-6 h-6 text-primary" />
                  </motion.div>

                  {/* Title */}
                  <h3 className="text-xl font-bold text-foreground mb-2">
                    {step.title}
                  </h3>

                  {/* Description */}
                  <p className="text-muted-foreground">
                    {step.description}
                  </p>
                </div>
              </motion.div>
            );
          })}
        </motion.div>

        {/* Demo section */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8 } as any}
          viewport={{ once: true }}
          className="glass-card p-8 md:p-12 rounded-2xl relative overflow-hidden"
        >
          {/* Animated background */}
          <motion.div
            animate={{
              backgroundPosition: ['0% 0%', '100% 100%'],
            }}
            transition={{ duration: 8, repeat: Infinity } as any}
            className="absolute inset-0 opacity-30 pointer-events-none"
            style={{
              background:
                'linear-gradient(45deg, #00d9ff, #a855f7, #00d9ff)',
              backgroundSize: '200% 200%',
            }}
          />

          <div className="relative z-10">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
              {/* Left side - Result example */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.2 } as any}
                viewport={{ once: true }}
              >
                <h3 className="text-2xl font-bold text-foreground mb-4">
                  Analysis Result
                </h3>
                <div className="space-y-4">
                  <motion.div
                    whileHover={{ x: 8 }}
                    className="flex items-center gap-3 p-4 bg-success/10 rounded-lg border border-success/30"
                  >
                    <CheckCircle className="w-5 h-5 text-success flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-foreground">Authentic</p>
                      <p className="text-sm text-muted-foreground">
                        Confidence: 99.2%
                      </p>
                    </div>
                  </motion.div>

                  <motion.div
                    whileHover={{ x: 8 }}
                    transition={{ delay: 0.1 } as any}
                    className="flex items-center gap-3 p-4 bg-warning/10 rounded-lg border border-warning/30"
                  >
                    <AlertCircle className="w-5 h-5 text-warning flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-foreground">Suspicious</p>
                      <p className="text-sm text-muted-foreground">
                        Confidence: 87.5%
                      </p>
                    </div>
                  </motion.div>
                </div>
              </motion.div>

              {/* Right side - Stats */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.2 } as any}
                viewport={{ once: true }}
                className="grid grid-cols-2 gap-4"
              >
                {[
                  { label: 'Detection Speed', value: '0.8s' },
                  { label: 'Accuracy', value: '99.8%' },
                  { label: 'Files Processed', value: '10M+' },
                  { label: 'Uptime', value: '99.99%' },
                ].map((stat, idx) => (
                  <motion.div
                    key={idx}
                    whileHover={{ scale: 1.05 }}
                    className="p-4 bg-primary/10 rounded-lg border border-primary/20 text-center"
                  >
                    <motion.div
                      initial={{ opacity: 0, scale: 0 }}
                      whileInView={{ opacity: 1, scale: 1 }}
                      transition={{
                        duration: 0.6,
                        delay: idx * 0.1,
                      } as any}
                      viewport={{ once: true }}
                    >
                      <p className="text-2xl font-bold text-primary mb-1">
                        {stat.value}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {stat.label}
                      </p>
                    </motion.div>
                  </motion.div>
                ))}
              </motion.div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
