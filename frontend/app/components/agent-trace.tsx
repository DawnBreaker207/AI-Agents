import {useEffect, useState} from "react";
import {Card, CardContent} from "~/components/ui/card";
import {Activity, CheckCircle2, Cpu, Globe, Loader2, Terminal} from "lucide-react";
import type {Sentiment} from "~/types";

export function AgentTraceLog() {
    const [steps, setSteps] = useState([
        {id: 1, text: "Khởi tạo thư viện điều phối Maestro...", status: "loading"},
        {id: 2, text: "Kết nối internet và quét các nguồn dữ liệu uy tín...", status: "pending"},
        {id: 3, text: "Phân tích xu hướng công nghệ (Tech Trends)...", status: "pending"},
        {id: 4, text: "Trích xuất dữ liệu việc làm và lương (Job Intelligence)...", status: "pending"},
        {id: 5, text: "Đánh giá Impact Score và Sentiment...", status: "pending"},
        {id: 6, text: "Đang tổng hợp báo cáo cuối cùng...", status: "pending"},
    ]);

    // Giả lập hiệu ứng chạy log để người dùng thấy AI đang làm việc
    useEffect(() => {
        const intervals = [1000, 3000, 6000, 9000, 12000, 15000];

        intervals.forEach((time, index) => {
            setTimeout(() => {
                setSteps(prev => prev.map((step, i) => {
                    if (i === index) return {...step, status: "complete"};
                    if (i === index + 1) return {...step, status: "loading"};
                    return step;
                }));
            }, time);
        });
    }, []);

    return (
        <Card className="border-slate-800 bg-slate-950 text-slate-300 font-mono text-sm overflow-hidden shadow-2xl">
            <div className="bg-slate-900 px-4 py-2 border-b border-slate-800 flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <Terminal size={14} className="text-green-500"/>
                    <span
                        className="text-xs font-bold uppercase tracking-widest text-slate-400">Maestro Execution Trace</span>
                </div>
                <div className="flex gap-1.5">
                    <div className="w-2 h-2 rounded-full bg-red-500/50"/>
                    <div className="w-2 h-2 rounded-full bg-yellow-500/50"/>
                    <div className="w-2 h-2 rounded-full bg-green-500/50"/>
                </div>
            </div>
            <CardContent className="p-6 space-y-3">
                {steps.map((step) => (
                    <div key={step.id} className="flex items-start gap-3">
                        {step.status === "complete" ? (
                            <CheckCircle2 size={16} className="text-green-500 shrink-0 mt-0.5"/>
                        ) : step.status === "loading" ? (
                            <Loader2 size={16} className="text-blue-500 animate-spin shrink-0 mt-0.5"/>
                        ) : (
                            <div className="w-4 h-4 rounded-full border border-slate-800 shrink-0 mt-0.5"/>
                        )}
                        <span className={step.status === "complete" ? "text-slate-200" :
                            step.status === "loading" ? "text-blue-400 animate-pulse" : "text-slate-600"}>
                            {step.text}
                        </span>
                    </div>
                ))}

                {/* Simulated live activity sensor */}
                <div
                    className="pt-4 mt-4 border-t border-slate-900 flex items-center justify-between text-[10px] text-slate-500 uppercase tracking-tighter">
                    <div className="flex items-center gap-2">
                        <Activity size={12} className="text-red-500"/>
                        <span>System Load: 14%</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <Globe size={12} className="text-blue-500"/>
                        <span>Sources: Scanning Internet...</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <Cpu size={12} className="text-purple-500"/>
                        <span>Memory: 1.2GB/4.0GB</span>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}

export const getSentimentColor = (sentiment: Sentiment) => {
    switch (sentiment) {
        case "Tích cực":
            return "bg-green-500/10 text-green-500 border-green-500/20";
        case "Tiêu cực":
            return "bg-red-500/10 text-red-500 border-red-500/20";
        case "Trung tính":
            return "bg-blue-500/10 text-blue-500 border-blue-500/20";
        default:
            return "bg-slate-500/10 text-slate-500 border-slate-500/20";
    }
};