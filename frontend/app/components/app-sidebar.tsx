import {Link, useLocation} from "react-router";
import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarGroup, SidebarGroupContent, SidebarGroupLabel,
    SidebarHeader, SidebarMenu,
    SidebarMenuButton, SidebarMenuItem
} from "~/components/ui/sidebar";
import {Cpu, Database, FilePieChart, LayoutDashboard, Rss, Settings, Terminal} from "lucide-react";

const items = [
    {title: "Dashboard", url: "/", icon: LayoutDashboard},
    {title: "Live Market Feed", url: "/feed", icon: Rss},
    {title: "Insight Reports", url: "/reports", icon: FilePieChart},
    {title: "Research Center", url: "/research", icon: Terminal},
    {title: "Knowledge Sources", url: "/sources", icon: Database},
]

export function AppSidebar() {
    const location = useLocation();
    return (
        <Sidebar collapsible="icon">
            <SidebarHeader className="py-4">
                <div className="flex items-center gap-3 px-2">
                    <div className="bg-primary p-1.5 rounded-lg">
                        <Cpu className="text-primary-foreground" size={20}/>
                    </div>
                    <span className="font-bold text-lg group-data-[collapsible=icon]:hidden">
                        IT Agentic
                    </span>
                </div>
            </SidebarHeader>
            {/*    */}
            <SidebarContent>
                <SidebarGroup>
                    <SidebarGroupLabel>Menu</SidebarGroupLabel>
                    <SidebarGroupContent>
                        <SidebarMenu>
                            {items.map((item) => (
                                <SidebarMenuItem key={item.title}>
                                    <SidebarMenuButton
                                        asChild
                                        isActive={location.pathname === item.url}
                                        tooltip={item.title}
                                    >
                                        <Link to={item.url}>
                                            <item.icon/>
                                            <span>{item.title}</span>
                                        </Link>
                                    </SidebarMenuButton>
                                </SidebarMenuItem>
                            ))}
                        </SidebarMenu>
                    </SidebarGroupContent>
                </SidebarGroup>
            </SidebarContent>
            {/*    */}
            <SidebarFooter className="p-4">
                <div className="bg-muted/50 rounded-lg p-3 group-data-[collapsible=icon]:hidden">
                    <div className="flex items-center justify-between mb-1">
                        <span className="text-[10px] font-bold uppercase opacity-50">Agent Status</span>
                        <span className="relative flex h-2 w-2">
                <span
                    className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
             </span>
                    </div>
                    <p className="text-xs font-medium text-foreground">AI is Scanning...</p>
                </div>
                <SidebarMenuButton size="lg">
                    <Settings/>
                    <span>Settings</span>
                </SidebarMenuButton>
            </SidebarFooter>
        </Sidebar>
    )
}