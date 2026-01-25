import { SignupForm } from "./SignupForm";
import { Battery, Zap, TrendingUp } from "lucide-react";

export function HeroSection() {
  return (
    <section className="relative gradient-hero overflow-hidden">
      {/* Decorative background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 rounded-full bg-primary/5 blur-3xl" />
        <div className="absolute top-1/2 -left-40 w-96 h-96 rounded-full bg-secondary/5 blur-3xl" />
      </div>

      <div className="container relative px-4 sm:px-6 lg:px-8 py-16 lg:py-24">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Left Column - Content */}
          <div className="text-center lg:text-left">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6">
              <Zap className="w-4 h-4" />
              Daily insights for battery professionals
            </div>

            {/* Headline */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground leading-tight mb-6">
              Stay Charged on{" "}
              <span className="text-gradient">Battery Industry</span>{" "}
              News
            </h1>

            {/* Subheadline */}
            <p className="text-lg sm:text-xl text-muted-foreground leading-relaxed mb-8 max-w-xl mx-auto lg:mx-0">
              Your curated daily briefing on the latest in energy storage—from 
              lithium-ion breakthroughs to policy shifts and market moves.
            </p>

            {/* Trust indicators */}
            <div className="flex flex-wrap items-center justify-center lg:justify-start gap-6 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <Battery className="w-5 h-5 text-primary" />
                <span>Expert-curated content</span>
              </div>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-secondary" />
                <span>Industry trends & analysis</span>
              </div>
            </div>
          </div>

          {/* Right Column - Form */}
          <div className="w-full max-w-md mx-auto lg:ml-auto lg:mr-0">
            <div className="bg-card rounded-2xl shadow-lg border border-border p-6 sm:p-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-lg gradient-energy flex items-center justify-center">
                  <Zap className="w-5 h-5 text-primary-foreground" />
                </div>
                <div>
                  <h2 className="font-semibold text-foreground">Subscribe for Free</h2>
                  <p className="text-sm text-muted-foreground">Join thousands of industry pros</p>
                </div>
              </div>
              <SignupForm />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
