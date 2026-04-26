import type {Route} from "./+types/report-detail";
import {Link, useLoaderData, useSearchParams} from "react-router";
import {Button} from "~/components/ui/button";
import {agentApi} from "~/lib/api";
import {Activity, Briefcase, Calendar, ChevronLeft, Cpu, ExternalLink, Microscope, ShieldCheck} from "lucide-react";
import {Badge} from "~/components/ui/badge";
import {Separator} from "~/components/ui/separator";
import remarkGfm from "remark-gfm";
import ReactMarkdown from "react-markdown";

export async function loader({params}: Route.LoaderArgs) {
    const report = await agentApi.getReportById(params.id);
    if (!report) throw new Response("Not Found", {status: 404});
    return {report};
}

export default function ReportDetail() {
    const {report} = useLoaderData<typeof loader>();
    const [searchParams] = useSearchParams();
    const view = searchParams.get("view") || "news"; // Lấy type từ URL

    return (
        <div className="min-h-screen bg-background text-foreground pb-20 overflow-x-hidden">
            {/* STICKY HEADER CHO TRANG CHI TIẾT */}
            <div className="sticky top-0 z-50 w-full bg-background/80 backdrop-blur-md border-b">
                <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
                    <Button variant="ghost" asChild size="sm" className="gap-2 text-muted-foreground">
                        <Link to="/"><ChevronLeft size={16}/> Trở lại Dashboard</Link>
                    </Button>
                    <div className="flex items-center gap-3">
                        <Badge variant="outline" className="font-mono text-[10px]">{report.id}</Badge>
                        <Badge className="bg-primary text-[10px] uppercase tracking-tighter">Verified by Maestro</Badge>
                    </div>
                </div>
            </div>

            <article className="max-w-4xl mx-auto px-6 pt-12 space-y-10">
                {/* TIÊU ĐỀ BÁO CÁO */}
                <header className="space-y-6">
                    <div className="space-y-2">
                        <p className="text-[10px] font-black uppercase tracking-[0.3em] text-primary">
                            Strategic_Intelligence_Protocol
                        </p>
                        <h1 className="text-4xl md:text-6xl font-black tracking-tighter leading-tight italic wrap-break-word">
                            {report.title}
                        </h1>
                    </div>

                    <div
                        className="flex flex-wrap gap-6 text-[10px] font-bold text-muted-foreground uppercase tracking-widest border-y py-4">
                        <div className="flex items-center gap-2"><Calendar
                            size={14}/> {new Date(report.created_at).toLocaleDateString()}</div>
                        <div className="flex items-center gap-2"><Activity size={14}/> Impact: {report.impact_score}/10
                        </div>
                        <div className="flex items-center gap-2"><ShieldCheck size={14}/> Sắc thái: {report.sentiment}
                        </div>
                    </div>
                </header>

                {/* NỘI DUNG CHI TIẾT THEO TỪNG MỤC */}
                <div className="relative overflow-hidden rounded-[2.5rem] border bg-card shadow-2xl p-8 md:p-12">
                    <div
                        className="absolute inset-0 bg-[radial-gradient(#80808012_1px,transparent_1px)] bg-size-[20px_20px] pointer-events-none"/>

                    <div className="relative z-10">
                        {(view === "news" || view === "pulse") && (
                            <div className="space-y-8">
                                <Badge
                                    className="bg-blue-600 px-4 py-1 text-[10px] font-black uppercase tracking-widest">
                                    Market Analysis Data
                                </Badge>
                                <div className="prose prose-slate dark:prose-invert lg:prose-xl max-w-none
                                    prose-headings:font-black prose-headings:tracking-tighter prose-headings:italic
                                    prose-h3:text-primary prose-h3:mt-10 prose-h3:mb-4
                                    prose-p:leading-relaxed prose-p:text-muted-foreground prose-p:mb-6
                                    wrap-break-word overflow-hidden">
                                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                        {report.summary}
                                    </ReactMarkdown>
                                </div>
                            </div>
                        )}

                        {/* 2. VIEW TECH TRENDS */}
                        {view === "trends" && (
                            <div className="space-y-10">
                                <div
                                    className="flex items-center gap-3 text-indigo-500 font-black uppercase text-xs tracking-widest">
                                    <Cpu size={24}/> Tech Stack Evolution
                                </div>
                                <div className="grid gap-6">
                                    {report.tech_trends.map((t: any, i: number) => (
                                        <div key={i}
                                             className="group p-8 rounded-3xl bg-muted/40 border hover:border-primary/50 transition-all">
                                            <h3 className="font-black text-xl text-primary mb-4 italic tracking-tight"># {t.name}</h3>
                                            <div
                                                className="prose dark:prose-invert max-w-none text-muted-foreground leading-loose">
                                                <ReactMarkdown>{t.update}</ReactMarkdown>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* 3. VIEW EMPLOYMENT (JOB) */}
                        {view === "jobs" && (
                            <div className="space-y-12 w-full max-w-full">
                                <div
                                    className="flex items-center gap-3 text-emerald-500 font-black uppercase text-xs tracking-widest">
                                    <Briefcase size={24}/> 03. Lao động & Mức lương
                                </div>
                                <div
                                    className="bg-primary p-8 md:p-12 rounded-[3rem] text-primary-foreground shadow-2xl relative overflow-hidden w-full">
                                    <div
                                        className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -mr-32 -mt-32 blur-[80px]"/>

                                    <div className="relative z-10 space-y-8 w-full">
                                        <div className="space-y-4 w-full">
                                            <p className="text-[10px] font-black uppercase tracking-[0.3em] opacity-50">Global_Comp_Benchmark</p>
                                            <h2 className="text-xl md:text-3xl font-black tracking-tight leading-[1.3] break-words whitespace-pre-line w-full">
                                                {report.job_details.salary}
                                            </h2>
                                        </div>

                                        <div className="h-[1px] w-full bg-white/10"/>

                                        <div className="space-y-4 w-full">
                                            <p className="text-[10px] font-black uppercase tracking-widest opacity-50">Market_Intelligence_Analysis</p>
                                            <p className="text-lg md:text-xl font-medium italic leading-relaxed border-l-4 border-white/20 pl-6 break-words whitespace-normal w-full opacity-90">
                                                "{report.employment_status.market}"
                                            </p>
                                        </div>
                                    </div>
                                </div>
                                <div className="space-y-6 w-full">
                                    <p className="text-[10px] font-black uppercase tracking-widest opacity-40 italic">Essential_Skillset_Matrix</p>
                                    <div className="flex flex-col gap-4 w-full">
                                        {report.job_details.skills.map((s, index) => (
                                            <div
                                                key={index}
                                                className="group flex gap-6 p-6 bg-muted/20 border border-border rounded-2xl shadow-sm hover:border-primary/40 transition-all w-full"
                                            >
                                                <span className="text-xs font-black opacity-20 mt-1 shrink-0 font-mono">
                                                    SKILL_0{index + 1}
                                                </span>
                                                <p className="text-sm md:text-base font-bold text-foreground leading-relaxed break-words whitespace-normal w-full">
                                                    {s}
                                                </p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* 4. VIEW ACADEMIC */}
                        {view === "academic" && (
                            <div className="space-y-8">
                                <div
                                    className="flex items-center gap-3 text-orange-500 font-black uppercase text-xs tracking-widest">
                                    <Microscope size={24}/> Evidence Grounds
                                </div>
                                <div className="grid gap-4">
                                    {report.research_articles.map((art: any, i: number) => (
                                        <a key={i} href={art.url} target="_blank" rel="noreferrer"
                                           className="flex items-center justify-between p-8 border rounded-[2rem] bg-muted/20 hover:bg-primary hover:text-primary-foreground transition-all group group shadow-lg">
                                            <div className="space-y-1 pr-4">
                                                <div
                                                    className="text-[10px] font-black opacity-40 uppercase tracking-widest">Reference_0{i + 1}</div>
                                                <span
                                                    className="font-bold text-lg leading-tight block">{art.title}</span>
                                            </div>
                                            <ExternalLink size={24}
                                                          className="shrink-0 opacity-40 group-hover:opacity-100"/>
                                        </a>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                <footer className="pt-10 border-t border-dashed space-y-6">
                    <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Data_Verified_Sources</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {report.sources.map((url, i) => (
                            <a key={i} href={url} target="_blank"
                               className="text-xs font-mono text-primary hover:underline truncate bg-muted/50 p-3 rounded-xl border border-transparent hover:border-primary/20 transition-all">
                                [{i + 1}] {url}
                            </a>
                        ))}
                    </div>
                </footer>
            </article>
        </div>
    );
}