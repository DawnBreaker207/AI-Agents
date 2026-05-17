import { Link, useLocation, useMatches } from "react-router";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "~/components/ui/sidebar";
import { 
  Rss as RssIcon, 
  FileText as FileTextIcon, 
  FlaskConical as FlaskConicalIcon, 
  Radio as RadioIcon, 
  LayoutDashboard as LayoutDashboardIcon,
  Radar as RadarIcon,
  Briefcase as BriefcaseIcon
} from "lucide-react";
import { ModeToggle } from "~/components/mode-toggle";
import type { FeedMetrics } from "~/types";

const MAIN_ITEMS = [
  { to: "/dashboard", label: "Tổng quan thị trường", icon: LayoutDashboardIcon, badgeKey: null },
  { to: "/feed",      label: "Live News Feed",       icon: RssIcon,             badgeKey: "keep_urgent" as const },
  { to: "/jobs",      label: "Tìm kiếm việc làm",    icon: BriefcaseIcon,       badgeKey: null },
  { to: "/reports",   label: "Báo cáo chiến lược",   icon: FileTextIcon,        badgeKey: "processed" as const   },
  { to: "/research",  label: "Nghiên cứu chuyên sâu",icon: FlaskConicalIcon,    badgeKey: null                   },
] as const;

const CONFIG_ITEMS = [
  { to: "/sources",   label: "Quản lý nguồn tin",    icon: RadioIcon,           badgeKey: null },
] as const;

export function AppSidebar() {
  const location = useLocation();
  
  // Safe extraction of metrics from parent layout loader using useMatches
  const matches = useMatches();
  const layoutMatch = matches.find((m) => m.data && typeof m.data === "object" && "metrics" in m.data);
  const metrics = (layoutMatch?.data as { metrics: FeedMetrics })?.metrics || {
    total_today: 0,
    keep_urgent: 0,
    keep: 0,
    watch: 0,
    trash: 0,
    processed: 0,
    last_run_at: null,
  };

  const renderMenuItem = (item: typeof MAIN_ITEMS[number] | typeof CONFIG_ITEMS[number]) => {
    const isActive = location.pathname === item.to || location.pathname.startsWith(item.to + "/");
    const count = item.badgeKey ? metrics[item.badgeKey] : 0;

    return (
      <SidebarMenuItem key={item.to}>
        <SidebarMenuButton
          asChild
          className="w-full"
        >
          <Link
            to={item.to}
            className={`text-[13px] rounded-md px-2 py-1.5 w-full flex items-center gap-2 transition-colors ${
              isActive
                ? "bg-secondary text-foreground font-medium"
                : "text-muted-foreground hover:bg-secondary/60 hover:text-foreground"
            }`}
          >
            <item.icon className="w-4 h-4 shrink-0" />
            <span>{item.label}</span>
            {count > 0 && item.badgeKey === "keep_urgent" && (
              <span className="ml-auto text-[10px] font-medium px-1.5 py-0.5 rounded-full bg-red-50 text-red-700 dark:bg-red-950 dark:text-red-300">
                {count}
              </span>
            )}
            {count > 0 && item.badgeKey === "processed" && (
              <span className="ml-auto text-[10px] font-medium px-1.5 py-0.5 rounded-full bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300">
                {count}
              </span>
            )}
          </Link>
        </SidebarMenuButton>
      </SidebarMenuItem>
    );
  };

  return (
    <Sidebar className="w-[200px] border-r border-border/50 shrink-0 bg-background h-full flex flex-col justify-between" collapsible="none">
      {/* Header */}
      <SidebarHeader className="p-0 shrink-0">
        <div className="flex items-center gap-2 px-4 py-3 border-b border-border/50">
          <div className="w-[22px] h-[22px] rounded-[5px] bg-foreground flex items-center justify-center">
            <RadarIcon className="w-3 h-3 text-background" />
          </div>
          <span className="text-[13px] font-medium text-foreground tracking-tight">
            Tech<span className="text-muted-foreground font-normal">Scout</span>
          </span>
        </div>
      </SidebarHeader>

      {/* Content */}
      <SidebarContent className="p-2 flex-1 overflow-y-auto">
        <div className="flex flex-col gap-4">
          
          {/* Main items */}
          <div className="flex flex-col">
            <p className="text-[10px] font-medium text-muted-foreground/60 uppercase tracking-widest px-2 pt-3 pb-1">
              Main
            </p>
            <SidebarMenu>
              {MAIN_ITEMS.map(renderMenuItem)}
            </SidebarMenu>
          </div>

          {/* Config items */}
          <div className="flex flex-col">
            <p className="text-[10px] font-medium text-muted-foreground/60 uppercase tracking-widest px-2 pt-3 pb-1">
              Config
            </p>
            <SidebarMenu>
              {CONFIG_ITEMS.map(renderMenuItem)}
            </SidebarMenu>
          </div>

        </div>
      </SidebarContent>

      {/* Footer */}
      <SidebarFooter className="border-t border-border/50 p-2 shrink-0 flex items-center justify-between">
        <div className="flex items-center gap-2 w-full justify-between">
          <span className="text-[11px] text-muted-foreground/50 font-medium pl-2">v1.5</span>
          <ModeToggle />
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}