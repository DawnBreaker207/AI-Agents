import {CheckCircle2, Loader2, Search, Send, Terminal} from "lucide-react";
import type {Route} from "./+types/research";
import {Button} from "~/components/ui/button";
import {Badge} from "~/components/ui/badge";
import {ScrollArea} from "~/components/ui/scroll-area";

export async function action({request}: Route.ActionArgs) {
    const formData = await request.formData();
    const prompt = formData.get("prompt") as string;
    return {success: true};
}

export default function ResearchCenter() {
    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-180px)]">
            {/* Cột trái: Nhập yêu cầu */}
            <div className="lg:col-span-1 space-y-4 flex flex-col">
                <div className="p-4 border rounded-xl bg-card space-y-4">
                    <h3 className="font-bold flex items-center gap-2 text-primary">
                        <Search size={18}/> New Research Task
                    </h3>
                    <p className="text-xs text-muted-foreground italic">
                        Yêu cầu Agent tìm kiếm thông tin ngách hoặc phân tích dữ liệu cụ thể.
                    </p>
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Research Prompt</label>
                        <textarea
                            placeholder="Ví dụ: Phân tích mức lương của Golang Developer tại Hà Nội và so sánh với TP.HCM..."
                            className="min-h-[150px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                        />
                    </div>
                    <Button className="w-full gap-2">
                        <Send size={16}/> Run Agentic Task
                    </Button>
                </div>
            </div>

            {/* Cột phải: Execution Tracing (Log hệ thống) */}
            <div
                className="lg:col-span-2 border rounded-xl bg-slate-950 text-slate-50 flex flex-col overflow-hidden shadow-2xl">
                <div className="p-3 border-b border-slate-800 bg-slate-900 flex justify-between items-center px-6">
                    <div className="flex items-center gap-2">
                        <Terminal size={16} className="text-green-400"/>
                        <span className="text-xs font-mono font-bold uppercase tracking-widest text-slate-400">Agent Trace Logs</span>
                    </div>
                    <Badge variant="outline"
                           className="text-[10px] border-green-900 text-green-400 bg-green-950">Active</Badge>
                </div>

                <ScrollArea className="flex-1 p-6 font-mono text-sm leading-relaxed">
                    <div className="space-y-3">
                        <p className="text-slate-500">[{new Date().toLocaleTimeString()}] System: Agent "MarketAnalyst"
                            initialized.</p>
                        <p className="flex items-center gap-2">
                            <CheckCircle2 size={14} className="text-green-500"/>
                            Step 1: Browsing 12 sources for "Golang Salary Vietnam"...
                        </p>
                        <p className="flex items-center gap-2">
                            <CheckCircle2 size={14} className="text-green-500"/>
                            Step 2: Found 3 relevant reports from TopDev, Navigos, and LinkedIn.
                        </p>
                        <p className="flex items-center gap-2 text-blue-400">
                            <Loader2 size={14} className="animate-spin"/>
                            Step 3: Extracting salary data and normalization...
                        </p>
                        <p className="text-slate-500 animate-pulse">_</p>
                    </div>
                </ScrollArea>
            </div>
        </div>
    )
}