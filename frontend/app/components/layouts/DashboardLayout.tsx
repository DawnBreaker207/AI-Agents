import { Outlet, useLocation } from "react-router";
import { SidebarProvider } from "~/components/ui/sidebar";
import { AppSidebar } from "~/components/app-sidebar";
import { ModeToggle } from "~/components/mode-toggle";
import { ChevronRight as ChevronRightIcon, Clock as ClockIcon } from "lucide-react";
import { getFeedMetrics } from "~/lib/api";
import { relativeTime } from "~/lib/utils";
import type { Route } from "./+types/DashboardLayout";

export async function loader({ request }: Route.LoaderArgs) {
  try {
    const metrics = await getFeedMetrics();
    return { metrics };
  } catch (err) {
    console.error("DashboardLayout loader failed, returning fallback metrics:", err);
    return {
      metrics: {
        total_today: 0,
        keep_urgent: 0,
        keep: 0,
        watch: 0,
        trash: 0,
        processed: 0,
        last_run_at: null,
      }
    };
  }
}

export default function DashboardLayout({ loaderData }: Route.ComponentProps) {
  const { metrics } = loaderData;
  const location = useLocation();
  
  // Format current page label from pathname
  const pathParts = location.pathname.split("/").filter(Boolean);
  const pageLabel = pathParts[0] === "feed" ? "Live Feed"
                  : pathParts[0] === "reports" ? "Báo cáo"
                  : pathParts[0] === "research" ? "Nghiên cứu"
                  : pathParts[0] === "sources" ? "Nguồn tin"
                  : pathParts[0] === "dashboard" ? "Dashboard"
                  : "Tổng quan";

  return (
    <SidebarProvider className="h-screen overflow-hidden flex bg-background">
      <AppSidebar />
      
      <div className="flex-1 flex flex-col h-full overflow-hidden min-w-0">
        {/* Topbar (48px / h-12 fixed height) */}
        <header className="h-12 border-b border-border/50 bg-background flex items-center justify-between px-5 shrink-0 sticky top-0 z-20">
          {/* Trái: breadcrumb */}
          <div className="flex items-center gap-1.5 text-[13px]">
            <span className="text-muted-foreground">TechScout</span>
            <ChevronRightIcon className="w-3.5 h-3.5 text-muted-foreground/40" />
            <span className="font-medium text-foreground">{pageLabel}</span>
          </div>

          {/* Phải: status pills */}
          <div className="flex items-center gap-2">
            {/* Pipeline running indicator */}
            <span className="flex items-center gap-1.5 text-[11px] border border-border/50 rounded-full px-2.5 py-1 text-muted-foreground bg-secondary/20">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
              Pipeline đang chạy
            </span>

            {/* Last updated */}
            <span className="flex items-center gap-1 text-[11px] border border-border/50 rounded-full px-2.5 py-1 text-muted-foreground bg-secondary/20">
              <ClockIcon className="w-3 h-3" />
              {relativeTime(metrics.last_run_at ?? new Date().toISOString())}
            </span>

            {/* Mode toggle — góc phải cùng */}
            <ModeToggle />
          </div>
        </header>

        {/* Content area: independent scroll, p-5 wrapper */}
        <main className="flex-1 overflow-y-auto p-5 min-w-0">
          <Outlet />
        </main>
      </div>
    </SidebarProvider>
  );
}