import { useQuery } from "@tanstack/react-query";
import { ArticleCard } from "./ArticleCard";
import { supabase } from "@/integrations/supabase/client";

const categoryColorMap: Record<string, string> = {
  "Industry News": "industry",
  "Technology & Innovation": "technology",
  "Supply Chain & Materials": "supply",
  "Manufacturing & Production": "manufacturing",
  "Policy & Regulations": "policy",
  "Battery Recycling": "recycling",
  "Market Applications": "market",
};

export const SampleNewsletterSection = () => {
  const { data: articles, isLoading } = useQuery({
    queryKey: ["articles"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("articles")
        .select("*")
        .order("publish_date", { ascending: false })
        .limit(6);

      if (error) throw error;
      return data;
    },
  });

  return (
    <section className="py-20 bg-secondary/30">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            What You'll Get
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Here's a preview from this week — curated insights delivered
            straight to your inbox
          </p>
        </div>

        {isLoading ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
            {[...Array(6)].map((_, i) => (
              <div
                key={i}
                className="bg-card rounded-xl p-6 shadow-md animate-pulse"
              >
                <div className="h-4 bg-muted rounded w-1/3 mb-3" />
                <div className="h-6 bg-muted rounded w-full mb-3" />
                <div className="h-4 bg-muted rounded w-full mb-2" />
                <div className="h-4 bg-muted rounded w-2/3" />
              </div>
            ))}
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
            {articles?.map((article, index) => (
              <div
                key={article.id}
                className="animate-fade-in"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <ArticleCard
                  flag={article.source_country}
                  source={article.source_name}
                  title={article.title}
                  summary={article.summary}
                  category={article.category}
                  categoryColor={categoryColorMap[article.category] || "industry"}
                  url={article.url || "#"}
                />
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
};
