import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Battery, Zap, Mail } from "lucide-react";
import { toast } from "sonner";
import { supabase } from "@/integrations/supabase/client";
import { z } from "zod";

const emailSchema = z.string().email("Please enter a valid email address").max(255);

const categories = [
  { id: "industry", label: "Industry News" },
  { id: "technology", label: "Technology & Innovation" },
  { id: "supply", label: "Supply Chain & Materials" },
  { id: "manufacturing", label: "Manufacturing & Production" },
  { id: "policy", label: "Policy & Regulations" },
  { id: "recycling", label: "Battery Recycling" },
  { id: "market", label: "Market Applications" },
];

export const HeroSection = () => {
  const [email, setEmail] = useState("");
  const [frequency, setFrequency] = useState<"daily" | "weekly">("daily");
  const [selectedCategories, setSelectedCategories] = useState<string[]>([
    "industry",
    "technology",
  ]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleCategoryToggle = (categoryId: string) => {
    setSelectedCategories((prev) =>
      prev.includes(categoryId)
        ? prev.filter((id) => id !== categoryId)
        : [...prev, categoryId]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate email
    const emailValidation = emailSchema.safeParse(email.trim());
    if (!emailValidation.success) {
      toast.error(emailValidation.error.errors[0].message);
      return;
    }

    if (selectedCategories.length === 0) {
      toast.error("Please select at least one category");
      return;
    }

    setIsSubmitting(true);

    const insertData = {
      email: email.trim().toLowerCase(),
      frequency: frequency,
      categories: selectedCategories,
    };
    
    console.log("=== Form Submission Debug ===");
    console.log("Insert data:", insertData);

    try {
      const { data, error } = await supabase.from("subscribers").insert(insertData);

      console.log("Supabase response - data:", data);
      console.log("Supabase response - error:", error);
      
      if (error) {
        console.log("Error code:", error.code);
        console.log("Error message:", error.message);
        console.log("Error details:", error.details);
        console.log("Error hint:", error.hint);
        
        // 23505 is the PostgreSQL unique violation error code
        if (error.code === "23505") {
          toast.error("This email is already subscribed!");
        } else {
          toast.error(`Error: ${error.message || "Something went wrong. Please try again."}`);
        }
        return;
      }

      console.log("Success! Subscription saved.");
      toast.success("Welcome to Battery Brief! You're all set.");
      setEmail("");
    } catch (err) {
      console.error("Caught exception:", err);
      toast.error("Something went wrong. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="hero-gradient min-h-screen flex items-center relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-20 left-10 w-72 h-72 bg-teal rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-teal rounded-full blur-3xl" />
      </div>

      <div className="container mx-auto px-4 py-20 relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          {/* Logo and Title */}
          <div className="flex items-center justify-center gap-3 mb-6 animate-fade-in">
            <div className="p-3 rounded-2xl bg-teal/20 glow-teal">
              <Battery className="w-10 h-10 text-teal" />
            </div>
            <h1 className="text-5xl md:text-7xl font-bold text-primary-foreground">
              Battery Brief
            </h1>
          </div>

          {/* Tagline */}
          <p
            className="text-xl md:text-2xl text-teal font-medium mb-4 animate-fade-in"
            style={{ animationDelay: "0.1s" }}
          >
            Global Battery Industry Intelligence, Delivered Daily
          </p>

          {/* Subheading */}
          <p
            className="text-lg text-primary-foreground/70 mb-12 max-w-2xl mx-auto animate-fade-in"
            style={{ animationDelay: "0.2s" }}
          >
            Curated news across 7 key categories with AI-powered summaries.
            Stay ahead in the lithium-ion battery industry.
          </p>

          {/* Signup Form */}
          <form
            onSubmit={handleSubmit}
            className="bg-card/95 backdrop-blur-sm rounded-2xl p-8 shadow-2xl max-w-2xl mx-auto animate-fade-in"
            style={{ animationDelay: "0.3s" }}
          >
            {/* Email Input */}
            <div className="flex flex-col sm:flex-row gap-3 mb-6">
              <div className="relative flex-1">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <Input
                  type="email"
                  placeholder="Enter your email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-10 h-12 text-base"
                  required
                />
              </div>
            </div>

            {/* Frequency Selector */}
            <div className="mb-6">
              <Label className="text-sm font-medium text-muted-foreground mb-3 block">
                Delivery Frequency
              </Label>
              <RadioGroup
                value={frequency}
                onValueChange={(val) => setFrequency(val as "daily" | "weekly")}
                className="flex gap-6 justify-center"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="daily" id="daily" />
                  <Label htmlFor="daily" className="cursor-pointer font-medium">
                    Daily
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="weekly" id="weekly" />
                  <Label htmlFor="weekly" className="cursor-pointer font-medium">
                    Weekly
                  </Label>
                </div>
              </RadioGroup>
            </div>

            {/* Category Checkboxes */}
            <div className="mb-6">
              <Label className="text-sm font-medium text-muted-foreground mb-3 block">
                Select Categories
              </Label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-left">
                {categories.map((category) => (
                  <div key={category.id} className="flex items-center space-x-2">
                    <Checkbox
                      id={category.id}
                      checked={selectedCategories.includes(category.id)}
                      onCheckedChange={() => handleCategoryToggle(category.id)}
                    />
                    <Label
                      htmlFor={category.id}
                      className="text-sm cursor-pointer"
                    >
                      {category.label}
                    </Label>
                  </div>
                ))}
              </div>
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              size="lg"
              disabled={isSubmitting}
              className="w-full h-12 text-base font-semibold bg-accent hover:bg-accent/90 text-accent-foreground animate-pulse-glow"
            >
              <Zap className="w-5 h-5 mr-2" />
              {isSubmitting ? "Subscribing..." : "Subscribe to Battery Brief"}
            </Button>

            <p className="text-xs text-muted-foreground mt-4">
              Free forever. Unsubscribe anytime.
            </p>
          </form>
        </div>
      </div>
    </section>
  );
};
