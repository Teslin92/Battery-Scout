import { useState } from "react";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Loader2, CheckCircle2, AlertCircle, Zap } from "lucide-react";
import { signup } from "@/lib/api";

// Hardcoded topics matching backend categories
const topics = [
  { id: "companies-deals", label: "Companies & Deals" },
  { id: "policy-regulation", label: "Policy & Regulation" },
  { id: "supply-chain", label: "Supply Chain" },
  { id: "lithium-ion-solid-state", label: "Lithium-ion & Solid-state" },
  { id: "sodium-ion-alternatives", label: "Sodium-ion & Alternatives" },
  { id: "recycling-second-life", label: "Recycling & Second-life" },
] as const;

// Map frontend topic IDs to backend category names
const topicIdToBackendCategory: Record<string, string> = {
  "companies-deals": "Companies & Deals",
  "policy-regulation": "Policy & Regulation",
  "supply-chain": "Supply Chain",
  "lithium-ion-solid-state": "Lithium-ion & Solid-state",
  "sodium-ion-alternatives": "Sodium-ion & Alternatives",
  "recycling-second-life": "Recycling & Second-life",
};

const regions = [
  { id: "North America", label: "North America" },
  { id: "Europe", label: "Europe" },
  { id: "Asia", label: "Asia" },
  { id: "Global", label: "Global" },
] as const;

const signupSchema = z.object({
  email: z
    .string()
    .trim()
    .email({ message: "Please enter a valid email address" })
    .max(255, { message: "Email must be less than 255 characters" }),
  topics: z
    .array(z.string())
    .min(1, { message: "Please select at least one topic" }),
  frequency: z.enum(["daily", "weekly"], {
    required_error: "Please select a frequency",
  }),
  regions: z.array(z.string()).optional(),
});

type SignupFormData = z.infer<typeof signupSchema>;

