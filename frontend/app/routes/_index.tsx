import {Link, useFetcher, useLoaderData} from "react-router";
import {Input} from "~/components/ui/input";
import {Button} from "~/components/ui/button";
import {Card, CardContent} from "~/components/ui/card";
import {Activity, Briefcase, Cpu, MessageSquare, Microscope, Send, X} from "lucide-react";
import {Badge} from "~/components/ui/badge";
import {ScrollArea} from "~/components/ui/scroll-area";
import {agentApi} from "~/lib/api";
import {useState} from "react";


export async function loader() {
    const streams = await agentApi.getSignals();
    return {streams};
}

export default function Dashboard() {
    const {streams} = useLoaderData<typeof loader>();
    const [isAssistantOpen, setIsAssistantOpen] = useState(false);
    const chatFetcher = useFetcher<{ answer: string }>();
    return (
        <div
            className="flex flex-col h-[calc(100vh-(--spacing(16))-(--spacing(12)))] overflow-hidden -m-6 bg-background">

            {/* SUB-HEADER */}
            <div className="h-10 border-b bg-muted/30 flex items-center justify-between px-6 shrink-0 z-10">
                <div className="flex items-center gap-4">
                    <div
                        className="flex items-center gap-2 text-[10px] font-bold text-muted-foreground uppercase tracking-widest">
                        <div
                            className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_#10b981]"/>
                        Automated_Market_Stream
                    </div>
                </div>
                <div className="flex items-center gap-4 text-[9px] font-mono opacity-50 font-bold">
                    <span>SYNC_LEVEL: STABLE</span>
                </div>
            </div>

            {/* 4-COLUMN GRID */}
            <div
                className="flex-1 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 divide-x border-t min-h-0 overflow-hidden">
                <StreamColumn title="Market Pulse" icon={<Activity size={14} className="text-blue-500"/>}
                              items={streams.news} type="news"/>
                <StreamColumn title="Employment Intel" icon={<Briefcase size={14} className="text-emerald-500"/>}
                              items={streams.jobs} type="jobs"/>
                <StreamColumn title="Academic/Research" icon={<Microscope size={14} className="text-orange-500"/>}
                              items={streams.academic} type="academic"/>
                <StreamColumn title="Tech Trends" icon={<Cpu size={14} className="text-indigo-500"/>}
                              items={streams.trends} type="trends"/>
            </div>

            {/* FLOATING ASSISTANT */}
            <div className="fixed bottom-6 right-6 z-50">
                {isAssistantOpen ? (
                    <Card
                        className="w-80 h-112.5 shadow-2xl flex flex-col border-primary/20 animate-in slide-in-from-bottom-5 duration-300">
                        <header
                            className="p-4 border-b bg-primary text-primary-foreground flex flex-row justify-between items-center shrink-0 rounded-t-xl">
                            <div className="flex items-center gap-2 text-xs font-black uppercase tracking-widest">
                                <MessageSquare size={14}/> Maestro Analyst
                            </div>
                            <Button variant="ghost" size="icon" className="h-6 w-6 hover:bg-white/20"
                                    onClick={() => setIsAssistantOpen(false)}>
                                <X size={14}/>
                            </Button>
                        </header>
                        <ScrollArea className="flex-1 p-4">
                            <div className="space-y-4">
                                <div
                                    className="text-[11px] leading-relaxed p-3 rounded-lg bg-muted border italic text-muted-foreground">
                                    "Chào! Tôi đang giám sát 4 luồng dữ liệu nghiệp vụ. Bạn cần tôi bóc tách điều gì?"
                                </div>
                                {chatFetcher.data?.answer && (
                                    <div
                                        className="text-[11px] leading-relaxed p-3 rounded-lg bg-primary/5 border border-primary/10 text-foreground wrap-break-word">
                                        {chatFetcher.data.answer}
                                    </div>
                                )}
                            </div>
                        </ScrollArea>
                        <div className="p-3 border-t bg-muted/30 shrink-0">
                            <chatFetcher.Form method="post" action="/api/chat" className="relative">
                                <Input name="prompt" placeholder="Command..."
                                       className="text-xs h-9 pr-10 bg-background" autoComplete="off"/>
                                <Button size="icon" variant="ghost"
                                        className="absolute right-1 top-1 h-7 w-7 text-primary"><Send
                                    size={14}/></Button>
                            </chatFetcher.Form>
                        </div>
                    </Card>
                ) : (
                    <Button onClick={() => setIsAssistantOpen(true)}
                            className="h-14 w-14 rounded-full shadow-2xl bg-primary text-primary-foreground hover:scale-110 transition-transform border-none">
                        <MessageSquare size={24}/>
                    </Button>
                )}
            </div>
        </div>
    );
}

function StreamColumn({title, icon, items, type}: any) {
    return (
        <div className="flex flex-col h-full bg-muted/5 min-w-0 overflow-hidden">
            <div className="p-4 border-b flex items-center gap-2 bg-muted/20 shrink-0">
                {icon}
                <h3 className="text-[10px] font-black uppercase tracking-[0.2em] opacity-70 truncate">{title}</h3>
                <Badge variant="outline" className="ml-auto text-[8px] opacity-40">{items.length}</Badge>
            </div>
            <ScrollArea className="flex-1 overflow-y-auto">
                <div className="p-4 space-y-4">
                    {items.map((item: any) => (
                        <Card key={item.id}
                              className="bg-card border-muted/50 hover:border-primary/40 transition-all shadow-sm group w-full overflow-hidden">
                            <CardContent className="p-4 space-y-3 w-full min-w-0 overflow-hidden">
                                <div className="flex justify-between items-start gap-2">
                                    <div className="min-w-0 shrink">
                                        <Badge variant="secondary"
                                               className="text-[8px] uppercase font-black truncate inline-block max-w-25">
                                            {type === "jobs" ? item.job_details?.salary : item.sentiment}
                                        </Badge>
                                    </div>
                                    <span className="text-[9px] font-mono opacity-40 whitespace-nowrap">
                                        {new Date(item.last_updated).toLocaleTimeString([], {
                                            hour: '2-digit',
                                            minute: '2-digit'
                                        })}
                                    </span>
                                </div>

                                <h4 className="text-[12px] font-bold leading-tight group-hover:text-primary transition-colors italic break-all w-full line-clamp-3">
                                    {item.title}
                                </h4>

                                <p className="text-[11px] text-muted-foreground leading-relaxed border-l-2 border-muted pl-2 wrap-break-word overflow-hidden line-clamp-5">
                                    {type === "jobs" ? item.employment_status?.market : item.summary}
                                </p>

                                <div className="pt-1 shrink-0">
                                    <Button variant="link" asChild
                                            className="p-0 h-auto text-[10px] font-black text-primary uppercase">
                                        <Link to={`/reports/${item.id}?view=${type}`}>BÓC TÁCH CHI TIẾT →</Link>
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                    <div className="h-6 shrink-0"/>
                </div>
            </ScrollArea>
        </div>
    );
}