import { motion } from 'framer-motion';

/**
 * AnimatedOrbs Component
 * Design: Futuristic Trust - Glassmorphism
 * 
 * Floating gradient orbs that create depth and visual interest in the background.
 * Uses framer-motion for smooth, GPU-accelerated animations.
 */
export default function AnimatedOrbs() {
  const orbVariants = {
    animate: (custom: number) => ({
      y: [0, -30, 0],
      x: [0, 20, 0],
      transition: {
        duration: 6 + custom,
        repeat: Infinity,
        ease: [0.42, 0, 0.58, 1] as any,
      },
    }),
  };

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none">
      {/* Orb 1 - Top Left */}
      <motion.div
        custom={0}
        animate="animate"
        variants={orbVariants}
        className="absolute top-20 left-10 w-72 h-72 rounded-full blur-3xl opacity-20"
        style={{
          background: "linear-gradient(135deg, #00d9ff, #a855f7)",
        }}
      />

      {/* Orb 2 - Top Right */}
      <motion.div
        custom={1}
        animate="animate"
        variants={orbVariants}
        className="absolute top-40 right-20 w-96 h-96 rounded-full blur-3xl opacity-15"
        style={{
          background: "linear-gradient(135deg, #a855f7, #00d9ff)",
        }}
      />

      {/* Orb 3 - Bottom Left */}
      <motion.div
        custom={2}
        animate="animate"
        variants={orbVariants}
        className="absolute bottom-20 left-1/4 w-80 h-80 rounded-full blur-3xl opacity-10"
        style={{
          background: "linear-gradient(135deg, #10b981, #00d9ff)",
        }}
      />

      {/* Orb 4 - Bottom Right */}
      <motion.div
        custom={3}
        animate="animate"
        variants={orbVariants}
        className="absolute bottom-40 right-1/4 w-96 h-96 rounded-full blur-3xl opacity-15"
        style={{
          background: "linear-gradient(135deg, #00d9ff, #10b981)",
        }}
      />
    </div>
  );
}
