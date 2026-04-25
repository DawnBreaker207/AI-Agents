import {Link} from "react-router";

import type {ResearchReport} from "~/types";
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "~/components/ui/card";
import {Button} from "~/components/ui/button";

export function ReportCard({report}: { report: ResearchReport }) {
    return (
        <Card className="h-full flex flex-col hover:border-indigo-400 transition-colors">
            <CardHeader>
                <CardTitle className="line-clamp-2">
                    {/* Đường dẫn khớp với cấu hình trong routes.ts */}
                    <Link to={`/reports/${report.id}`} className="hover:underline">
                        {report.title}
                    </Link>
                </CardTitle>
                <CardDescription className="line-clamp-3">
                    {report.summary}
                </CardDescription>
            </CardHeader>
            <CardContent className="mt-auto">
                <Button variant="link" asChild className="p-0 text-indigo-600">
                    <Link to={`/reports/${report.id}`}>Xem chi tiết →</Link>
                </Button>
            </CardContent>
        </Card>
    );
}