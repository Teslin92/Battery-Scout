import { Header } from "@/components/Header";
import { HeroSection } from "@/components/HeroSection";
import { ContentSection } from "@/components/ContentSection";
import { Footer } from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <div id="subscribe">
          <HeroSection />
        </div>
        <ContentSection />
      </main>
      <Footer />
    </div>
  );
};

export default Index;
