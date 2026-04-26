import {Activity, ArrowRight, Info, Loader2, ShieldCheck, Terminal, Zap} from "lucide-react";
import {Button} from "~/components/ui/button";
import {Link, useFetcher} from "react-router";
import {Card, CardContent} from "~/components/ui/card";
import {agentApi} from "~/lib/api";
import {ScrollArea} from "~/components/ui/scroll-area";
import {Badge} from "~/components/ui/badge";
import type {ResearchReport} from "~/types";

type ActionData =
    | { success: true; report: ResearchReport }
    | { success: false; error: string };

export async function action({request}: { request: Request }) {
    const formData = await request.formData();
    const topic = formData.get("topic") as string;

    try {
        const report = await agentApi.startResearch(topic, true);
        return {success: true, report};
    } catch (error) {
        return {success: false, error: "Agent protocol failure: Không thể truy cập luồng dữ liệu."};
    }
}

export default function ResearchCenter() {
    const fetcher = useFetcher<ActionData>();
    const isRunning = fetcher.state !== "idle";
    const result = fetcher.data;
    return (
        <div className="h-full bg-background flex flex-col overflow-y-auto relative">
            {/* Grid background thích ứng theme */}
            <div
                className="absolute inset-0 bg-[radial-gradient(hsl(var(--muted-foreground)/0.15)_1px,transparent_1px)] bg-size-[24px_24px] pointer-events-none"/>

            <div className="relative p-8 max-w-4xl mx-auto w-full space-y-8 animate-in fade-in duration-700">

                {/* HEADER SECTION */}
                <div className="space-y-2 border-l-4 border-primary pl-6">
                    <h1 className="text-4xl font-black flex items-center gap-3 italic tracking-tighter text-foreground">
                        <Activity className="text-primary animate-pulse" size={32}/>
                        MAESTRO DEEP SCANNER
                    </h1>
                    <p className="text-muted-foreground text-xs font-mono uppercase tracking-[0.3em]">
                        Advanced_Knowledge_Extraction_Protocol
                    </p>
                </div>

                {/* FORM SECTION */}
                <Card className="bg-card/50 backdrop-blur-xl border-border shadow-2xl rounded-[2rem] overflow-hidden">
                    <CardContent className="p-8">
                        <fetcher.Form method="post" className="space-y-6">
                            <div className="space-y-3">
                                <div className="flex justify-between items-center px-1">
                                    <label className="text-[10px] font-black uppercase tracking-widest text-primary">
                                        Research_Target_Prompt
                                    </label>
                                    <Badge variant="outline"
                                           className="text-[9px] opacity-60 font-mono">ENGINE_v1.5</Badge>
                                </div>
                                <textarea
                                    name="topic"
                                    required
                                    className="w-full min-h-35 bg-muted/50 border-input rounded-2xl p-5 text-sm text-foreground focus:ring-2 ring-primary/50 outline-none transition-all placeholder:text-muted-foreground/40 font-medium"
                                    placeholder="Ví dụ: Phân tích sự dịch chuyển từ Microservices sang Monolith của các tập đoàn Tech năm 2025..."
                                />
                            </div>

                            <Button
                                type="submit"
                                className="w-full h-14 gap-3 font-black text-sm tracking-widest bg-primary text-primary-foreground hover:opacity-90 shadow-[0_10px_20px_-10px_rgba(hsl(var(--primary)),0.5)] transition-all"
                                disabled={isRunning}
                            >
                                {isRunning ? (
                                    <Loader2 className="animate-spin" size={20}/>
                                ) : (
                                    <Zap size={20} className="fill-current"/>
                                )}
                                {isRunning ? "AGENT_EXECUTING_WORKFLOW..." : "KÍCH HOẠT QUY TRÌNH MAESTRO"}
                            </Button>
                        </fetcher.Form>
                    </CardContent>
                </Card>

                {/* LOGS & RESULTS SECTION */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pb-10">
                    {/* TRACE LOG */}
                    <Card
                        className="dark:bg-black border-border rounded-2xl overflow-hidden shadow-2xl">
                        <div className="p-4 border-b border-white/5 bg-white/3 flex items-center justify-between">
                            <div
                                className="flex items-center gap-2 text-[10px] font-black text-emerald-500 uppercase tracking-tighter">
                                <Terminal size={14}/> System_Trace_Log
                            </div>
                            <div
                                className={`w-2 h-2 rounded-full ${isRunning ? "bg-emerald-500 animate-pulse" : "bg-zinc-700"}`}/>
                        </div>
                        <ScrollArea className="h-48 p-5 font-mono text-[10px] leading-relaxed">
                            <div className="space-y-2">
                                {isRunning ? (
                                    <>
                                        <p className="text-emerald-500/80">[{new Date().toLocaleTimeString()}] Maestro
                                            Orchestrator initialized...</p>
                                        <p className="text-emerald-500/60">[{new Date().toLocaleTimeString()}] Strategy:
                                            Reasoning with ReAct Loop...</p>
                                        <p className="text-emerald-500/40">[{new Date().toLocaleTimeString()}]
                                            Searching: Multi-source Signal Extraction...</p>
                                        <p className="text-blue-400 animate-pulse">[{new Date().toLocaleTimeString()}]
                                            Thought: Identifying system architecture shifts...</p>
                                    </>
                                ) : result?.success ? (
                                    <p className="text-blue-400 font-bold">[{new Date().toLocaleTimeString()}]
                                        COMPLETED: Knowledge bóc tách thành công.</p>
                                ) : result?.success === false ? (
                                    <p className="text-destructive font-bold">[{new Date().toLocaleTimeString()}]
                                        ERROR: {result.error}</p>
                                ) : (
                                    <p className="text-muted-foreground/30 italic">Awaiting strategic command...</p>
                                )}
                            </div>
                        </ScrollArea>
                    </Card>

                    {/* STATUS / RESULT QUICK VIEW */}
                    <Card
                        className="bg-card border-border rounded-2xl p-6 flex flex-col justify-center items-center text-center shadow-xl">
                        {result?.success && result.report ? (
                            <div className="space-y-4 animate-in zoom-in-95 duration-500">
                                <div
                                    className="mx-auto w-14 h-14 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.2)]">
                                    <ShieldCheck size={32}/>
                                </div>
                                <div>
                                    <h3 className="text-foreground font-black text-sm uppercase tracking-tight">Intelligence
                                        Ready</h3>
                                    <p className="text-[10px] text-muted-foreground mt-1 max-w-45 mx-auto italic">
                                        Dữ liệu đã được phân luồng vào 4 trụ cột Dashboard.
                                    </p>
                                </div>
                                <Button asChild variant="outline" size="sm"
                                        className="font-black gap-2 border-primary/20 hover:bg-primary hover:text-primary-foreground transition-all">
                                    <Link to={`/reports/${result.report.id}?view=trends`}>
                                        XEM CHI TIẾT <ArrowRight size={14}/>
                                    </Link>
                                </Button>
                            </div>
                        ) : (
                            <div className="opacity-20 flex flex-col items-center gap-4 py-6">
                                <Info size={40} className="text-muted-foreground"/>
                                <p className="text-[10px] font-black uppercase tracking-[0.3em] text-muted-foreground">
                                    {isRunning ? "PROCESSING_STREAM..." : "STANDBY_MODE"}
                                </p>
                            </div>
                        )}
                    </Card>
                </div>
            </div>
        </div>
    )
}