import {Button} from "~/components/ui/button";
import {Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle} from "~/components/ui/card";
import {Badge} from "~/components/ui/badge";
import {Calendar, Download, Eye, FileText, Globe, Search, TrendingUp} from "lucide-react";
import type {Route} from "./+types/reports";
import {agentApi} from "~/lib/api";
import {Link, useLoaderData} from "react-router";
import type {ResearchReport} from "~/types";
import {getSentimentColor} from "~/components/agent-trace";


export async function loader({request}: { request: Request }) {
    const url = new URL(request.url);
    const search = url.searchParams.get("search") || undefined;
    const category = url.searchParams.get("category") || undefined;
    const reports = await agentApi.getHistory(search, category);
    return {reports};
}

export default function ReportsPage() {
    const {reports} = useLoaderData<{ reports: ResearchReport[] }>();
    return (
        <div className="space-y-8 p-6 bg-background min-h-screen animate-in fade-in duration-700">
            {/* --- HEADER: TRẠM ĐIỀU KHIỂN BÁO CÁO --- */}
            <div
                className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 border-b pb-8 border-border/50">
                <div className="space-y-2">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-primary rounded-lg shadow-xl shadow-primary/20">
                            <FileText className="text-primary-foreground" size={24}/>
                        </div>
                        <h2 className="text-4xl font-black tracking-tighter italic text-foreground uppercase">
                            Insight Reports
                        </h2>
                    </div>
                    <p className="text-muted-foreground font-medium text-sm max-w-md italic">
                        Thư viện bóc tách tri thức từ Agentic AI - Được xác thực dựa trên bằng chứng và số liệu thực
                        chứng.
                    </p>
                </div>
                <div className="flex gap-3 w-full md:w-auto">
                    <Button variant="outline"
                            className="font-bold gap-2 text-xs uppercase tracking-widest border-primary/20 hover:bg-primary/5 transition-all">
                        <Download size={14}/> Xuất báo cáo (.PDF)
                    </Button>
                </div>
            </div>

            {/* --- GRID DANH SÁCH BÁO CÁO --- */}
            {reports.length > 0 ? (
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {reports.map((report) => (
                        <Card
                            key={report.id}
                            className={`flex flex-col group transition-all duration-500 hover:-translate-y-1 border-l-4 rounded-2xl bg-card/50 backdrop-blur-sm overflow-hidden ${getSentimentColor(report.sentiment)}`}
                        >
                            <CardHeader className="p-6 pb-4">
                                <div className="flex justify-between items-start mb-4">
                                    <div className="flex flex-wrap gap-1.5">
                                        {report.categories.slice(0, 2).map(cat => (
                                            <Badge key={cat} variant="secondary"
                                                   className="text-[9px] font-black uppercase px-2 py-0">
                                                {cat}
                                            </Badge>
                                        ))}
                                    </div>
                                    <div className="text-right">
                                        <div
                                            className="text-[10px] font-black uppercase text-muted-foreground opacity-50 tracking-widest">Impact
                                        </div>
                                        <div
                                            className="text-lg font-black text-orange-500 leading-none">{report.impact_score}<span
                                            className="text-[10px]">/10</span></div>
                                    </div>
                                </div>
                                <CardTitle
                                    className="text-xl font-black italic leading-tight group-hover:text-primary transition-colors line-clamp-2 tracking-tight">
                                    {report.title}
                                </CardTitle>
                                <CardDescription
                                    className="line-clamp-3 pt-3 text-sm font-medium leading-relaxed italic opacity-80">
                                    {report.summary}
                                </CardDescription>
                            </CardHeader>

                            <CardContent className="px-6 flex-1">
                                <div className="space-y-4">
                                    <div
                                        className="flex items-center text-[10px] font-bold text-muted-foreground gap-5 uppercase tracking-tighter">
                                        <span className="flex items-center gap-1.5"><Calendar size={12}
                                                                                              className="text-primary"/> {new Date(report.created_at).toLocaleDateString('vi-VN')}</span>
                                        <span className="flex items-center gap-1.5"><TrendingUp size={12}
                                                                                                className="text-primary"/> {report.sentiment}</span>
                                    </div>
                                    <div className="flex flex-wrap gap-2 pt-2">
                                        {report.regions.map(r => (
                                            <span key={r}
                                                  className="text-[9px] font-black text-primary/60 flex items-center gap-1 uppercase">
                                                <Globe size={10}/> {r}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            </CardContent>

                            <CardFooter className="p-6 border-t border-border/50 bg-muted/20">
                                <Button asChild variant="default"
                                        className="w-full gap-2 font-black text-xs uppercase tracking-widest shadow-lg shadow-primary/10">
                                    <Link to={`/reports/${report.id}?view=news`}>
                                        <Eye size={16}/> Xem chi tiết bóc tách
                                    </Link>
                                </Button>
                            </CardFooter>
                        </Card>
                    ))}
                </div>
            ) : (
                <div className="py-32 text-center flex flex-col items-center gap-4 opacity-20">
                    <Search size={64} className="animate-pulse"/>
                    <p className="font-black uppercase tracking-[0.5em] text-sm">No_Reports_Found_In_Registry</p>
                </div>
            )}
        </div>
    )
}