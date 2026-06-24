"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { createBrowserClient } from "@supabase/ssr";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const supabase = createBrowserClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
    );

    const checkAuth = async () => {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      const user = session?.user;
      const isAuthRoute = pathname.startsWith("/auth");
      const isApiRoute = pathname.startsWith("/api");

      if (!user && !isAuthRoute && !isApiRoute && pathname !== "/") {
        router.replace("/auth/login");
      } else if (user && isAuthRoute) {
        router.replace("/dashboard");
      } else {
        setLoading(false);
      }
    };

    checkAuth();
  }, [pathname, router]);

  if (loading) {
    return null; // Or a loading spinner
  }

  return <>{children}</>;
}
