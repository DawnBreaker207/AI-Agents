import React from 'react';
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from '~/components/ui/card';
import type {ResearchReport} from "~/types";


const sentimentStyles: Record<string, string> = {
    'Tích cực': 'bg-green-100 text-green-800',
    'Tiêu cực': 'bg-red-100 text-red-800',
    'Trung tính': 'bg-blue-100 text-blue-800',
};

const ResearchReportCard: React.FC<{ report: ResearchReport }> = ({report}) => {
    const [dateString, setDateString] = React.useState<string>("");
    React.useEffect(() => {
        setDateString(new Date(report.created_at).toLocaleString('vi-VN'));
    }, [report.created_at]);

    return (
        <Card className="hover:shadow-lg transition-shadow duration-300">
            <CardHeader>
                <div className="flex justify-between items-start gap-2">
                    <CardTitle className="text-xl font-bold text-indigo-900 leading-tight">
                        {report.title}
                    </CardTitle>
                    <span
                        className={`text-[10px] px-2 py-1 rounded-full border ${sentimentStyles[report.sentiment] || sentimentStyles['Không xác định']}`}>
                        {report.sentiment}
                    </span>
                </div>
                <CardDescription className="text-xs italic">
                    Ngày tạo: {dateString || "Đang tải..."}
                </CardDescription>
            </CardHeader>

            <CardContent className="space-y-4">
                {/* Categories & Regions Badges */}
                <div className="flex flex-wrap gap-1">
                    {report.categories?.map(cat => (
                        <span key={cat} className="bg-indigo-50 text-indigo-600 text-[10px] px-2 py-0.5 rounded">
                            {cat}
                        </span>
                    ))}
                </div>

                {report.summary && (
                    <p className="text-sm text-gray-600 line-clamp-3 leading-relaxed">
                        {report.summary}
                    </p>
                )}

                {/* Hiển thị Key Points nếu có */}
                {report.key_points && report.key_points.length > 0 && (
                    <div className="pt-2">
                        <h4 className="text-xs font-bold text-gray-500 uppercase mb-2">Điểm chính:</h4>
                        <ul className="text-sm space-y-1">
                            {report.key_points.slice(0, 3).map((point, i) => (
                                <li key={i} className="flex gap-2">
                                    <span className="text-indigo-400">•</span>
                                    <span className="text-gray-700 line-clamp-1">{point}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </CardContent>
        </Card>
    );
};

export default ResearchReportCard;
