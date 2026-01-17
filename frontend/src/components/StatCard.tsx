import { motion } from 'framer-motion';

interface StatCardProps {
    number: string;
    label: string;
    index?: number;
}

/**
 * StatCard - Animated statistic display card
 * @description Displays a stat number and label with entrance animation
 */
export default function StatCard({ number, label, index = 0 }: StatCardProps) {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{
                duration: 0.5,
                delay: index * 0.1,
                ease: [0.4, 0, 0.2, 1]
            }}
            whileHover={{ scale: 1.05 }}
            className="relative p-6 rounded-2xl bg-white/5 backdrop-blur-sm border border-white/10 text-center group hover:border-cyan-500/30 transition-all duration-300"
        >
            {/* Glow effect */}
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-cyan-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

            <motion.div
                className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-orange-400 bg-clip-text text-transparent mb-2"
                initial={{ scale: 0 }}
                whileInView={{ scale: 1 }}
                viewport={{ once: true }}
                transition={{
                    type: 'spring',
                    stiffness: 200,
                    delay: index * 0.1 + 0.2
                }}
            >
                {number}
            </motion.div>
            <div className="text-gray-400 text-sm uppercase tracking-wider">
                {label}
            </div>
        </motion.div>
    );
}
