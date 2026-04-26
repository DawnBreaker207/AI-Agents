import React from 'react';
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from '~/components/ui/card';
import type {ResearchReport} from "~/types";
import {BookOpen, Briefcase, ExternalLink, MapPin, Users, Zap} from "lucide-react";
import {Badge} from "~/components/ui/badge";


const SENTIMENT_CONFIG: Record<string, string> = {
    "Tích cực": "bg-green-100 text-green-700 border-green-200",
    "Tiêu cực": "bg-red-100 text-red-700 border-red-200",
    "Trung tính": "bg-blue-100 text-blue-700 border-blue-200",
};
const DEFAULT_SENTIMENT_STYLE = "bg-slate-100 text-slate-700 border-slate-200";

export function ResearchReportCard({report}: { report: ResearchReport }) {
    const sentimentColor = SENTIMENT_CONFIG[report.sentiment] || DEFAULT_SENTIMENT_STYLE;
    return (
        <div className="space-y-6">
            {/* Header Info */}
            <Card className="border-l-4 border-l-primary shadow-sm">
                <CardHeader>
                    <div className="flex justify-between items-start">
                        <div className="space-y-1">
                            <div className="flex gap-2 mb-2">
                                {report.categories.map(c => <Badge key={c} variant="secondary">{c}</Badge>)}
                                <Badge className={sentimentColor}>{report.sentiment}</Badge>
                            </div>
                            <CardTitle className="text-2xl font-bold">{report.title}</CardTitle>
                            <div className="flex items-center gap-4 text-sm text-muted-foreground pt-1">
                                <span className="flex items-center gap-1">
                                    <MapPin size={14}/> {report.regions.join(", ")}</span>
                                <span
                                    className="font-medium text-orange-600">Impact Score: {report.impact_score}/10</span>
                            </div>
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    <p className="text-slate-700 leading-relaxed italic border-l-2 pl-4">"{report.summary}"</p>
                </CardContent>
            </Card>

            {/* 4 Trụ cột nội dung */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Tech Trends */}
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle
                            className="text-sm font-bold flex items-center gap-2 uppercase tracking-wider text-blue-600">
                            <Zap size={16}/> Tech Trends
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                        {report.tech_trends.map((trend, i) => (
                            <div key={i} className="text-sm">
                                <div className="font-bold">{trend.name}</div>
                                <div className="text-muted-foreground">{trend.update}</div>
                            </div>
                        ))}
                    </CardContent>
                </Card>

                {/* Employment Status */}
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle
                            className="text-sm font-bold flex items-center gap-2 uppercase tracking-wider text-green-600">
                            <Users size={16}/> Employment Status
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm">
                        <p><strong>Thị trường:</strong> {report.employment_status.market}</p>
                        <p><strong>Nhu cầu:</strong> {report.employment_status.demand}</p>
                    </CardContent>
                </Card>

                {/* Job Intelligence */}
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle
                            className="text-sm font-bold flex items-center gap-2 uppercase tracking-wider text-purple-600">
                            <Briefcase size={16}/> Job Intelligence
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm">
                        <p><strong>Lương:</strong> {report.job_details.salary}</p>
                        <div className="flex flex-wrap gap-1 mt-1">
                            {report.job_details.skills.map(s => (
                                <Badge key={s} variant="outline" className="text-[10px]">{s}</Badge>
                            ))}
                        </div>
                    </CardContent>
                </Card>

                {/* Research Library */}
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle
                            className="text-sm font-bold flex items-center gap-2 uppercase tracking-wider text-orange-600">
                            <BookOpen size={16}/> Research Library
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                        {report.research_articles.map((art, i) => (
                            <a key={i} href={art.url} target="_blank"
                               className="text-sm flex items-center justify-between hover:text-blue-600 underline decoration-dotted">
                                <span className="line-clamp-1">{art.title}</span>
                                <ExternalLink size={12} className="shrink-0 ml-2"/>
                            </a>
                        ))}
                    </CardContent>
                </Card>
            </div>

            {/* Sources Footer */}
            <div className="pt-4 border-t text-[10px] text-muted-foreground flex justify-between">
                <div className="flex gap-2">
                    Nguồn trích dẫn: {report.sources.map((s, i) => <span key={i}
                                                                         className="hover:underline cursor-pointer">[{i + 1}]</span>)}
                </div>
                <div>Cập nhật gần nhất: {report.last_updated}</div>
            </div>
        </div>
    );
}
;

export default ResearchReportCard;
