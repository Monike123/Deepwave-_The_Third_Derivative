import Navigation from '@/components/Navigation';
import AnimatedOrbs from '@/components/AnimatedOrbs';
import HeroSection from '@/components/HeroSection';
import FeaturesSection from '@/components/FeaturesSection';
import AnalysisSection from '@/components/AnalysisSection';
import CTASection from '@/components/CTASection';
import Footer from '@/components/Footer';

/**
 * Home Page
 * Design: Futuristic Trust - Glassmorphism
 * 
 * Premium landing page for Deepfake Detector with animated sections,
 * glassmorphic design, and smooth scroll animations.
 */
export default function Home() {
  return (
    <div className="min-h-screen bg-background text-foreground overflow-hidden">
      {/* Animated background orbs */}
      <AnimatedOrbs />

      {/* Navigation */}
      <Navigation />

      {/* Main content */}
      <main className="relative z-10">
        {/* Hero Section */}
        <HeroSection />

        {/* Features Section */}
        <FeaturesSection />

        {/* Analysis Section */}
        <AnalysisSection />

        {/* CTA Section */}
        <CTASection />
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}
