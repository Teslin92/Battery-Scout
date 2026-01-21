import { Battery } from "lucide-react";

export const Footer = () => {
  return (
    <footer className="hero-gradient py-16">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          {/* Links */}
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            {/* Logo */}
            <div className="flex items-center gap-2">
              <Battery className="w-6 h-6 text-teal" />
              <span className="font-semibold text-primary-foreground">
                Battery Brief
              </span>
            </div>

            {/* Navigation Links */}
            <div className="flex items-center gap-6 text-sm">
              <a
                href="#"
                className="text-primary-foreground/70 hover:text-primary-foreground transition-colors"
              >
                About
              </a>
              <a
                href="#"
                className="text-primary-foreground/70 hover:text-primary-foreground transition-colors"
              >
                Contact
              </a>
              <a
                href="#"
                className="text-primary-foreground/70 hover:text-primary-foreground transition-colors"
              >
                Privacy
              </a>
            </div>
          </div>

          {/* Privacy Note */}
          <p className="text-center text-sm text-primary-foreground/50 mt-8">
            We respect your inbox. Unsubscribe anytime.
          </p>

          <p className="text-center text-xs text-primary-foreground/40 mt-4">
            © {new Date().getFullYear()} Battery Brief. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};
