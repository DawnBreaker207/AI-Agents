import {Button} from "~/components/ui/button";
import {Activity, Database, Plus, Search} from "lucide-react";
import {Badge} from "~/components/ui/badge";
import {agentApi} from "~/lib/api";
import {useLoaderData} from "react-router";
import {Card, CardContent, CardHeader, CardTitle} from "~/components/ui/card";
import {ScrollArea} from "~/components/ui/scroll-area";

export async function loader() {
    const streams = await agentApi.getSignals();
    return {
        academicSignals: streams.academic
    };
}


export default function SourcesPage() {
    const {academicSignals} = useLoaderData<typeof loader>();
    return (
        <div className="flex flex-col h-[calc(100vh-(--spacing(16)))] bg-background overflow-hidden -m-6 font-sans">

            {/* --- HEADER: INGESTION CONTROL (shrink-0) --- */}
            <div
                className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 border-b pb-8 border-border/50 px-8 pt-8 shrink-0">
                <div className="space-y-2">
                    <div className="flex items-center gap-3 text-primary">
                        <div className="p-2 bg-primary rounded-lg shadow-lg shadow-primary/20">
                            <Database className="text-primary-foreground" size={24}/>
                        </div>
                        <h2 className="text-4xl font-black tracking-tighter uppercase italic">
                            Knowledge Ingestion
                        </h2>
                    </div>
                    <p className="text-muted-foreground font-medium text-sm max-w-2xl">
                        Hệ thống nạp dữ liệu tuyến tính cấp cao. Giám sát toàn bộ kết quả bóc tách học thuật từ các
                        nguồn tri thức đã xác thực.
                    </p>
                </div>
                <Button
                    className="font-black gap-2 text-xs uppercase tracking-widest shadow-lg shadow-primary/20 h-11 px-6">
                    <Plus size={16}/> Add New Source Node
                </Button>
            </div>

            {/* --- MAIN CONTENT: FULL WIDTH CARD --- */}
            <div className="flex-1 min-h-0 p-8">
                <Card
                    className="rounded-[2.5rem] border-muted/50 overflow-hidden bg-zinc-950 text-white shadow-2xl relative flex flex-col h-full w-full">
                    <div
                        className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(79,70,229,0.1),transparent)] pointer-events-none"/>

                    <CardHeader className="border-b border-white/5 p-6 bg-white/5 relative z-10 shrink-0">
                        <CardTitle
                            className="text-[10px] font-black uppercase tracking-[0.3em] flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <Activity size={18} className="text-rose-500 animate-pulse"/>
                                <span className="text-slate-200">Extracted Intelligence Stream</span>
                            </div>
                            <div className="flex items-center gap-4">
                                <Badge variant="outline"
                                       className="text-[9px] border-emerald-500/30 text-emerald-500 font-mono h-6 bg-emerald-500/5 px-3">
                                    NODE_ID: ACADEMIC_MASTER
                                </Badge>
                                <Badge variant="outline"
                                       className="text-[9px] border-white/20 text-white font-mono h-6 px-3">
                                    API_ACTIVE
                                </Badge>
                            </div>
                        </CardTitle>
                    </CardHeader>

                    <ScrollArea className="flex-1 min-h-0 relative z-10 w-full">
                        <CardContent className="p-8 space-y-6 max-w-5xl">
                            {academicSignals.length > 0 ? academicSignals.map((signal: any, idx: number) => (
                                <div key={`${signal.id}-${idx}`}
                                     className="group flex flex-col space-y-3 p-6 rounded-[1.5rem] bg-white/2 border border-white/5 hover:border-indigo-500/40 hover:bg-white/4 transition-all duration-500 w-full min-w-0 overflow-hidden shadow-sm">

                                    <div className="flex justify-between items-center gap-4 w-full shrink-0">
                                        <div className="flex items-center gap-3">
                                            <Badge
                                                className="bg-indigo-600 text-white border-none text-[9px] font-black uppercase px-3 py-0.5 tracking-widest">
                                                {signal.badge}
                                            </Badge>
                                            <span
                                                className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-tighter">
                                                Verified_Signal_ID_{signal.id}
                                            </span>
                                        </div>
                                        <span
                                            className="text-[10px] font-mono opacity-30 font-bold uppercase whitespace-nowrap">
                                            {new Date(signal.time).toLocaleDateString()} — {new Date(signal.time).toLocaleTimeString()}
                                        </span>
                                    </div>
                                    <h4 className="text-xl md:text-2xl font-black leading-tight text-slate-100 group-hover:text-indigo-400 transition-colors wrap-break-word whitespace-normal w-full tracking-tighter">
                                        {signal.title}
                                    </h4>

                                    <p className="text-sm md:text-base text-slate-400 leading-relaxed italic border-l-2 border-white/10 pl-6 wrap-break-word whitespace-normal w-full max-w-4xl opacity-80 group-hover:opacity-100 transition-opacity">
                                        {signal.content}
                                    </p>

                                    <div className="flex items-center gap-6 pt-4 shrink-0">
                                        <div className="flex items-center gap-2">
                                            <div
                                                className="w-1.5 h-1.5 rounded-full bg-indigo-500 shadow-[0_0_8px_rgba(99,102,241,0.8)]"/>
                                            <span
                                                className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Source_Protocol: Verified</span>
                                        </div>
                                        <Button variant="link"
                                                className="p-0 h-auto text-[10px] font-black text-indigo-500 uppercase tracking-widest hover:text-indigo-400 flex items-center gap-2">
                                            Open Research Link <Search size={12}/>
                                        </Button>
                                    </div>
                                </div>
                            )) : (
                                <div className="py-40 text-center flex flex-col items-center gap-4 opacity-20 shrink-0">
                                    <Database size={48}/>
                                    <p className="font-black uppercase tracking-[0.5em] text-sm">Waiting_For_Ingestion_Signals...</p>
                                </div>
                            )}
                            <div className="h-10 shrink-0"/>
                            {/* Padding bottom */}
                        </CardContent>
                    </ScrollArea>
                </Card>
            </div>
        </div>
    )
}