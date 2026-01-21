import { Coffee } from "lucide-react";
import { Button } from "@/components/ui/button";

export const SupportBanner = () => {
  return (
    <div className="bg-[#FFDD00] py-3">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-center gap-4">
          <span className="text-black font-medium text-sm">
            Love Battery Brief? Support us!
          </span>
          <Button
            asChild
            size="sm"
            className="bg-black hover:bg-black/80 text-white font-semibold"
          >
            <a
              href="https://buymeacoffee.com"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Coffee className="w-4 h-4 mr-2" />
              Buy Me a Coffee
            </a>
          </Button>
        </div>
      </div>
    </div>
  );
};
