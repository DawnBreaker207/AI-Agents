import type {ReactNode} from "react";
import {Outlet, useLocation} from "react-router";
import {SidebarInset, SidebarProvider, SidebarTrigger} from "~/components/ui/sidebar";
import {AppSidebar} from "~/components/app-sidebar";
import {Separator} from "~/components/ui/separator";
import {
    Breadcrumb,
    BreadcrumbItem,
    BreadcrumbLink,
    BreadcrumbList,
    BreadcrumbPage,
    BreadcrumbSeparator
} from "~/components/ui/breadcrumb";
import {Bell, Search} from "lucide-react";
import {Input} from "~/components/ui/input";
import {Avatar, AvatarFallback, AvatarImage} from "~/components/ui/avatar";
import {TooltipProvider} from "~/components/ui/tooltip";
import {ModeToggle} from "~/components/mode-toggle";


export function DashboardLayout() {
    const location = useLocation();
    const pathname = location.pathname.split("/").pop();

    return (
        <SidebarProvider>
            <TooltipProvider delayDuration={0}>


                <AppSidebar/>
                <SidebarInset>
                    {/* HEADER */}
                    <header
                        className="flex h-16 shrink-0 items-center gap-2 border-b px-4 justify-between sticky top-0 bg-background z-10">
                        <div className="flex items-center gap-2">
                            <SidebarTrigger className="-ml-1"/>
                            <Separator orientation="vertical" className="mr-2 h-4"/>
                            <Breadcrumb>
                                <BreadcrumbList>
                                    <BreadcrumbItem className="hidden md:block">
                                        <BreadcrumbLink href="/dashboard">Dashboard</BreadcrumbLink>
                                    </BreadcrumbItem>
                                    <BreadcrumbSeparator className="hidden md:block"/>
                                    <BreadcrumbItem>
                                        <BreadcrumbPage className="capitalize">{pathname || "Overview"}</BreadcrumbPage>
                                    </BreadcrumbItem>
                                </BreadcrumbList>
                            </Breadcrumb>
                        </div>

                        <div className="flex items-center gap-4">

                            {/* Search Bar */}
                            <div className="relative w-64 hidden lg:block">
                                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground"/>
                                <Input
                                    type="search"
                                    placeholder="Ask Agent anything..."
                                    className="pl-8 bg-muted/50 focus-visible:ring-1"
                                />
                            </div>

                            <button className="relative p-2 text-muted-foreground hover:bg-muted rounded-full">
                                <Bell size={20}/>
                                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-destructive rounded-full"></span>
                            </button>

                            <ModeToggle/>

                            <Avatar className="h-9 w-9 border">
                                <AvatarImage src="https://github.com/shadcn.png"/>
                                <AvatarFallback>AD</AvatarFallback>
                            </Avatar>
                        </div>
                    </header>

                    <main className="flex flex-1 flex-col gap-4 p-6 overflow-y-auto">
                        <Outlet/>
                    </main>
                </SidebarInset>
            </TooltipProvider>
        </SidebarProvider>
    );
}