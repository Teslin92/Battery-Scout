import { SupportBanner } from "@/components/SupportBanner";
import { HeroSection } from "@/components/HeroSection";
import { SampleNewsletterSection } from "@/components/SampleNewsletterSection";
import { FeaturesSection } from "@/components/FeaturesSection";
import { Footer } from "@/components/Footer";

const Index = () => {
  return (
    <main className="min-h-screen">
      <SupportBanner />
      <HeroSection />
      <SampleNewsletterSection />
      <FeaturesSection />
      <Footer />
    </main>
  );
};

export default Index;
