import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';

/**
 * FeatureCard Component
 * Design: Futuristic Trust - Glassmorphism
 * 
 * Reusable card component for displaying features with icon, title, and description.
 * Includes hover animations and glassmorphic styling.
 */
interface FeatureCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  index?: number;
}

export default function FeatureCard({
  icon: Icon,
  title,
  description,
  index = 0,
}: FeatureCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      whileHover={{ y: -8, transition: { duration: 0.3 } }}
      transition={{
        duration: 0.6,
        delay: index * 0.1,
      } as any}
      viewport={{ once: true }}
      className="glass-card p-6 md:p-8 rounded-xl group cursor-pointer relative overflow-hidden"
    >
      {/* Hover glow effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/0 to-secondary/0 group-hover:from-primary/10 group-hover:to-secondary/10 transition-all duration-300" />

      {/* Content */}
      <div className="relative z-10">
        {/* Icon container */}
        <motion.div
          whileHover={{ rotate: 360, scale: 1.1 }}
          transition={{ duration: 0.6 } as any}
          className="w-12 h-12 rounded-lg bg-gradient-to-br from-primary to-secondary p-2.5 mb-4 flex items-center justify-center"
        >
          <Icon className="w-6 h-6 text-primary-foreground" />
        </motion.div>

        {/* Title */}
        <h3 className="text-xl font-bold text-foreground mb-3 group-hover:text-primary transition-colors">
          {title}
        </h3>

        {/* Description */}
        <p className="text-muted-foreground leading-relaxed">
          {description}
        </p>

        {/* Accent line */}
        <motion.div
          initial={{ width: 0 }}
          whileHover={{ width: 40 }}
          transition={{ duration: 0.3 } as any}
          className="h-1 bg-gradient-to-r from-primary to-secondary mt-4 rounded-full"
        />
      </div>
    </motion.div>
  );
}
