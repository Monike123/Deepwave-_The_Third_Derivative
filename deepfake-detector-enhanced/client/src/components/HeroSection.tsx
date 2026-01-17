import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { ArrowRight, Shield } from 'lucide-react';

/**
 * HeroSection Component
 * Design: Futuristic Trust - Glassmorphism
 * 
 * Premium hero section with animated title, subtitle, and call-to-action buttons.
 * Features staggered animations and glassmorphic design elements.
 */
export default function HeroSection() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.3,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.8,
      } as any,
    },
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20 pb-20">
      {/* Background gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-transparent via-transparent to-primary/5 pointer-events-none" />

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="container relative z-10 max-w-4xl mx-auto px-4"
      >
        {/* Badge */}
        <motion.div variants={itemVariants} className="flex justify-center mb-8">
          <div className="glass-card px-4 py-2 flex items-center gap-2">
            <Shield className="w-4 h-4 text-primary" />
            <span className="text-sm font-medium text-foreground">
              AI-Powered Media Authentication
            </span>
          </div>
        </motion.div>

        {/* Main Title */}
        <motion.h1
          variants={itemVariants}
          className="text-5xl md:text-7xl font-bold text-center mb-6 leading-tight"
          style={{
            backgroundImage: 'linear-gradient(135deg, #e2e8f0 0%, #00d9ff 50%, #a855f7 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          Detect Deepfakes
          <br />
          <span className="neon-glow">Instantly</span>
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          variants={itemVariants}
          className="text-lg md:text-xl text-muted-foreground text-center mb-8 max-w-2xl mx-auto"
        >
          Advanced AI technology that analyzes media authenticity with precision.
          Protect yourself from manipulated content with our intelligent detection system.
        </motion.p>

        {/* CTA Buttons */}
        <motion.div
          variants={itemVariants}
          className="flex flex-col sm:flex-row gap-4 justify-center items-center"
        >
          <Button
            size="lg"
            className="bg-primary hover:bg-primary/90 text-primary-foreground px-8 py-6 text-lg font-semibold rounded-lg group"
          >
            Start Analyzing
            <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
          </Button>
          <Button
            size="lg"
            variant="outline"
            className="border-primary text-primary hover:bg-primary/10 px-8 py-6 text-lg font-semibold rounded-lg"
          >
            Learn More
          </Button>
        </motion.div>

        {/* Stats Row */}
        <motion.div
          variants={itemVariants}
          className="grid grid-cols-3 gap-4 mt-16 pt-12 border-t border-border"
        >
          {[
            { number: '99.8%', label: 'Accuracy Rate' },
            { number: '<1s', label: 'Analysis Time' },
            { number: '10M+', label: 'Files Analyzed' },
          ].map((stat, idx) => (
            <motion.div
              key={idx}
              whileHover={{ y: -5 }}
              className="text-center"
            >
              <div className="text-2xl md:text-3xl font-bold text-primary mb-2">
                {stat.number}
              </div>
              <div className="text-sm text-muted-foreground">{stat.label}</div>
            </motion.div>
          ))}
        </motion.div>
      </motion.div>

      {/* Animated accent elements */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
        className="absolute top-1/4 right-10 w-32 h-32 border border-primary/20 rounded-full pointer-events-none"
      />
      <motion.div
        animate={{ rotate: -360 }}
        transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
        className="absolute bottom-1/4 left-10 w-40 h-40 border border-secondary/20 rounded-full pointer-events-none"
      />
    </section>
  );
}
