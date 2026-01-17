import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldCheck, Github, Menu, X, Sparkles } from 'lucide-react';
import { useState, useEffect } from 'react';
import './Header.css';

export default function Header() {
    const location = useLocation();
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [isScrolled, setIsScrolled] = useState(false);

    // Handle scroll for header background change
    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 20);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    return (
        <motion.header
            initial={{ y: -100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
            className={`
                fixed top-0 left-0 right-0 z-50 
                transition-all duration-300
                ${isScrolled
                    ? 'bg-black/80 backdrop-blur-xl border-b border-white/10 shadow-lg shadow-black/20'
                    : 'bg-transparent'
                }
            `}
        >
            <div className="container mx-auto px-4 py-4 flex items-center justify-between max-w-6xl">
                {/* Logo */}
                <Link to="/" className="flex items-center gap-2 group">
                    <motion.div
                        whileHover={{ rotate: 360 }}
                        transition={{ duration: 0.6 }}
                        className="relative"
                    >
                        <ShieldCheck className="w-8 h-8 text-cyan-400 group-hover:text-cyan-300 transition-colors" />
                        <div className="absolute inset-0 bg-cyan-400/20 blur-lg rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
                    </motion.div>
                    <span className="text-xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                        Deepwave
                    </span>
                </Link>

                {/* Desktop Navigation */}
                <nav className="hidden md:flex items-center gap-1">
                    <NavLink to="/" active={location.pathname === '/'}>
                        Home
                    </NavLink>
                    <NavLink to="/analyze" active={location.pathname === '/analyze'}>
                        Analyze
                    </NavLink>

                    {/* CTA Button */}
                    <Link to="/analyze">
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="ml-4 px-5 py-2.5 rounded-xl font-medium text-sm bg-gradient-to-r from-cyan-500 to-purple-500 text-white shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/30 transition-all duration-300 flex items-center gap-2"
                        >
                            <Sparkles className="w-4 h-4" />
                            Start Free
                        </motion.button>
                    </Link>

                    {/* GitHub Link */}
                    <a
                        href="https://github.com/Monike123/Deepwave-_The_Third_Derivative"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="ml-2 p-2.5 rounded-xl text-gray-400 hover:text-white hover:bg-white/10 transition-all duration-300"
                    >
                        <Github className="w-5 h-5" />
                    </a>
                </nav>

                {/* Mobile Menu Toggle */}
                <motion.button
                    whileTap={{ scale: 0.95 }}
                    className="md:hidden p-2 rounded-xl text-gray-300 hover:text-white hover:bg-white/10 transition-all"
                    onClick={() => setIsMenuOpen(!isMenuOpen)}
                >
                    {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                </motion.button>
            </div>

            {/* Mobile Navigation */}
            <AnimatePresence>
                {isMenuOpen && (
                    <motion.nav
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.3 }}
                        className="md:hidden bg-black/95 backdrop-blur-xl border-t border-white/10 overflow-hidden"
                    >
                        <div className="container mx-auto px-4 py-4 flex flex-col gap-2">
                            <MobileNavLink
                                to="/"
                                active={location.pathname === '/'}
                                onClick={() => setIsMenuOpen(false)}
                            >
                                Home
                            </MobileNavLink>
                            <MobileNavLink
                                to="/analyze"
                                active={location.pathname === '/analyze'}
                                onClick={() => setIsMenuOpen(false)}
                            >
                                Analyze
                            </MobileNavLink>
                            <a
                                href="https://github.com/Monike123/Deepwave-_The_Third_Derivative"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-2 px-4 py-3 rounded-xl text-gray-400 hover:text-white hover:bg-white/10 transition-all"
                                onClick={() => setIsMenuOpen(false)}
                            >
                                <Github className="w-5 h-5" />
                                GitHub
                            </a>
                            <Link
                                to="/analyze"
                                onClick={() => setIsMenuOpen(false)}
                                className="mt-2"
                            >
                                <button className="w-full px-5 py-3 rounded-xl font-medium bg-gradient-to-r from-cyan-500 to-purple-500 text-white shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-2">
                                    <Sparkles className="w-4 h-4" />
                                    Start Free Analysis
                                </button>
                            </Link>
                        </div>
                    </motion.nav>
                )}
            </AnimatePresence>
        </motion.header>
    );
}

// Desktop Nav Link Component
function NavLink({ to, active, children }: { to: string; active: boolean; children: React.ReactNode }) {
    return (
        <Link to={to}>
            <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={`
                    px-4 py-2 rounded-xl font-medium text-sm transition-all duration-300
                    ${active
                        ? 'bg-white/10 text-white'
                        : 'text-gray-400 hover:text-white hover:bg-white/5'
                    }
                `}
            >
                {children}
            </motion.div>
        </Link>
    );
}

// Mobile Nav Link Component
function MobileNavLink({ to, active, onClick, children }: { to: string; active: boolean; onClick: () => void; children: React.ReactNode }) {
    return (
        <Link to={to} onClick={onClick}>
            <motion.div
                whileTap={{ scale: 0.98 }}
                className={`
                    px-4 py-3 rounded-xl font-medium transition-all duration-300
                    ${active
                        ? 'bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-white border border-cyan-500/20'
                        : 'text-gray-400 hover:text-white hover:bg-white/5'
                    }
                `}
            >
                {children}
            </motion.div>
        </Link>
    );
}
