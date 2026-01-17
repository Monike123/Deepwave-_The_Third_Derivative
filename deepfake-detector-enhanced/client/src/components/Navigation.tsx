import { motion } from 'framer-motion';
import { Shield, Menu, X } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';

/**
 * Navigation Component
 * Design: Futuristic Trust - Glassmorphism
 * 
 * Premium navigation bar with glassmorphic styling and smooth animations.
 */
export default function Navigation() {
  const [isOpen, setIsOpen] = useState(false);

  const navItems = [
    { label: 'Features', href: '#features' },
    { label: 'How It Works', href: '#how-it-works' },
    { label: 'Pricing', href: '#pricing' },
    { label: 'Documentation', href: '#docs' },
  ];

  const menuVariants = {
    hidden: { opacity: 0, y: -20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: -10 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.4 } as any,
    },
  };

  return (
    <motion.nav
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 } as any}
      className="fixed top-0 left-0 right-0 z-50 glass-card backdrop-blur-xl border-b border-border"
    >
      <div className="container flex items-center justify-between h-16">
        {/* Logo */}
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="flex items-center gap-2 font-bold text-lg"
        >
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
            <Shield className="w-5 h-5 text-primary-foreground" />
          </div>
          <span className="text-foreground">DeepfakeDetector</span>
        </motion.div>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-8">
          {navItems.map((item, idx) => (
            <motion.a
              key={idx}
              href={item.href}
              whileHover={{ color: '#00d9ff' }}
              className="text-muted-foreground hover:text-primary transition-colors text-sm font-medium"
            >
              {item.label}
            </motion.a>
          ))}
        </div>

        {/* CTA Buttons */}
        <div className="hidden md:flex items-center gap-3">
          <Button
            variant="ghost"
            className="text-foreground hover:text-primary hover:bg-primary/10"
          >
            Sign In
          </Button>
          <Button className="bg-primary hover:bg-primary/90 text-primary-foreground">
            Get Started
          </Button>
        </div>

        {/* Mobile Menu Button */}
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setIsOpen(!isOpen)}
          className="md:hidden p-2 rounded-lg hover:bg-primary/10 transition-colors"
        >
          {isOpen ? (
            <X className="w-6 h-6 text-foreground" />
          ) : (
            <Menu className="w-6 h-6 text-foreground" />
          )}
        </motion.button>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <motion.div
          variants={menuVariants}
          initial="hidden"
          animate="visible"
          className="md:hidden border-t border-border bg-background/80 backdrop-blur-xl"
        >
          <div className="container py-4 space-y-4">
            {navItems.map((item, idx) => (
              <motion.a
                key={idx}
                href={item.href}
                variants={itemVariants}
                onClick={() => setIsOpen(false)}
                className="block text-muted-foreground hover:text-primary transition-colors py-2"
              >
                {item.label}
              </motion.a>
            ))}
            <motion.div
              variants={itemVariants}
              className="flex gap-3 pt-4 border-t border-border"
            >
              <Button
                variant="ghost"
                className="flex-1 text-foreground hover:text-primary hover:bg-primary/10"
              >
                Sign In
              </Button>
              <Button className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground">
                Get Started
              </Button>
            </motion.div>
          </div>
        </motion.div>
      )}
    </motion.nav>
  );
}
