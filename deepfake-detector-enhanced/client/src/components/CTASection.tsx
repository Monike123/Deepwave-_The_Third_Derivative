import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { ArrowRight, Zap } from 'lucide-react';

/**
 * CTASection Component
 * Design: Futuristic Trust - Glassmorphism
 * 
 * Final call-to-action section with animated elements and premium styling.
 */
export default function CTASection() {
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

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6 } as any,
    },
  };

  return (
    <section className="relative py-20 md:py-32 overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-primary/10 via-transparent to-secondary/10 pointer-events-none" />

      {/* Animated background orbs */}
      <motion.div
        animate={{ y: [0, 30, 0] }}
        transition={{ duration: 8, repeat: Infinity } as any}
        className="absolute top-10 right-20 w-64 h-64 rounded-full blur-3xl opacity-20 bg-gradient-to-br from-primary to-secondary pointer-events-none"
      />
      <motion.div
        animate={{ y: [0, -30, 0] }}
        transition={{ duration: 10, repeat: Infinity } as any}
        className="absolute bottom-10 left-20 w-72 h-72 rounded-full blur-3xl opacity-15 bg-gradient-to-br from-secondary to-primary pointer-events-none"
      />

      <motion.div
        variants={containerVariants}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        className="container relative z-10 max-w-3xl mx-auto text-center"
      >
        {/* Badge */}
        <motion.div variants={itemVariants} className="flex justify-center mb-8">
          <div className="glass-card px-4 py-2 flex items-center gap-2">
            <Zap className="w-4 h-4 text-primary" />
            <span className="text-sm font-medium text-foreground">
              Ready to Get Started?
            </span>
          </div>
        </motion.div>

        {/* Main heading */}
        <motion.h2
          variants={itemVariants}
          className="text-4xl md:text-6xl font-bold mb-6 leading-tight"
        >
          <span className="text-foreground">Protect Your</span>
          <br />
          <span className="neon-glow">Digital Assets</span>
        </motion.h2>

        {/* Description */}
        <motion.p
          variants={itemVariants}
          className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto"
        >
          Join thousands of organizations using our AI-powered deepfake detection
          to protect against media manipulation and ensure content authenticity.
        </motion.p>

        {/* CTA Buttons */}
        <motion.div
          variants={itemVariants}
          className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12"
        >
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Button
              size="lg"
              className="bg-gradient-to-r from-primary to-secondary hover:shadow-lg hover:shadow-primary/50 text-primary-foreground px-8 py-6 text-lg font-semibold rounded-lg group"
            >
              Start Free Trial
              <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
            </Button>
          </motion.div>
          <Button
            size="lg"
            variant="outline"
            className="border-primary text-primary hover:bg-primary/10 px-8 py-6 text-lg font-semibold rounded-lg"
          >
            View Pricing
          </Button>
        </motion.div>

        {/* Trust indicators */}
        <motion.div
          variants={itemVariants}
          className="glass-card p-6 rounded-xl inline-block"
        >
          <p className="text-sm text-muted-foreground mb-3">
            Trusted by industry leaders
          </p>
          <div className="flex items-center justify-center gap-6">
            {['Enterprise', 'Verified', 'Secure'].map((badge, idx) => (
              <motion.div
                key={idx}
                whileHover={{ scale: 1.1 }}
                className="px-3 py-1 bg-primary/10 rounded-full text-xs font-semibold text-primary"
              >
                ✓ {badge}
              </motion.div>
            ))}
          </div>
        </motion.div>
      </motion.div>
    </section>
  );
}
