import {Activity, ArrowRight, ShieldCheck, Zap} from "lucide-react";
import {Button} from "~/components/ui/button";
import {ScrollArea} from "~/components/ui/scroll-area";
import {Card, CardContent} from "~/components/ui/card";
import {Badge} from "~/components/ui/badge";
import {agentApi} from "~/lib/api";
import {Link, useLoaderData} from "react-router";
import {getSentimentColor} from "~/components/agent-trace";
import {Separator} from "~/components/ui/separator";

export async function loader() {
    const streams = await agentApi.getSignals();
    return {marketSignals: [...streams.jobs]};
}


export default function MarketFeed() {
    const {marketSignals} = useLoaderData<{ marketSignals: any[] }>();

    return (
        <div className="p-6 space-y-6 bg-background min-h-screen animate-in fade-in duration-700">
            {/* --- HEADER: COMMAND CENTER STYLE --- */}
            <div
                className="flex justify-between items-center bg-zinc-950 text-white p-8 rounded-[2rem] shadow-2xl border border-white/5 relative overflow-hidden">
                <div
                    className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(79,70,229,0.15),transparent)]"/>
                <div className="relative z-10">
                    <h2 className="text-3xl font-black flex items-center gap-3 italic tracking-tighter uppercase">
                        <Activity className="text-rose-500 animate-pulse" size={32}/>
                        Live Market Monitor
                    </h2>
                    <p className="text-slate-500 text-[10px] mt-2 font-mono uppercase tracking-[0.4em]">
                        Autonomous_Signal_Extraction_v3.1
                    </p>
                </div>
                <div className="text-right relative z-10 space-y-2 hidden md:block">
                    <Badge variant="outline"
                           className="text-emerald-400 border-emerald-400/30 bg-emerald-400/5 font-mono px-4">
                        NODES: ONLINE
                    </Badge>
                    <p className="text-[9px] text-slate-600 font-bold uppercase tracking-widest">
                        Refresh: {new Date().toLocaleTimeString()}
                    </p>
                </div>
            </div>

            {/* --- FEED STREAM --- */}
            <ScrollArea className="h-[calc(100vh-280px)] pr-4">
                <div className="grid gap-6 max-w-5xl mx-auto">
                    {marketSignals.length > 0 ? marketSignals.map((item) => (
                        <Card
                            key={item.id}
                            className={`group transition-all duration-500 border-l-4 hover:translate-x-1 overflow-hidden min-w-0 ${getSentimentColor(item.badge === "Tuyển dụng" ? "Trung tính" : item.badge)}`}
                        >
                            <CardContent className="p-6 space-y-6 min-w-0">
                                {/* TOP ROW: Badge & Impact */}
                                <div className="flex justify-between items-start gap-4">
                                    <div className="flex items-center gap-4">
                                        <div className="flex flex-col">
                                            <span
                                                className="text-[10px] font-black uppercase text-muted-foreground opacity-50 mb-1 tracking-widest">Type</span>
                                            <Badge variant={item.type === "jobs" ? "default" : "secondary"}
                                                   className="font-black uppercase text-[9px] px-2 py-0 h-5">
                                                {item.badge}
                                            </Badge>
                                        </div>
                                        <Separator orientation="vertical" className="h-8 bg-border/50"/>
                                        <div className="flex flex-col">
                                            <span
                                                className="text-[10px] font-black uppercase text-muted-foreground opacity-50 tracking-widest mb-1">Time</span>
                                            <span className="text-[10px] font-mono font-bold">
                                                {new Date(item.time).toLocaleTimeString()}
                                            </span>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <span
                                            className="text-[10px] font-black text-rose-500 font-mono tracking-widest uppercase block mb-1 opacity-50">Impact</span>
                                        <span className="text-xl font-black tabular-nums">{item.impact || 0}</span>
                                    </div>
                                </div>

                                {/* CONTENT ROW: XỬ LÝ TEXT DÀI ĐỂ KHÔNG VỠ KHUNG */}
                                <div className="space-y-4 w-full min-w-0">
                                    <h4 className={`font-black tracking-tight leading-tight italic group-hover:text-primary transition-colors wrap-break-word whitespace-normal w-full
                                        ${item.type === "jobs" ? 'text-lg md:text-xl text-emerald-600 dark:text-emerald-400' : 'text-xl md:text-2xl'}`}>
                                        {item.title}
                                    </h4>

                                    {/* Summary text */}
                                    <p className="text-sm md:text-base text-muted-foreground leading-relaxed font-medium opacity-80 wrap-break-word whitespace-normal border-l-2 pl-4 border-muted">
                                        {item.content}
                                    </p>
                                </div>

                                {/* ACTION ROW */}
                                <div className="flex justify-between items-center pt-4 border-t border-border/40">
                                    <div className="flex items-center gap-2 opacity-40">
                                        <ShieldCheck size={14} className="text-primary"/>
                                        <span
                                            className="text-[9px] font-black uppercase tracking-widest">Autonomous_Verified</span>
                                    </div>
                                    <Button variant="default" size="sm" asChild
                                            className="text-[10px] font-black uppercase tracking-widest gap-2 shadow-lg shadow-primary/20 rounded-full px-5">
                                        <Link to={`/reports/${item.id}?view=${item.type}`}>
                                            Bóc tách chuyên sâu <ArrowRight size={14}/>
                                        </Link>
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    )) : (
                        <div className="py-32 text-center flex flex-col items-center gap-4 opacity-20">
                            <Zap size={64} className="animate-pulse"/>
                            <p className="font-black uppercase tracking-[0.5em] text-sm">Awaiting_Signals...</p>
                        </div>
                    )}
                </div>
            </ScrollArea>
        </div>
    )
}