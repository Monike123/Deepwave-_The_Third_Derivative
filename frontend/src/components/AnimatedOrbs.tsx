import { motion } from 'framer-motion';

/**
 * AnimatedOrbs - Floating gradient orbs for premium background effect
 * @description Renders four animated gradient orbs that float continuously
 * Uses GPU-accelerated transforms for smooth performance
 */
export default function AnimatedOrbs() {
    return (
        <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
            {/* Primary Orb - Cyan/Purple */}
            <motion.div
                className="absolute w-[600px] h-[600px] rounded-full opacity-30"
                style={{
                    background: 'radial-gradient(circle, rgba(0,217,255,0.4) 0%, rgba(168,85,247,0.2) 50%, transparent 70%)',
                    filter: 'blur(60px)',
                    top: '10%',
                    left: '20%',
                }}
                animate={{
                    y: [0, -50, 0],
                    x: [0, 30, 0],
                    scale: [1, 1.1, 1],
                }}
                transition={{
                    duration: 8,
                    repeat: Infinity,
                    ease: 'easeInOut',
                }}
            />

            {/* Secondary Orb - Orange/Pink */}
            <motion.div
                className="absolute w-[500px] h-[500px] rounded-full opacity-25"
                style={{
                    background: 'radial-gradient(circle, rgba(255,107,0,0.4) 0%, rgba(213,0,249,0.2) 50%, transparent 70%)',
                    filter: 'blur(50px)',
                    top: '50%',
                    right: '10%',
                }}
                animate={{
                    y: [0, 40, 0],
                    x: [0, -40, 0],
                    scale: [1.1, 1, 1.1],
                }}
                transition={{
                    duration: 10,
                    repeat: Infinity,
                    ease: 'easeInOut',
                    delay: 1,
                }}
            />

            {/* Tertiary Orb - Purple */}
            <motion.div
                className="absolute w-[400px] h-[400px] rounded-full opacity-20"
                style={{
                    background: 'radial-gradient(circle, rgba(123,31,162,0.5) 0%, rgba(74,20,140,0.2) 50%, transparent 70%)',
                    filter: 'blur(40px)',
                    bottom: '20%',
                    left: '10%',
                }}
                animate={{
                    y: [0, 30, 0],
                    x: [0, 20, 0],
                }}
                transition={{
                    duration: 7,
                    repeat: Infinity,
                    ease: 'easeInOut',
                    delay: 2,
                }}
            />

            {/* Accent Orb - Cyan glow */}
            <motion.div
                className="absolute w-[300px] h-[300px] rounded-full opacity-15"
                style={{
                    background: 'radial-gradient(circle, rgba(0,217,255,0.6) 0%, transparent 60%)',
                    filter: 'blur(30px)',
                    top: '70%',
                    right: '30%',
                }}
                animate={{
                    y: [0, -25, 0],
                    scale: [1, 1.2, 1],
                }}
                transition={{
                    duration: 6,
                    repeat: Infinity,
                    ease: 'easeInOut',
                    delay: 0.5,
                }}
            />
        </div>
    );
}
