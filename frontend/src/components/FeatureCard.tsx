import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';

interface FeatureCardProps {
    icon: LucideIcon;
    title: string;
    description: string;
    index?: number;
    accentColor?: 'cyan' | 'purple' | 'orange';
}

/**
 * FeatureCard - Premium glassmorphic feature card with hover animations
 * @description Displays a feature with icon, title, and description
 * Includes 3D hover effects and staggered entrance animations
 */
export default function FeatureCard({
    icon: Icon,
    title,
    description,
    index = 0,
    accentColor = 'cyan'
}: FeatureCardProps) {
    const accentColors = {
        cyan: {
            gradient: 'from-cyan-500/20 to-purple-500/20',
            border: 'border-cyan-500/30',
            iconBg: 'bg-cyan-500/10',
            iconColor: 'text-cyan-400',
            glow: 'hover:shadow-cyan-500/20',
        },
        purple: {
            gradient: 'from-purple-500/20 to-pink-500/20',
            border: 'border-purple-500/30',
            iconBg: 'bg-purple-500/10',
            iconColor: 'text-purple-400',
            glow: 'hover:shadow-purple-500/20',
        },
        orange: {
            gradient: 'from-orange-500/20 to-red-500/20',
            border: 'border-orange-500/30',
            iconBg: 'bg-orange-500/10',
            iconColor: 'text-orange-400',
            glow: 'hover:shadow-orange-500/20',
        },
    };

    const colors = accentColors[accentColor];

    return (
        <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{
                duration: 0.6,
                delay: index * 0.1,
                ease: [0.4, 0, 0.2, 1]
            }}
            whileHover={{
                y: -8,
                transition: { duration: 0.3 }
            }}
            className={`
                relative p-6 rounded-2xl 
                bg-gradient-to-br ${colors.gradient}
                backdrop-blur-xl
                border ${colors.border}
                hover:border-white/20
                transition-all duration-300
                hover:shadow-2xl ${colors.glow}
                group
                cursor-pointer
            `}
        >
            {/* Glow effect on hover */}
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

            {/* Icon container */}
            <motion.div
                whileHover={{ rotate: 360 }}
                transition={{ duration: 0.6 }}
                className={`
                    w-14 h-14 rounded-xl ${colors.iconBg}
                    flex items-center justify-center mb-4
                    border border-white/10
                `}
            >
                <Icon className={`w-7 h-7 ${colors.iconColor}`} />
            </motion.div>

            {/* Content */}
            <h3 className="text-xl font-bold text-white mb-2 group-hover:text-cyan-300 transition-colors">
                {title}
            </h3>
            <p className="text-gray-400 text-sm leading-relaxed group-hover:text-gray-300 transition-colors">
                {description}
            </p>

            {/* Bottom accent line */}
            <div className="absolute bottom-0 left-6 right-6 h-[2px] bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        </motion.div>
    );
}
