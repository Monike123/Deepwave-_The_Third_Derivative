import { motion } from 'framer-motion';
import { Shield, Github, Twitter, Linkedin, Mail } from 'lucide-react';

/**
 * Footer Component
 * Design: Futuristic Trust - Glassmorphism
 * 
 * Premium footer with company info, links, and social media.
 */
export default function Footer() {
  const footerLinks = {
    Product: ['Features', 'Pricing', 'Security', 'Roadmap'],
    Company: ['About', 'Blog', 'Careers', 'Contact'],
    Resources: ['Documentation', 'API Docs', 'Community', 'Support'],
    Legal: ['Privacy', 'Terms', 'Cookies', 'License'],
  };

  const socialLinks = [
    { icon: Github, href: '#' },
    { icon: Twitter, href: '#' },
    { icon: Linkedin, href: '#' },
    { icon: Mail, href: '#' },
  ];

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
    <footer className="relative border-t border-border bg-background/50 backdrop-blur-xl">
      <div className="container py-16 md:py-24">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-5 gap-8 mb-12"
        >
          {/* Brand column */}
          <motion.div variants={itemVariants} className="md:col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                <Shield className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="font-bold text-foreground">DeepfakeDetector</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Advanced AI-powered deepfake detection and media authenticity analysis.
            </p>
            <div className="flex gap-3 mt-4">
              {socialLinks.map((social, idx) => {
                const Icon = social.icon;
                return (
                  <motion.a
                    key={idx}
                    href={social.href}
                    whileHover={{ scale: 1.2, color: '#00d9ff' }}
                    className="text-muted-foreground hover:text-primary transition-colors"
                  >
                    <Icon className="w-5 h-5" />
                  </motion.a>
                );
              })}
            </div>
          </motion.div>

          {/* Links columns */}
          {Object.entries(footerLinks).map(([category, links], colIdx) => (
            <motion.div
              key={colIdx}
              variants={itemVariants}
              className="md:col-span-1"
            >
              <h4 className="font-semibold text-foreground mb-4">{category}</h4>
              <ul className="space-y-3">
                {links.map((link, idx) => (
                  <li key={idx}>
                    <motion.a
                      href="#"
                      whileHover={{ x: 4, color: '#00d9ff' }}
                      className="text-sm text-muted-foreground hover:text-primary transition-colors"
                    >
                      {link}
                    </motion.a>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </motion.div>

        {/* Divider */}
        <motion.div
          initial={{ scaleX: 0 }}
          whileInView={{ scaleX: 1 }}
          transition={{ duration: 0.8 } as any}
          viewport={{ once: true }}
          className="h-px bg-gradient-to-r from-transparent via-border to-transparent mb-8 origin-left"
        />

        {/* Bottom section */}
        <motion.div
          variants={itemVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="flex flex-col md:flex-row items-center justify-between gap-4"
        >
          <p className="text-sm text-muted-foreground">
            © 2024 DeepfakeDetector. All rights reserved.
          </p>
          <div className="flex gap-6">
            <motion.a
              href="#"
              whileHover={{ color: '#00d9ff' }}
              className="text-sm text-muted-foreground hover:text-primary transition-colors"
            >
              Privacy Policy
            </motion.a>
            <motion.a
              href="#"
              whileHover={{ color: '#00d9ff' }}
              className="text-sm text-muted-foreground hover:text-primary transition-colors"
            >
              Terms of Service
            </motion.a>
            <motion.a
              href="#"
              whileHover={{ color: '#00d9ff' }}
              className="text-sm text-muted-foreground hover:text-primary transition-colors"
            >
              Cookie Settings
            </motion.a>
          </div>
        </motion.div>
      </div>
    </footer>
  );
}
