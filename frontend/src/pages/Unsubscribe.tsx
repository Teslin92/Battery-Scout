import { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { Battery, CheckCircle, XCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { verifyUnsubscribeToken, confirmUnsubscribe } from "@/lib/api";
import { toast } from "sonner";

type UnsubscribeState = "loading" | "confirm" | "success" | "error" | "invalid";

const Unsubscribe = () => {
  const [searchParams] = useSearchParams();
  const [state, setState] = useState<UnsubscribeState>("loading");
  const [email, setEmail] = useState<string | null>(null);
  const [error, setError] = useState<string>("");

  const token = searchParams.get("token");

  useEffect(() => {
    if (!token) {
      setState("invalid");
      return;
    }

    // Verify token and extract email
    verifyToken(token);
  }, [token]);

  const verifyToken = async (token: string) => {
    try {
      const response = await verifyUnsubscribeToken(token);

      if (!response.valid || !response.email) {
        setState("invalid");
        return;
      }

      setEmail(response.email);
      setState("confirm");
    } catch (e) {
      console.error("Token verification error:", e);
      setState("invalid");
    }
  };

  const handleUnsubscribe = async () => {
    if (!email) return;

    setState("loading");

    try {
      const response = await confirmUnsubscribe(email);

      if (response.success) {
        setState("success");
        toast.success(response.message);
      } else {
        setError(response.message || "Failed to unsubscribe");
        setState("error");
      }
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : "An unexpected error occurred. Please try again.";
      setError(errorMessage);
      setState("error");
      toast.error(errorMessage);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white/10 backdrop-blur-lg rounded-2xl p-8 text-center">
        {/* Logo */}
        <div className="flex items-center justify-center gap-2 mb-6">
          <Battery className="w-8 h-8 text-green-400" />
          <span className="text-2xl font-bold text-white">Battery Brief</span>
        </div>

        {/* Loading State */}
        {state === "loading" && (
          <div className="space-y-4">
            <Loader2 className="w-12 h-12 text-purple-400 animate-spin mx-auto" />
            <p className="text-gray-300">Processing your request...</p>
          </div>
        )}

        {/* Confirm State */}
        {state === "confirm" && (
          <div className="space-y-6">
            <h1 className="text-2xl font-bold text-white">Unsubscribe</h1>
            <p className="text-gray-300">
              Are you sure you want to unsubscribe{" "}
              <span className="text-purple-300 font-medium">{email}</span> from
              Battery Brief updates?
            </p>
            <div className="flex flex-col gap-3">
              <Button
                onClick={handleUnsubscribe}
                variant="destructive"
                className="w-full"
              >
                Yes, Unsubscribe
              </Button>
              <Link to="/">
                <Button variant="outline" className="w-full bg-white/10 border-white/20 text-white hover:bg-white/20">
                  No, Keep Me Subscribed
                </Button>
              </Link>
            </div>
          </div>
        )}

        {/* Success State */}
        {state === "success" && (
          <div className="space-y-6">
            <CheckCircle className="w-16 h-16 text-green-400 mx-auto" />
            <h1 className="text-2xl font-bold text-white">Unsubscribed</h1>
            <p className="text-gray-300">
              You've been successfully unsubscribed from Battery Brief. We're
              sorry to see you go!
            </p>
            <p className="text-gray-400 text-sm">
              Changed your mind? You can always{" "}
              <Link to="/" className="text-purple-300 hover:text-purple-200 underline">
                subscribe again
              </Link>
              .
            </p>
          </div>
        )}

        {/* Error State */}
        {state === "error" && (
          <div className="space-y-6">
            <XCircle className="w-16 h-16 text-red-400 mx-auto" />
            <h1 className="text-2xl font-bold text-white">Something Went Wrong</h1>
            <p className="text-gray-300">{error}</p>
            <Button
              onClick={() => setState("confirm")}
              variant="outline"
              className="bg-white/10 border-white/20 text-white hover:bg-white/20"
            >
              Try Again
            </Button>
          </div>
        )}

        {/* Invalid Token State */}
        {state === "invalid" && (
          <div className="space-y-6">
            <XCircle className="w-16 h-16 text-yellow-400 mx-auto" />
            <h1 className="text-2xl font-bold text-white">Invalid Link</h1>
            <p className="text-gray-300">
              This unsubscribe link is invalid or has expired. If you need help,
              please contact us.
            </p>
            <Link to="/">
              <Button className="bg-purple-600 hover:bg-purple-700">
                Go to Homepage
              </Button>
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default Unsubscribe;
