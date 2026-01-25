import { useState, useEffect } from "react";
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
import { signup, getTopics, type TopicsResponse } from "@/lib/api";

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
  const [topicsData, setTopicsData] = useState<TopicsResponse | null>(null);
  const [loadingTopics, setLoadingTopics] = useState(true);

  const form = useForm<SignupFormData>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      email: "",
      topics: [],
      frequency: "daily",
      regions: [],
    },
  });

  // Fetch topics from backend
  useEffect(() => {
    const fetchTopics = async () => {
      try {
        const data = await getTopics();
        setTopicsData(data);
      } catch (error) {
        console.error("Failed to fetch topics:", error);
        setStatus("error");
        setMessage("Failed to load topics. Please refresh the page.");
      } finally {
        setLoadingTopics(false);
      }
    };

    fetchTopics();
  }, []);

  async function onSubmit(data: SignupFormData) {
    setStatus("loading");
    setMessage("");

    try {
      const response = await signup({
        email: data.email,
        topics: data.topics,
        frequency: data.frequency,
        regions: data.regions && data.regions.length > 0 ? data.regions : undefined,
      });

      setStatus("success");
      setMessage(response.message);
      form.reset();
    } catch (error) {
      setStatus("error");
      const errorMessage = error instanceof Error ? error.message : "Something went wrong. Please try again.";
      
      if (errorMessage.includes("already subscribed") || errorMessage.includes("409")) {
        setMessage("This email is already subscribed!");
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

  // Map backend topics to the format needed for the form
  const topics = topicsData?.all_categories.map((category) => ({
    id: category,
    label: category,
  })) || [];

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
              {loadingTopics ? (
                <div className="text-sm text-muted-foreground py-4">Loading topics...</div>
              ) : (
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
              )}
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
          disabled={status === "loading" || loadingTopics}
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