export function SignupForm() {
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  const form = useForm<SignupFormData>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      email: "",
      topics: [],
      frequency: "daily",
      regions: [],
    },
  });

  async function onSubmit(data: SignupFormData) {
    setStatus("loading");
    setMessage("");

    try {
      // Map frontend topic IDs to backend category names
      const backendTopics = data.topics.map(
        (topicId) => topicIdToBackendCategory[topicId] || topicId
      );

      // Use hardcoded Railway URL (like Lovable version) - always use production backend
      // Only use env var if it's a valid production URL, otherwise use hardcoded
      const envUrl = import.meta.env.VITE_API_URL;
      let API_URL = (envUrl && envUrl.includes('railway.app')) 
        ? envUrl 
        : 'https://battery-scout-production.up.railway.app';
      
      // Remove trailing slash if present to avoid double slashes
      API_URL = API_URL.replace(/\/+$/, '');
      
      console.log('Signup request to:', `${API_URL}/api/signup`);
      console.log('Payload:', { email: data.email, topics: backendTopics, frequency: data.frequency, regions: data.regions || [] });
      
      const response = await fetch(`${API_URL}/api/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: data.email,
          topics: backendTopics,
          frequency: data.frequency,
          regions: data.regions || [],
        }),
      });

      console.log('Response status:', response.status, response.statusText);

      if (!response.ok) {
        // Try to parse error response
        let errorData;
        try {
          errorData = await response.json();
        } catch {
          // If not JSON, use status text
          if (response.status === 404) {
            throw new Error(`API endpoint not found (404). Check if backend is deployed at ${API_URL}`);
          }
          throw new Error(`Server error: ${response.status} ${response.statusText}`);
        }
        
        setStatus("error");
        setMessage(errorData.detail || errorData.message || `Error: ${response.status} ${response.statusText}`);
        return;
      }

      const result = await response.json();
      console.log('Success response:', result);

      setStatus("success");
      setMessage(result.message || "You're subscribed! Check your inbox.");
      form.reset();
    } catch (error) {
      setStatus("error");
      const errorMessage = error instanceof Error ? error.message : "Something went wrong. Please try again.";
      
      if (errorMessage.includes("already subscribed") || errorMessage.includes("409")) {
        setMessage("This email is already subscribed!");
      } else if (errorMessage.includes("fetch") || errorMessage.includes("network")) {
        setMessage("Cannot connect to server. Please check your internet connection and try again.");
      } else {
        setMessage(errorMessage);
      }
    }
  }

  if (status === "success") {
    return (
      <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
        <div className="w-16 h-16 rounded-full gradient-energy flex items-center justify-center mb-4 animate-pulse-glow">
          <CheckCircle2 className="w-8 h-8 text-primary-foreground" />
        </div>
        <h3 className="text-xl font-semibold text-foreground mb-2">
          You're In!
        </h3>
        <p className="text-muted-foreground">{message}</p>
      </div>
    );
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        {/* Email Field */}
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-foreground font-medium">
                Email Address
              </FormLabel>
              <FormControl>
                <Input
                  type="email"
                  placeholder="you@company.com"
                  className="h-12 bg-background border-border focus:border-primary focus:ring-primary"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Topics Field */}
        <FormField
          control={form.control}
          name="topics"
          render={() => (
            <FormItem>
              <FormLabel className="text-foreground font-medium">
                Topics <span className="text-muted-foreground font-normal">(select at least 1)</span>
              </FormLabel>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-2">
                {topics.map((topic) => (
                  <FormField
                    key={topic.id}
                    control={form.control}
                    name="topics"
                    render={({ field }) => (
                      <FormItem className="flex items-center space-x-3 space-y-0">
                        <FormControl>
                          <Checkbox
                            checked={field.value?.includes(topic.id)}
                            onCheckedChange={(checked) => {
                              return checked
                                ? field.onChange([...field.value, topic.id])
                                : field.onChange(
                                    field.value?.filter((value) => value !== topic.id)
                                  );
                            }}
                            className="border-border data-[state=checked]:bg-primary data-[state=checked]:border-primary"
                          />
                        </FormControl>
                        <Label className="text-sm text-foreground font-normal cursor-pointer">
                          {topic.label}
                        </Label>
                      </FormItem>
                    )}
                  />
                ))}
              </div>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Frequency Field */}
        <FormField
          control={form.control}
          name="frequency"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-foreground font-medium">
                Frequency
              </FormLabel>
              <FormControl>
                <RadioGroup
                  onValueChange={field.onChange}
                  defaultValue={field.value}
                  className="flex gap-6 mt-2"
                >
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem
                      value="daily"
                      id="daily"
                      className="border-border text-primary"
                    />
                    <Label htmlFor="daily" className="text-foreground font-normal cursor-pointer">
                      Daily
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem
                      value="weekly"
                      id="weekly"
                      className="border-border text-primary"
                    />
                    <Label htmlFor="weekly" className="text-foreground font-normal cursor-pointer">
                      Weekly
                    </Label>
                  </div>
                </RadioGroup>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Regions Field */}
        <FormField
          control={form.control}
          name="regions"
          render={() => (
            <FormItem>
              <FormLabel className="text-foreground font-medium">
                Regions <span className="text-muted-foreground font-normal">(optional)</span>
              </FormLabel>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-2">
                {regions.map((region) => (
                  <FormField
                    key={region.id}
                    control={form.control}
                    name="regions"
                    render={({ field }) => (
                      <FormItem className="flex items-center space-x-3 space-y-0">
                        <FormControl>
                          <Checkbox
                            checked={field.value?.includes(region.id)}
                            onCheckedChange={(checked) => {
                              return checked
                                ? field.onChange([...(field.value || []), region.id])
                                : field.onChange(
                                    field.value?.filter((value) => value !== region.id)
                                  );
                            }}
                            className="border-border data-[state=checked]:bg-primary data-[state=checked]:border-primary"
                          />
                        </FormControl>
                        <Label className="text-sm text-foreground font-normal cursor-pointer">
                          {region.label}
                        </Label>
                      </FormItem>
                    )}
                  />
                ))}
              </div>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Error Message */}
        {status === "error" && (
          <div className="flex items-center gap-2 text-destructive text-sm bg-destructive/10 p-3 rounded-lg">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{message}</span>
          </div>
        )}

        {/* Submit Button */}
        <Button
          type="submit"
          disabled={status === "loading"}
          className="w-full h-12 gradient-primary text-primary-foreground font-semibold text-base shadow-glow hover:opacity-90 transition-opacity"
        >
          {status === "loading" ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Subscribing...
            </>
          ) : (
            <>
              <Zap className="w-5 h-5 mr-2" />
              Subscribe Now
            </>
          )}
        </Button>

        <p className="text-xs text-center text-muted-foreground">
          No spam, ever. Unsubscribe anytime with one click.
        </p>
      </form>
    </Form>
  );
}
