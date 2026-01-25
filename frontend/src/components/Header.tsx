import { Zap, Coffee } from "lucide-react";

export function Header() {
  return (
    <header className="border-b border-border bg-card/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="container px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <a href="/" className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg gradient-energy flex items-center justify-center">
              <Zap className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold text-foreground">
              Battery Scout
            </span>
          </a>

          {/* Right side */}
          <div className="flex items-center gap-4">
            {/* Support link */}
            <a
              href="https://buymeacoffee.com/zmeseldzijv"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              <Coffee className="w-4 h-4" />
              <span>Support</span>
            </a>

            {/* CTA */}
            <a
              href="#subscribe"
              className="hidden sm:inline-flex items-center px-4 py-2 rounded-lg gradient-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition-opacity"
            >
              Subscribe for Free
            </a>
          </div>
        </div>
      </div>
    </header>
  );
}
