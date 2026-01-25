import { Zap, Coffee } from "lucide-react";

export function Footer() {
  return (
    <footer className="bg-foreground text-background py-12">
      <div className="container px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center text-center">
          {/* Logo */}
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg gradient-energy flex items-center justify-center">
              <Zap className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold">Battery Scout</span>
          </div>

          {/* Tagline */}
          <p className="text-background/70 max-w-md mb-8">
            Your daily intelligence source for the battery industry. 
            Curated by experts, delivered to your inbox.
          </p>

          {/* Links */}
          <div className="flex flex-wrap justify-center gap-6 text-sm text-background/60 mb-6">
            <a
              href="mailto:hello@batteryscout.com"
              className="hover:text-background transition-colors"
            >
              Contact
            </a>
            <a
              href="/unsubscribe"
              className="hover:text-background transition-colors"
            >
              Unsubscribe
            </a>
          </div>

          {/* Support Button */}
          <a
            href="https://buymeacoffee.com/zmeseldzijv"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 mb-8 rounded-full text-sm font-medium bg-background/10 text-background/70 hover:bg-background/20 hover:text-background transition-all"
          >
            <Coffee className="w-4 h-4" />
            Support this project
          </a>

          {/* Copyright */}
          <p className="text-sm text-background/50">
            © {new Date().getFullYear()} Battery Scout. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
